from pathlib import Path
import json
D=Path(__file__).resolve().parent
c=json.loads((D/'collision-audit.json').read_text())
starts=list(c['spawns'].values());actions=['dragon','dragon proa','dragon habitacion','dragon capitan','dragon galeria']
array=lambda a:'{'+','.join('{'+','.join(map(str,v))+'}' for v in a)+'}'
decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
layers={int(k):[(decode(v),v&15) for v in vs] for k,vs in json.loads((D/'encoded-layers.json').read_text()).items()}
walks=[];blocks=[]
for cell,vs in sorted(layers.items()):
 x,y=cell%2048,cell//2048;wx=131072+x*16+8;wy=32768+y*16+8
 if not (145000<wx<148000 and 51600<wy<52400):continue
 for z,ns in vs:
  if not 11900<z<12500:continue
  for dx,dy,bit,rev in [(1,0,1,2),(0,1,4,8)]:
   nc=(y+dy)*2048+x+dx;dest=next((n for h,n in layers.get(nc,[]) if h==z),None)
   if dest is None:continue
   row=[wx,wy,z+24,wx+dx*16,wy+dy*16,z+24]
   if ns&bit and dest&rev and len(walks)<24:walks.append(row)
   elif not ns&bit and not dest&rev and len(blocks)<16:blocks.append(row)
 if len(walks)>=24 and len(blocks)>=16:break
assert len(walks)==24 and len(blocks)==16
routes=json.loads((D/'navigation-routes.json').read_text());route_edges=[a+b for path in routes.values() for a,b in zip(path,path[1:])]
s='''import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
public class VigiliaScaleSmoke {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder out=new StringBuilder();Player p=null;
  try {
   var geo=GeoEngine.getInstance();int[][] starts=@STARTS@;
   int[][] walks=@WALKS@,walls=@BLOCKS@;
   for(int[] e:walks)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Open edge blocked "+java.util.Arrays.toString(e));
   for(int[] e:walls)if(geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Wall open "+java.util.Arrays.toString(e));
   out.append("open_edges=24 closed_edges=16\\n");
   if(Math.abs(geo.getHeight(152000,46700,12040)-12040)>40||Math.abs(geo.getHeight(149000,46700,12040)-12016)>8||Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Prior floors changed");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"vigilia-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("VigiliaProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("Missing handler");
   String[] actions={"dragon","dragon proa","dragon habitacion","dragon capitan","dragon galeria"};
   for(int i=0;i<starts.length;i++) {
    int[] q=starts[i];if(geo.getHeight(q[0],q[1],q[2]-24)!=q[2]-24)throw new IllegalStateException("Spawn floor mismatch "+actions[i]);
    handler.onCommand("muelle",p,actions[i]);p.onTeleported();Thread.sleep(300);p.revalidateZone(true);
    if(p.getX()!=q[0]||p.getY()!=q[1]||Math.abs(p.getZ()-(q[2]-24))>40||p.isTeleporting())throw new IllegalStateException("Arrival mismatch "+actions[i]);
    if(!p.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Peace zone absent");
    var rz=org.l2jmobius.gameserver.managers.ZoneManager.getInstance().getZone(p,org.l2jmobius.gameserver.entity.zone.type.RespawnZone.class);
    if(rz==null||!"gludio_sky".equals(rz.getRespawnPoint(p)))throw new IllegalStateException("Safe respawn absent");
    int moves=0;for(int[] d:new int[][]{{64,0},{-64,0},{0,64},{0,-64}})if(geo.canMoveToTarget(q[0],q[1],q[2],q[0]+d[0],q[1]+d[1],q[2],0))moves++;
    if(moves<2)throw new IllegalStateException("Arrival boxed in "+actions[i]);
    out.append(actions[i]+"="+p.getX()+","+p.getY()+","+p.getZ()+" moves="+moves+" peace=true respawn=gludio_sky\\n");
   }
   handler.onCommand("muelle",p,"coliseo");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=148900||p.getY()!=46100||p.getZ()>0)throw new IllegalStateException("Coliseum return failed");
   handler.onCommand("muelle",p,"");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=149000||p.getY()!=46700)throw new IllegalStateException("Dock return failed");
   handler.onCommand("muelle",p,"nave");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=152000||p.getY()!=46700)throw new IllegalStateException("Old airship travel changed");
   handler.onCommand("muelle",p,"aurelia");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=153400||p.getY()!=55800)throw new IllegalStateException("Aurelia travel changed");
   if(Math.abs(geo.getHeight(156000,55000,11296)-11296)>16||Math.abs(geo.getHeight(156000,55000,10792)-10792)>16)throw new IllegalStateException("Aurelia interior floors changed");
   int[][] routeEdges=@ROUTES@;
   for(int[] e:routeEdges)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Stair/door route blocked "+java.util.Arrays.toString(e));
   out.append("stair_up_down_and_door_edges="+routeEdges.length+" verified\\n");
   var script=org.l2jmobius.gameserver.managers.ScriptManager.getInstance().getScript("VigiliaCrew");
   if(script==null)throw new IllegalStateException("Crew script missing");
   var crew=org.l2jmobius.gameserver.entity.World.getVisibleObjects().stream().filter(o->o instanceof org.l2jmobius.gameserver.entity.actor.Npc).map(o->(org.l2jmobius.gameserver.entity.actor.Npc)o).filter(n->n.getId()==902710).toList();
   if(crew.size()!=3)throw new IllegalStateException("Expected 3 crew, found "+crew.size());
   String[] events={"galeria","capitan","habitacion","cubierta"};int[] destIndex={4,3,2,0};
   for(int k=0;k<events.length;k++) {
    var n=crew.get(k%3);p.teleToLocation(n.getX()+60,n.getY(),n.getZ()+24,0,0,false);p.onTeleported();Thread.sleep(200);
    String menu=script.onFirstTalk(n,p);if(menu==null||!menu.contains("Quest VigiliaCrew galeria"))throw new IllegalStateException("NPC menu missing");
    script.onEvent(events[k],n,p);p.onTeleported();Thread.sleep(200);int[] target=starts[destIndex[k]];
    if(p.getX()!=target[0]||p.getY()!=target[1]||Math.abs(p.getZ()-(target[2]-24))>40)throw new IllegalStateException("NPC travel failed "+events[k]);
   }
   var lower=crew.stream().min(java.util.Comparator.comparingInt(org.l2jmobius.gameserver.entity.actor.Npc::getZ)).orElseThrow();
   p.teleToLocation(149000,46700,12040,0,0,false);p.onTeleported();Thread.sleep(200);script.onEvent("galeria",lower,p);
   if(p.getX()!=149000||p.getY()!=46700)throw new IllegalStateException("Remote bypass accepted");
   p.teleToLocation(lower.getX()+60,lower.getY(),lower.getZ()+24,0,0,false);p.onTeleported();Thread.sleep(200);p.setDead(true);script.onEvent("galeria",lower,p);
   if(p.getX()!=lower.getX()+60)throw new IllegalStateException("Dead bypass accepted");p.setDead(false);
   var upper=crew.stream().filter(n->n.getX()==145350).findFirst().orElseThrow();
   p.teleToLocation(upper.getX()+60,upper.getY(),12056+24,0,0,false);p.onTeleported();Thread.sleep(200);script.onEvent("galeria",upper,p);
   if(p.getX()!=upper.getX()+60||p.getY()!=upper.getY())throw new IllegalStateException("Other-floor NPC bypass accepted");
   out.append("crew_count=3 menu=true 4_transfers=PASS remote_dead_other_floor_bypass_refused=true\\n");
   out.append("PASS: five V3 arrivals + crew and complete stair/door routes, movement, peace/respawn, Aurelia + original airship/dock/Coliseum, 24 open and 16 closed edges. Transient probe only. Client rendering/physics and moving transport not tested.\\n");
  }catch(Throwable e){out.append("FAIL: "+e+"\\n");throw e;}
  finally {if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(Path.of(directory,"server-smoke.txt"),out);}
 }
}
'''.replace('@ROUTES@',array(route_edges)).replace('@STARTS@',array(starts)).replace('@WALKS@',array(walks)).replace('@BLOCKS@',array(blocks))
(D/'VigiliaScaleSmoke.java').write_text(s);(D/'smoke-agent.mf').write_text('Manifest-Version: 1.0\nAgent-Class: VigiliaScaleSmoke\n\n')
print('Prepared transient runtime test.')
