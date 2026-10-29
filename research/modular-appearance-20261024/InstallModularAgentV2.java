import java.lang.classfile.*;
import java.lang.instrument.*;
import java.lang.invoke.MethodHandles;
import java.nio.file.*;
import java.security.ProtectionDomain;
import java.util.*;
import java.util.jar.JarFile;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

public class InstallModularAgentV2 {
 private static JarFile helper;
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Path root=Path.of(directory);for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Player client connected; reload refused");
  var voices=VoicedCommandHandler.getInstance();if(voices.getHandler("cuerpo")!=null)throw new IllegalStateException(".cuerpo already registered");
  var raceHandler=voices.getHandler("raza");if(raceHandler==null)throw new IllegalStateException(".raza missing");Class<?> race=raceHandler.getClass();
  Map<Class<?>,Set<String>> targets=new LinkedHashMap<>();
  targets.put(Class.forName("org.l2jmobius.gameserver.entity.actor.Player"),Set.of("create","getCollisionRadius","getCollisionHeight"));
  targets.put(Class.forName("org.l2jmobius.gameserver.entity.actor.stat.PlayerStat"),Set.of("getSTR","getDEX","getCON","getINT","getWIT","getMEN"));
  for(String n:List.of("CharInfo","UserInfo","CharSelectionInfo"))targets.put(Class.forName("org.l2jmobius.gameserver.network.serverpackets."+n),Set.of("writeImpl"));
  targets.put(race,Set.of("readStats","comparisonHtml","applyConfiguration"));
  Map<Class<?>,byte[]> before=new HashMap<>();
  ClassFileTransformer capture=new ClassFileTransformer(){@Override public byte[] transform(Module module,ClassLoader loader,String name,Class<?> type,ProtectionDomain domain,byte[] bytes){if(targets.containsKey(type))before.put(type,bytes.clone());return null;}};
  inst.addTransformer(capture,true);try{inst.retransformClasses(targets.keySet().toArray(Class<?>[]::new));}finally{inst.removeTransformer(capture);}
  if(before.size()!=targets.size())throw new IllegalStateException("Could not capture rollback classes");
  for(var entry:before.entrySet()){Path file=root.resolve("rollback-classes").resolve(entry.getKey().getName().replace('.','/')+".class");Files.createDirectories(file.getParent());Files.write(file,entry.getValue());}
  helper=new JarFile(root.resolve("modular-helper.jar").toFile());inst.appendToSystemClassLoaderSearch(helper);
  var cf=ClassFile.of();List<ClassDefinition> changes=new ArrayList<>(),rollback=new ArrayList<>();
  for(var entry:targets.entrySet()){
   Class<?> type=entry.getKey();String name=type.getName().replace('.','/')+".class";
   Path file=root.resolve(type==race?"compiled-scripts":"compiled").resolve(name);var fresh=cf.parse(file);Map<String,MethodModel> methods=new HashMap<>();
   for(var m:fresh.methods())methods.put(m.methodName().stringValue()+m.methodType().stringValue(),m);
   byte[] bytes=cf.transformClass(cf.parse(before.get(type)),(builder,element)->{if(element instanceof MethodModel m&&entry.getValue().contains(m.methodName().stringValue()))builder.with(methods.get(m.methodName().stringValue()+m.methodType().stringValue()));else builder.with(element);});
   changes.add(new ClassDefinition(type,bytes));rollback.add(new ClassDefinition(type,before.get(type)));
  }
  inst.redefineClasses(changes.toArray(ClassDefinition[]::new));
  try{
   VerifyModular.run(root);
   org.l2jmobius.gameserver.scripting.ScriptEngine.getInstance().executeScript(root.resolve("../../server/game/data/scripts/custom/RaceCustomization/ModularBodyMenu.java").normalize());
   if(voices.getHandler("cuerpo")==null)throw new IllegalStateException(".cuerpo did not register");
   Files.writeString(root.resolve("live-install-proof.txt"),"PASS: six classes atomically redefined with only selected method bodies replaced; reserved-probe engine checks passed; .cuerpo registered with existing .raza authorization; no user characters modified.\n");
  }catch(Throwable e){var registered=voices.getHandler("cuerpo");if(registered!=null)voices.removeHandler(registered);inst.redefineClasses(rollback.toArray(ClassDefinition[]::new));Files.writeString(root.resolve("live-install-error.txt"),e.toString());throw new IllegalStateException("Modular install failed; live core restored",e);}
 }
}
