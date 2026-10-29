import java.lang.instrument.Instrumentation;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.ClassDefinition;
import java.security.ProtectionDomain;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public final class DeactivateStickers {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Close player clients before rollback");
  var voices=VoicedCommandHandler.getInstance();var handler=voices.getHandler("sticker");
  Path oldGate=Path.of(directory).getParent().resolve("stickers-native-bypass-v4/runtime-before.class");
  if(Files.exists(oldGate)){
   try{Class.forName("EnableNativeStickerActionsV4").getMethod("disableStartupPatch",Instrumentation.class).invoke(null,ignored);}catch(ClassNotFoundException absent){}
   Class<?> gate=Class.forName("org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView");byte[][] bytes={null};
   ClassFileTransformer capture=new ClassFileTransformer(){@Override public byte[] transform(Module module,ClassLoader loader,String name,Class<?> type,ProtectionDomain domain,byte[] data){if(type==gate)bytes[0]=data.clone();return null;}};
   ignored.addTransformer(capture,true);try{ignored.retransformClasses(gate);}finally{ignored.removeTransformer(capture);}
   if(bytes[0]==null)throw new IllegalStateException("Native gate rollback capture failed");
   byte[] restored=GraftStickerNativeAction.graft(bytes[0],Files.readAllBytes(oldGate));ignored.redefineClasses(new ClassDefinition(gate,restored));
  }
  if(handler!=null){
   if(!handler.getClass().getName().equals("custom.StickerEmotes.StickerEmotes") && !handler.getClass().getName().equals("custom.StickerEmotes.MaggieStickerEmotes"))throw new IllegalStateException("Different sticker handler");
   voices.removeHandler(handler);
  }
  Files.writeString(Path.of(directory,"live-deactivated.txt"),"PASS: sticker handler removed; no player or core state changed.\n");
 }
}
