import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.IdManager;
import org.l2jmobius.gameserver.scripting.ScriptEngine;
import org.l2jmobius.gameserver.network.serverpackets.AbstractNpcInfo;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.commons.network.pool.ResourcePool;
public class InstallGiranScreen {
 public static void agentmain(String directory,Instrumentation unused)throws Exception{
  Path root=Path.of(directory);String report="";
  NpcData.getInstance().parseFile(Path.of("data/stats/npcs/custom/giran_screen.xml").toFile());
  var template=NpcData.getInstance().getTemplate(59890);
  if(template==null||template.getDisplayId()!=59890)throw new IllegalStateException("Template failed");
  ScriptEngine.getInstance().executeScript(Path.of("E:/l2-local/server/game/data/scripts/custom/GiranScreen/GiranScreen.java"));
  var handler=VoicedCommandHandler.getInstance().getHandler("pantalla");
  if(handler==null||handler.onCommand("pantalla",null,"on"))throw new IllegalStateException("Handler test failed");
  report+="PASS screen template, script engine registration, null caller denied.\n";
  var create=handler.getClass().getMethod("createScreen");var screen=(org.l2jmobius.gameserver.entity.actor.Npc)create.invoke(null);
  try{
   if(screen.isDecayed()||World.findObject(screen.getObjectId())!=null)throw new IllegalStateException("Screen world isolation failed");
   report+="PASS screen is drawable but absent from global World registry.\n";
   Player camera=World.getPlayer(268436061);boolean loaded=camera==null;
   if(loaded)camera=Player.load(268436061);
   try{
    var packet=new AbstractNpcInfo.NpcInfo(screen,camera);
    var buffer=new WriteBuffer(new ResourcePool(),InstallGiranScreen.class);
    packet.writeImpl(null,buffer);
    if(buffer.position()<100||buffer.readInt(5)!=1059890)throw new IllegalStateException("NPC packet display ID mismatch");
    report+="PASS native NPC_INFO serialization; display ID1059890; bytes="+buffer.position()+"\n";
    buffer.releaseResources();
   }finally{if(loaded){camera.deleteMe();camera.setOnlineStatus(false,true);}}
  }finally{screen.setDecayed(true);IdManager.getInstance().releaseId(screen.getObjectId());}
  Files.writeString(root.resolve("server-verification.txt"),report+"No live viewer opted in during this smoke; graphical client integration still pending.\n");
 }
}
