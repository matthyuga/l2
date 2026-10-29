package custom.GiranScreen;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.IdManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.*;

/** Opt-in, client-local decorative screen. Unpatched clients never receive its display ID. */
public final class GiranScreen extends Script implements IVoicedCommandHandler {
    public static final int DISPLAY_ID=59890,X=82165,Y=148611;
    private static final Logger LOG=Logger.getLogger(GiranScreen.class.getName());
    private static GiranScreen instance;
    private final Map<Integer,View> viewers=new ConcurrentHashMap<>();
    private static final class View {
        final Player player;final Npc screen;boolean visible;
        View(Player p,Npc n){player=p;screen=n;}
    }
    public GiranScreen(){
        if(instance!=null)throw new IllegalStateException("Giran screen already loaded");
        instance=this;VoicedCommandHandler.getInstance().registerHandler(this);
        ThreadPool.scheduleAtFixedRate(this::refresh,1000,1000);
        LOG.info("GIRAN_SCREEN READY: opt-in .pantalla; no global NPC spawn");
    }
    public String[] getCommandList(){return new String[]{"pantalla"};}
    private static boolean local(Player p){
        if(p==null||p.getClient()==null)return false;
        String ip=p.getClient().getIp();return "127.0.0.1".equals(ip)||"::1".equals(ip)||"0:0:0:0:0:0:0:1".equals(ip);
    }
    public static Npc createScreen(){
        Npc n=new Npc(DISPLAY_ID);n.setXYZ(X,Y,-3490); // East face of the original AdenaGirl pedestal.
        n.setHeading(0);n.setName("Nexus TV");n.setTitle("NexusCam en vivo");n.setInvul(true);n.setDecayed(false);
        if(World.findObject(n.getObjectId())!=null)throw new IllegalStateException("Screen unexpectedly global");
        return n;
    }
    public boolean onCommand(String command,Player p,String params){
        if(!local(p)){if(p!=null)p.sendMessage("Pantalla de laboratorio disponible solo en conexion local.");return false;}
        String action=params==null?"":params.trim().toLowerCase(java.util.Locale.ROOT);
        if(action.equals("off")){remove(p.getObjectId());p.sendMessage("Pantalla oculta para esta sesion.");return true;}
        if(!action.isEmpty()&&!action.equals("on")&&!action.equals("ir")){p.sendMessage("Usa .pantalla, .pantalla ir o .pantalla off");return true;}
        if(p.getInstanceId()!=0||p.isInCombat()||p.isDead()||p.inObserverMode()){
            p.sendMessage("Usa tu jugador en el mundo principal, vivo y fuera de combate/observacion.");return true;
        }
        View v=viewers.computeIfAbsent(p.getObjectId(),id->new View(p,createScreen()));
        if(action.equals("ir"))p.teleToLocation(new Location(X+600,Y,GeoEngine.getInstance().getHeight(X+600,Y,-3400),32768),false);
        update(v);
        p.sendMessage("Nexus TV sobre el mural de Giran, mirando hacia la plaza. .pantalla ir te lleva delante; .pantalla off la oculta.");
        return true;
    }
    private void update(View v){
        Player p=v.player;
        boolean nearby=p.getInstanceId()==0&&!p.isTeleporting()&&Math.abs((long)p.getX()-X)<7000&&Math.abs((long)p.getY()-Y)<7000;
        if(nearby&&!v.visible){p.sendPacket(new AbstractNpcInfo.NpcInfo(v.screen,p));v.visible=true;}
        else if(!nearby&&v.visible){p.sendPacket(new DeleteObject(v.screen));v.visible=false;}
    }
    private void remove(int id){
        View v=viewers.remove(id);if(v==null)return;
        if(v.visible&&v.player.isOnline()&&v.player.getClient()!=null)v.player.sendPacket(new DeleteObject(v.screen));
        v.screen.setDecayed(true);IdManager.getInstance().releaseId(v.screen.getObjectId());
    }
    private void refresh(){
        for(View v:viewers.values())try{
            Player p=v.player;if(!p.isOnline()||p.getClient()==null||World.getPlayer(p.getObjectId())!=p)remove(p.getObjectId());else update(v);
        }catch(Exception e){LOG.log(Level.WARNING,"Giran screen refresh",e);remove(v.player.getObjectId());}
    }
    public static void main(String[] args){if(instance==null)new GiranScreen();}
}
