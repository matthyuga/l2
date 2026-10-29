import java.lang.instrument.Instrumentation;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.data.xml.ItemData;
import org.l2jmobius.gameserver.network.serverpackets.FakePlayerInfo;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.commons.network.pool.ResourcePool;
public class ShowcaseRuntimeCheck {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  var report=new ArrayList<String>();Path out=Path.of(dir,"runtime-verification.txt");
  try {
   var seen=new HashSet<Integer>();int packets=0;
   for(var object:World.getVisibleObjects())if(object instanceof Npc npc && npc.getId()>=62000 && npc.getId()<=62156){
    if(!seen.add(npc.getId())||!npc.isFakePlayer()||!npc.isInvul()||!npc.isImmobilized()||npc.canMove()||npc.isAutoAttackable(null)||npc.isInCombat())throw new AssertionError("Unsafe/duplicate mannequin "+npc.getId());
    if(Math.hypot(npc.getX()-81920,npc.getY()-148608)>1000 || npc.getZ()!=-3400)throw new AssertionError("Misplaced mannequin "+npc.getId());
    var fp=npc.getTemplate().getFakePlayerInfo();
    int[] expected={0,fp.getEquipHead(),fp.getEquipRHand(),fp.getEquipLHand(),fp.getEquipGloves(),fp.getEquipChest(),fp.getEquipLegs(),fp.getEquipFeet(),fp.getEquipCloak(),fp.getEquipRHand(),fp.getEquipHair(),fp.getEquipHair2()};
    WriteBuffer buffer=new WriteBuffer(new ResourcePool(),FakePlayerInfo.class);byte[] bytes;
    try {new FakePlayerInfo(npc).writeImpl(null,buffer);buffer.mark();bytes=buffer.toByteArray();}finally{buffer.releaseResources();}
    ByteBuffer b=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);b.get();
    if(b.getInt()!=npc.getX()||b.getInt()!=npc.getY()||b.getInt()!=npc.getZ())throw new AssertionError("Bad packet position");
    b.getInt();if(b.getInt()!=npc.getObjectId())throw new AssertionError("Bad object ID");
    while(b.getShort()!=0){};b.getInt();b.getInt();b.getInt();
    for(int item:expected){if(b.getInt()!=item)throw new AssertionError("Wrong visual paperdoll slot "+npc.getId());if(item>0 && ItemData.getInstance().getTemplate(item)==null)throw new AssertionError("Missing equipped template "+item);}
    packets++;report.add("PASS "+npc.getId()+" "+npc.getName()+" xyz="+npc.getX()+","+npc.getY()+","+npc.getZ()+" protected/static; CHAR_INFO paperdoll verified");
   }
   if(seen.size()!=157||packets!=157)throw new AssertionError("Expected 157, found "+seen.size());
   report.add("SUCCESS: 157 live mannequins, 157 serialized native CHAR_INFO packets, all equipment references resolve; no display inventory or player account created. In-client appearance remains to review.");
  }catch(Throwable e){report.add("FAILED "+e);throw e;}
  finally{Files.write(out,report);}
 }
}
