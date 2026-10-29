import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;

/** Isolates the observer paralysis gate without changing privileges or packet handling. */
public class CameraMobilityProbe implements IVoicedCommandHandler {
    private static Path output;
    private static long generation;
    private static boolean running;
    private static boolean originalParalysis;
    public static void agentmain(String directory, Instrumentation unused) throws Exception {
        output = Path.of(directory,"mobility-probe.txt");
        Player p=World.getPlayer(268436061);
        Files.writeString(output,p==null ? "Camera offline\n" : describe(p));
        if (VoicedCommandHandler.getInstance().getHandler("cammovil") != null)
            throw new IllegalStateException("Mobility probe already installed");
        VoicedCommandHandler.getInstance().registerHandler(new CameraMobilityProbe());
    }
    private static boolean allowed(Player p) {
        return p!=null && p.getObjectId()==268436061 && "nexuscamera".equals(p.getAccountName())
            && "NexusCam".equals(p.getName()) && !p.isGM();
    }
    private static String describe(Player p) {
        return "observer="+p.inObserverMode()+" movementDisabled="+p.isMovementDisabled()
            +" paralyzed="+p.isParalyzed()+" teleporting="+p.isTeleporting()+" rooted="+p.isRooted()
            +" stunned="+p.isStunned()+" overloaded="+p.isOverloaded()+" invul="+p.isInvul()
            +" invisible="+p.isInvisible()+" flying="+p.isFlying()+" speed="+p.getMoveSpeed()
            +" xyz="+p.getX()+","+p.getY()+","+p.getZ()+"\n";
    }
    public String[] getCommandList() { return new String[]{"cammovil"}; }
    public synchronized boolean onCommand(String command, Player p, String params) {
        if (!allowed(p)) return false;
        if ("off".equalsIgnoreCase(params==null ? "" : params.trim())) { restore(p); return true; }
        if (!p.inObserverMode() || p.isTeleporting() || !p.isInvul() || !p.isInvisible() || p.isDead()) {
            p.sendMessage("Primero .camara on y espera a que termine el teleport."); return true;
        }
        if (running) { p.sendMessage("Prueba ya activa. .cammovil off la termina."); return true; }
        originalParalysis=p.isParalyzed(); running=true;
        long token=++generation;
        try {
            Files.writeString(output,"BEFORE "+describe(p),StandardOpenOption.APPEND);
            p.setParalyzed(false);
            Files.writeString(output,"AFTER "+describe(p),StandardOpenOption.APPEND);
            p.sendMessage("PRUEBA MOVIL 120s: flechas o click. Conservas observacion, invisibilidad e invulnerabilidad. .cammovil off termina.");
            ThreadPool.schedule(() -> { synchronized(CameraMobilityProbe.this) { if(running && generation==token) restore(p); } },120000);
        } catch(Exception e) { restore(p); p.sendMessage("Prueba cancelada por error de registro."); }
        return true;
    }
    private void restore(Player p) {
        if (!running) return;
        running=false; generation++;
        p.stopMove(null);
        // Return may already have left observer mode. Do not paralyze a normal character.
        if (p.inObserverMode()) p.setParalyzed(originalParalysis);
        try { Files.writeString(output,"RESTORED "+describe(p),StandardOpenOption.APPEND); } catch(Exception e) {}
        if(p.isOnline()) p.sendMessage("Prueba movil terminada; estado de observador restaurado.");
    }
}
