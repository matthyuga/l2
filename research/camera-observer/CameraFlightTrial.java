import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.concurrent.ScheduledFuture;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.network.serverpackets.*;

/** Bounded native flying-mount experiment. It is not a detached free-camera plugin. */
public class CameraFlightTrial implements IVoicedCommandHandler {
    private static Path output;
    private Player pilot;
    private Location origin;
    private boolean oldInvul, oldInvisible, oldParalyzed;
    private long generation;
    private ScheduledFuture<?> monitor;
    public static void agentmain(String directory, Instrumentation ignored) throws Exception {
        output=Path.of(directory,"flight-trial.txt");
        if(VoicedCommandHandler.getInstance().getHandler("camvuelo")!=null)
            throw new IllegalStateException("Flight trial already registered");
        Files.writeString(output,"Native flying mount trial; detached free-camera not implemented.\n");
        if(World.getPlayer(268436061)==null) smoke();
        VoicedCommandHandler.getInstance().registerHandler(new CameraFlightTrial());
        log("READY .camvuelo; no online character changed at installation");
    }
    private static boolean allowed(Player p) {
        return p!=null && p.getObjectId()==268436061 && "nexuscamera".equals(p.getAccountName())
            && "NexusCam".equals(p.getName()) && !p.isGM();
    }
    private static synchronized void log(String text) {
        try { Files.writeString(output,text+"\n",StandardOpenOption.APPEND); }catch(Exception e){}
    }
    private static void configure(Player p) {
        p.stopMove(null); p.setParalyzed(false); p.setInvul(true); p.setInvisible(true);
        // Same native mount mechanism as AdminRide; level55 avoids a missing level1 pet speed row.
        p.setMount(12621,55);
        p.broadcastPacket(new Ride(p)); p.broadcastUserInfo();
    }
    private static void smoke() throws Exception {
        Player p=Player.load(268436061);
        if(!allowed(p) || p.inObserverMode() || p.isMounted() || p.hasSummon())
            throw new IllegalStateException("Reserved offline character not suitable for smoke");
        boolean invul=p.isInvul(),invisible=p.isInvisible(),paralyzed=p.isParalyzed();
        p.setOnlineStatus(true,false);
        try {
            configure(p);
            if(!p.isFlying() || !p.isMounted() || p.isMovementDisabled() || p.getMoveSpeed()<=0 || p.isGM())
                throw new IllegalStateException("Native flight flags failed");
            log("PASS offline native configure: flying=true mounted=true movementDisabled=false GM=false speed="+p.getMoveSpeed());
            p.setMount(0,0);
            if(p.isFlying() || p.isMounted()) throw new IllegalStateException("Unmount did not restore native state");
            log("PASS offline native cleanup: flying=false mounted=false; no position or level changes");
        } finally {
            p.setMount(0,0); p.setInvul(invul);p.setInvisible(invisible);p.setParalyzed(paralyzed);
            p.deleteMe();p.setOnlineStatus(false,true);
        }
    }
    public String[] getCommandList(){return new String[]{"camvuelo"};}
    public synchronized boolean onCommand(String command,Player p,String params) {
        if(!allowed(p)) return false;
        String action=params==null?"":params.trim().toLowerCase();
        if(action.equals("off")){if(pilot==p)stop("manual");return true;}
        if(pilot==p) {
            if(action.equals("subir")||action.equals("bajar")) {
                int z=p.getZ()+(action.equals("subir")?200:-200);
                if(z < -15000 || z > 9000){p.sendMessage("Altura fuera del rango de la prueba.");return true;}
                if(p.isTeleporting()){p.sendMessage("Espera al cambio de altura anterior.");return true;}
                p.teleToLocation(new Location(p.getX(),p.getY(),z),false);
                long token=generation;ThreadPool.schedule(()->firstPerson(p,token),1500);
            } else p.sendMessage("Vuelo de prueba activo. .camvuelo subir / bajar / off");
            return true;
        }
        if(p.inObserverMode()){p.sendMessage("Pulsa Return para salir del observador fijo y luego escribe .camvuelo");return true;}
        if(pilot!=null || p.isTeleporting() || p.isDead() || p.hasSummon() || p.isMounted() || p.isInCombat()) {
            p.sendMessage("La prueba requiere estar vivo, sin summon/montura, fuera de combate y sin teleport pendiente.");return true;
        }
        origin=new Location(p.getX(),p.getY(),p.getZ());
        oldInvul=p.isInvul();oldInvisible=p.isInvisible();oldParalyzed=p.isParalyzed();
        pilot=p;long token=++generation;
        try {
            configure(p);
            p.teleToLocation(new Location(origin.getX(),origin.getY(),Math.min(9000,origin.getZ()+400)),false);
            ThreadPool.schedule(()->firstPerson(p,token),1500);
            monitor=ThreadPool.scheduleAtFixedRate(()->{
                synchronized(CameraFlightTrial.this){
                    if(pilot!=p || generation!=token)return;
                    if(!p.isOnline()||p.getClient()==null||p.inObserverMode())stop("disconnect or observer changed");
                }
            },1000,1000);
            ThreadPool.schedule(()->{synchronized(CameraFlightTrial.this){if(pilot==p&&generation==token)stop("120s timeout");}},120000);
            log("START xyz="+p.getX()+","+p.getY()+","+p.getZ()+" flying="+p.isFlying()+" observer="+p.inObserverMode());
            p.sendMessage("VUELO NATIVO DE PRUEBA 120s. Flechas/click; .camvuelo subir / bajar / off. Usa montura wyvern y primera persona; no es camara libre separada.");
        }catch(Exception e){log("ERROR "+e);stop("start failure");p.sendMessage("Prueba de vuelo cancelada; revisar registro.");}
        return true;
    }
    private synchronized void firstPerson(Player p,long token){
        if(pilot==p&&generation==token&&p.isOnline()&&!p.isTeleporting())p.sendPacket(new CameraMode(1));
    }
    private synchronized void stop(String reason) {
        Player p=pilot;if(p==null)return;
        pilot=null;generation++;if(monitor!=null){monitor.cancel(false);monitor=null;}
        log("STOP "+reason+" last_xyz="+p.getX()+","+p.getY()+","+p.getZ());
        try {
            p.stopMove(null);
            if(p.inObserverMode())p.leaveObserverMode();
            if(p.isOnline()&&p.getClient()!=null)p.teleToLocation(origin,false);else p.setXYZ(origin.getX(),origin.getY(),origin.getZ());
        }finally {
            p.setMount(0,0);p.setInvul(oldInvul);p.setInvisible(oldInvisible);p.setParalyzed(oldParalyzed);p.setFalling();
            p.sendPacket(new CameraMode(0));p.broadcastPacket(new Ride(p));p.broadcastUserInfo();
            if(!p.isOnline()||p.getClient()==null)p.storeMe();
            if(p.isOnline())p.sendMessage("Prueba de vuelo terminada; montura retirada y origen restaurado.");
        }
    }
}
