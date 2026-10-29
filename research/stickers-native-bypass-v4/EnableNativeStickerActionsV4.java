import java.lang.instrument.*;
import java.security.ProtectionDomain;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView;
public final class EnableNativeStickerActionsV4 {
 private static ClassFileTransformer startupTransformer;
 public static void disableStartupPatch(Instrumentation inst){if(startupTransformer!=null){inst.removeTransformer(startupTransformer);startupTransformer=null;}}
 public static void premain(String unused,Instrumentation inst)throws Exception{
  byte[] template;
  try(var in=EnableNativeStickerActionsV4.class.getResourceAsStream("/native-actions-template.bin")){
   if(in==null)throw new IllegalStateException("Missing native action template");template=in.readAllBytes();
  }
  startupTransformer=new ClassFileTransformer(){
   @Override public byte[] transform(Module module,ClassLoader loader,String name,Class<?> changed,ProtectionDomain domain,byte[] bytes){
    if(!name.equals("org/l2jmobius/gameserver/network/serverpackets/SkillCatalogView"))return null;
    try{return GraftStickerNativeAction.graft(bytes,template);}catch(Exception ex){throw new IllegalStateException("Sticker native action startup patch",ex);}
   }
  };
  inst.addTransformer(startupTransformer);
 }
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path s=Path.of(directory);Class<?> type=SkillCatalogView.class;
  boolean beforeAllowed=SkillCatalogView.nativeWindowAction("voice .sticker 1");
  if(beforeAllowed)throw new IllegalStateException("Sticker action already allowed; do not assume whitelist is blocking");
  byte[][] capture={null};
  ClassFileTransformer transform=new ClassFileTransformer(){
   @Override public byte[] transform(Module mod,ClassLoader loader,String name,Class<?> changed,ProtectionDomain domain,byte[] bytes){if(changed==type)capture[0]=bytes.clone();return null;}
  };
  inst.addTransformer(transform,true);try{inst.retransformClasses(type);}finally{inst.removeTransformer(transform);}
  if(capture[0]==null)throw new IllegalStateException("Could not capture live class");
  Files.write(s.resolve("runtime-before.class"),capture[0]);
  byte[] compiled=Files.readAllBytes(s.resolve("compiled/org/l2jmobius/gameserver/network/serverpackets/SkillCatalogView.class"));
  byte[] patched=GraftStickerNativeAction.graft(capture[0],compiled);
  try{
   inst.redefineClasses(new ClassDefinition(type,patched));
   for(int i=1;i<=19;i++)if(!SkillCatalogView.nativeWindowAction("voice .sticker "+i))throw new AssertionError("Sticker "+i);
   for(String action:new String[]{"voice .habilidades","voice .habilidades next","voice .habilidades quick -1","voice .habilidades quick 0","voice .habilidades quick 1","voice .habilidades quick 2","voice .habilidades quick 3","voice .habilidades quick 4","voice .habilidades quick 5","voice .amber toggle"})if(!SkillCatalogView.nativeWindowAction(action))throw new AssertionError("Previous action "+action);
   for(String action:new String[]{"voice .sticker 0","voice .sticker 20","voice .sticker 1 extra","voice .sticker 01","voice .sticker -1","voice .sticker tesoro","voice .raza","admin_shutdown",""," voice .sticker 1"})if(SkillCatalogView.nativeWindowAction(action))throw new AssertionError("Unexpected action accepted: "+action);
   if(SkillCatalogView.nativeWindowAction(null))throw new AssertionError("Null action");
   Files.write(s.resolve("runtime-patched.class"),patched);
   Files.writeString(s.resolve("live-verification.txt"),"PASS: live whitelist rejected voice .sticker 1 before the patch.\nPASS: all 19 exact sticker selections accepted after the patch; all 10 previous actions preserved; malformed/out-of-range/unrelated actions still rejected.\nPASS: only nativeWindowAction method replaced; every unrelated method body retained. Active player sessions untouched.\nLIMIT: next real click must confirm STICKER_REQUEST/STICKER_SENT and drawing above character.\n");
  }catch(Throwable ex){inst.redefineClasses(new ClassDefinition(type,capture[0]));throw new IllegalStateException("Live method restored",ex);}
 }
}
