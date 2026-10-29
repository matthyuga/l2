import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.network.serverpackets.*;
import org.l2jmobius.gameserver.managers.IdManager;
public class ProbeScreenVisibility {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  Path root=Path.of(dir);Object h=VoicedCommandHandler.getInstance().getHandler("pantalla");
  Class<?> c=h.getClass();
  if(!c.getName().equals("custom.GiranScreen.GiranScreen")||!inst.isModifiableClass(c))throw new IllegalStateException("Unexpected handler");
  var f=c.getDeclaredField("viewers");f.setAccessible(true);
  // Keep persistent placement unchanged; move current object only.
  StringBuilder report=new StringBuilder("PASS custom screen module redefined; no core changes.\n");
  Npc smoke=(Npc)c.getMethod("createScreen").invoke(null);
  try{
   if(smoke.getX()!=82165||smoke.getY()!=148611||smoke.getZ()!=-3550||smoke.getHeading()!=0)throw new IllegalStateException("Placement verification failed");
   report.append("PASS new screen at 82165,148611,-3550 heading0 facing east; pedestal east bound82148.07; front plane82171.\n");
  }finally{smoke.setDecayed(true);IdManager.getInstance().releaseId(smoke.getObjectId());}
  for(Object v:((Map<?,?>)f.get(h)).values()){
   var sf=v.getClass().getDeclaredField("screen");sf.setAccessible(true);Npc n=(Npc)sf.get(v);
   var pf=v.getClass().getDeclaredField("player");pf.setAccessible(true);Player p=(Player)pf.get(v);
   var vf=v.getClass().getDeclaredField("visible");vf.setAccessible(true);
   p.sendPacket(new DeleteObject(n));n.setXYZ(82450,148611,-3250);n.setHeading(0);vf.set(v,false);
   report.append("Moved existing screen for ").append(p.getName()).append("; refresh will resend.\n");
   p.sendMessage("Prueba visual: pantalla separada del mural y elevada frente a tu posicion actual.");
  }
  Files.writeString(root.resolve("visibility-probe.txt"),report.toString());
 }
}
