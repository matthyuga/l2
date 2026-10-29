import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.*;
public class GalleryProbeV2 {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  List<String> report=new ArrayList<>();
  Class<?> gallery=Arrays.stream(inst.getAllLoadedClasses()).filter(c->c.getName().equals("custom.EquipmentShowcase.EquipmentShowcase")).findFirst().orElseThrow();
  Class<?> roster=Arrays.stream(inst.getAllLoadedClasses()).filter(c->c.getName().equals("custom.NormalNpcRoster.NormalNpcRoster")).findFirst().orElseThrow();
  inst.redefineClasses(new java.lang.instrument.ClassDefinition(gallery,Files.readAllBytes(Path.of(dir,"classes/custom/EquipmentShowcase/EquipmentShowcase.class"))));
  try{
   if(!gallery.getMethod("count").invoke(null).equals(0))throw new AssertionError("gallery not hidden");report.add("PASS startup gallery hidden: 0");
   if((boolean)roster.getMethod("isReady").invoke(null))throw new AssertionError("roster prepared automatically");report.add("PASS combat roster deferred");
   if(AdminCommandHandler.getInstance().getHandler("admin_galeria")==null || VoicedCommandHandler.getInstance().getHandler("galeria")==null || VoicedCommandHandler.getInstance().getHandler("roster")==null)throw new AssertionError("missing command");report.add("PASS gallery native/voiced and roster commands registered");
   for(int i=0;i<2;i++){
    Object count=gallery.getMethod("show",boolean.class).invoke(null,false);
    if(!count.equals(51))throw new AssertionError("set count "+count);report.add("PASS show exactly 51 armor mannequins, cycle "+i);
    if(World.getVisibleObjects().stream().filter(o->o instanceof org.l2jmobius.gameserver.entity.actor.Npc n && n.getId()>=62051 && n.getId()<=62156).count()!=0)throw new AssertionError("weapons visible");
    gallery.getMethod("hide").invoke(null);
    if(!gallery.getMethod("count").invoke(null).equals(0))throw new AssertionError("hide failed");report.add("PASS hide all gallery mannequins, cycle "+i);
   }
   report.add("SUCCESS");
  }catch(Throwable e){report.add("FAIL "+e);throw e;}
  finally{gallery.getMethod("hide").invoke(null);Files.write(Path.of(dir,"verification.txt"),report);}
 }
}
