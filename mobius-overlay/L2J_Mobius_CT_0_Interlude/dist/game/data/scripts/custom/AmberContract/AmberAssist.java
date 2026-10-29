package custom.AmberContract;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.mechanics.effects.EffectFlag;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType;
import org.l2jmobius.gameserver.mechanics.stats.Stat;

/** Server-side assistant. Uses ordinary bow attacks and the contract's resource/reuse checks. */
final class AmberAssist
{
    static final int SCAN_RANGE=1100, LEASH=1200;
    private final AmberServitor amber;
    private final Player owner;
    private final Map<Integer,Observation> observations=new ConcurrentHashMap<>();
    private final Map<Integer,Threat> threats=new ConcurrentHashMap<>();
    private final Map<SupportKey,Support> supporters=new ConcurrentHashMap<>();
    private static final long THREAT_MS=6000;
    private volatile boolean enabled=false;
    private volatile Creature focus,current;
    private long lastSwitch;
    private volatile long manualSkillUntil;

    AmberAssist(AmberServitor amber){this.amber=amber;owner=amber.getOwner();}
    boolean enabled(){return enabled;}
    String status(){return enabled?"Asistencia IA"+(focus!=null?" / foco manual":""):"Manual";}
    void enable(boolean value)
    {
        if(value)
        {
            if(!owner.isAffectedBySkill(AmberContract.ASSIST))
                SkillData.getInstance().getSkill(AmberContract.ASSIST,1).applyEffects(owner,owner);
        }
        else
        {
            owner.getEffectList().stopSkillEffects(SkillFinishType.REMOVED,AmberContract.ASSIST);
            setEnabled(false);
        }
    }
    // Called by the native toggle effect, never reapplies or removes that effect.
    void setEnabled(boolean value)
    {
        boolean changed=enabled!=value;
        if(changed)amber.clearForcedTarget();
        enabled=value;focus=null;current=null;observations.clear();threats.clear();supporters.clear();
        if(changed&&!amber.charging){amber.abortAttack();amber.setFollowStatus(true);}
        if(changed)AmberContract.LOG.info("AMBER_AI "+owner.getName()+" mode="+(value?"assist":"manual"));
    }
    void manualFocus(Creature target){focus=target;current=target;lastSwitch=System.currentTimeMillis();}
    void manualSkill(){manualSkillUntil=System.currentTimeMillis()+6000;}
    void damaged(Creature attacker,Creature target,double damage)
    {
        if(!enabled||attacker==null||damage<=0||!protectedActor(target)||attacker.asPlayer()==owner
            ||!AmberContract.validVictim(owner,amber,attacker)||owner.calculateDistance3D(attacker)>SCAN_RANGE)return;
        long now=System.currentTimeMillis();boolean ownerHit=target==owner;
        rememberThreat(attacker,damage,ownerHit,now);
        // A hostile summon and its master belong to the same fight. This also links healing and TP.
        if(attacker.isSummon())rememberThreat(attacker.asSummon().getOwner(),damage,ownerHit,now);
    }
    private void rememberThreat(Creature attacker,double damage,boolean ownerHit,long now)
    {
        threats.compute(attacker.getObjectId(),(id,previous)->{
            boolean recent=previous!=null&&now-previous.time<THREAT_MS;
            return new Threat(now,Math.min(5000,damage+(recent?previous.damage:0)),ownerHit||recent&&previous.ownerHit);
        });
    }
    private Threat threat(Creature target,long now)
    {
        if(target==null)return null;
        Threat threat=threats.get(target.getObjectId());
        if(threat!=null&&now-threat.time<THREAT_MS)return threat;
        if(target.isSummon())
        {
            threat=threats.get(target.asSummon().getOwner().getObjectId());
            if(threat!=null&&now-threat.time<THREAT_MS)return threat;
        }
        return null;
    }
    void healed(Creature healer,Creature recipient,double restored)
    {
        if(!enabled||restored<=0||healer==null||recipient==null||healer==recipient||healer.asPlayer()==owner
            ||owner.calculateDistance3D(healer)>SCAN_RANGE||healer.getInstanceId()!=owner.getInstanceId())return;
        long now=System.currentTimeMillis();
        if(threat(recipient,now)==null||!AmberContract.validVictim(owner,amber,recipient))return;
        supporters.compute(new SupportKey(healer.getObjectId(),recipient.getObjectId()),(key,previous)->
            new Support(now,recipient,Math.min(6000,restored+(previous!=null&&now-previous.time<THREAT_MS?previous.restored:0))));
    }
    boolean protectedActor(Creature actor)
    {
        if(actor==null)return false;
        if(custom.LabCombatPilots.LabCombatPilots.isCombatOpponent(owner,actor))return false;
        Player player=actor.isSummon()?actor.asSummon().getOwner():actor.asPlayer();
        return player==owner||player!=null&&(owner.isInParty()&&player.isInParty()&&owner.getParty()==player.getParty()
            ||owner.getClanId()!=0&&(owner.getClanId()==player.getClanId()||owner.getAllyId()!=0&&owner.getAllyId()==player.getAllyId()));
    }
    boolean eligible(Creature target)
    {
        return target!=null&&(target.isPlayer()||target.isSummon()||target.isMonster()||target.isDoor()
            ||target instanceof org.l2jmobius.gameserver.entity.actor.Tower
            ||target.isAttackable()&&(target==focus||target.isAutoAttackable(owner)))&&target.isSpawned()&&!target.isInvisible()
            &&!owner.isSiegeFriend(target)
            &&(!protectedActor(target)||target==focus||threat(target,System.currentTimeMillis())!=null)
            &&AmberContract.validVictim(owner,amber,target)&&owner.calculateDistance3D(target)<=SCAN_RANGE
            &&Math.abs(amber.getZ()-target.getZ())<=150&&amber.calculateDistance3D(target)<=LEASH
            &&GeoEngine.getInstance().canSeeTarget(amber,target);
    }
    double score(Creature target,long now)
    {
        double score=150-owner.calculateDistance3D(target)*0.10;
        // A modest summon preference; an actual attacker is more important than a harmless summon.
        if(target.isSummon())score+=35;
        if(defending(target))score-=180; // UD/Vengeance: a motionless tank is not necessarily a profitable target.
        if(target.hasAI())
        {
            if(protectedActor(target.getAI().getAttackTarget()))score+=150;
            if(target.isCastingNow()&&protectedActor(target.getAI().getCastTarget()))score+=180;
        }
        double transferPriority=transferPainPriority(target,now);
        double summonPriority=preventTransferPriority(target,now)+transferPriority;
        Threat threat=threats.get(target.getObjectId());
        if(threat!=null&&now-threat.time>=THREAT_MS)threat=null;
        if(threat==null&&summonPriority>0)threat=threat(target,now);
        if(threat!=null)
        {
            score+=(threat.ownerHit?260:120)+Math.min(120,threat.damage/25);
            // At critical owner HP, stopping the actual attacker takes precedence over dismantling support.
            if(threat.ownerHit&&owner.getCurrentHp()/Math.max(1,owner.getMaxHp())<0.30
                &&threats.containsKey(target.getObjectId()))score+=650;
        }
        score+=summonPriority+healerPriority(target,now);
        score+=30*(1-target.getCurrentHp()/Math.max(1,target.getMaxHp()));
        if(target.isDoor())score+=200+Math.min(600,custom.GiranSiegeLab.GiranRules.doorSupport(owner,(org.l2jmobius.gameserver.entity.actor.instance.Door)target)*120);
        else if(target.isAttackable()){
            score+=Math.min(70,7000/Math.max(1,target.getPDef(amber)));
            int[] neighbors={0};World.forEachVisibleObjectInRange(target,Creature.class,200,other->{if(other!=target&&other.isAttackable()&&!other.isDead()&&AmberContract.validVictim(owner,amber,other))neighbors[0]++;});
            if(neighbors[0]==0)score+=45;
        }
        if(target==current)score+=35; // Avoid switching after every shot.
        return score;
    }
    double transferPainPriority(Creature target,long now)
    {
        if(!target.isSummon()||target.getCurrentHp()<=1)return 0;
        Player enemy=target.asSummon().getOwner();
        if(!enemy.hasServitor()||enemy.getSummon()!=target||enemy.calculateDistance3D(target)>1000
            ||!eligible(enemy)||threat(enemy,now)==null)return 0;
        double transfer=enemy.getStat().calcStat(Stat.TRANSFER_DAMAGE_PERCENT,0,null,null);
        if(transfer<=0)return 0;
        // Compare approximate bow effort, including the player's CP. This is a heuristic, not a damage promise.
        double summonEffort=target.getCurrentHp()*Math.max(1,target.getPDef(amber));
        double playerEffort=(enemy.getCurrentHp()+enemy.getCurrentCp())*Math.max(1,enemy.getPDef(amber));
        return Math.min(300,transfer*4)+Math.max(-200,Math.min(120,120*(1-summonEffort/Math.max(1,playerEffort))));
    }
    double preventTransferPriority(Creature target,long now)
    {
        if(!target.isSummon())return 0;
        Player enemy=target.asSummon().getOwner();
        // Preventive removal: the aggressor need not have activated TP yet, or stand in transfer range.
        if(!enemy.hasServitor()||enemy.getSummon()!=target||!eligible(enemy)||threat(enemy,now)==null)return 0;
        return 150;
    }
    double healerPriority(Creature target,long now)
    {
        double best=0;
        for(var entry:supporters.entrySet())
        {
            Support support=entry.getValue();Threat threat=threat(support.recipient,now);
            if(entry.getKey().healer!=target.getObjectId()||now-support.time>=THREAT_MS||threat==null
                ||!eligible(support.recipient))continue;
            double bonus=(threat.ownerHit?250:120)+Math.min(450,support.restored/8);
            best=Math.max(best,bonus);
        }
        return best;
    }
    void observe(Creature target,long now)
    {
        observations.computeIfAbsent(target.getObjectId(),id->new Observation(target,now)).update(target,now);
    }
    String rainReason(Creature target,long now)
    {
        if(target!=null&&target.isDoor())return null; // Native bow damage only: no area-damage bypass against siege structures.
        if(!eligible(target)||amber.calculateDistance3D(target)>900)return null;
        if(defending(target))
        {
            // UD immobilizes through ImmobileBuff, not a hostile Root/Paralyze flag.
            if(target.isImmobilized())for(int id:new int[]{110,368})
            {
                var info=target.getEffectList().getBuffInfoBySkillId(id);
                if(info!=null&&info.isInUse()&&!info.isRemoved()&&info.getTime()>=7)return "ud>=6s";
            }
            return null;
        }
        if(target.isMoving())return null;
        int holdMask=EffectFlag.ROOTED.getMask()|EffectFlag.STUNNED.getMask()|EffectFlag.PARALYZED.getMask();
        if(target.isRooted()||target.isStunned()||target.isParalyzed())
            for(var info:target.getEffectList().getDebuffs())
                // getTime rounds the elapsed seconds down; 7 displayed seconds guarantee at least 6 real ones.
                if(info.isInUse()&&!info.isRemoved()&&info.getTime()>=7)
                    for(var effect:info.getEffects())if((effect.getEffectFlags()&holdMask)!=0)return "held>=6s";
        Observation observation=observations.get(target.getObjectId());
        // Standing still is a prediction, not a guarantee. Require a longer observation for idle enemies.
        if(observation!=null&&now-observation.stillSince>=3000
            &&(target.isCastingNow()||target.isAttackingNow()||now-observation.stillSince>=5000))return "stationary";
        return null;
    }
    static boolean defending(Creature target)
    {
        for(int id:new int[]{110,368})
        {
            var info=target.getEffectList().getBuffInfoBySkillId(id);
            if(info!=null&&info.isInUse()&&!info.isRemoved()&&info.getTime()>0)return true;
        }
        return false;
    }
    record RainChoice(Creature target,String reason,double value){}
    RainChoice chooseRain(List<Creature> candidates,long now)
    {
        List<Creature> anchors=focus!=null&&eligible(focus)?List.of(focus):candidates;
        boolean heldAvailable=false;
        for(Creature target:anchors)if("held>=6s".equals(rainReason(target,now))){heldAvailable=true;break;}
        RainChoice best=null,bestUd=null;
        for(Creature target:anchors)
        {
            if(target.isDoor()||!eligible(target)||amber.calculateDistance3D(target)>900)continue;
            String reason=rainReason(target,now);
            if(heldAvailable&&!"held>=6s".equals(reason))continue;
            if(reason==null)
            {
                // A dense group is an opportunity even without a guaranteed hold; retain the escape risk.
                int nearby=0;for(Creature other:candidates)if(!other.isDoor()&&target.calculateDistance3D(other)<=175)nearby++;
                if(nearby<3||defending(target))continue;
                reason="cluster";
            }
            double value=0;
            for(Creature other:candidates)
            {
                if(other.isDoor())continue;
                double distance=target.calculateDistance2D(other);
                if(distance>200||Math.abs(target.getZ()-other.getZ())>100)continue;
                String control=rainReason(other,now);
                boolean secure="held>=6s".equals(control)||"ud>=6s".equals(control);
                // Heuristic weights, not calibrated hit probabilities. CC and UD are less risky than motion.
                double confidence=secure?0.95:other.isMoving()?0.12:"stationary".equals(control)?0.60:0.40;
                if(!secure)confidence*=Math.max(0.20,1-distance/240);
                double element=AmberContract.attributeBonus(amber.getAttackElementValue(amber.getAttackElement()),other.getDefenseElementValue(amber.getAttackElement()));
                double power=SkillData.getInstance().getSkill(AmberContract.RAIN,1).getPower(amber,other,amber.isPlayable()&&other.isPlayable(),amber.isPlayable()&&other.isAttackable());
                value+=76*(amber.getPAtk(other)*2+power)/Math.max(1,other.getPDef(amber))*element*confidence;
            }
            RainChoice choice=new RainChoice(target,reason,value);
            if("ud>=6s".equals(reason)){if(bestUd==null||value>bestUd.value())bestUd=choice;}
            else if(best==null||value>best.value())best=choice;
        }
        // Prefer a known stationary UD when no hostile hold is available. A substantially better group can justify the risk.
        if(bestUd!=null&&(best==null||best.value()<bestUd.value()*2))return bestUd;
        return best;
    }
    private boolean ready(int skill,long now)
    {
        return now>=manualSkillUntil&&owner.getVariables().getLong("AMBER_REUSE_"+skill,0)<=now
            &&!amber.isSkillDisabled(amber.getKnownSkill(skill));
    }
    void tick()
    {
        if(!enabled)return;
        long now=System.currentTimeMillis();
        threats.values().removeIf(threat->now-threat.time>THREAT_MS);
        supporters.values().removeIf(support->now-support.time>THREAT_MS);
        observations.values().removeIf(observation->now-observation.seen>2000);
        if(!amber.isSpawned()||amber.isDead()||owner.isDead()||owner.isInvul()||owner.isMounted()
            ||owner.isInDuel()||owner.isInOlympiadMode()||!AmberContract.contracted(owner)
            ||owner.getInstanceId()!=amber.getInstanceId())
        {stopCombat();return;}
        if(amber.isBetrayed()||amber.isLockedTarget()||amber.isControlBlocked()||amber.isConfused()||amber.isStunned()||amber.isParalyzed()
            ||amber.isSleeping()||amber.isMuted()||amber.isAllSkillsDisabled()||amber.charging||amber.isCastingNow())return;
        if(amber.getAI().getIntention()==Intention.CAST)return; // Do not steal a queued native skill order.
        if(amber.getAI().getIntention()==Intention.MOVE_TO)return; // Move has priority; the toggle remains armed after arrival.
        if(owner.calculateDistance3D(amber)>LEASH){focus=null;stopCombat();return;}
        List<Creature> candidates=new ArrayList<>();
        World.forEachVisibleObjectInRange(owner,Creature.class,SCAN_RANGE,target->{
            if(eligible(target)){candidates.add(target);observe(target,now);}
        });
        if(!eligible(focus))focus=null;
        Creature chosen=focus;
        if(chosen==null)
        {
            double best=Double.NEGATIVE_INFINITY;
            for(Creature target:candidates){double value=score(target,now);if(value>best){chosen=target;best=value;}}
            // Keep ordinary shot stability, but a substantially greater defensive priority can interrupt it.
            if(chosen!=null&&eligible(current)&&now-lastSwitch<2500&&score(chosen,now)<score(current,now)+100)chosen=current;
        }
        if(chosen==null){stopCombat();return;}
        if(chosen!=current)
        {
            current=chosen;lastSwitch=now;
            AmberContract.LOG.info("AMBER_AI "+owner.getName()+" target="+chosen.getObjectId()+":"+chosen.getName()
                +" summon="+chosen.isSummon()+" score="+(int)score(chosen,now)
                +" reason="+(focus!=null?"manual":healerPriority(chosen,now)>0?"enemy-healer":preventTransferPriority(chosen,now)>0?"deny-transfer-pain":threat(chosen,now)!=null?"protect-owner":"opportunity"));
        }
        // Activate fire before a rain so its launch captures the enchant. Keep 120 MP in reserve.
        if(ready(AmberContract.FIRE,now)&&amber.getCurrentMp()>=180
            &&amber.getEffectList().getBuffInfoBySkillId(AmberContract.FIRE_BUFF)==null&&amber.calculateDistance3D(chosen)<=900)
            if(AmberContract.automaticOrder(amber,AmberContract.FIRE,chosen))
                AmberContract.LOG.info("AMBER_AI "+owner.getName()+" skill=fire target="+chosen.getObjectId());
        AmberContract.Session session=AmberContract.session(owner);
        if(!chosen.isDoor()&&ready(AmberContract.RAIN,now)&&amber.getCurrentMp()>=120&&session.marker==null
            &&owner.getInventory().getInventoryItemCount(AmberContract.SHOTS,-1)>=3)
        {
            RainChoice choice=chooseRain(candidates,now);
            if(choice!=null&&AmberContract.automaticOrder(amber,AmberContract.RAIN,choice.target()))
            {
                AmberContract.LOG.info("AMBER_AI "+owner.getName()+" skill=rain target="+choice.target().getObjectId()+" reason="+choice.reason()+" estimate="+(int)choice.value());
                return;
            }
        }
        if(amber.getAI().getIntention()!=Intention.ATTACK||amber.getAI().getAttackTarget()!=chosen)
        {amber.abortAttack();amber.assistAttack(chosen);}
    }
    private void stopCombat()
    {
        focus=null;current=null;
        if(amber.charging){AmberContract.session(owner).cancel();}
        if(amber.getAI().getIntention()==Intention.ATTACK||!amber.getFollowStatus())
        {amber.abortAttack();amber.setTarget(null);amber.setFollowStatus(true);}
    }
    private record Threat(long time,double damage,boolean ownerHit){}
    private record SupportKey(int healer,int recipient){}
    private record Support(long time,Creature recipient,double restored){}
    private static final class Observation
    {
        int x,y,z;long stillSince,seen;
        Observation(Creature target,long now){x=target.getX();y=target.getY();z=target.getZ();stillSince=seen=now;}
        void update(Creature target,long now)
        {
            if(target.isMoving()||Math.hypot(target.getX()-x,target.getY()-y)>12||Math.abs(target.getZ()-z)>20)
            {stillSince=now;x=target.getX();y=target.getY();z=target.getZ();}
            seen=now;
        }
    }
}
