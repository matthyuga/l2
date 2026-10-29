package handlers.chat.commands.admin;

import java.util.List;
import java.util.Map;

import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.MacroType;
import org.l2jmobius.gameserver.entity.actor.holders.player.Macro;
import org.l2jmobius.gameserver.entity.actor.holders.player.MacroCmd;
import org.l2jmobius.gameserver.handler.IAdminCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/** Native GM aliases: macro presses use admin bypasses instead of ordinary chat. */
public class AdminLabActions implements IAdminCommandHandler
{
    @Override
    public boolean onCommand(String fullCommand, Player player)
    {
        if (!player.isGM()) return false;
        String[] parts=fullCommand.split("\\s+",2);
        String command=parts[0].equals("admin_amenaza")?"amenaza":"ia";
        String params=parts.length==2?parts[1]:"";
        if(command.equals("ia") && params.equalsIgnoreCase("macros"))
        {
            installPilotMacro(player,"IA Mago","//ia mago","MAGO");
            installPilotMacro(player,"IA Fisico","//ia fisico","FISC");
            player.sendMessage("Macros IA listos en Alt+R. Arrastralos a la barra.");
            return true;
        }
        var handler=VoicedCommandHandler.getInstance().getHandler(command);
        if(handler==null){player.sendMessage("El controlador de "+command+" no esta disponible.");return false;}
        return handler.onCommand(command,player,params);
    }

    private static void installPilotMacro(Player p,String name,String text,String acronym)
    {
        Map<Integer,Macro> all=p.getMacros().getAllMacroses();
        synchronized(all)
        {
            for(Macro macro:all.values())
            {
                if(macro.getCommands().size()==1 && macro.getCommands().getFirst().getCmd().equalsIgnoreCase(text))return;
            }
            if(all.size()>=24){p.sendMessage("Libera un espacio de macros para "+name+".");return;}
            String unique=name;
            for(int suffix=2;containsName(all,unique);suffix++)unique=name+suffix;
            p.registerMacro(new Macro(0,0,unique,"Inicia piloto IA del laboratorio",acronym,
                List.of(new MacroCmd(0,MacroType.TEXT,0,0,text))));
        }
    }

    private static boolean containsName(Map<Integer,Macro> all,String name)
    {
        return all.values().stream().anyMatch(m->m.getName().equalsIgnoreCase(name));
    }

    @Override
    public String[] getCommandList(){return new String[]{"admin_amenaza","admin_ia"};}
}
