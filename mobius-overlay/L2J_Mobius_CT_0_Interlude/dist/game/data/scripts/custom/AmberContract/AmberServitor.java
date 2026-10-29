package custom.AmberContract;

import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.instance.Servitor;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.entity.item.Weapon;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.ai.CreatureAI;
import org.l2jmobius.gameserver.ai.SummonAI;

/** No hero item is equipped: weapon is cosmetic and bow timing comes from this actor. */
public class AmberServitor extends Servitor
{
    volatile boolean charging;
    private long nextBowAttackNanos;
    private java.util.concurrent.Future<?> bowRetry;
    private volatile Creature forcedTarget;
    boolean isForcedTarget(Creature target){return target!=null&&forcedTarget==target;}
    void clearForcedTarget(){forcedTarget=null;}
    final AmberAssist assist=new AmberAssist(this);
    public AmberServitor(NpcTemplate template,Player owner){super(template,owner);}
    @Override protected CreatureAI initAI()
    {
        return new SummonAI(this){
        @Override public void setIntentionAttack(WorldObject object){
            Creature target=object==null?null:object.asCreature();
            if(target!=null&&(target.isDoor()||target.isNpc()&&calculateDistance3D(target)<=getPhysicalAttackRange())){
                // Native SummonAI demands a path into the target's center. A closed gate
                // deliberately blocks that path, although its near face is a valid bow target.
                // An NPC already within bow range also needs visibility, not a walkable endpoint.
                // Keep native thinkAttack, movement offsets, bow cadence, packets and damage.
                if(charging||isOutOfControl()||isControlBlocked()||!isSpawned()
                    ||!AmberContract.validVictim(getOwner(),AmberServitor.this,target)
                    ||!org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance().canSeeTarget(AmberServitor.this,target))return;
                if(getIntention()==org.l2jmobius.gameserver.ai.Intention.CAST)return;
                _intention=org.l2jmobius.gameserver.ai.Intention.ATTACK;setAttackTarget(target);stopFollow();
                var next=getNextAction();if(next!=null&&next.isRemovedBy(org.l2jmobius.gameserver.ai.Intention.ATTACK))setNextAction(null);
                notifyActionThink();return;
            }
            super.setIntentionAttack(object);
        }
        @Override public void notifyFollowStatusChange(){
            synchronized(AmberContract.session(getOwner())){
                if(charging)return;
                clearForcedTarget();
                if(assist!=null)assist.enable(false);
                abortAttack();super.notifyFollowStatusChange();setStartFollowController(true);setFollowStatus(true);
            }
        }};
    }
    @Override public void doSummonAttack(WorldObject target)
    {
        synchronized(AmberContract.session(getOwner())){
            Creature victim=target==null?null:target.asCreature();
            if(charging||!AmberContract.validVictim(getOwner(),this,victim))return;
            if(forcedTarget!=victim)clearForcedTarget();
            assist.manualFocus(victim);super.doSummonAttack(target);
        }
    }
    void assistAttack(Creature target){super.doSummonAttack(target);}
    @Override public void cancelAction()
    {
        synchronized(AmberContract.session(getOwner())){
            if(charging)return;
            clearForcedTarget();
            if(assist!=null)assist.enable(false);
            abortAttack();super.cancelAction();
        }
    }
    @Override public void doCast(Skill skill)
    {
        if(skill.getId()==AmberContract.FIRE||skill.getId()==AmberContract.RAIN){assist.manualSkill();AmberContract.order(this,skill.getId());if(skill.getId()==AmberContract.FIRE)getAI().notifyActionFinishCasting();return;}
        super.doCast(skill);
    }
    @Override public void storeEffect(boolean save){getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,AmberContract.FIRE_BUFF);super.storeEffect(false);}
    /** Cosmetic variant switch: preserve actor, HP/MP, effects, shots and reuse state. */
    void applyVisualTemplate(NpcTemplate model)
    {
        if(!AmberModelVariants.isTemplate(model.getId()))throw new IllegalArgumentException("Unknown Amber model");
        setTemplate(model);
        broadcastPacket(new org.l2jmobius.gameserver.network.serverpackets.DeleteObject(this));
        org.l2jmobius.gameserver.entity.World.forEachVisibleObject(this,Player.class,observer->{if(observer!=getOwner())sendInfo(observer);});
        sendInfo(getOwner());
    }
    @Override public int getWeapon(){return 6619;}
    // One complete bow preparation per shot, without the old extra idle reload.
    @Override public int calculateReuseTime(Weapon unused){return 0;}
    @Override public boolean isMovementDisabled(){return charging||super.isMovementDisabled();}
    @Override public boolean canAttack(boolean ctrlPressed)
    {
        if(charging){getOwner().sendMessage("Amber esta cargando la lluvia.");return false;}
        Creature victim=getOwner().getTarget()==null?null:getOwner().getTarget().asCreature();
        String reason=AmberContract.targetRejection(getOwner(),this,victim,ctrlPressed);
        if(reason!=null){getOwner().sendMessage("Amber: "+reason);return false;}
        if(victim!=null&&victim.isDoor()){
            if(isBetrayed()||isLockedTarget()||isControlBlocked()||getOwner().calculateDistance3D(victim)>3000
                ||!org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance().canSeeTarget(this,victim))return false;
        }else if(!super.canAttack(ctrlPressed))return false;
        forcedTarget=ctrlPressed?victim:null;
        return true;
    }
    @Override public synchronized void doAttack(Creature target)
    {
        if(charging||getOwner().isDead()||getOwner().isInvul()||isBetrayed()||!AmberContract.validVictim(getOwner(),this,target))return;
        long started=System.nanoTime();
        // Repeated manual orders and native ready-to-act callbacks share the same deadline.
        if(started<nextBowAttackNanos){
            // A native ready callback can arrive before the complete bow preparation.
            // Leaving ATTACK armed without a new callback stalls autonomous shooting.
            if(bowRetry==null||bowRetry.isDone())bowRetry=ThreadPool.schedule(()->{
                synchronized(AmberServitor.this){bowRetry=null;
                    if(isSpawned()&&!isDead()&&!charging&&getOwner().getSummon()==AmberServitor.this
                        &&getAI().getIntention()==org.l2jmobius.gameserver.ai.Intention.ATTACK)
                        getAI().notifyActionReadyToAct();
                }
            },Math.max(1,java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(nextBowAttackNanos-started)+1));
            return;
        }
        int preparation=calculateTimeBetweenAttacks();
        long before=getAttackEndTime();boolean fire=getEffectList().getBuffInfoBySkillId(AmberContract.FIRE_BUFF)!=null;
        super.doAttack(target);
        if(getAttackEndTime()>before)nextBowAttackNanos=started+java.util.concurrent.TimeUnit.MILLISECONDS.toNanos(preparation);
        if(fire&&getAttackEndTime()>before)
        {
            setHeading(org.l2jmobius.gameserver.util.LocationUtil.calculateHeadingFrom(this,target));
            int level=fireVisualLevel(calculateDistance2D(target));
            int flightMs=(int)Math.round(level*50.0/1400*1000);
            int delay=Math.max(0,calculateTimeBetweenAttacks()-flightMs);
            long sequence=getAttackEndTime();
            // The native Attack packet remains responsible for the actual arrow, hit/miss and damage.
            // Start the cosmetic fire tracer at release, then let it end near the native impact time.
            ThreadPool.schedule(()->{
                if(isSpawned()&&!isDead()&&!charging&&getOwner().getSummon()==this&&getAttackEndTime()==sequence)
                    {
                    broadcastPacket(new MagicSkillUse(this,target,19009,level,0,0));
                }
            },delay);
        }
    }
    static int fireVisualLevel(double distance){return Math.max(1,Math.min(16,(int)Math.ceil(Math.max(0,distance-20)/50)));}
    @Override public boolean doDie(Creature killer){assist.enable(false);var s=AmberContract.SESSIONS.get(getOwner().getObjectId());if(s!=null)s.cancel();return super.doDie(killer);}
    @Override public void unSummon(Player owner)
    {
        assist.enable(false);var s=AmberContract.SESSIONS.get(owner.getObjectId());if(s!=null)s.cancel();setRestoreSummon(false);super.unSummon(owner);
        owner.getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,AmberContract.FIRE_INDICATOR);
        if(owner.getSummon()==this){owner.setPet(null);deleteMe();}
    }
}
