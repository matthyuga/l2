package custom.AmberContract;

import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.logging.Level;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.enums.ShotType;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.handler.ItemHandler;
import org.l2jmobius.gameserver.handler.BypassHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.clientpackets.RequestActionUse;

/** Opt-in tests with two reserved headless Players in a private Coliseum instance. */
public class AmberContractVerification extends Script
{
    private int checks;
    public AmberContractVerification(){if(Boolean.getBoolean("lab.amber.verify"))ThreadPool.schedule(Boolean.getBoolean("lab.amber.protection.only")?this::verifyProtectionOnly:Boolean.getBoolean("lab.amber.targets.only")?this::verifyTargetsOnly:this::verify,30000);}
    private void check(boolean ok,String message){if(!ok)throw new IllegalStateException(message);checks++;}
    private void verifyProtectionOnly()
    {
        Player p=null,t=null,h=null;int instanceId=0;
        try
        {
            instanceId=InstanceManager.getInstance().createDynamicInstance(0).getId();
            p=probe("AmberOwnerProbe",103,instanceId);t=probe("AmberTargetProbe",90,instanceId);h=probe("AmberHealerProbe",97,instanceId);
            p.getVariables().set(AmberContract.CONTRACT,true);AmberContract.grant(p);resetReuse(p,AmberContract.INVOKE);
            AmberContract.order(p,AmberContract.INVOKE);AmberServitor a=(AmberServitor)p.getSummon();a.assist.enable(false);
            h.setXYZ(p.getX()-400,p.getY(),p.getZ());h.revalidateZone(true);h.setInsideZone(ZoneId.PVP,true);
            verifyTargetPolicy(p,t,a);verifyProtection(p,t,h,a);
            if(Boolean.getBoolean("lab.amber.ui.rain"))verifyUiRain(p,t,a);
            if(Boolean.getBoolean("lab.amber.cadence"))verifyCadence(p,t,h,a);
            AmberContract.LOG.info(verificationName()+" SUCCESS: "+checks+" checks; actual damage retaliation, TP, healing, direct UI filters/toggle, rain skill damage/resources, continuous bow cadence and native defenses.");
        }
        catch(Exception e){AmberContract.LOG.log(Level.SEVERE,verificationName()+" FAILED after "+checks+" checks",e);}
        finally
        {
            if(p!=null){p.getVariables().set(AmberContract.CONTRACT,false);AmberContract.cleanup(p);AmberContract.revokeSavedEffects(p);p.storeMe();p.deleteMe();p.setLabControlled(false);p.setOnlineStatus(false,true);}
            for(Player actor:new Player[]{t,h})if(actor!=null){actor.stopAllEffects();actor.stopPvPFlag();actor.storeMe();actor.deleteMe();actor.setLabControlled(false);actor.setOnlineStatus(false,true);}
            if(instanceId!=0)InstanceManager.getInstance().destroyInstance(instanceId);
        }
    }
    private static String verificationName(){return Boolean.getBoolean("lab.amber.cadence")?"AmberCadenceVerification":Boolean.getBoolean("lab.amber.ui.rain")?"AmberUiRainVerification":"AmberProtectionVerification";}
    private void verifyCadence(Player p,Player t,Player h,AmberServitor a)throws Exception
    {
        Object reserve=new Object();
        t.addStatFunc(new org.l2jmobius.gameserver.mechanics.stats.functions.FuncAdd(org.l2jmobius.gameserver.mechanics.stats.Stat.MAX_HP,0x40,reserve,100000,null));
        var launches=new java.util.concurrent.CopyOnWriteArrayList<Long>();
        var hits=new java.util.concurrent.atomic.AtomicInteger();
        var attackListener=new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_ATTACK,(org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureAttack e)->{
            if(e.getAttacker()==a&&e.getTarget()==t)launches.add(System.nanoTime());
        },this);
        var damageListener=new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,(OnCreatureDamageDealt e)->{
            if(e.getAttacker()==a&&e.getTarget()==t&&e.getDamage()>0)hits.incrementAndGet();
        },this);
        Containers.Global().addListener(attackListener);Containers.Global().addListener(damageListener);
        try
        {
            synchronized(AmberContract.session(p))
            {
                a.assist.enable(false);a.stopAllEffects();a.fullRestore();a.setCurrentMp(0);p.setInvul(false);p.fullRestore();t.stopAllEffects();t.fullRestore();t.setInvul(false);
                a.setXYZ(p.getX(),p.getY(),p.getZ());t.setXYZ(p.getX()+200,p.getY(),p.getZ());h.setXYZ(p.getX()+3000,p.getY(),p.getZ());
                t.stopMove(null);t.abortAttack();t.getAI().setIntentionIdle();p.setTarget(null);
                check(a.calculateReuseTime(null)==0,"Amber no longer adds an idle reload after the complete bow preparation");
                a.assist.enable(true);
            }
            int preparation=a.calculateTimeBetweenAttacks();long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.MILLISECONDS.toNanos(preparation*7L+2500);
            while(launches.size()<5&&System.nanoTime()<deadline){p.fullRestore();t.fullRestore();Thread.sleep(20);}
            check(launches.size()>=5,"Assistance launches five consecutive native bow shots without any manual attack order");
            long[] auto=launches.stream().mapToLong(Long::longValue).toArray();
            check(cadenceBounds(auto,preparation),"Automatic cadence follows one full preparation, without the old extra reload");
            check(a.assist.enabled()&&p.getTarget()==null,"Continuous assistance leaves owner target unset");
            check(hits.get()>0,"Autonomous continuous shots land real native damage");
            synchronized(AmberContract.session(p)){a.assist.enable(false);a.cancelAction();}
            Thread.sleep(preparation+150);launches.clear();p.setTarget(t);
            deadline=System.nanoTime()+java.util.concurrent.TimeUnit.MILLISECONDS.toNanos(preparation*7L+2500);
            while(launches.size()<5&&System.nanoTime()<deadline){a.doSummonAttack(t);p.fullRestore();t.fullRestore();Thread.sleep(20);}
            check(launches.size()>=5,"Repeated manual commands also produce continuous native shots");
            long[] manual=launches.stream().mapToLong(Long::longValue).toArray();
            check(cadenceBounds(manual,preparation),"Spamming manual Attack cannot bypass the complete shot preparation");
            double autoMs=meanGap(auto),manualMs=meanGap(manual);
            check(Math.abs(autoMs-manualMs)<preparation*0.15,"Manual and autonomous sustained cadence are equal within scheduler tolerance");
            synchronized(AmberContract.session(p)){a.charging=true;}
            int before=launches.size();long until=System.nanoTime()+java.util.concurrent.TimeUnit.MILLISECONDS.toNanos(preparation+200);
            while(System.nanoTime()<until){a.doSummonAttack(t);a.assist.tick();Thread.sleep(20);}
            check(launches.size()==before,"Rain charging blocks all continuous or repeated attack launches even after the shot deadline");
            synchronized(AmberContract.session(p)){a.charging=false;a.cancelAction();}
            Thread.sleep(preparation+200);check(launches.size()==before&&!a.assist.enabled(),"Stop remains effective after the native bow ready callback");
            AmberContract.LOG.info("AMBER_CADENCE preparationMs="+preparation+" autoMeanMs="+autoMs+" manualMeanMs="+manualMs+" autoShots="+auto.length+" manualShots="+manual.length+" actualDamageHits="+hits.get());
        }
        finally
        {
            a.charging=false;a.assist.enable(false);a.cancelAction();
            Containers.Global().removeListener(attackListener);Containers.Global().removeListener(damageListener);t.removeStatsOwner(reserve);
        }
    }
    private static boolean cadenceBounds(long[] shots,int preparation)
    {
        for(int i=1;i<shots.length;i++){double ms=(shots[i]-shots[i-1])/1_000_000.0;if(ms<preparation-15||ms>preparation*1.35+100)return false;}
        return shots.length>=5;
    }
    private static double meanGap(long[] shots){return (shots[shots.length-1]-shots[0])/1_000_000.0/(shots.length-1);}
    private void verifyProtection(Player p,Player t,Player h,AmberServitor a)throws Exception
    {
        var enemy=new org.l2jmobius.gameserver.entity.actor.instance.Servitor(org.l2jmobius.gameserver.data.xml.NpcData.getInstance().getTemplate(AmberContract.SUMMON),t);
        try
        {
            synchronized(AmberContract.session(p))
            {
                a.assist.enable(false);a.setCurrentMp(0);a.setFollowStatus(false);p.fullRestore();t.fullRestore();h.fullRestore();
                a.setXYZ(p.getX(),p.getY(),p.getZ());t.setXYZ(p.getX()+600,p.getY(),p.getZ());h.setXYZ(p.getX()-200,p.getY(),p.getZ());
                a.assist.enable(true);a.assist.tick();check(a.getAI().getAttackTarget()==h,"Baseline chooses the nearer unprotected opponent");
                double before=a.assist.score(t,System.currentTimeMillis());double hp=health(p);
                t.setXYZ(p.getX()+60,p.getY(),p.getZ());
                // Exercise native magical damage and its real global event without a random auto-attack miss.
                for(int attempt=0;attempt<8&&health(p)>=hp;attempt++)t.callSkill(SkillData.getInstance().getSkill(1235,28),java.util.List.of(p));
                check(health(p)<hp,"Opponent's native damage skill lands actual damage on owner");
                t.abortAttack();t.getAI().setIntentionActive();t.setXYZ(p.getX()+600,p.getY(),p.getZ());
                check(a.assist.score(t,System.currentTimeMillis())>before+250,"Global actual-damage event raises defensive threat");
                a.assist.tick();check(a.getAI().getAttackTarget()==t,"Defensive priority interrupts ordinary 2.5-second target stability");
                p.fullRestore();
                enemy.setName("TransferPainProbe");enemy.setLifeTime(86400000);enemy.setItemConsume(new org.l2jmobius.gameserver.entity.item.holders.ItemHolder(0,0));enemy.setItemConsumeInterval(60000);
                enemy.setInstanceId(p.getInstanceId());t.setPet(enemy);enemy.spawnMe(t.getX(),t.getY(),t.getZ());enemy.setFollowStatus(false);enemy.fullRestore();
                check(a.assist.transferPainPriority(enemy,System.currentTimeMillis())==0,"A summon without actual TP receives no TP priority");
                check(a.assist.preventTransferPriority(enemy,System.currentTimeMillis())>0,"Aggressor's servitor is prioritized preventively before TP activation");
                check(a.assist.score(enemy,System.currentTimeMillis())>a.assist.score(t,System.currentTimeMillis()),"Aggressor's summon is preferred before it can enable Transfer Pain");
                SkillData.getInstance().getSkill(1262,5).applyEffects(t,t);
                check(t.getStat().calcStat(org.l2jmobius.gameserver.mechanics.stats.Stat.TRANSFER_DAMAGE_PERCENT,0,null,null)==50,"Native Transfer Pain toggle supplies real 50 percent transfer stat");
                enemy.setCurrentHp(enemy.getMaxHp()*0.15);
                check(a.assist.transferPainPriority(enemy,System.currentTimeMillis())>0,"Active nearby TP servitor becomes a useful defensive target");
                check(a.assist.score(enemy,System.currentTimeMillis())>a.assist.score(t,System.currentTimeMillis()),"Weak TP summon is prioritized before healthy master");
                a.assist.tick();check(a.getAI().getAttackTarget()==enemy,"Scheduler switches to TP summon");
                enemy.setXYZ(t.getX()+1001,t.getY(),t.getZ());check(a.assist.transferPainPriority(enemy,System.currentTimeMillis())==0,"Out-of-transfer-range summon gets no TP bonus");enemy.setXYZ(t.getX(),t.getY(),t.getZ());
                enemy.setCurrentHp(1);check(a.assist.transferPainPriority(enemy,System.currentTimeMillis())==0,"One-HP summon cannot absorb TP and is not prioritized for transfer");enemy.setCurrentHp(enemy.getMaxHp()*0.15);
                t.stopAllEffects();check(a.assist.transferPainPriority(enemy,System.currentTimeMillis())==0,"Removing TP immediately removes the transfer bonus");
                enemy.setInvul(true);h.fullRestore();t.fullRestore();
                var heal=SkillData.getInstance().getSkill(1011,18);
                h.callSkill(heal,java.util.List.of(t));check(a.assist.healerPriority(h,System.currentTimeMillis())==0,"Overheal at full HP creates no healing-support threat");
                t.setCurrentHp(Math.max(1,t.getMaxHp()-1000));double hurt=t.getCurrentHp();h.callSkill(heal,java.util.List.of(t));
                check(t.getCurrentHp()>hurt&&a.assist.healerPriority(h,System.currentTimeMillis())>0,"Actual native HP heal identifies the aggressor's healer");
                double small=a.assist.healerPriority(h,System.currentTimeMillis());
                for(int i=0;i<7;i++){t.setCurrentHp(Math.max(1,t.getMaxHp()-1000));h.callSkill(heal,java.util.List.of(t));}
                check(a.assist.healerPriority(h,System.currentTimeMillis())>small+150,"Repeated effective healing increases support importance");
                check(a.assist.score(h,System.currentTimeMillis())>a.assist.score(t,System.currentTimeMillis()),"Strong supporting healer outranks healthy aggressor");
                a.assist.tick();check(a.getAI().getAttackTarget()==h,"Scheduler switches to strongly supporting healer");
                p.setCurrentHp(p.getMaxHp()*0.20);check(a.assist.score(t,System.currentTimeMillis())>a.assist.score(h,System.currentTimeMillis()),"Critical owner HP favors stopping the direct attacker");p.fullRestore();
                a.assist.manualFocus(t);a.assist.tick();check(a.getAI().getAttackTarget()==t,"Manual focus overrides defensive healer choice");
                a.assist.enable(false);a.assist.enable(true);
                t.setCurrentHp(Math.max(1,t.getMaxHp()-1000));h.callSkill(heal,java.util.List.of(t));check(a.assist.healerPriority(h,System.currentTimeMillis())==0,"Unrelated recipient without recent aggression creates no support priority");
                a.assist.damaged(t,p,100);t.setCurrentCp(0);h.callSkill(SkillData.getInstance().getSkill(1306,6),java.util.List.of(t));
                check(t.getCurrentCp()>0&&a.assist.healerPriority(h,System.currentTimeMillis())>0,"Real CP restoration also identifies enemy support");
                verifyHealingVariants(p,t,h,a,heal);
                a.assist.enable(false);check(a.assist.healerPriority(h,System.currentTimeMillis())==0,"Disabling toggle clears remembered healing support");
                a.assist.enable(true);a.assist.damaged(t,p,100);h.setInsideZone(ZoneId.PEACE,true);check(!a.assist.eligible(h),"Healer priority never bypasses peace protection");h.setInsideZone(ZoneId.PEACE,false);
                h.setInsideZone(ZoneId.PVP,false);h.stopPvPFlag();p.setInsideZone(ZoneId.PVP,false);a.setInsideZone(ZoneId.PVP,false);check(!a.assist.eligible(h),"White healer outside arena remains protected from automatic PK");
                p.setInsideZone(ZoneId.PVP,true);a.setInsideZone(ZoneId.PVP,true);h.setInsideZone(ZoneId.PVP,true);
                long later=System.currentTimeMillis()+6001;check(a.assist.healerPriority(h,later)==0&&a.assist.transferPainPriority(enemy,later)==0,"Expired aggression and support no longer influence priorities");
                a.assist.enable(false);
            }
        }
        finally{a.assist.enable(false);t.stopAllEffects();enemy.unSummon(t);t.setPet(null);p.fullRestore();}
    }
    private void verifyHealingVariants(Player p,Player t,Player h,AmberServitor a,org.l2jmobius.gameserver.mechanics.skill.Skill skill)
    {
        var set=new org.l2jmobius.gameserver.util.StatSet();set.set("name","AmberHealProbe");set.set("ticks",1);
        var params=new org.l2jmobius.gameserver.util.StatSet();params.set("power",100);
        org.l2jmobius.gameserver.mechanics.effects.AbstractEffect[] effects={
            new handlers.skill.effects.HealPercent(null,null,set,params),
            new handlers.skill.effects.CpHealPercent(null,null,set,params),
            new handlers.skill.effects.HealOverTime(null,null,set,params),
            new handlers.skill.effects.CpHealOverTime(null,null,set,params)};
        for(int i=0;i<effects.length;i++)
        {
            a.assist.enable(false);a.assist.enable(true);a.assist.damaged(t,p,100);
            t.setCurrentHp(Math.max(1,t.getMaxHp()-1000));t.setCurrentCp(0);double before=health(t);
            if(i<2)effects[i].onStart(h,t,skill);else effects[i].onActionTime(h,t,skill);
            check(health(t)>before&&a.assist.healerPriority(h,System.currentTimeMillis())>0,"Actual restoration detected from "+effects[i].getClass().getSimpleName());
        }
        a.assist.enable(false);a.assist.enable(true);a.assist.damaged(t,p,100);t.setCurrentHp(Math.max(1,t.getMaxHp()-1000));t.callSkill(skill,java.util.List.of(t));
        check(a.assist.healerPriority(t,System.currentTimeMillis())==0,"Self healing is not misclassified as an external support target");
        p.setCurrentHp(Math.max(1,p.getMaxHp()-1000));h.callSkill(skill,java.util.List.of(p));
        check(a.assist.healerPriority(h,System.currentTimeMillis())==0,"Healing owner creates no hostile healer priority");p.fullRestore();
    }
    private void verifyUiRain(Player p,Player t,AmberServitor a)throws Exception
    {
        Object reserve=new Object();
        t.addStatFunc(new org.l2jmobius.gameserver.mechanics.stats.functions.FuncAdd(org.l2jmobius.gameserver.mechanics.stats.Stat.MAX_HP,0x40,reserve,20000,null));
        try
        {
            double healthBefore;
            synchronized(AmberContract.session(p))
            {
                a.assist.enable(false);
                check(p.getKnownSkill(AmberContract.ASSIST).getIcon().equals("AmberAssistIconsV1.Assist"),"Owner's native activable has a distinct IA icon");
                double mp=a.getCurrentMp();AmberContract.instance.onCommand("amber",p,"toggle");
                check(a.assist.enabled()&&p.isAffectedBySkill(AmberContract.ASSIST)&&a.getCurrentMp()==mp,"Both UI buttons' command activates native toggle at zero resource cost");
                AmberContract.instance.onCommand("amber",p,"toggle");check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST),"Second UI command deactivates effect and AI");
                var handler=org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().getHandler("habilidades");int skills=p.getAllSkills().size(),classId=p.getPlayerClass().getId();
                for(int filter:new int[]{0,4,5,-1})
                {
                    handler.onCommand("habilidades",p,"quick "+filter);
                    check(org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView.filter(p)==filter,"Direct Alt+K group filter "+filter);
                }
                check(p.getAllSkills().size()==skills&&p.getPlayerClass().getId()==classId,"Direct filters preserve build and class");
                t.stopAllEffects();p.fullRestore();t.fullRestore();a.fullRestore();t.setXYZ(p.getX()+200,p.getY(),p.getZ());a.setXYZ(p.getX(),p.getY(),p.getZ());
                double launch=a.getPAtk(t),base=0,enhanced=0;byte element=a.getAttackElement();int power=a.getAttackElementValue(element);
                for(int i=0;i<32;i++)
                {
                    base+=org.l2jmobius.gameserver.mechanics.stats.Formulas.calcPhysDam(a,t,null,(byte)0,false,true);
                    enhanced+=AmberContract.rainDamage(a,t,launch,element,power,(byte)0);
                }
                check(enhanced>base*1.5,"Rain skill power substantially exceeds ordinary shot damage against normal defenses");
                check(SkillData.getInstance().getSkill(AmberContract.RAIN,1).getPower()==3000,"Own rain potency is 3000 per impact");
                double defenseBefore=t.getPDef(a);SkillData.getInstance().getSkill(110,1).applyEffects(t,t);double ud=0;
                for(int i=0;i<32;i++)ud+=AmberContract.rainDamage(a,t,launch,element,power,(byte)0);
                double defenseAfter=t.getPDef(a);
                check(defenseAfter>defenseBefore&&ud>0&&ud<enhanced&&Math.abs(ud/enhanced-defenseBefore/defenseAfter)<0.12,"Native UD reduction follows actual physical defense ratio");t.stopAllEffects();
                check(AmberContract.rainDamage(a,t,launch*1.25,(byte)0,20,org.l2jmobius.gameserver.mechanics.stats.Formulas.SHIELD_DEFENSE_PERFECT_BLOCK)==1,"Perfect shield block remains exactly one even with fire snapshot");
                p.getInventory().addItem(ItemProcessType.NONE,AmberContract.SHOTS,10,p,null);long shots=p.getInventory().getInventoryItemCount(AmberContract.SHOTS,-1);
                resetReuse(p,AmberContract.RAIN);a.assist.enable(false);a.abortAttack();a.getAI().setIntentionActive();a.fullRestore();p.setTarget(t);t.fullRestore();
                healthBefore=health(t);double mpBefore=a.getCurrentMp();AmberContract.order(p,AmberContract.RAIN);
                check(a.charging&&AmberContract.session(p).marker!=null,"New rain enters real 3.5-second channel");
                check(a.getCurrentMp()<=mpBefore-119&&p.getInventory().getInventoryItemCount(AmberContract.SHOTS,-1)==shots-3,"Rain keeps original 120 MP and three shots cost");
            }
                Thread.sleep(3200);check(AmberContract.session(p).impacts==0,"No damage before the telegraphed channel and arrow flight");
                long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(5);
                while(System.nanoTime()<deadline){synchronized(AmberContract.session(p)){if(AmberContract.session(p).marker==null)break;}Thread.sleep(25);}
            synchronized(AmberContract.session(p))
            {
                var session=AmberContract.session(p);
                check(session.marker==null&&session.impacts==3&&session.damage>0&&health(t)<healthBefore,"Three real enhanced impacts reduce player's native CP/HP");
                check(session.cpDamage+session.hpDamage>0,"Player-facing summary records actual observed CP/HP loss");
                check(!a.charging&&!a.isCastingNow(),"Amber can move again after launching rain");
            }
        }
        finally{a.assist.enable(false);AmberContract.session(p).cancel();t.stopAllEffects();t.removeStatsOwner(reserve);t.fullRestore();}
    }
    private void verifyTargetsOnly()
    {
        Player p=null,t=null;int instanceId=0;
        try
        {
            instanceId=InstanceManager.getInstance().createDynamicInstance(0).getId();
            p=probe("AmberOwnerProbe",103,instanceId);t=probe("AmberTargetProbe",90,instanceId);
            p.getVariables().set(AmberContract.CONTRACT,true);AmberContract.grant(p);resetReuse(p,AmberContract.INVOKE);
            AmberContract.order(p,AmberContract.INVOKE);AmberServitor a=(AmberServitor)p.getSummon();a.assist.enable(false);a.setFollowStatus(false);
            verifyTargetPolicy(p,t,a);AmberContract.cleanup(p);verifyLabOpponent(p);
            AmberContract.LOG.info("AmberTargetVerification SUCCESS: "+checks+" checks; native monster/white-player damage, owner flag, actual same-clan Noctis, autonomous and manual damage events.");
        }
        catch(Exception e){AmberContract.LOG.log(Level.SEVERE,"AmberTargetVerification FAILED after "+checks+" checks",e);}
        finally
        {
            if(p!=null){p.getVariables().set(AmberContract.CONTRACT,false);AmberContract.cleanup(p);AmberContract.revokeSavedEffects(p);p.storeMe();p.deleteMe();p.setLabControlled(false);p.setOnlineStatus(false,true);}
            if(t!=null){t.storeMe();t.deleteMe();t.setLabControlled(false);t.setOnlineStatus(false,true);}
            if(instanceId!=0)InstanceManager.getInstance().destroyInstance(instanceId);
        }
    }
    private Player probe(String name,int classId,int instanceId)throws Exception
    {
        int id=0;
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name=?"))
        {
            q.setString(1,name);try(var r=q.executeQuery()){if(r.next()){if(!"ambercontracttest".equals(r.getString(2))||r.getInt(3)!=0||World.getPlayer(r.getInt(1))!=null)throw new IllegalStateException("Reserved probe unavailable: "+name);id=r.getInt(1);}}
        }
        Player p=id==0?Player.create(PlayerTemplateData.getInstance().getTemplate(classId),"ambercontracttest",name,new PlayerAppearance((byte)0,(byte)0,(byte)0,false)):Player.load(id);
        if(p==null)throw new IllegalStateException("Probe creation failed");
        p.setLabControlled(true);p.setOnlineStatus(true,true);p.setDead(false);p.stopAllEffects();p.setAccessLevel(name.equals("AmberOwnerProbe")?100:0);
        p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(80));p.getStat().setLevel((byte)80);p.rewardSkills();
        if(id==0)for(int item:new int[]{6383,6384,6385,6386,6377}){var it=p.getInventory().addItem(ItemProcessType.NONE,item,1,p,null);p.getInventory().equipItem(it);}
        p.setInstanceId(instanceId);p.setEnteredWorld();p.spawnMe(148900,name.equals("AmberOwnerProbe")?46100:46600,-3408);p.setSpawnProtection(false);p.setInvul(false);p.revalidateZone(true);p.fullRestore();
        return p;
    }
    private static void resetReuse(Player p,int id)
    {
        p.getVariables().set("AMBER_REUSE_"+id,0L);var skill=SkillData.getInstance().getSkill(id,1);p.enableSkill(skill);p.removeTimeStamp(skill);
        if(p.hasSummon()){p.getSummon().enableSkill(skill);p.getSummon().removeTimeStamp(skill);}
    }
    private static void awaitRain(AmberContract.Session session)throws InterruptedException
    {
        long end=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(3);
        while(session.marker!=null&&System.nanoTime()<end)Thread.sleep(25);
    }
    private static double health(Player p){return p.getCurrentHp()+p.getCurrentCp();}
    private void verifyTargetPolicy(Player p,Player t,AmberServitor a)throws Exception
    {
        var clanId=Player.class.getDeclaredField("_clanId");clanId.setAccessible(true);
        int ownerClan=clanId.getInt(p),targetClan=clanId.getInt(t);
        Npc monster=null;
        try
        {
            clanId.setInt(p,777777);clanId.setInt(t,777777);
            check(t.isAutoAttackable(p)&&AmberContract.validVictim(p,a,t),"Manual arena attack follows native rules even for same-clan players");
            check(!a.assist.eligible(t),"Unselected same-clan bystander remains protected from automatic targeting");
            a.assist.manualFocus(t);check(a.assist.eligible(t),"Explicit manual focus allows the arena training opponent despite clan");
            a.assist.setEnabled(false);clanId.setInt(p,ownerClan);clanId.setInt(t,targetClan);
            p.setInsideZone(ZoneId.PVP,false);a.setInsideZone(ZoneId.PVP,false);t.setInsideZone(ZoneId.PVP,false);
            p.stopPvPFlag();t.stopPvPFlag();p.setTarget(t);
            check(!AmberContract.validVictim(p,a,t)&&!a.canAttack(false),"White player outside arena requires an explicit forced order");
            check(!a.assist.eligible(t),"AI does not initiate an unrequested attack on a white player");
            monster=AmberContract.instance.addSpawn(20001,a.getX()+80,a.getY(),a.getZ(),0,false,0,false,a.getInstanceId());
            monster.setInsideZone(ZoneId.PVP,false);monster.setInvul(false);
            check(monster.isAttackable()&&AmberContract.validVictim(p,a,monster)&&a.assist.eligible(monster),"Combat NPC is accepted outside PvP by both manual and autonomous targeting");
            p.setTarget(monster);check(a.canAttack(false),"Native summon Attack accepts a normal monster outside PvP");
            double monsterHp=monster.getCurrentHp();a.doSummonAttack(monster);
            long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(4);
            while(monster.getCurrentHp()>=monsterHp&&System.nanoTime()<deadline)Thread.sleep(25);
            check(monster.getCurrentHp()<monsterHp,"Native bow deals real damage to a normal monster outside PvP");
            check(p.getPvpFlag()==0,"Attacking an ordinary monster does not flag its owner");
            a.cancelAction();p.setTarget(t);t.fullRestore();
            check(a.canAttack(true)&&AmberContract.validVictim(p,a,t),"Ctrl attack authorizes only the selected white player");
            double hp=health(t);a.doSummonAttack(t);
            check(awaitDamage(t,hp)&&p.getPvpFlag()!=0,"Real summon attack outside PvP damages player and flags owner through native combat");
            a.cancelAction();check(!a.isForcedTarget(t)&&!AmberContract.validVictim(p,a,t),"Stop clears forced-player authorization");
            p.stopPvPFlag();AmberContract.flagRainAttack(p,t);check(p.getPvpFlag()!=0,"Custom rain attributes player aggression to owner outside PvP");
            p.stopPvPFlag();AmberContract.flagRainAttack(p,monster);check(p.getPvpFlag()==0,"Custom rain against an ordinary monster leaves owner unflagged");
            p.setInsideZone(ZoneId.PVP,true);a.setInsideZone(ZoneId.PVP,true);t.setInsideZone(ZoneId.PVP,true);
            AmberContract.flagRainAttack(p,t);check(p.getPvpFlag()==0,"Arena combat does not require or introduce a purple flag");
        }
        finally
        {
            clanId.setInt(p,ownerClan);clanId.setInt(t,targetClan);
            if(!p.isInsideZone(ZoneId.PVP))p.setInsideZone(ZoneId.PVP,true);
            if(!a.isInsideZone(ZoneId.PVP))a.setInsideZone(ZoneId.PVP,true);
            if(!t.isInsideZone(ZoneId.PVP))t.setInsideZone(ZoneId.PVP,true);
            a.cancelAction();p.stopPvPFlag();t.stopPvPFlag();t.fullRestore();p.setTarget(t);a.setTarget(t);
            long settled=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(4);
            while(a.isAttackingNow()&&System.nanoTime()<settled)Thread.sleep(25);
            if(monster!=null)monster.deleteMe();
        }
    }
    private void verifyLabOpponent(Player p)throws Exception
    {
        var clanId=Player.class.getDeclaredField("_clanId");clanId.setAccessible(true);
        int savedClan=clanId.getInt(p),savedInstance=p.getInstanceId();
        var handler=org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().getHandler("ia");
        boolean started=false;ConsumerEventListener combatListener=null;Object survivalProbe=new Object();
        try
        {
            long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(120);
            while(!custom.NormalNpcRoster.NormalNpcRoster.isReady()&&System.nanoTime()<deadline)Thread.sleep(100);
            check(custom.NormalNpcRoster.NormalNpcRoster.isReady(),"Real lab roster ready before Noctis integration test");
            // Reserved owner has no full PvP jewellery. A temporary HP reserve prevents a one-shot
            // ending the session before the damage-event assertions; no invulnerability or pilot changes.
            p.addStatFunc(new org.l2jmobius.gameserver.mechanics.stats.functions.FuncAdd(org.l2jmobius.gameserver.mechanics.stats.Stat.MAX_HP,0x40,survivalProbe,100000,null));
            p.setDead(false);p.setInvul(false);p.fullRestore();p.abortAttack();p.abortCast();
            p.setInstanceId(0);p.revalidateZone(true);
            p.getVariables().set(AmberContract.CONTRACT,true);AmberContract.grant(p);resetReuse(p,AmberContract.INVOKE);
            AmberContract.order(p,AmberContract.INVOKE);AmberServitor a=(AmberServitor)p.getSummon();a.assist.enable(false);a.setCurrentMp(0);
            deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(20);
            while(p.isInCombat()&&System.nanoTime()<deadline)Thread.sleep(100);
            check(!p.isInCombat(),"Previous probe combat expires naturally before .ia start");
            handler.onCommand("ia",p,"mago");
            Player bot=World.getPlayer("ArenaNoctis");started=bot!=null;
            check(started,"Actual .ia mago loads the reserved Noctis Player");
            clanId.setInt(p,bot.getClanId());check(bot.getClanId()!=0&&p.getClanId()==bot.getClanId(),"Same-clan training condition reproduces Hellsing conflict");
            check(bot.isInvul()&&!a.assist.eligible(bot),"Noctis remains protected during preparation");
            try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("UPDATE lab_ai_runs SET test_mode='AMBER_TARGET' WHERE controller_id=? AND pilot_id=? AND outcome='PREPARING'"))
            {q.setInt(1,p.getObjectId());q.setInt(2,bot.getObjectId());q.executeUpdate();}
            deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(35);
            while(!custom.LabCombatPilots.LabCombatPilots.isCombatOpponent(p,bot)&&System.nanoTime()<deadline){p.fullRestore();Thread.sleep(100);}
            check(custom.LabCombatPilots.LabCombatPilots.isCombatOpponent(p,bot)&&a.assist.eligible(bot),"AI recognizes active .ia opponent despite the same clan");
            var actualHits=new java.util.concurrent.atomic.AtomicInteger();var mageHits=new java.util.concurrent.atomic.AtomicInteger();
            combatListener=new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,(OnCreatureDamageDealt event)->{
                if(event.getAttacker()==a&&event.getDamage()>0&&event.getTarget()!=null&&event.getTarget().asPlayer()==bot)
                {actualHits.incrementAndGet();if(event.getTarget()==bot)mageHits.incrementAndGet();}
            },this);
            Containers.Global().addListener(combatListener);
            a.assist.enable(true);deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(6);
            while(actualHits.get()==0&&System.nanoTime()<deadline){p.fullRestore();Thread.sleep(50);}
            check(actualHits.get()>0,"Real damage event confirms autonomous Amber attacks Noctis or his summon; excludes Noctis self-costs");
            int mageBefore=mageHits.get();p.setTarget(bot);check(a.canAttack(false),"Native manual Attack accepts actual same-clan Noctis during .ia combat");
            a.doSummonAttack(bot);deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(6);
            while(mageHits.get()<=mageBefore&&System.nanoTime()<deadline){p.fullRestore();Thread.sleep(50);}
            check(mageHits.get()>mageBefore,"Real damage event confirms manual focus makes Amber hit the actual Noctis Player");
            a.assist.enable(false);handler.onCommand("ia",p,"cancelar");started=false;
            check(!custom.LabCombatPilots.LabCombatPilots.isCombatOpponent(p,bot)&&!a.assist.eligible(bot),"Cancelling .ia removes the temporary opponent relationship");
        }
        finally
        {
            if(combatListener!=null)Containers.Global().removeListener(combatListener);
            if(p.getSummon() instanceof AmberServitor a)a.assist.enable(false);
            if(started)handler.onCommand("ia",p,"cancelar");
            AmberContract.cleanup(p);p.removeStatsOwner(survivalProbe);clanId.setInt(p,savedClan);p.setInstanceId(savedInstance);p.revalidateZone(true);p.fullRestore();
        }
    }
    private static void applyProbeRoot(Player owner,Player target,int seconds)
    {
        var skill=SkillData.getInstance().getSkill(1201,33);
        // A real hostile root has a chance to fail. Retry setup; never assume a debuff landed.
        for(int attempt=0;attempt<128&&!target.isRooted();attempt++)skill.applyEffects(owner,target,true,seconds);
        if(!target.isRooted())throw new IllegalStateException("Probe root did not land after 128 attempts");
    }
    private void verifyControlSources(Player p,Player t,AmberServitor a)
    {
        for(int[] entry:new int[][]{{1170,13},{279,5},{4164,9},{4166,9}})
        {
            t.stopAllEffects();a.assist.enable(false);
            var skill=SkillData.getInstance().getSkill(entry[0],entry[1]);
            // Probe setup retries a real chance-based skill; no forced flags or extra skills on the owner.
            for(int attempt=0;attempt<64&&!t.isParalyzed()&&!t.isStunned();attempt++)skill.applyEffects(p,t);
            check((t.isParalyzed()||t.isStunned())&&"held>=6s".equals(a.assist.rainReason(t,System.currentTimeMillis())),"Rain recognizes actual control from "+skill.getName()+" id="+entry[0]);
        }
        t.stopAllEffects();
        long now=System.currentTimeMillis();double baseline=a.assist.score(t,now);
        SkillData.getInstance().getSkill(110,2).applyEffects(t,t);
        check(t.isImmobilized()&&AmberAssist.defending(t)&&a.assist.score(t,now)<baseline-150,"Assist detects actual Ultimate Defense and lowers target priority");
        a.assist.observe(t,now-5500);a.assist.observe(t,now);
        check("ud>=6s".equals(a.assist.rainReason(t,now)),"UD is a lower-damage stationary rain opportunity");
        t.stopAllEffects();check(!AmberAssist.defending(t),"UD detection ends when the buff is removed");
    }
    private static boolean awaitDamage(Player target,double before)throws InterruptedException
    {
        // Bow shots can miss; observe an actual hit rather than assuming the first shot lands.
        long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(8);
        while(health(target)>=before&&System.nanoTime()<deadline)Thread.sleep(50);
        return health(target)<before;
    }
    private void verifyRainPanorama(Player p,Player t,org.l2jmobius.gameserver.entity.actor.instance.Servitor enemy,AmberServitor a)throws Exception
    {
        Player middle=null,edge=null;int tx=t.getX(),ty=t.getY(),tz=t.getZ(),ex=enemy.getX(),ey=enemy.getY(),ez=enemy.getZ();
        try
        {
            a.assist.enable(false);t.stopAllEffects();enemy.stopAllEffects();enemy.setInvul(false);
            a.cancelAction();a.setFollowStatus(false);a.stopMove(null);
            t.stopMove(null);t.getAI().setIntentionIdle();enemy.cancelAction();enemy.setFollowStatus(false);enemy.stopMove(null);
            middle=probe("AmberAreaMiddleProbe",90,p.getInstanceId());edge=probe("AmberAreaEdgeProbe",90,p.getInstanceId());
            t.setXYZ(tx,ty,tz);middle.setXYZ(tx+100,ty,tz);enemy.setXYZ(tx+200,ty,tz);edge.setXYZ(tx+800,ty,tz);
            var group=java.util.List.<org.l2jmobius.gameserver.entity.actor.Creature>of(t,middle,enemy);
            var choice=a.assist.chooseRain(group,System.currentTimeMillis());
            check(choice!=null&&choice.target()==middle&&choice.reason().equals("cluster"),"Rain chooses the middle enemy to cover a compact group without an immobilization: "+choice);
            SkillData.getInstance().getSkill(110,2).applyEffects(middle,middle);
            choice=a.assist.chooseRain(group,System.currentTimeMillis());
            check(choice!=null&&choice.target()==middle&&choice.reason().equals("ud>=6s"),"UD target anchors rain and covers nearby less defended enemies");
            applyProbeRoot(p,t,30);choice=a.assist.chooseRain(group,System.currentTimeMillis());
            check(choice!=null&&choice.target()==t&&choice.reason().equals("held>=6s"),"Hostile root has priority over UD even when UD is in the middle");
            t.stopAllEffects();middle.stopAllEffects();a.assist.enable(false);
            t.setXYZ(tx-400,ty,tz);enemy.setXYZ(tx+100,ty,tz);middle.setXYZ(tx+200,ty,tz);edge.setXYZ(tx+300,ty,tz);
            SkillData.getInstance().getSkill(110,2).applyEffects(t,t);
            choice=a.assist.chooseRain(java.util.List.of(t,enemy,middle,edge),System.currentTimeMillis());
            check(choice!=null&&choice.target()==middle&&choice.reason().equals("cluster"),"Much better unprotected group can justify escape risk over an isolated UD tank");
        }
        finally
        {
            a.assist.enable(false);t.stopAllEffects();t.setXYZ(tx,ty,tz);enemy.setXYZ(ex,ey,ez);
            for(Player actor:new Player[]{middle,edge})if(actor!=null){actor.storeMe();actor.deleteMe();actor.setLabControlled(false);actor.setOnlineStatus(false,true);}
        }
    }
    /** Runs the same packet handler as a click in the native summon window. */
    private static void nativeAction(Player owner,int id)throws Exception
    {
        RequestActionUse packet=new RequestActionUse(){@Override protected Player getPlayer(){return owner;}};
        var field=RequestActionUse.class.getDeclaredField("_actionId");field.setAccessible(true);field.setInt(packet,id);packet.run();
    }
    private static void nativeToggle(Player p)throws Exception
    {
        long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(3);
        while(p.isCastingNow()&&System.nanoTime()<deadline)Thread.sleep(25);
        p.useMagic(SkillData.getInstance().getSkill(AmberContract.ASSIST,1),false,false);
        Thread.sleep(700);
    }
    private void verifyToggle(Player p,Player t,AmberServitor a)throws Exception
    {
        check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST),"New Amber defaults to manual with toggle off");
        long attack=a.getAttackEndTime();synchronized(AmberContract.session(p)){a.assist.tick();}
        check(a.getAttackEndTime()==attack,"Manual default never acquires an enemy autonomously");
        var skill=p.getKnownSkill(AmberContract.ASSIST);
        check(skill.isToggle()&&skill.getMpConsume()==0,"Assistance is a native toggle with zero MP cost");
        t.setInvul(true);p.fullRestore();double mp=p.getCurrentMp(),patk=p.getPAtk(t),matk=p.getMAtk(t,null);
        long shots=p.getInventory().getInventoryItemCount(6645,-1);var target=p.getTarget();
        nativeToggle(p);check(a.assist.enabled()&&p.isAffectedBySkill(AmberContract.ASSIST),"First native skill click enables AI and its toggle indicator");
        check(p.getCurrentMp()==mp&&p.getPAtk(t)==patk&&p.getMAtk(t,null)==matk&&p.getInventory().getInventoryItemCount(6645,-1)==shots&&p.getTarget()==target,"Toggle changes no player stats, MP, shots or selected target");
        nativeToggle(p);check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST),"Second native skill click disables AI and removes indicator");
        AmberContract.control(p,"auto");check(a.assist.enabled()&&p.isAffectedBySkill(AmberContract.ASSIST),"Legacy auto command shares native toggle state");
        nativeAction(p,23);check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST),"Native Stop clears AI and toggle indicator together");
        nativeToggle(p);nativeAction(p,21);check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST)&&a.getFollowStatus(),"Native Follow clears the toggle and follows owner");
        nativeToggle(p);AmberContract.control(p,"manual");check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST),"Legacy manual command clears native toggle");
        t.setInvul(false);
    }
    private void verify()
    {
        Player p=null,t=null;Npc npc=null;int instanceId=0;ConsumerEventListener rainListener=null;
        try
        {
            instanceId=InstanceManager.getInstance().createDynamicInstance(0).getId();p=probe("AmberOwnerProbe",103,instanceId);t=probe("AmberTargetProbe",90,instanceId);
            check(p.isInsideZone(ZoneId.PVP)&&t.isInsideZone(ZoneId.PVP),"Private Coliseum PVP zones");
            p.addSkill(SkillData.getInstance().getSkill(1204,2),false);resetReuse(p,AmberContract.INVOKE);resetReuse(p,AmberContract.FIRE);resetReuse(p,AmberContract.RAIN);
            p.getVariables().set(AmberContract.CONTRACT,false);
            npc=AmberContract.instance.addSpawn(AmberContract.NPC,p.getX()+50,p.getY(),p.getZ(),0,false,0,false,instanceId);
            var entry=BypassHandler.getInstance().getHandler("voice .amber firmar");
            check(entry!=null,"NPC button bypass is registered");
            p.setTarget(t);entry.onCommand("voice .amber firmar",p,t);check(!AmberContract.contracted(p),"Contract cannot be signed through another target");
            p.setTarget(npc);check(entry.onCommand("voice .amber firmar",p,npc),"NPC voice button dispatches successfully");
            check(AmberContract.contracted(p)&&p.getSummon() instanceof AmberServitor,"Quest grants contract and real servitor");
            for(int id:AmberContract.GRANTS)check(p.getKnownSkill(id)!=null,"Temporary skill "+id);
            String[] icons={"AmberIconsV1.Contract","AmberIconsV1.Fire","AmberIconsV1.Rain","AmberIconsV1.Break","AmberAssistIconsV1.Assist"};
            for(int i=0;i<AmberContract.GRANTS.length;i++)check(p.getKnownSkill(AmberContract.GRANTS[i]).getIcon().equals(icons[i]),"Skill icon "+icons[i]);
            String menu=AmberContract.menuHtml(p);
            check(menu.length()<8192&&java.util.Arrays.stream(icons).allMatch(icon->menu.contains("src=\""+icon+"\""))&&menu.contains("voice .amber fuego")&&menu.contains("voice .amber lluvia"),"Visible skill menu has five icon textures and executable fire/rain buttons");
            AmberServitor a=(AmberServitor)p.getSummon();a.setFollowStatus(false);a.setTarget(t);p.setTarget(t);
            verifyToggle(p,t,a);a.setFollowStatus(false);a.setTarget(t);p.setTarget(t);
            check(a.getInstanceId()==instanceId&&a.getWeapon()==6619&&a.getPhysicalAttackRange()>=700,"Instance, cosmetic Infinity Bow and ranged attack");
            check(a.getKnownSkill(19002)!=null&&a.getKnownSkill(19003)!=null,"Pet skill list");
            check(AmberContract.validVictim(p,a,t)&&!AmberContract.validVictim(p,a,p),"Enemy accepted, owner excluded");
            t.setInvul(true);check(!AmberContract.validVictim(p,a,t),"Invulnerable victim excluded");t.setInvul(false);
            t.setInsideZone(ZoneId.PEACE,true);check(!AmberContract.validVictim(p,a,t),"Peace victim excluded");t.setInsideZone(ZoneId.PEACE,false);
            t.setInstanceId(0);check(!AmberContract.validVictim(p,a,t),"Cross-instance victim excluded");t.setInstanceId(instanceId);
            verifyTargetPolicy(p,t,a);
            check(a.getTemplate().getParameters().getSkillHolder("AmberFire").getSkillId()==19002&&a.getTemplate().getParameters().getSkillHolder("AmberRain").getSkillId()==19003,"Native action names map to Amber's own skills");
            a.stopAllEffects();double patk=a.getPAtk(t),ownerPatk=p.getPAtk(t),mp=a.getCurrentMp();nativeAction(p,19021);
            long fireDeadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(3);
            while(a.getEffectList().getBuffInfoBySkillId(19005)==null&&System.nanoTime()<fireDeadline)Thread.sleep(25);
            check(a.getEffectList().getBuffInfoBySkillId(19005)!=null&&Math.abs(a.getPAtk(t)/patk-1.25)<0.001,"Fire adds 25 percent PAtk; buff="+(a.getEffectList().getBuffInfoBySkillId(19005)!=null)+" ratio="+(a.getPAtk(t)/patk)+" mp="+a.getCurrentMp()+" ai="+a.getAI().getIntention()+" casting="+a.isCastingNow()+" disabled="+a.isSkillDisabled(a.getKnownSkill(19002))+" ownerDead="+p.isDead()+" sameSummon="+(p.getSummon()==a));
            check(a.getCurrentMp()<=mp-59,"Fire consumes summon MP");
            check(a.getAttackElement()==0&&a.getAttackElementValue((byte)0)==20,"Fire enchant uses native fire element and power");
            check(p.getEffectList().getBuffInfoBySkillId(19011)!=null&&p.getEffectList().getBuffInfoBySkillId(19011).getTime()<=15&&p.getPAtk(t)==ownerPatk,"Owner's native timed icon is informational; owner stats unchanged");
            long fireRemaining=p.getSkillRemainingReuseTime(p.getKnownSkill(19002).getReuseHashCode());
            long fireAuthoritative=p.getVariables().getLong("AMBER_REUSE_19002",0)-System.currentTimeMillis();
            check(fireRemaining>25000&&Math.abs(fireRemaining-fireAuthoritative)<100&&a.isSkillDisabled(a.getKnownSkill(19002)),"Fire reuse is registered for owner skill bar and summon: native="+fireRemaining+" persistent="+fireAuthoritative+" summonDisabled="+a.isSkillDisabled(a.getKnownSkill(19002)));
            double afterFireMp=a.getCurrentMp();nativeAction(p,19021);check(a.getCurrentMp()==afterFireMp,"Repeated native fire click during reuse consumes no MP");
            double vulnerable=org.l2jmobius.gameserver.mechanics.stats.Formulas.calcAttributeBonus(a,t,null);
            Object resistanceProbe=new Object();
            t.addStatFunc(new org.l2jmobius.gameserver.mechanics.stats.functions.FuncAdd(org.l2jmobius.gameserver.mechanics.stats.Stat.FIRE_RES,0x40,resistanceProbe,50,null));
            check(org.l2jmobius.gameserver.mechanics.stats.Formulas.calcAttributeBonus(a,t,null)<vulnerable,"Native fire resistance reduces elemental attack damage");
            t.removeStatsOwner(resistanceProbe);
            p.getInventory().addItem(ItemProcessType.NONE,6645,100,p,null);
            a.setChargedShot(ShotType.SOULSHOTS,false);long beforeShots=p.getInventory().getInventoryItemCount(6645,-1);
            var shot=p.getInventory().getItemByItemId(6645);ItemHandler.getInstance().getHandler(shot.getEtcItem()).onItemUse(p,shot,false);
            check(a.isChargedShot(ShotType.SOULSHOTS)&&p.getInventory().getInventoryItemCount(6645,-1)==beforeShots-1,"Native Beast Soulshot handler consumes one shot");
            p.setTarget(npc);check(!a.canAttack(true),"Native summon attack rejects contract NPC even with force attack");p.setTarget(t);
            double before=health(t);entry.onCommand("voice .amber atacar",p,npc);
            check(awaitDamage(t,before),"Menu command enters native SummonAI and deals actual ranged damage against Player; ai="+a.getAI().getIntention()+" valid="+a.canAttack(false)+" range="+a.calculateDistance3D(t));
            entry.onCommand("voice .amber detener",p,npc);check(!a.getFollowStatus()&&!a.isMoving()&&a.getAI().getIntention()!=org.l2jmobius.gameserver.ai.Intention.ATTACK,"Stop order stops movement, future attacks and follow");
            entry.onCommand("voice .amber seguir",p,npc);check(a.getFollowStatus(),"Follow order enables native owner following");
            entry.onCommand("voice .amber detener",p,npc);t.fullRestore();
            before=health(t);nativeAction(p,22);
            check(awaitDamage(t,before),"Native Attack button enters SummonAI and deals actual ranged damage");
            nativeAction(p,23);check(a.getAI().getIntention()!=org.l2jmobius.gameserver.ai.Intention.ATTACK,"Native Stop button cancels further ranged attacks");t.fullRestore();
            final AmberServitor observedAttacker=a;final Player observedTarget=t;
            var rainEvents=new java.util.concurrent.atomic.AtomicInteger();
            var rainEventDamage=new java.util.concurrent.atomic.DoubleAdder();
            rainListener=new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,(OnCreatureDamageDealt event)->{
                if(event.getAttacker()==observedAttacker&&event.getTarget()==observedTarget&&event.getSkill()!=null&&event.getSkill().getId()==AmberContract.RAIN){
                    rainEvents.incrementAndGet();rainEventDamage.add(event.getDamage());
                }
            },this);
            Containers.Global().addListener(rainListener);
            a.fullRestore();long shots=p.getInventory().getInventoryItemCount(6645,-1);mp=a.getCurrentMp();resetReuse(p,19003);nativeAction(p,19022);
            // The native AI waits out the bow's remaining reload before starting a cast.
            // Measure the 3500ms channel from the charge itself, not from the click.
            long chargeDeadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(4);
            while(!a.charging&&System.nanoTime()<chargeDeadline)Thread.sleep(25);
            var session=AmberContract.session(p);check(a.charging&&a.isMovementDisabled()&&session.marker!=null,"Rain charge locks movement and creates fixed marker");
            check(!a.canAttack(false),"Native attack command is blocked during the rain charge");
            entry.onCommand("voice .amber seguir",p,npc);check(a.charging&&!a.getFollowStatus(),"Follow command cannot bypass rain movement lock");
            check(p.getInventory().getInventoryItemCount(6645,-1)==shots-3&&a.getCurrentMp()<=mp-119,"Rain consumes 3 shots and 120 MP");
            check(p.getSkillRemainingReuseTime(p.getKnownSkill(19003).getReuseHashCode())>44000,"Rain reuse is registered on native owner skill bar");
            Thread.sleep(2800);check(session.impacts==0,"No impact before 3.5 second charge");Thread.sleep(950);
            check(!a.charging&&!a.isCastingNow()&&!a.isMovementDisabled(),"Movement restored immediately after charge");
            check(session.impacts==0,"Rain arrows fall before the first damage pulse");awaitRain(session);
            check(session.impacts==3&&session.damage>0,"Three actual Player impacts");
            check(rainEvents.get()==3&&Math.abs(rainEventDamage.sum()-session.damage)<0.001,"Each rain hit notifies the global damage-number listener exactly once with Amber as attacker");
            Containers.Global().removeListener(rainListener);rainListener=null;
            double rainDamage=session.damage;resetReuse(p,19003);t.fullRestore();a.doCast(SkillData.getInstance().getSkill(19003,1));
            int oldX=t.getX();t.setXYZ(oldX+201,t.getY(),t.getZ());Thread.sleep(5500);
            check(session.impacts==0,"Target at radius 201 is outside fixed circular rain");t.setXYZ(oldX,t.getY(),t.getZ());
            resetReuse(p,19003);t.fullRestore();a.doCast(SkillData.getInstance().getSkill(19003,1));
            t.setXYZ(oldX+199,t.getY(),t.getZ());Thread.sleep(5500);
            check(session.impacts==3&&session.damage>0,"Target at radius 199 remains inside circular rain");t.setXYZ(oldX,t.getY(),t.getZ());
            check(AmberServitor.fireVisualLevel(300)==6&&AmberServitor.fireVisualLevel(700)==14,"Tracer distance selects appropriate visual length");
            check(AmberServitor.fireVisualLevel(0)==1&&AmberServitor.fireVisualLevel(5000)==16,"Tracer levels clamp to installed catalog bounds");
            a.getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,19005);
            check(a.getAttackElementValue((byte)0)==0&&p.getEffectList().getBuffInfoBySkillId(19011)==null,"Removing or expiring the enchant removes element and owner timer");
            resetReuse(p,19003);a.doCast(SkillData.getInstance().getSkill(19003,1));Thread.sleep(3750);
            check(!a.charging&&session.rain!=null,"Rain continues after actor is unlocked");a.setXYZ(a.getX()+300,a.getY(),a.getZ());awaitRain(session);
            check(session.impacts==3&&session.damage>0,"Moving Amber after launch does not cancel fixed rain");t.fullRestore();
            resetReuse(p,19003);a.doCast(SkillData.getInstance().getSkill(19003,1));a.abortCast();Thread.sleep(200);
            check(!a.charging&&session.marker==null&&session.channel==null,"Interrupted charge cleans marker and unlocks actor");
            resetReuse(p,19003);a.doCast(SkillData.getInstance().getSkill(19003,1));check(a.charging,"New rain starts");
            // Disconnect cleanup keeps contract but withdraws its actor and temporary grant.
            AmberContract.cleanup(p);check(!p.hasSummon()&&session.marker==null&&!a.charging,"Disconnect cancels pending rain and summon");
            AmberContract.restore(p);check(AmberContract.contracted(p)&&p.getKnownSkill(19001)!=null,"Login/subclass grant restoration");
            nativeToggle(p);check(!p.isAffectedBySkill(AmberContract.ASSIST),"Valid contract without a summon cannot enable assistance");
            long reuse=p.getVariables().getLong("AMBER_REUSE_19003",0);p.abortAttack();p.abortCast();p.getAI().setIntentionIdle();
            // Outside combat is enforced in production; probe waits out its bow combat timestamp.
            Thread.sleep(16000);resetReuse(p,19001);AmberContract.order(p,19001);a=(AmberServitor)p.getSummon();a.assist.enable(false);a.setFollowStatus(false);session=AmberContract.session(p);
            resetReuse(p,19003);AmberContract.order(p,19003);check(a.charging,"Pending charge before break");reuse=p.getVariables().getLong("AMBER_REUSE_19003",0);
            nativeToggle(p);check(a.assist.enabled()&&a.charging,"Toggle can enable assistance during a rain charge");
            nativeToggle(p);check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST)&&a.charging,"Toggle can disable assistance during charge without cancelling already committed rain");
            a.assist.enable(true);
            entry.onCommand("voice .amber romper",p,npc);check(!p.hasSummon()&&!a.charging&&session.marker==null,"Break cancels live charge and withdraws actor");
            check(!p.isAffectedBySkill(AmberContract.ASSIST),"Break removes active assistance toggle");
            check(!AmberContract.contracted(p),"Break contract revoked persistence");
            for(int id:AmberContract.GRANTS)check(p.getKnownSkill(id)==null,"Revoke skill "+id);
            check(p.getKnownSkill(1204)!=null&&p.getInventory().getInventoryItemCount(6645,-1)>0,"Original skill and unused shots preserved");
            check(p.getVariables().getLong("AMBER_REUSE_19003",0)==reuse,"Reuse survives cleanup and contract break");
            nativeToggle(p);check(!p.isAffectedBySkill(AmberContract.ASSIST),"A stale skill click without contract or summon cannot leave a toggle active");
            verifyAssist(p,t,npc);
            verifyLabOpponent(p);
            AmberContract.LOG.info("AmberContractVerification SUCCESS: "+checks+" checks; rainDamage="+rainDamage+"; real Players, quest, ranged bow, fire, fixed area, 3500ms channel, cancellation, cleanup.");
        }
        catch(Exception e){AmberContract.LOG.log(Level.SEVERE,"AmberContractVerification FAILED after "+checks+" checks",e);}
        finally
        {
            if(rainListener!=null)Containers.Global().removeListener(rainListener);
            if(npc!=null)npc.deleteMe();
            if(p!=null){p.getVariables().set(AmberContract.CONTRACT,false);AmberContract.cleanup(p);AmberContract.revokeSavedEffects(p);p.storeMe();p.deleteMe();p.setLabControlled(false);p.setOnlineStatus(false,true);}
            if(t!=null){t.storeMe();t.deleteMe();t.setLabControlled(false);t.setOnlineStatus(false,true);}
            if(instanceId!=0)InstanceManager.getInstance().destroyInstance(instanceId);
        }
    }
    private void verifyAssist(Player p,Player t,Npc npc)throws Exception
    {
        p.getVariables().set(AmberContract.CONTRACT,true);AmberContract.grant(p);resetReuse(p,19001);resetReuse(p,19002);resetReuse(p,19003);
        p.setInvul(false);p.setDead(false);p.fullRestore();t.setDead(false);t.fullRestore();t.stopMove(null);t.getAI().setIntentionIdle();
        t.setXYZ(p.getX(),p.getY()+500,p.getZ());p.setTarget(npc);
        AmberContract.order(p,19001);AmberServitor a=(AmberServitor)p.getSummon();a.assist.enable(false);
        check(a.assist.eligible(t)&&!a.assist.eligible(p)&&!a.assist.eligible(npc),"Assist scans enemy Players but excludes owner and quest NPC");
        t.setInvisible(true);check(!a.assist.eligible(t),"Assist cannot acquire invisible targets");t.setInvisible(false);
        var party=new org.l2jmobius.gameserver.entity.groups.Party(p,org.l2jmobius.gameserver.entity.groups.PartyDistributionType.FINDERS_KEEPERS);
        p.setParty(party);t.setParty(party);party.addPartyMember(t);
        check(!a.assist.eligible(t)&&a.assist.protectedActor(t),"Assist protects party allies and excludes them from targets");
        party.removePartyMember(t,org.l2jmobius.gameserver.entity.groups.PartyMessageType.NONE);
        p.setParty(null);t.setParty(null);
        t.setXYZ(p.getX()+1500,p.getY(),p.getZ());check(!a.assist.eligible(t),"Assist limits pursuit to the owner's vicinity");t.setXYZ(p.getX(),p.getY()+500,p.getZ());
        var enemy=new org.l2jmobius.gameserver.entity.actor.instance.Servitor(org.l2jmobius.gameserver.data.xml.NpcData.getInstance().getTemplate(AmberContract.SUMMON),t);
        try
        {
            enemy.setName("EnemySummonProbe");enemy.setLifeTime(86400000);enemy.setItemConsume(new org.l2jmobius.gameserver.entity.item.holders.ItemHolder(0,0));enemy.setItemConsumeInterval(60000);
            enemy.setInstanceId(p.getInstanceId());t.setPet(enemy);enemy.spawnMe(t.getX(),t.getY(),t.getZ());enemy.setFollowStatus(false);enemy.fullRestore();
            synchronized(AmberContract.session(p)){
            check(a.assist.eligible(enemy),"Assist accepts enemy summons");
            long now=System.currentTimeMillis();check(a.assist.score(enemy,now)>a.assist.score(t,now),"Nearby summon gets a modest priority");
            a.assist.enable(true);a.assist.damaged(t,p,1000);
            check(a.assist.score(enemy,System.currentTimeMillis())>a.assist.score(t,System.currentTimeMillis()),"Owner aggression prioritizes preventive removal of that opponent's summon");
            a.assist.enable(false);
            // Observe actual position changes rather than flags alone.
            now=System.currentTimeMillis();a.assist.observe(t,now-5500);a.assist.observe(t,now);
            check("stationary".equals(a.assist.rainReason(t,now)),"Five seconds idle predicts a rain opportunity");
            t.setXYZ(t.getX()+40,t.getY(),t.getZ());a.assist.observe(t,now+1);
            check(a.assist.rainReason(t,now+1)==null,"Position change invalidates stationary rain prediction");t.setXYZ(p.getX(),p.getY()+500,p.getZ());
            // Check the real shared skill path, resources and owner target preservation.
            a.fullRestore();double mp=a.getCurrentMp();long shots=p.getInventory().getInventoryItemCount(6645,-1);
            a.assist.enable(true);
            check(AmberContract.automaticOrder(a,19002,t)&&a.getCurrentMp()<=mp-59,"AI fire consumes normal summon MP");
            mp=a.getCurrentMp();check(!AmberContract.automaticOrder(a,19002,t)&&a.getCurrentMp()==mp,"AI fire cannot bypass reuse");
            check(AmberContract.automaticOrder(a,19003,t)&&a.charging&&p.getInventory().getInventoryItemCount(6645,-1)==shots-3,"AI rain uses normal charge and soulshots");
            check(p.getTarget()==npc,"AI skills never replace the player's selected target");AmberContract.session(p).cancel();a.assist.enable(false);
            }
            // Let the real scheduler choose and shoot an enemy summon without any owner selection.
            resetReuse(p,19002);p.getVariables().set("AMBER_REUSE_19003",System.currentTimeMillis()+30000);enemy.fullRestore();t.fullRestore();
            p.addAutoSoulShot(6645);a.setChargedShot(ShotType.SOULSHOTS,false);
            long autoShotsBefore=p.getInventory().getInventoryItemCount(6645,-1);
            double before=enemy.getCurrentHp();a.assist.enable(true);
            long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(10);
            while(enemy.getCurrentHp()>=before&&System.nanoTime()<deadline)Thread.sleep(50);
            check(enemy.getCurrentHp()<before,"Autonomous scheduler chooses enemy summon and deals native bow damage");
            check(p.getInventory().getInventoryItemCount(6645,-1)<autoShotsBefore,"Autonomous bow uses native Beast Soulshot auto recharge");
            check(p.getTarget()==npc,"Automatic bow attack preserves owner target");
            nativeAction(p,23);check(!a.assist.enabled(),"Native Stop disables assistance");long stoppedSequence=a.getAttackEndTime();Thread.sleep(4000);
            check(a.getAttackEndTime()==stoppedSequence&&a.getAI().getIntention()!=org.l2jmobius.gameserver.ai.Intention.ATTACK,"Native Stop does not start new attacks despite enemy HP regeneration or an arrow already released");
            a.assist.enable(true);nativeAction(p,21);check(!a.assist.enabled()&&a.getFollowStatus(),"Native Follow pauses assistance and follows owner");
            resetReuse(p,19002);nativeAction(p,19021);Thread.sleep(400);
            check(!a.assist.enabled()&&a.getFollowStatus(),"A native fire cast preserves manual Follow after casting completes");
            a.assist.enable(true);p.setTarget(t);nativeAction(p,22);
            synchronized(AmberContract.session(p)){a.assist.tick();check(a.getAI().getAttackTarget()==t,"Manual Attack overrides summon priority");}
            p.setTarget(npc);
            // An invalid manual focus disappears without needing another Attack order.
            t.setInvul(true);enemy.fullRestore();before=enemy.getCurrentHp();
            deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(10);
            while(enemy.getCurrentHp()>=before&&System.nanoTime()<deadline)Thread.sleep(50);
            check(enemy.getCurrentHp()<before&&a.getAI().getAttackTarget()==enemy,"Assist releases invalid manual focus and attacks remaining enemy summon without a new order");
            a.cancelAction();t.setInvul(false);
            // A real timed root should permit immediate rain, not a forced root or simulated damage.
            applyProbeRoot(p,t,30);
            check(t.isRooted()&&"held>=6s".equals(a.assist.rainReason(t,System.currentTimeMillis())),"Real timed root qualifies for immediate rain");
            t.stopAllEffects();a.assist.enable(false);applyProbeRoot(p,t,2);
            check(a.assist.rainReason(t,System.currentTimeMillis())==null,"Short root does not promise enough time for the rain");
            t.stopAllEffects();applyProbeRoot(p,t,6);
            check(a.assist.rainReason(t,System.currentTimeMillis())==null,"Rounded six-second timer is not treated as six guaranteed real seconds");
            t.stopAllEffects();verifyControlSources(p,t,a);
            verifyRainPanorama(p,t,enemy,a);
            t.stopAllEffects();enemy.setInvul(true);resetReuse(p,19003);a.fullRestore();a.assist.enable(true);
            // Keep the stationary target safe from bow damage until observing actual automatic charge.
            applyProbeRoot(p,t,30);
            deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(8);
            while(!a.charging&&System.nanoTime()<deadline)Thread.sleep(25);
            check(a.charging&&AmberContract.session(p).marker!=null,"Scheduler autonomously starts rain on rooted target");
            check(p.getTarget()==npc,"Autonomous rain keeps owner target");
            a.assist.enable(false);AmberContract.session(p).cancel();t.stopAllEffects();
            a.assist.enable(true);p.setInvul(true);synchronized(AmberContract.session(p)){a.assist.tick();}
            check(a.getAI().getIntention()!=org.l2jmobius.gameserver.ai.Intention.ATTACK&&!a.charging,"Preparation/intermission invulnerability pauses autonomous combat");p.setInvul(false);
            a.doDie(t);check(!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST)&&p.getKnownSkill(AmberContract.ASSIST)!=null,"Summon death disables toggle while retaining the contract skill");
            AmberContract.cleanup(p);check(!p.hasSummon()&&!a.assist.enabled()&&!p.isAffectedBySkill(AmberContract.ASSIST)&&!AmberContract.SESSIONS.containsKey(p.getObjectId()),"Withdraw clears assist controller, toggle, session and live actor");
        }
        finally{p.removeAutoSoulShot(6645);enemy.unSummon(t);t.setPet(null);t.setInvul(false);t.stopAllEffects();}
    }
    public static void main(String[] args){new AmberContractVerification();}
}




