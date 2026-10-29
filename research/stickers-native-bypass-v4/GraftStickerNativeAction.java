import java.lang.classfile.*;
import java.nio.file.*;
import java.util.*;
public final class GraftStickerNativeAction {
 public static byte[] graft(byte[] before,byte[] compiled)throws Exception{
  var cf=ClassFile.of();var model=cf.parse(before);var fresh=cf.parse(compiled);
  if(model.methods().stream().noneMatch(m->m.methodName().equalsString("nativeWindowAction")&&m.methodType().equalsString("(Ljava/lang/String;)Z")))throw new IllegalStateException("Expected nativeWindowAction method");
  var replacement=fresh.methods().stream().filter(m->m.methodName().equalsString("nativeWindowAction")&&m.methodType().equalsString("(Ljava/lang/String;)Z")).findFirst().orElseThrow();
  byte[] after=cf.transformClass(model,(builder,element)->{
   if(element instanceof MethodModel m&&m.methodName().equalsString("nativeWindowAction")&&m.methodType().equalsString("(Ljava/lang/String;)Z"))builder.with(replacement);
   else builder.with(element);
  });
  Map<String,MethodModel> next=new HashMap<>();for(var m:cf.parse(after).methods())next.put(m.methodName().stringValue()+m.methodType().stringValue(),m);
  for(var m:model.methods())if(!m.methodName().equalsString("nativeWindowAction")){
   var n=next.get(m.methodName().stringValue()+m.methodType().stringValue());
   if(n==null||m.code().isPresent()!=n.code().isPresent()||m.code().isPresent()&&!Arrays.equals(((java.lang.classfile.attribute.CodeAttribute)m.code().get()).codeArray(),((java.lang.classfile.attribute.CodeAttribute)n.code().get()).codeArray()))throw new AssertionError("Unrelated method changed: "+m.methodName());
  }
  return after;
 }
 public static void main(String[] args)throws Exception{Files.write(Path.of(args[2]),graft(Files.readAllBytes(Path.of(args[0])),Files.readAllBytes(Path.of(args[1]))));}
}
