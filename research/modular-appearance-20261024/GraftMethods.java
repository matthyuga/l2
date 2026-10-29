import java.lang.classfile.*;
import java.lang.classfile.attribute.CodeAttribute;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
/** Retain runtime bytecode for every method outside the exact requested edits. */
public class GraftMethods {
 public static void main(String[] args)throws Exception {
  Path root=Path.of(args[0]);Map<String,Set<String>> targets=new LinkedHashMap<>();
  targets.put("org/l2jmobius/gameserver/entity/actor/Player",Set.of("create","getCollisionRadius","getCollisionHeight"));
  targets.put("org/l2jmobius/gameserver/entity/actor/stat/PlayerStat",Set.of("getSTR","getDEX","getCON","getINT","getWIT","getMEN"));
  for(String n:List.of("CharInfo","UserInfo","CharSelectionInfo"))targets.put("org/l2jmobius/gameserver/network/serverpackets/"+n,Set.of("writeImpl"));
  var cf=ClassFile.of();int replaced=0,preserved=0;
  try(var jar=new ZipFile(root.resolve("../../server/libs/GameServer.jar").normalize().toFile())){
   for(var entry:targets.entrySet()){
    String name=entry.getKey()+".class";var original=cf.parse(jar.getInputStream(jar.getEntry(name)).readAllBytes());var replacement=cf.parse(root.resolve("compiled").resolve(name));
    var fresh=new HashMap<String,MethodModel>();for(var m:replacement.methods())fresh.put(m.methodName().stringValue()+m.methodType().stringValue(),m);
    byte[] bytes=cf.transformClass(original,(builder,element)->{
     if(element instanceof MethodModel method&&entry.getValue().contains(method.methodName().stringValue()))builder.with(fresh.get(method.methodName().stringValue()+method.methodType().stringValue()));
     else builder.with(element);
    });
    var after=cf.parse(bytes);
    if(!cf.verify(bytes).isEmpty())throw new IllegalStateException(cf.verify(bytes).toString());
    for(int i=0;i<original.methods().size();i++){
     var before=original.methods().get(i);var now=after.methods().get(i);
     if(!before.methodName().equalsString(now.methodName().stringValue())||!before.methodType().equalsString(now.methodType().stringValue())||before.flags().flagsMask()!=now.flags().flagsMask())throw new IllegalStateException("Changed method schema");
     if(entry.getValue().contains(before.methodName().stringValue()))replaced++;
     else if(before.code().isPresent()){
      if(!Arrays.equals(((CodeAttribute)before.code().get()).codeArray(),((CodeAttribute)now.code().get()).codeArray()))throw new IllegalStateException("Unrelated method changed: "+before.methodName());
      preserved++;
     }
    }
    Path output=root.resolve("patched-core").resolve(name);Files.createDirectories(output.getParent());Files.write(output,bytes);
   }
  }
  Files.writeString(root.resolve("graft-proof.txt"),"PASS: "+replaced+" targeted method bodies; "+preserved+" unrelated method bodies preserved byte for byte; class-file verification passed.\n");
  System.out.println(Files.readString(root.resolve("graft-proof.txt")));
 }
}
