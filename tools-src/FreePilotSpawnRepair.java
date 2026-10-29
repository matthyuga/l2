import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.IdManager;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.taskmanagers.AttackStanceTaskManager;

/** Method-only patch and isolated spawn checks; no attacks on the connected player. */
public class FreePilotSpawnRepair
{
    private static final List<String> report=new ArrayList<>();
    private static void check(boolean ok,String name){if(!ok)throw new AssertionError(name);report.add("PASS "+name);}
    private static Object field(Object o,String name)throws Exception{var f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
    public static void agentmain(String directory,Instrumentation inst)throws Exception
    {
        Path dir=Path.of(directory),root=dir.getParent().getParent();
        Object handler=VoicedCommandHandler.getInstance().getHandler("ia");
        Class<?> type=handler.getClass();
        Player probe=null;int instance=0;
        var finish=type.getDeclaredMethod("finish",String.class,Player.class);finish.setAccessible(true);
        Object lock=field(handler,"LOCK");
        try
        {
            inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(root.resolve("build/ia-free-spawn/custom/LabCombatPilots/LabCombatPilots.class"))));
            report.add("APPLIED live LabCombatPilots methods without restarting server");
            synchronized(lock)
            {
                if(field(handler,"active")!=null || field(handler,"smoke")!=null)
                {report.add("SKIP isolated spawn test: existing session preserved");}
                else
                {
                    instance=InstanceManager.getInstance().createDynamicInstance(0).getId();
                    var ctor=Player.class.getDeclaredConstructor(int.class,PlayerTemplate.class,String.class,PlayerAppearance.class);ctor.setAccessible(true);
                    probe=ctor.newInstance(IdManager.getInstance().getNextId(),PlayerTemplateData.getInstance().getTemplate(0),"spawnprobe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));
                    probe.setName("SpawnProbe");probe.setOnlineStatus(true,false);probe.setInvul(true);probe.setInstanceId(instance);probe.setEnteredWorld();
                    probe.spawnMe(45500,48300,GeoEngine.getInstance().getHeight(45500,48300,-3056));probe.revalidateZone(true);
                    AttackStanceTaskManager.getInstance().addAttackStanceTask(probe);
                    probe.getAI().setAutoAttacking(true);
                    check(probe.isInCombat() && probe.isInvul() && !probe.isInsideZone(ZoneId.PVP),"test controller outside PvP, in combat, invulnerable, private instance");
                    var start=type.getDeclaredMethod("start",Player.class,boolean.class);start.setAccessible(true);
                    start.invoke(handler,probe,true);
                    Object mage=field(handler,"active");check(mage!=null,"mage spawns despite previous location/combat/invulnerability restrictions");
                    Player bot=(Player)field(mage,"bot");
                    check(bot.getInstanceId()==instance && bot.calculateDistance2D(probe)<=310,"mage spawns near controller in same instance");
                    var tick=type.getDeclaredMethod("tick");tick.setAccessible(true);tick.invoke(handler);
                    check(field(handler,"active")==mage,"pilot survives tick outside Coliseum");
                    start.invoke(handler,probe,false);
                    Object physical=field(handler,"active");check(physical!=null && physical!=mage,"repeat invocation replaces own active pilot");
                    check(World.getPlayer(bot.getObjectId())==null && !bot.isOnline(),"previous mage unloaded and marked offline");
                    Player physicalBot=(Player)field(physical,"bot");
                    check(physicalBot.getName().equals("ArenaRiven") && physicalBot.getInstanceId()==instance && physicalBot.calculateDistance2D(probe)<=310,"physical pilot spawns near controller");
                    finish.invoke(handler,"SPAWN_REGRESSION",probe);
                    check(field(handler,"active")==null && World.getPlayer(physicalBot.getObjectId())==null && !physicalBot.isOnline(),"cancel releases pilot cleanly");
                }
            }
            for(Player p:World.getPlayers())if(p.getClient()!=null)
            {report.add("CONNECTED "+p.getName());p.sendMessage("IA actualizada: puedes invocar mago/fisico cerca tuyo sin salir de combate ni entrar al suelo PvP. Repetir el macro reemplaza tu piloto.");}
            report.add("SUCCESS");
        }
        catch(Throwable e){report.add("FAILED "+e);throw e;}
        finally
        {
            synchronized(lock)
            {
                Object s=field(handler,"active");
                if(probe!=null && s!=null && ((Integer)field(s,"controllerId"))==probe.getObjectId())finish.invoke(handler,"SPAWN_REGRESSION_CLEANUP",probe);
                if(probe!=null){AttackStanceTaskManager.getInstance().removeAttackStanceTask(probe);probe.setOnlineStatus(false,false);probe.deleteMe();IdManager.getInstance().releaseId(probe.getObjectId());}
                if(instance!=0)InstanceManager.getInstance().destroyInstance(instance);
            }
            Files.writeString(dir.resolve("verification.txt"),String.join("\n",report)+"\n");
        }
    }
}
