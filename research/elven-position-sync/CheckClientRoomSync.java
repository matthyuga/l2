import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.network.clientpackets.*;
public class CheckClientRoomSync {
 static void require(boolean b,String s){if(!b)throw new IllegalStateException(s);}
 static void value(Object o,String name,int v)throws Exception {Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);f.setInt(o,v);}
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  StringBuilder b=new StringBuilder();
  try {
   var p=World.getPlayer(268473899);require(p!=null && p.getName().equals("Hellkevin") && p.getClient()!=null,"Connected player missing");
   int oldX=p.getX(),oldY=p.getY(),oldZ=p.getZ();
   VoicedCommandHandler.getInstance().getHandler("salas").onCommand("salas",p,"entrar");
   int room=p.getInstanceId();require(room>0 && p.getPvpFlag()==1,"Room entry failed");
   int x=p.getX(),y=p.getY(),z=p.getZ();
   ValidatePosition stale=new ValidatePosition();stale.init(p.getClient(),null);
   value(stale,"_x",oldX);value(stale,"_y",oldY);value(stale,"_z",oldZ);stale.run();
   require(p.getX()==x && p.getY()==y && p.getInstanceId()==room,"Stale ValidatePosition changed arena position");
   MoveToLocation move=new MoveToLocation();move.init(p.getClient(),null);
   value(move,"_originX",oldX);value(move,"_originY",oldY);value(move,"_originZ",oldZ);
   value(move,"_targetX",oldX+30);value(move,"_targetY",oldY);value(move,"_targetZ",oldZ);value(move,"_movementMode",0);move.run();
   require(p.getX()==x && p.getY()==y && p.getInstanceId()==room,"Stale MoveToLocation changed arena position");
   ValidatePosition current=new ValidatePosition();current.init(p.getClient(),null);value(current,"_x",x);value(current,"_y",y);value(current,"_z",z);current.run();
   require(p.getClientX()==x && p.getClientY()==y,"Current ValidatePosition was not accepted");
   b.append("PASS stale position/movement packets rejected; current position accepted.\n");
   for(int i=0;i<20;i++){
    b.append(i*500).append("ms instance=").append(p.getInstanceId()).append(" flag=").append(p.getPvpFlag()).append(" xyz=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append('\n');
    require(p.getInstanceId()==room && p.getPvpFlag()==1,"Client left room or lost flag during synchronization observation");
    Thread.sleep(500);
   }
   b.append("PASS real connected client retained arena and flag beyond six-second synchronization window.\n");
  }catch(Throwable t){b.append("FAIL ").append(t).append('\n');throw t;}
  finally{Files.writeString(Path.of(dir,"client-verification.txt"),b);}
 }
}
