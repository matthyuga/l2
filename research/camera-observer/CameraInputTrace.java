import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.config.DevelopmentConfig;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;

/** Temporary names-only diagnostic. No packet payloads, credentials, or movement changes. */
public class CameraInputTrace implements IVoicedCommandHandler {
    private static final AtomicBoolean active = new AtomicBoolean();
    private static Path output;
    public static void agentmain(String directory, Instrumentation unused) throws Exception {
        output = Path.of(directory, "online-input-trace.txt");
        if (VoicedCommandHandler.getInstance().getHandler("camdiag") != null)
            throw new IllegalStateException("Diagnostic command already registered");
        VoicedCommandHandler.getInstance().registerHandler(new CameraInputTrace());
        Files.writeString(output, "READY: .camdiag; no trace active until reserved user starts it.\n");
    }
    public String[] getCommandList() { return new String[]{"camdiag"}; }
    public boolean onCommand(String command, Player player, String params) {
        if (player == null || player.getObjectId() != 268436061 || player.isGM()
            || !"nexuscamera".equals(player.getAccountName()) || !"NexusCam".equals(player.getName())) return false;
        // PacketLogger has no per-client field. Only trace while this is the sole real client.
        long clients = World.getPlayers().stream().filter(p -> p.isOnline() && p.getClient() != null).count();
        if (clients != 1) { player.sendMessage("Diagnostico requiere solo el cliente NexusCam conectado."); return true; }
        if (!active.compareAndSet(false,true)) { player.sendMessage("Diagnostico ya activo."); return true; }
        Logger logger = Logger.getLogger("org.l2jmobius.gameserver.network.PacketLogger");
        boolean oldDebug = DevelopmentConfig.DEBUG_CLIENT_PACKETS;
        Set<String> oldExcluded = DevelopmentConfig.EXCLUDED_DEBUG_PACKETS;
        Handler capture = new Handler() {
            public synchronized void publish(LogRecord record) {
                String msg = record.getMessage();
                if (msg != null && msg.matches("\\[C\\] (MoveToLocation|MoveWithDelta|CannotMoveAnymore|ValidatePosition|ObserverReturn|Say2)")) {
                    try { Files.writeString(output, System.currentTimeMillis()+" "+msg+"\n",StandardOpenOption.APPEND); }
                    catch (Exception e) { /* No effect on packet execution. */ }
                }
            }
            public void flush() {}
            public void close() {}
        };
        try {
            Files.writeString(output,"START: reserved camera was sole online client; packet names only; observer="+player.inObserverMode()+"\n");
            logger.addHandler(capture);
            Set<String> excluded = new HashSet<>(oldExcluded);
            excluded.removeAll(Set.of("MoveToLocation","MoveWithDelta","CannotMoveAnymore","ValidatePosition","ObserverReturn","Say2"));
            DevelopmentConfig.EXCLUDED_DEBUG_PACKETS = excluded;
            DevelopmentConfig.DEBUG_CLIENT_PACKETS = true;
            ThreadPool.schedule(() -> {
                DevelopmentConfig.DEBUG_CLIENT_PACKETS = oldDebug;
                DevelopmentConfig.EXCLUDED_DEBUG_PACKETS = oldExcluded;
                logger.removeHandler(capture);
                active.set(false);
                try { Files.writeString(output,"STOP: previous logging settings restored.\n",StandardOpenOption.APPEND); } catch(Exception e) {}
                if (player.isOnline()) player.sendMessage("Diagnostico terminado; registro guardado.");
            }, 90000);
            player.sendMessage("DIAGNOSTICO ACTIVO 90 segundos. .camara on; proba flechas, W/S y click en suelo. Registro solo de nombres de paquetes.");
        } catch(Exception e) {
            DevelopmentConfig.DEBUG_CLIENT_PACKETS = oldDebug;
            DevelopmentConfig.EXCLUDED_DEBUG_PACKETS = oldExcluded;
            logger.removeHandler(capture); active.set(false);
            player.sendMessage("No se pudo activar diagnostico.");
        }
        return true;
    }
}
