import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.util.StatSet;
public class M4A1DemoAgentV4 {
 static final int ID=902684;static Npc npc;static ScheduledExecutorService timer;static int attempts;static long started;static int state=-1,x,y,z,heading,instance;
 static final String[] NAMES={"M4A1 - Reposo","M4A1 - Alerta","M4A1 - Caminar","M4A1 - Correr","M4A1 - Apuntar","M4A1 - Disparar"};
 public static void agentmain(String directory,Instrumentation instrumentation)throws Exception {
  if(timer!=null)throw new IllegalStateException("V4 already loaded");
  if(NpcData.getInstance().getTemplate(ID)!=null||World.getVisibleObjects().stream().anyMatch(o->o instanceof Npc n&&n.getId()==ID))throw new IllegalStateException("NPC ID occupied");
  if(M4A1DemoAgentV3.timer!=null)M4A1DemoAgentV3.timer.shutdownNow();if(M4A1DemoAgentV3.npc!=null)M4A1DemoAgentV3.npc.deleteMe();
  Path log=Path.of(directory,"rifle-runtime-v4.txt");Files.writeString(log,"READY: 6-state visual cycle; no AI/core changes; no damage or inventory mutation.\n");
  timer=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"M4A1VisualDemoV4");t.setDaemon(true);return t;});
  timer.scheduleAtFixedRate(()->{try{
   if(started==0){
    if(++attempts>600){Files.writeString(log,"EXPIRED: no connected Hellkevin.\n",StandardOpenOption.APPEND);timer.shutdown();return;}
    var p=World.getPlayers().stream().filter(a->a.getName().equalsIgnoreCase("Hellkevin")&&a.isOnline()&&a.getClient()!=null&&!a.isTeleporting()).findFirst().orElse(null);if(p==null)return;
    double angle=p.getHeading()*Math.PI*2/65536.;x=p.getX()+(int)Math.round(65*Math.cos(angle));y=p.getY()+(int)Math.round(65*Math.sin(angle));z=GeoEngine.getInstance().getHeight(x,y,p.getZ());
    if(Math.abs(z-p.getZ())>20){x=p.getX()+(int)Math.round(30*Math.cos(angle));y=p.getY()+(int)Math.round(30*Math.sin(angle));z=GeoEngine.getInstance().getHeight(x,y,p.getZ());if(Math.abs(z-p.getZ())>20)z=p.getZ();}
    heading=(p.getHeading()+32768)&65535;instance=p.getInstanceId();started=System.currentTimeMillis();
   }
   long elapsed=System.currentTimeMillis()-started;if(elapsed>=20*60*1000){if(npc!=null)npc.deleteMe();Files.writeString(log,"REMOVED after20min.\n",StandardOpenOption.APPEND);timer.shutdown();return;}
   int next=(int)(elapsed/12000)%6;if(next==state)return;if(npc!=null)npc.deleteMe();
   StatSet s=new StatSet();s.set("id",ID);s.set("displayId",59084+next);s.set("level",80);s.set("name",NAMES[next]);s.set("title","Demo visual "+(next+1)+"/6 | 12 segundos");s.set("type","Folk");s.set("usingServerSideName",true);s.set("usingServerSideTitle",true);s.set("randomWalk",false);s.set("randomAnimation",false);s.set("attackable",false);s.set("talkable",false);s.set("isAggressive",false);s.set("baseHpMax",10000);s.set("baseMpMax",1000);s.set("collisionRadius",8);s.set("collisionHeight",25);s.set("basePDef",1000);s.set("baseMDef",1000);
   var template=new NpcTemplate(s);template.setSkills(java.util.Map.of());npc=new Npc(template);npc.setName(NAMES[next]);npc.setTitle("Demo visual "+(next+1)+"/6 | 12 segundos");npc.setInvul(true);npc.setInstanceId(instance);npc.setHeading(heading);npc.spawnMe(x,y,z);state=next;
   Files.writeString(log,"STAGE="+next+" display="+(59084+next)+" object="+npc.getObjectId()+" xyz="+x+","+y+","+z+" collisionHeight=25 meshOriginZ=25 "+NAMES[next]+"\n",StandardOpenOption.APPEND);
  }catch(Throwable e){try{Files.writeString(log,"FAIL "+e+"\n",StandardOpenOption.APPEND);}catch(Exception ignored){}if(npc!=null)npc.deleteMe();timer.shutdown();}},1,1,TimeUnit.SECONDS);
 }
}
