import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.util.StatSet;
public class M4A1DemoAgentV5 {
 static final int ID=902685;
 static Npc npc;
 static ScheduledExecutorService timer;
 static int attempts;
 public static void agentmain(String directory,Instrumentation instrumentation)throws Exception {
  Path log=Path.of(directory,"rifle-runtime-v5.txt"); if(M4A1DemoAgentV4.timer!=null)M4A1DemoAgentV4.timer.shutdownNow(); if(M4A1DemoAgentV4.npc!=null)M4A1DemoAgentV4.npc.deleteMe();
  if(NpcData.getInstance().getTemplate(ID)!=null)throw new IllegalStateException("NPC id already registered");
  if(World.getVisibleObjects().stream().anyMatch(o->o instanceof Npc n && n.getId()==ID))throw new IllegalStateException("Demo NPC already active");
  if(timer!=null)throw new IllegalStateException("Demo agent already started");
  timer=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"M4A1DemoAgentV5Demo");t.setDaemon(true);return t;});
  Files.writeString(log,"READY: waiting for connected Hellkevin; no DB or script changes.\n");
  timer.scheduleAtFixedRate(()->{
   try{
    if(npc!=null)return;
    if(++attempts>600){Files.writeString(log,"EXPIRED: no connected Hellkevin in 10 minutes.\n");timer.shutdown();return;}
    var p=World.getPlayers().stream().filter(x->x.getName().equalsIgnoreCase("Hellkevin")&&x.isOnline()&&x.getClient()!=null&&!x.isTeleporting()).findFirst().orElse(null);
    if(p==null)return;
    StatSet s=new StatSet();s.set("id",ID);s.set("displayId",59084);s.set("level",80);s.set("name","M4A1 - Ciclo continuo");s.set("title","6 estados | Sin recrear NPC");s.set("type","Folk");s.set("usingServerSideName",true);s.set("usingServerSideTitle",true);s.set("randomWalk",false);s.set("randomAnimation",false);s.set("attackable",false);s.set("talkable",false);s.set("isAggressive",false);s.set("baseHpMax",10000);s.set("baseMpMax",1000);s.set("collisionRadius",8);s.set("collisionHeight",25);s.set("basePDef",1000);s.set("baseMDef",1000);
    double angle=p.getHeading()*2.0*Math.PI/65536.0;int x=p.getX()+(int)Math.round(90*Math.cos(angle)),y=p.getY()+(int)Math.round(90*Math.sin(angle)),z=p.getZ();
    if(Math.abs(z-p.getZ())>80){x=p.getX();y=p.getY();z=p.getZ();}
    var template=new NpcTemplate(s);template.setSkills(java.util.Map.of());npc=new Npc(template);npc.setName("M4A1 - Ciclo continuo");npc.setTitle("6 estados | Sin recrear NPC");npc.setInvul(true);npc.setInstanceId(p.getInstanceId());npc.setHeading(p.getHeading()+32768);npc.spawnMe(x,y,z);
    Files.writeString(log,"SPAWNED object="+npc.getObjectId()+" npc="+ID+" display=59084 xyz="+x+","+y+","+z+" instance="+npc.getInstanceId()+"\nOnly transient NPC; client appearance not yet verified.\n");
    timer.schedule(()->{try{npc.deleteMe();Files.writeString(log,"REMOVED: 20-minute temporary demo finished.\n",StandardOpenOption.APPEND);}catch(Exception e){}finally{timer.shutdown();}},20,TimeUnit.MINUTES);
   }catch(Throwable e){try{Files.writeString(log,"FAIL: "+e+"\n",StandardOpenOption.APPEND);}catch(Exception ignored){}timer.shutdown();}
  },1,1,TimeUnit.SECONDS);
 }
}




