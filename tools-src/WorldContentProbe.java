import java.lang.instrument.*;
import java.lang.management.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
public class WorldContentProbe {
 public static void agentmain(String dir,Instrumentation i){Thread t=new Thread(()->{try{observe(Path.of(dir));}catch(Throwable e){e.printStackTrace();}},"WorldContentProbe");t.setDaemon(true);t.start();}
 static boolean ours(int id){return id==50008||id==50010||id==900202||id==902500||id==903200||id==903201||id>=901100&&id<=901138;}
 static void census(Path dir)throws Exception{
  Map<String,Integer> counts=new TreeMap<>();Map<Integer,Integer> npcIds=new TreeMap<>();List<String> custom=new ArrayList<>();
  for(var o:World.getVisibleObjects()){
   String type=o instanceof Door?"doors":o instanceof Player?"players":o instanceof Summon?"summons":o instanceof Npc n?(ours(n.getId())?"our_npcs":n instanceof Monster?"classic_monsters":"classic_npcs"):"other";
   counts.merge(type,1,Integer::sum);if(o instanceof Npc n){npcIds.merge(n.getId(),1,Integer::sum);if(ours(n.getId()))custom.add(n.getId()+"\t"+n.getName()+"\t"+n.getX()+"\t"+n.getY()+"\t"+n.getZ());}
  }
  Files.writeString(dir.resolve("counts.txt"),"utc="+java.time.Instant.now()+"\n"+counts+"\nclients="+World.getPlayers().stream().filter(p->p.getClient()!=null).count()+"\n");
  Files.writeString(dir.resolve("our-npcs.tsv"),"id\tname\tx\ty\tz\n"+String.join("\n",custom)+"\n");StringBuilder ids=new StringBuilder("npc_id,count,ours\n");npcIds.forEach((id,count)->ids.append(id+","+count+","+ours(id)+"\n"));Files.writeString(dir.resolve("npc-ids.csv"),ids.toString());
 }
 static void observe(Path dir)throws Exception{
  Files.createDirectories(dir);census(dir);var os=(com.sun.management.OperatingSystemMXBean)ManagementFactory.getOperatingSystemMXBean();long time=System.nanoTime(),cpu=os.getProcessCpuTime();
  try(var w=Files.newBufferedWriter(dir.resolve("samples.csv"))){w.write("utc,heap_used,heap_committed,cpu_machine_percent,free_physical_ram\n");for(int k=0;k<30;k++){Thread.sleep(2000);long now=System.nanoTime(),c=os.getProcessCpuTime();var heap=ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();w.write(java.time.Instant.now()+","+heap.getUsed()+","+heap.getCommitted()+","+(100.0*(c-cpu)/(now-time)/os.getAvailableProcessors())+","+os.getFreeMemorySize()+"\n");w.flush();time=now;cpu=c;}}
  census(dir);Files.writeString(dir.resolve("DONE"),"PASS\n");System.err.println("WORLD_CONTENT_PROBE complete: "+dir);
 }
}
