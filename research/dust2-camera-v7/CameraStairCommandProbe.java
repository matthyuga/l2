import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class CameraStairCommandProbe {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  Path d=Path.of(dir);StringBuilder out=new StringBuilder();Player p=null;
  try{
   Class<?> handler=Arrays.stream(inst.getAllLoadedClasses()).filter(c->c.getName().equals("custom.Dust2Arena.Dust2Arena")).findFirst().orElseThrow();
   inst.redefineClasses(new ClassDefinition(handler,Files.readAllBytes(d.resolve("compiled/custom/Dust2Arena/Dust2Arena.class"))));
   var g=GeoEngine.getInstance();if(!g.reloadRegion(24,19))throw new IllegalStateException("Geo reload failed");
   int checks=0;
   for(int x=139240;x<139440;x+=16)for(int y=56552;y>=56448;y-=8){
    int z=g.getHeight(x,y,8060),nz=g.getHeight(x,y-8,8060);
    if(!g.canMoveToTarget(x,y,z,x,y-8,nz,0))throw new AssertionError("Up blocked "+x+","+y+","+z+" -> "+nz);
    if(!g.canMoveToTarget(x,y-8,nz,x,y,z,0))throw new AssertionError("Down blocked "+x+","+y);
    checks+=2;
   }
   out.append("ramp_movement_checks="+checks+" PASS\n");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"ramp-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("RampProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var command=VoicedCommandHandler.getInstance().getHandler("dust2");command.onCommand("dust2",p,"escalera2");p.onTeleported();
   if(p.getX()!=141320 || p.getY()!=55440 || Math.abs(p.getZ()-8040)>30)throw new AssertionError("Ramp arrival failed");
   out.append("dust2_escalera2="+p.getX()+","+p.getY()+","+p.getZ()+" PASS\n");
   command.onCommand("dust2",p,"salir");p.onTeleported();
   if(p.getX()!=83020 || p.getY()!=147880)throw new AssertionError("Return failed");out.append("return PASS\nSUCCESS\n");
  }catch(Throwable e){out.append("FAIL "+e+"\n");throw e;}
  finally{if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(d.resolve("server-probe.txt"),out);}
 }
}
