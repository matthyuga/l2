import java.lang.instrument.Instrumentation;
import java.lang.ref.WeakReference;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.instance.Servitor;
import org.l2jmobius.gameserver.entity.actor.tasks.creature.HitTask;
import org.l2jmobius.gameserver.entity.actor.tasks.creature.MagicUseTask;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.IdManager;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.DirectThreat;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.stats.Stat;
import org.l2jmobius.gameserver.mechanics.stats.functions.FuncAdd;
import org.l2jmobius.gameserver.taskmanagers.AttackStanceTaskManager;

/** Opt-in live integration probes in a private instance; no saved character edits. */
public class DirectThreatVerification
{
    private static final List<String> CHECKS = new ArrayList<>();
    private static void check(boolean ok, String message)
    {
        if (!ok) throw new AssertionError(message);
        CHECKS.add("PASS " + message);
    }
    private static Player probe(String name, int instance) throws Exception
    {
        var ctor = Player.class.getDeclaredConstructor(int.class, PlayerTemplate.class, String.class, PlayerAppearance.class);
        ctor.setAccessible(true);
        Player p = ctor.newInstance(IdManager.getInstance().getNextId(), PlayerTemplateData.getInstance().getTemplate(103),
            "directthreatprobe", new PlayerAppearance((byte)0, (byte)0, (byte)0, false));
        p.setName(name); p.setLabControlled(true); p.setInstanceId(instance); p.setAccessLevel(0);
        p.getStat().setLevel((byte)80);
        p.addStatFunc(new FuncAdd(Stat.MAX_HP, 0x40, DirectThreatVerification.class, 1000000, null));
        p.setEnteredWorld(); p.spawnMe(148900, 46100, -3408); p.setSpawnProtection(false); p.setInvul(false); p.fullRestore();
        return p;
    }
    private static void hit(Creature source, Player victim, boolean primary)
    {
        new HitTask(source, victim, 10, false, false, (byte)0, false, false, primary).run();
    }
    private static double health(Player p) { return p.getCurrentHp()+p.getCurrentCp(); }
    private static void cast(Player source, Skill skill, Creature primary, List<WorldObject> targets)
    {
        source.fullRestore(); source.setCastingNow(true);
        source.onMagicHitTimer(new MagicUseTask(source, targets, skill, 0, false, primary));
        source.abortCast();
    }
    public static void agentmain(String directory, Instrumentation instrumentation) throws Exception
    {
        Path output = Path.of(directory, "verification.txt");
        List<Player> probes = new ArrayList<>(); Servitor summon = null;
        int instance = 0;
        try
        {
            check(World.getPlayers().stream().noneMatch(p -> p.getClient() != null), "no connected clients");
            instance = InstanceManager.getInstance().createDynamicInstance(0).getId();
            Player a = probe("ThreatA", instance); probes.add(a);
            Player b = probe("ThreatB", instance); probes.add(b);
            Player v = probe("ThreatVictim", instance); probes.add(v);
            a.setXYZ(148950,46100,-3408); b.setXYZ(149000,46100,-3408);
            var handler = VoicedCommandHandler.getInstance().getHandler("amenaza");
            check(handler != null && handler == VoicedCommandHandler.getInstance().getHandler("agresor"), "commands registered");
            v.setTarget(b); handler.onCommand("amenaza",v,"");
            check(v.getTarget()==b, "no threat leaves target untouched");
            double hp = health(v); hit(a,v,true);
            check(health(v)<hp && DirectThreat.last(v)==a, "real direct melee damage records attacker");
            handler.onCommand("amenaza",v,""); check(v.getTarget()==a, "command selects attacker");
            hp = health(v); hit(b,v,false);
            check(health(v)<hp && DirectThreat.last(v)==a, "secondary polearm damage does not replace threat");
            new HitTask(b,v,10,false,true,(byte)0,false,false).run();
            check(DirectThreat.last(v)==a, "miss does not replace threat");
            try(var context=DirectThreat.begin(b,v,null)){v.getStatus().reduceHp(10,b,true,true,false);}
            check(DirectThreat.last(v)==a, "periodic damage excluded even inside context");
            v.getStatus().reduceHp(10,b,true,false,false);
            check(DirectThreat.last(v)==a, "unattributed/script area damage excluded");
            try(var context=DirectThreat.begin(b,v,null)){a.getStatus().reduceHp(10,v,true,false,false);}
            check(DirectThreat.last(a)==null, "reflected damage excluded");
            v.setInvul(true); hit(b,v,true); v.setInvul(false);
            check(DirectThreat.last(v)==a, "invulnerability rejects threat update");
            try(var context=DirectThreat.begin(b,v,null)){DirectThreat.onDamage(v,b,0,false,false);}
            check(DirectThreat.last(v)==a, "zero damage excluded");
            Skill hydro=SkillData.getInstance().getSkill(1235,1), aqua=SkillData.getInstance().getSkill(1295,1);
            check(hydro!=null && aqua!=null, "native Hydro Blast and Aqua Splash loaded");
            a.setTarget(v); a.doCast(hydro); a.setTarget(b);
            long end=System.nanoTime()+8_000_000_000L;
            v.setLastDirectThreat(null);
            while(DirectThreat.last(v)==null && System.nanoTime()<end) Thread.sleep(50);
            check(DirectThreat.last(v)==a, "scheduled Hydro Blast keeps original target after caster changes selection");
            a.abortCast();
            b.setLastDirectThreat(null); v.setLastDirectThreat(null);
            cast(a,aqua,v,List.of(b,v));
            check(DirectThreat.last(v)==a && DirectThreat.last(b)==null, "Aqua Splash records primary only, independent of list order");
            cast(b,aqua,a,List.of(a,v));
            check(DirectThreat.last(v)==a, "Aqua Splash aimed at another leaves previous threat unchanged");
            try(var context=DirectThreat.begin(b,v,SkillData.getInstance().getSkill(1171,1)))
            {
                v.getStatus().reduceHp(10,b,true,false,false);
            }
            check(DirectThreat.last(v)==a, "untargeted aura excluded");
            summon=new Servitor(NpcData.getInstance().getTemplate(12077),b);
            summon.setInstanceId(instance); summon.spawnMe(148975,46100,-3408); summon.fullRestore();
            hit(summon,v,true);
            check(DirectThreat.last(v)==b, "summon hit resolves to owner");
            handler.onCommand("amenaza",v,""); check(v.getTarget()==b, "selects owner rather than summon");
            var saved=v.getLastDirectThreat();
            v.setLastDirectThreat(new DirectThreat.Entry(new WeakReference<>(b),System.nanoTime()-DirectThreat.MAX_AGE_NANOS-1,instance));
            v.setTarget(a); handler.onCommand("amenaza",v,""); check(v.getTarget()==a, "expired threat leaves target untouched");
            v.setLastDirectThreat(saved); b.setInvisible(true); handler.onCommand("amenaza",v,"");
            check(v.getTarget()==a, "invisible responsible is not selectable"); b.setInvisible(false);
            b.setXYZ(155000,46100,-3408); handler.onCommand("amenaza",v,"");
            check(v.getTarget()==a, "out of range responsible is not selectable"); b.setXYZ(149000,46100,-3408);
            b.setInstanceId(0); handler.onCommand("amenaza",v,"");
            check(v.getTarget()==a, "different instance responsible is not selectable"); b.setInstanceId(instance);
            b.setDead(true); handler.onCommand("amenaza",v,"");
            check(v.getTarget()==a, "dead responsible is not selectable"); b.setDead(false);
            handler.onCommand("amenaza",v,"macro");
            check(v.getMacros().getAllMacroses().size()==1 && v.getMacros().getAllMacroses().values().iterator().next().getCommands().getFirst().getCmd().equals(".amenaza"), "native macro created with command text");
            handler.onCommand("amenaza",v,"macro");
            check(v.getMacros().getAllMacroses().size()==1, "macro creation idempotent");
            Files.writeString(output,String.join("\n",CHECKS)+"\nSUCCESS checks="+CHECKS.size()+"\n");
        }
        catch(Throwable error)
        {
            Files.writeString(output,String.join("\n",CHECKS)+"\nFAILED: "+error+"\n");
            throw error;
        }
        finally
        {
            if(summon!=null)
            {
                var task=Servitor.class.getDeclaredField("_summonLifeTask");task.setAccessible(true);
                if(task.get(summon) instanceof java.util.concurrent.Future<?> future)future.cancel(false);
                summon.decayMe();summon.getStatus().stopHpMpRegeneration();World.removeObject(summon);IdManager.getInstance().releaseId(summon.getObjectId());
            }
            for(Player p:probes)
            {
                for(int id:List.copyOf(p.getMacros().getAllMacroses().keySet()))p.deleteMacro(id);
                p.abortAttack();p.abortCast();p.stopAllEffects();p.setTarget(null);p.stopAllTasks();p.stopVitalityTask();
                p.getStatus().stopHpMpRegeneration();AttackStanceTaskManager.getInstance().removeAttackStanceTask(p);
                p.decayMe();World.removeObject(p);IdManager.getInstance().releaseId(p.getObjectId());
            }
            if(instance!=0)InstanceManager.getInstance().destroyInstance(instance);
        }
    }
}
