import java.lang.instrument.*;
import java.lang.invoke.MethodHandles;
import java.nio.file.*;
import java.util.*;

import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.holders.player.Macro;
import org.l2jmobius.gameserver.entity.actor.holders.player.MacroCmd;
import org.l2jmobius.gameserver.entity.actor.enums.player.MacroType;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;
import org.l2jmobius.gameserver.data.xml.AdminData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.IdManager;
import org.l2jmobius.gameserver.mechanics.sevensigns.SevenSigns;

/** Apply narrow method-only repairs without disconnecting the local player. */
public class LabServiceRepair
{
    private static final List<String> REPORT=new ArrayList<>();
    private static void check(boolean ok,String name){if(!ok)throw new AssertionError(name);REPORT.add("PASS "+name);}
    private static Class<?> find(Instrumentation i,String name){return Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals(name)).findFirst().orElseThrow();}
    public static void agentmain(String directory,Instrumentation inst)throws Exception
    {
        Path dir=Path.of(directory),root=dir.getParent().getParent(),classes=root.resolve("build/lab-service-repair");
        Player probe=null;
        try
        {
            Class<?> threat=find(inst,"handlers.chat.commands.voiced.ThreatCommand");
            check(inst.isRedefineClassesSupported(),"method replacement supported");
            inst.redefineClasses(
                new ClassDefinition(SevenSigns.class,Files.readAllBytes(classes.resolve("org/l2jmobius/gameserver/mechanics/sevensigns/SevenSigns.class"))),
                new ClassDefinition(threat,Files.readAllBytes(classes.resolve("handlers/chat/commands/voiced/ThreatCommand.class"))));
            REPORT.add("APPLIED SevenSigns and ThreatCommand methods; active client retained");
            Class<?> anchor=find(inst,"handlers.chat.commands.admin.AdminBuildLab");
            Class<?> actions=MethodHandles.privateLookupIn(anchor,MethodHandles.lookup()).defineClass(
                Files.readAllBytes(classes.resolve("handlers/chat/commands/admin/AdminLabActions.class")));
            IAdminCommandHandler handler=(IAdminCommandHandler)actions.getConstructor().newInstance();
            AdminCommandHandler.getInstance().registerHandler(handler);
            AdminData.getInstance().load();
            check(AdminCommandHandler.getInstance().getHandler("admin_amenaza")!=null,"native threat alias registered");
            check(AdminCommandHandler.getInstance().getHandler("admin_ia")!=null,"native pilot alias registered");
            check(VoicedCommandHandler.getInstance().getHandler("ia")!=null,"original pilot controller available");
            SevenSigns signs=SevenSigns.getInstance();
            for(int seal:new int[]{SevenSigns.SEAL_AVARICE,SevenSigns.SEAL_GNOSIS,SevenSigns.SEAL_STRIFE})
            {
                check(signs.getSealOwner(seal)==SevenSigns.CABAL_NULL,"disabled seal "+seal+" has neutral owner");
                check(signs.getSealProportion(seal,SevenSigns.CABAL_DAWN)==0&&signs.getSealProportion(seal,SevenSigns.CABAL_DUSK)==0,"disabled seal "+seal+" has zero proportions");
            }
            var ctor=Player.class.getDeclaredConstructor(int.class,PlayerTemplate.class,String.class,PlayerAppearance.class);
            ctor.setAccessible(true);
            probe=ctor.newInstance(IdManager.getInstance().getNextId(),PlayerTemplateData.getInstance().getTemplate(0),"serviceprobe",
                new PlayerAppearance((byte)0,(byte)0,(byte)0,false));
            probe.setName("ServiceProbe");
            for(int id:new int[]{50008,50010})
            {
                var npc=World.getNpc(id);
                check(npc!=null,"service NPC present "+id);
                probe.setXYZ(npc.getX(),npc.getY(),npc.getZ());
                npc.showChatWindow(probe);
                check(true,"service dialogue completes without exception "+id+" "+npc.getName()+" "+npc.getClass().getSimpleName());
            }
            for(Player p:World.getPlayers())if(p.getClient()!=null && p.getName().equals("Hellkevin"))
            {
                check(p.isGM()&&AdminData.getInstance().hasAccess("admin_amenaza",p.getAccessLevel())&&AdminData.getInstance().hasAccess("admin_ia",p.getAccessLevel()),"local player authorized for native aliases");
                int changed=0;
                for(Macro m:List.copyOf(p.getMacros().getAllMacroses().values()))
                {
                    if(m.getCommands().size()!=1)continue;
                    String line=m.getCommands().getFirst().getCmd().trim().toLowerCase(Locale.ROOT);
                    if(!Set.of(".amenaza",".amenaza macro",".agresor",".agresor macro").contains(line))continue;
                    p.registerMacro(new Macro(m.getId(),m.getIcon(),m.getName(),"Selecciona al agresor directo",m.getAcronym(),
                        List.of(new MacroCmd(0,MacroType.TEXT,0,0,"//amenaza"))));changed++;
                }
                REPORT.add("MIGRATED "+changed+" threat macros to //amenaza; names/IDs/icons preserved");
                handler.onCommand("admin_ia macros",p);
                var macros=p.getMacros().getAllMacroses().values();
                check(macros.stream().anyMatch(m->m.getCommands().stream().anyMatch(c->c.getCmd().equals("//ia mago"))),"native IA Mago macro installed");
                check(macros.stream().anyMatch(m->m.getCommands().stream().anyMatch(c->c.getCmd().equals("//ia fisico"))),"native IA Fisico macro installed");
                handler.onCommand("admin_ia estado",p);
                check(p.getClient()!=null,"existing client remains connected");
                p.sendMessage("Reparados los NPC y macros. Amenaza usa //amenaza; IA Mago/IA Fisico estan en Alt+R.");
            }
            Files.writeString(dir.resolve("repair.txt"),String.join("\n",REPORT)+"\nSUCCESS\n");
        }
        catch(Throwable e){Files.writeString(dir.resolve("repair.txt"),String.join("\n",REPORT)+"\nFAILED "+e+"\n");throw e;}
        finally
        {
            if(probe!=null){probe.stopAllTasks();probe.stopVitalityTask();probe.getStatus().stopHpMpRegeneration();World.removeObject(probe);IdManager.getInstance().releaseId(probe.getObjectId());}
        }
    }
}
