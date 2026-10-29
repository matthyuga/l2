import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class LoadTacticsForTrial{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
   for(String prefix:List.of("RoomTacticalPolicy","PvpTacticalSelection","PvpLegacyBrain","PvpTacticalEngine")){
    List<Path> files;try(var stream=Files.list(folder)){files=stream.filter(p->p.getFileName().toString().startsWith(prefix)&&p.toString().endsWith(".class")).sorted().toList();}
    for(Path p:files)lookup.defineClass(Files.readAllBytes(p));
   }
   // The only temporary redefinition is exact-profile selection; default selection unchanged.
   Class<?> roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");inst.redefineClasses(new ClassDefinition(roster,Files.readAllBytes(folder.resolve("PvpSiegeRoster.class"))));
   Class<?> siege=loader.loadClass("custom.GiranSiegeLab.SiegeSquadBrain");MethodHandles.privateLookupIn(siege,MethodHandles.lookup()).defineClass(Files.readAllBytes(dir.resolve("test-classes/custom/GiranSiegeLab/RoomSiegeReference.class")));
   Class<?> benchmark=lookup.defineClass(Files.readAllBytes(dir.resolve("test-classes/custom/ElvenPvpRoom/TacticalBenchmark.class")));
   lookup.defineClass(Files.readAllBytes(dir.resolve("test-classes/custom/ElvenPvpRoom/TacticalBenchmark$Stats.class")));
   Files.writeString(dir.resolve("trial-load.txt"),"PASS helpers defined; production tactical engine disabled; only optional exact roster selector redefined.\n");
  }
 }
}
