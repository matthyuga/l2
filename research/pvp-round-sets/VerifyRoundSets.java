import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class VerifyRoundSets{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  Class<?> fixture=lookup.defineClass(Files.readAllBytes(Path.of(directory,"test-classes/custom/ElvenPvpRoom/RoundSetsFixture.class")));
  fixture.getMethod("verify",Path.class).invoke(null,Path.of(directory));
 }
}
