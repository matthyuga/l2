package custom.EquipmentShowcase;

import java.nio.file.Path;
import java.util.List;
import java.util.logging.Logger;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Element;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.holders.player.Macro;
import org.l2jmobius.gameserver.entity.actor.holders.player.MacroCmd;
import org.l2jmobius.gameserver.entity.actor.enums.player.MacroType;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Passive gallery, explicitly spawned by the local GM. */
public class EquipmentShowcase extends Script implements IVoicedCommandHandler {
    public static final int FIRST=62000, LAST=62156;
    private static final Logger LOG=Logger.getLogger(EquipmentShowcase.class.getName());
    private EquipmentShowcase(){
        int[] ids=new int[LAST-FIRST+1];for(int i=0;i<ids.length;i++)ids[i]=FIRST+i;
        addSpawnId(ids);
        VoicedCommandHandler.getInstance().registerHandler(this);
        AdminCommandHandler.getInstance().registerHandler(new IAdminCommandHandler(){
            public String[] getCommandList(){return new String[]{"admin_galeria"};}
            public boolean onCommand(String command,Player p){
                String[] parts=command.split("\\s+",2);
                return EquipmentShowcase.this.onCommand("galeria",p,parts.length>1?parts[1]:"");
            }
        });
        Containers.Players().addListener(new ConsumerEventListener(Containers.Players(), EventType.ON_PLAYER_LOGIN,
            (OnPlayerLogin e)->{if(e.getPlayer().isGM())installMacro(e.getPlayer());},this));
        hide();
        LOG.info("EQUIPMENT_SHOWCASE: hidden by default; .galeria / native Galeria macro enable 51 armor sets on demand.");
    }
    public static boolean owns(Npc n){return n.getId()>=FIRST && n.getId()<=LAST;}
    public static void protect(Npc n){
        if(!owns(n))return;
        n.setInvul(true);n.setImmobilized(true);n.setAutoAttackable(false);
        n.setRandomWalking(false);n.setRandomAnimationEnabled(false);
    }
    public static synchronized int count(){
        int count=0;for(var o:World.getVisibleObjects())if(o instanceof Npc n && owns(n))count++;return count;
    }
    public static synchronized void hide(){
        for(var o:List.copyOf(World.getVisibleObjects()))if(o instanceof Npc n && owns(n)){
            if(n.getSpawn()!=null)n.getSpawn().stopRespawn();n.deleteMe();
        }
    }
    public static synchronized int show(boolean all)throws Exception{
        hide();
        try{
            var factory=DocumentBuilderFactory.newInstance();
            factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
            var nodes=factory.newDocumentBuilder().parse(Path.of("data/lab/world-spawns/EquipmentShowcase.xml").toFile()).getElementsByTagName("npc");
            int expected=all?157:51;
            for(int i=0;i<nodes.getLength();i++){
                var e=(Element)nodes.item(i);int id=Integer.parseInt(e.getAttribute("id"));
                if(id<FIRST || id>(all?LAST:62050))continue;
                var s=new Spawn(id);
                s.setXYZ(Integer.parseInt(e.getAttribute("x")),Integer.parseInt(e.getAttribute("y")),Integer.parseInt(e.getAttribute("z")));
                s.setHeading(Integer.parseInt(e.getAttribute("heading")));s.stopRespawn();
                var n=s.doSpawn(false);if(n==null)throw new IllegalStateException("Cannot spawn "+id);protect(n);
            }
            if(count()!=expected)throw new IllegalStateException("Incomplete gallery: "+count()+"/"+expected);
            return count();
        }catch(Exception e){hide();throw e;}
    }
    public static void installMacro(Player p){
        var macros=p.getMacros().getAllMacroses().values();
        if(macros.stream().anyMatch(m->m.getCommands().stream().anyMatch(c->c.getCmd().equals("//galeria alternar"))))return;
        if(macros.size()>=48){p.sendMessage("Galeria: macros llenas. Usa .galeria alternar.");return;}
        p.registerMacro(new Macro(0,0,"Galeria","Mostrar u ocultar los sets de Giran","SETS",
            List.of(new MacroCmd(0,MacroType.TEXT,0,0,"//galeria alternar"))));
    }
    @Override public void onSpawn(Npc npc){protect(npc);}
    @Override public String[] getCommandList(){return new String[]{"galeria"};}
    @Override public synchronized boolean onCommand(String command,Player p,String params){
        if(!p.isGM()){p.sendMessage("Galeria: acceso de laboratorio GM.");return true;}
        String action=params==null?"":params.trim().toLowerCase(java.util.Locale.ROOT);
        if(action.equals("estado")){p.sendMessage("Galeria: "+count()+" maniquies visibles.");return true;}
        if(action.equals("macro")){installMacro(p);p.sendMessage("Macro Galeria disponible en Alt+R.");return true;}
        if(action.equals("ocultar") || action.equals("off") || (action.equals("alternar") && count()>0)){
            hide();p.sendMessage("Galeria oculta.");return true;
        }
        if(!List.of("","mostrar","sets","todos","alternar").contains(action)){
            p.sendMessage(".galeria [alternar|ocultar|todos|estado|macro]");return true;
        }
        if(p.isInCombat() || p.getInstanceId()!=0){p.sendMessage("Sal de combate y de la instancia para mostrar la galeria.");return true;}
        try{
            int n=show(action.equals("todos"));
            if(action.isEmpty())p.teleToLocation(81920,147950,-3400);
            p.sendMessage("Galeria: "+n+" maniquies. Usa la macro otra vez para ocultarlos.");
        }catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"Cannot show gallery",e);p.sendMessage("No se pudo mostrar la galeria; revisa el log.");}
        return true;
    }
    public static void main(String[] args){new EquipmentShowcase();}
}
