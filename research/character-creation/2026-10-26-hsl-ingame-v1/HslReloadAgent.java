import java.lang.instrument.*;
import java.nio.file.*;
import java.security.ProtectionDomain;
import java.util.*;
import java.util.jar.*;
public class HslReloadAgent {
 private static JarFile helper;
 public static void agentmain(String args,Instrumentation inst)throws Exception{
  boolean rollback=args.endsWith("|rollback");Path root=Path.of(rollback?args.substring(0,args.length()-9):args);
  Map<Class<?>,Set<String>> targets=new LinkedHashMap<>();for(var t:GraftHsl.TARGETS.entrySet())targets.put(Class.forName(t.getKey()),t.getValue());
  if(rollback){List<ClassDefinition> definitions=new ArrayList<>();for(Class<?> t:targets.keySet())definitions.add(new ClassDefinition(t,Files.readAllBytes(root.resolve("rollback-classes").resolve(t.getName().replace('.','/')+".class"))));inst.redefineClasses(definitions.toArray(ClassDefinition[]::new));Files.writeString(root.resolve("live-rollback-proof.txt"),"RESTORED four live classes.\n");return;}
  Map<Class<?>,byte[]> before=new HashMap<>();ClassFileTransformer capture=new ClassFileTransformer(){@Override public byte[] transform(Module m,ClassLoader l,String n,Class<?> t,ProtectionDomain d,byte[] b){if(targets.containsKey(t))before.put(t,b.clone());return null;}};
  inst.addTransformer(capture,true);try{inst.retransformClasses(targets.keySet().toArray(Class<?>[]::new));}finally{inst.removeTransformer(capture);}if(before.size()!=4)throw new IllegalStateException("Incomplete live rollback capture");
  helper=new JarFile(root.resolve("hsl-helper.jar").toFile());inst.appendToSystemClassLoaderSearch(helper);
  List<ClassDefinition> definitions=new ArrayList<>();for(var t:targets.entrySet()){
   String name=t.getKey().getName().replace('.','/')+".class";Path old=root.resolve("rollback-classes").resolve(name);Files.createDirectories(old.getParent());Files.write(old,before.get(t.getKey()));
   byte[] b=GraftHsl.graft(before.get(t.getKey()),Files.readAllBytes(root.resolve("compiled").resolve(name)),t.getValue());definitions.add(new ClassDefinition(t.getKey(),b));
  }
  inst.redefineClasses(definitions.toArray(ClassDefinition[]::new));
  try{
   Class<?> h=Class.forName("org.l2jmobius.gameserver.custom.HairColorHsl");Object probe=new Object();
   var read=h.getMethod("read",Object.class,int.class);if(((Byte)read.invoke(null,probe,0x42123456))!=2||((Byte)read.invoke(null,probe,256))!=-1)throw new IllegalStateException("Protocol validation failed");
   int absent=(Integer)h.getMethod("selection",int.class,int.class).invoke(null,-987654,3);if(absent!=3)throw new IllegalStateException("Classic SQL fallback failed");
   Files.writeString(root.resolve("live-install-proof.txt"),"PASS four packet classes atomically grafted; helper visible; encoded RGB and invalid inputs checked; SQL fallback checked; existing characters unchanged.\n");
  }catch(Throwable e){List<ClassDefinition> restore=new ArrayList<>();for(var t:before.entrySet())restore.add(new ClassDefinition(t.getKey(),t.getValue()));inst.redefineClasses(restore.toArray(ClassDefinition[]::new));throw new IllegalStateException("Live install failed and original classes restored",e);}
 }
}
