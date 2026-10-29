import java.lang.classfile.*;
import java.nio.file.*;
import java.util.*;
import java.util.jar.*;
public class GraftHsl {
 static final Map<String,Set<String>> TARGETS=Map.of(
  "org.l2jmobius.gameserver.network.clientpackets.CharacterCreate",Set.of("readImpl","runImpl"),
  "org.l2jmobius.gameserver.network.serverpackets.CharInfo",Set.of("writeImpl"),
  "org.l2jmobius.gameserver.network.serverpackets.UserInfo",Set.of("writeImpl"),
  "org.l2jmobius.gameserver.network.serverpackets.CharSelectionInfo",Set.of("writeImpl"));
 static byte[] graft(byte[] old,byte[] fresh,Set<String> names){
  var cf=ClassFile.of();var replacement=cf.parse(fresh);Map<String,MethodModel> methods=new HashMap<>();
  for(var m:replacement.methods())methods.put(m.methodName().stringValue()+m.methodType().stringValue(),m);
  return cf.transformClass(cf.parse(old),(builder,element)->{
   if(element instanceof MethodModel m&&names.contains(m.methodName().stringValue())){
    var found=methods.get(m.methodName().stringValue()+m.methodType().stringValue());if(found==null)throw new IllegalStateException("Missing replacement method");builder.with(found);
   }else builder.with(element);
  });
 }
 public static void main(String[] args)throws Exception{
  Path root=Path.of(args[0]);try(JarFile jar=new JarFile(args[1])){
   for(var t:TARGETS.entrySet()){
    String name=t.getKey().replace('.','/')+".class";byte[] old=jar.getInputStream(jar.getJarEntry(name)).readAllBytes();byte[] fresh=Files.readAllBytes(root.resolve("compiled").resolve(name));
    Path dest=root.resolve(args[2]).resolve(name);Files.createDirectories(dest.getParent());Files.write(dest,graft(old,fresh,t.getValue()));
   }
  }
 }
}
