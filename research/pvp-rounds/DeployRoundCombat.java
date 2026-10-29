import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import java.util.jar.JarFile;
public class DeployRoundCombat {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  Path s=Path.of(dir);inst.appendToSystemClassLoaderSearch(new JarFile(s.resolve("support.jar").toFile()));
  String[] names={"entity.actor.Player","entity.actor.Creature","entity.actor.status.PlayerStatus","entity.actor.status.SummonStatus","mechanics.skill.Skill"};
  List<ClassDefinition> defs=new ArrayList<>();
  for(String n:names){String full="org.l2jmobius.gameserver."+n;Class<?> c=Class.forName(full);defs.add(new ClassDefinition(c,Files.readAllBytes(s.resolve("compiled/"+full.replace('.','/')+".class"))));}
  inst.redefineClasses(defs.toArray(ClassDefinition[]::new));
  Files.writeString(s.resolve("combat-deployment.txt"),"PASS five combat classes redefined; rule registry empty until isolated test membership. Existing room and user untouched.\n");
 }
}
