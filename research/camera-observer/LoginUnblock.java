import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.loginserver.controller.LoginController;
public class LoginUnblock {
    public static void agentmain(String output, Instrumentation ignored) throws Exception {
        LoginController controller = LoginController.getInstance();
        Long expiry = controller.getBannedIps().get("127.0.0.1");
        // Clear only the temporary loopback lockout. Preserve permanent bans.
        boolean removed = expiry != null && expiry != Long.MAX_VALUE && controller.removeBanForAddress("127.0.0.1");
        Files.writeString(Path.of(output), "loopback_temporary_ban_present=" + (expiry != null && expiry != Long.MAX_VALUE) + "\nremoved=" + removed + "\npermanent_bans_preserved=true\n");
    }
}
