import java.lang.instrument.Instrumentation;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Properties;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/** Bounded native smoke probe, only the reserved offline camera character. */
public class ObserverProbe {
    private static int checks;
    private static void check(boolean value, String message) { if(!value) throw new IllegalStateException(message); checks++; }
    public static void agentmain(String directory, Instrumentation instrumentation) throws Exception {
        Path out=Path.of(directory,"native-verification.txt");
        Player p=null;
        try {
            Properties cfg=new Properties();try(var in=Files.newInputStream(Path.of("config/CameraObserver.properties"))){cfg.load(in);}
            String name=cfg.getProperty("Character"),account=cfg.getProperty("Account");
            int id;
            try(Connection con=DatabaseFactory.getConnection();PreparedStatement q=con.prepareStatement("SELECT charId,online,accesslevel,account_name FROM characters WHERE char_name=?")){
                q.setString(1,name);try(ResultSet rs=q.executeQuery()){
                    check(rs.next(),"reserved camera character missing");id=rs.getInt(1);
                    check(rs.getInt(2)==0,"camera already connected");
                    check(rs.getInt(3)==0&&account.equals(rs.getString(4)),"camera identity/privileges mismatch");
                }
            }
            check(World.getPlayer(id)==null,"reserved character already in world");
            IVoicedCommandHandler handler=VoicedCommandHandler.getInstance().getHandler("camara");
            check(handler!=null,"camera handler not registered");
            check(!handler.onCommand("camara",null,"giran"),"null caller authorized");
            p=Player.load(id);check(p!=null,"cannot reload camera");
            check(!p.isGM()&&account.equals(p.getAccountName()),"loaded camera identity");
            p.setOnlineStatus(true,false);
            handler.onCommand("camara",p,"giran");p.onTeleported();
            check(p.inObserverMode(),"native observer flag");
            check(p.isInvul()&&p.isInvisible()&&p.isParalyzed(),"native protections");
            int originX=p.getLastLocation().getX(),originY=p.getLastLocation().getY();
            handler.onCommand("camara",p,"ir 82738 148638 -3473");p.onTeleported();
            check(p.inObserverMode()&&p.getX()==82738,"change observation point");
            check(p.getLastLocation().getX()==originX&&p.getLastLocation().getY()==originY,"return anchor overwritten");
            handler.onCommand("camara",p,"ir 2147483647 0 0");
            check(p.getX()==82738,"out-of-range coordinate moved camera");
            handler.onCommand("camara",p,"salir");p.onTeleported();
            check(!p.inObserverMode()&&!p.isInvisible()&&!p.isParalyzed(),"native exit cleanup");
            check(p.getX()==originX&&p.getY()==originY,"native return position");
            check(!p.isGM(),"GM privilege unexpectedly granted");
            Files.writeString(out,"PASS checks="+checks+"; reserved offline character only; native enter/reposition/exit, protections, rejection, identity. No graphical client observed.\n");
        } catch(Throwable error) {
            Files.writeString(out,"FAIL checks="+checks+" "+error+"\n");
            throw new RuntimeException(error);
        } finally {
            if(p!=null){if(p.inObserverMode()){p.leaveObserverMode();p.onTeleported();}p.storeMe();p.deleteMe();p.setOnlineStatus(false,true);}
        }
    }
}
