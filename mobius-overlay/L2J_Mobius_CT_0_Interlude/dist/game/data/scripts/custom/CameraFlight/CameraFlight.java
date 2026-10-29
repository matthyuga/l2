package custom.CameraFlight;

import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.ScheduledFuture;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.*;

/** Dedicated flying camera pilot, based on native wyvern flight and first-person view. */
public final class CameraFlight extends Script implements IVoicedCommandHandler {
    private static final Logger LOG=Logger.getLogger(CameraFlight.class.getName());
    private static final Path RETURN_FILE=Path.of("config/CameraFlight-return.properties");
    private static final Map<String,Location> PLACES=Map.of(
        "giran",new Location(82698,148638,-3073),
        "coliseo",new Location(147450,46728,-3010),
        "elven",new Location(46934,51467,-2577));
    private static CameraFlight instance;
    private final String account,name;
    private final int characterId;
    private final boolean autoStart;
    private Player pilot,pending;
    private Location origin;
    private boolean oldInvul,oldInvisible,oldParalyzed;
    private long generation;
    private ScheduledFuture<?> monitor;

    public CameraFlight() throws Exception {
        if(instance!=null)throw new IllegalStateException("Camera flight already installed");
        Properties cfg=new Properties();try(var in=Files.newInputStream(Path.of("config/CameraObserver.properties"))){cfg.load(in);}
        account=cfg.getProperty("Account","");name=cfg.getProperty("Character","");
        autoStart="flight".equalsIgnoreCase(cfg.getProperty("StartMode","flight"));
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT charId,accesslevel FROM characters WHERE char_name=? AND account_name=?")){
            q.setString(1,name);q.setString(2,account);
            try(ResultSet r=q.executeQuery()){
                if(!r.next()||r.getInt(2)!=0)throw new IllegalStateException("Reserved non-GM camera missing");
                characterId=r.getInt(1);
            }
        }
        recoverReturnPoint();
        instance=this;VoicedCommandHandler.getInstance().registerHandler(this);
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_PLAYER_LOGIN,
            (OnPlayerLogin e)->{
                Player p=e.getPlayer();
                if(autoStart&&allowed(p))ThreadPool.schedule(()->{
                    if(p.isOnline()&&p.getClient()!=null&&World.getPlayer(characterId)==p)onCommand("camvuelo",p,"on");
                },4500);
            },this));
        LOG.info("CAMERA_FLIGHT READY name="+name+" id="+characterId+" automatic="+autoStart+" GM=false; no session timeout");
    }
    private boolean allowed(Player p){return p!=null&&p.getObjectId()==characterId&&account.equals(p.getAccountName())&&name.equals(p.getName())&&!p.isGM();}
    public String[] getCommandList(){return new String[]{"camvuelo"};}

    private void recoverReturnPoint() throws Exception {
        if(!Files.exists(RETURN_FILE))return;
        if(World.getPlayer(characterId)!=null)throw new IllegalStateException("Cannot recover active camera");
        Properties r=new Properties();try(var in=Files.newInputStream(RETURN_FILE)){r.load(in);}
        if(!account.equals(r.getProperty("Account"))||!name.equals(r.getProperty("Character"))||!Integer.toString(characterId).equals(r.getProperty("Id")))
            throw new IllegalStateException("Camera return record identity mismatch");
        Location loc=checked(Integer.parseInt(r.getProperty("X")),Integer.parseInt(r.getProperty("Y")),Integer.parseInt(r.getProperty("Z")));
        Player p=Player.load(characterId);if(!allowed(p))throw new IllegalStateException("Recovery identity mismatch");
        try{p.setXYZ(loc.getX(),loc.getY(),loc.getZ());p.storeMe();}finally{p.deleteMe();p.setOnlineStatus(false,true);}
        Files.delete(RETURN_FILE);LOG.info("CAMERA_FLIGHT recovered reserved pilot ground return point");
    }
    private void saveReturnPoint() throws Exception {
        Properties r=new Properties();r.setProperty("Account",account);r.setProperty("Character",name);r.setProperty("Id",Integer.toString(characterId));
        r.setProperty("X",Integer.toString(origin.getX()));r.setProperty("Y",Integer.toString(origin.getY()));r.setProperty("Z",Integer.toString(origin.getZ()));
        Path temp=RETURN_FILE.resolveSibling("CameraFlight-return.properties.tmp");
        try(var out=Files.newOutputStream(temp)){r.store(out,"Dedicated camera return position; local runtime state");}
        Files.move(temp,RETURN_FILE,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
    }
    private static Location checked(int x,int y,int z){
        if(Math.abs((long)x)>500000||Math.abs((long)y)>500000||z < -15000||z > 9000)throw new IllegalArgumentException("Coordenadas fuera del rango de camara.");
        return new Location(x,y,z);
    }
    private static void configure(Player p){
        p.stopMove(null);p.setParalyzed(false);p.setInvul(true);p.setInvisible(true);
        p.setMount(12621,55);p.broadcastPacket(new Ride(p));p.broadcastUserInfo();
    }
    public synchronized boolean onCommand(String command,Player p,String params){
        if(!allowed(p)){if(p!=null)p.sendMessage("Comando reservado a NexusCam.");return false;}
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        if(action.equals("off")||action.equals("salir")){
            pending=null;generation++;if(pilot==p)stop("manual");return true;
        }
        if(pilot==p){
            try{
                if(action.equals("subir")||action.equals("bajar")){
                    if(p.isTeleporting()){p.sendMessage("Espera al cambio de altura anterior.");return true;}
                    reposition(p,checked(p.getX(),p.getY(),p.getZ()+(action.equals("subir")?200:-200)));
                }else if(PLACES.containsKey(action))reposition(p,PLACES.get(action));
                else menu(p);
            }catch(IllegalArgumentException e){p.sendMessage(e.getMessage());}
            return true;
        }
        if(!Set.of("","on","estado").contains(action)){p.sendMessage("Primero .camvuelo on");return true;}
        if(pending==p){p.sendMessage("Preparando camara de vuelo...");return true;}
        if(p.isDead()||p.hasSummon()||p.isMounted()||p.isInCombat()||p.getInstanceId()!=0){p.sendMessage("La camara requiere mundo principal, sin combate, summon ni montura previa.");return true;}
        if(p.inObserverMode())p.leaveObserverMode();
        pending=p;long token=++generation;startWhenReady(p,token,0);return true;
    }
    private synchronized void startWhenReady(Player p,long token,int attempt){
        if(pending!=p||generation!=token)return;
        if(!allowed(p)||!p.isOnline()||p.getClient()==null||World.getPlayer(characterId)!=p){pending=null;return;}
        if(p.isTeleporting()){
            if(attempt>=20){pending=null;p.sendMessage("Teleport pendiente. Proba .camvuelo nuevamente al terminar.");return;}
            ThreadPool.schedule(()->startWhenReady(p,token,attempt+1),500);return;
        }
        pending=null;origin=new Location(p.getX(),p.getY(),p.getZ());
        oldInvul=p.isInvul();oldInvisible=p.isInvisible();oldParalyzed=p.isParalyzed();pilot=p;
        try{
            saveReturnPoint();configure(p);
            reposition(p,checked(origin.getX(),origin.getY(),Math.min(9000,origin.getZ()+400)));
            monitor=ThreadPool.scheduleAtFixedRate(()->{
                synchronized(CameraFlight.this){
                    if(pilot!=p)return;
                    if(!p.isOnline()||p.getClient()==null||World.getPlayer(characterId)!=p||p.inObserverMode())stop("disconnect or mode changed");
                }
            },1000,1000);
            LOG.info("CAMERA_FLIGHT START id="+characterId+" origin="+origin.getX()+","+origin.getY()+","+origin.getZ());
            p.sendMessage("Camara de vuelo activa, sin limite de tiempo. Teclado/mouse; .camvuelo para controles; .camvuelo off vuelve al origen.");
        }catch(Exception e){LOG.log(Level.WARNING,"Camera flight start",e);stop("start failure");p.sendMessage("No se pudo iniciar el vuelo.");}
    }
    private void reposition(Player p,Location loc){
        p.teleToLocation(loc,false);long token=generation;firstPersonWhenReady(p,token,0);
    }
    private synchronized void firstPersonWhenReady(Player p,long token,int attempt){
        if(pilot!=p||generation!=token||!p.isOnline())return;
        if(p.isTeleporting()){
            if(attempt<20)ThreadPool.schedule(()->firstPersonWhenReady(p,token,attempt+1),250);
        }else p.sendPacket(new CameraMode(1));
    }
    private synchronized void stop(String reason){
        Player p=pilot;if(p==null)return;
        pilot=null;generation++;if(monitor!=null){monitor.cancel(false);monitor=null;}
        try{
            p.stopMove(null);if(p.inObserverMode())p.leaveObserverMode();
            if(p.isOnline()&&p.getClient()!=null)p.teleToLocation(origin,false);else p.setXYZ(origin.getX(),origin.getY(),origin.getZ());
        }finally{
            p.setMount(0,0);p.setInvul(oldInvul);p.setInvisible(oldInvisible);p.setParalyzed(oldParalyzed);p.setFalling();
            p.sendPacket(new CameraMode(0));p.broadcastPacket(new Ride(p));p.broadcastUserInfo();
            try{p.storeMe();Files.deleteIfExists(RETURN_FILE);}catch(Exception e){LOG.log(Level.WARNING,"Camera return record retained for restart recovery",e);}
            LOG.info("CAMERA_FLIGHT STOP id="+characterId+" reason="+reason);
            if(p.isOnline())p.sendMessage("Camara de vuelo detenida; origen restaurado.");
        }
    }
    private void menu(Player p){
        StringBuilder h=new StringBuilder("<html><body><center><font color=LEVEL>Camara de vuelo</font><br>Teclado y mouse para desplazarte.<br>Sin limite de tiempo.<br>");
        for(String action:new String[]{"subir","bajar","giran","coliseo","elven","off"})
            h.append("<button value=\"").append(action).append("\" action=\"bypass -h voice .camvuelo ").append(action).append("\" width=160 height=24 back=\"L2UI_ch3.bigbutton_down\" fore=\"L2UI_ch3.bigbutton\"><br1>");
        h.append("subir/bajar: 200 de altura.<br>off: volver al origen.<br>Cuenta dedicada sin permisos GM.</center></body></html>");
        NpcHtmlMessage msg=new NpcHtmlMessage();msg.setHtml(h.toString());p.sendPacket(msg);
    }
    public static void main(String[] args)throws Exception{if(instance==null)new CameraFlight();}
}
