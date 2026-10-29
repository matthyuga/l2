import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.Map;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;

/** Live registered handlers, transient characters only; no database/account creation. */
public class VerifyElven
{
 static void require(boolean ok,String message) { if(!ok)throw new IllegalStateException(message); }
 static Field field(Class<?> cls,String name)throws Exception { Field f=cls.getDeclaredField(name);f.setAccessible(true);return f; }
 static Method method(Class<?> cls,String name,Class<?>... types)throws Exception { Method m=cls.getDeclaredMethod(name,types);m.setAccessible(true);return m; }
 static Player player(String name)throws Exception
 {
  var template=PlayerTemplateData.getInstance().getTemplate(0);
  var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
  Player p=ctor.newInstance(template,"elven-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
  p.setName(name);p.setLabControlled(true);p.setOnlineStatus(true,false);p.setEnteredWorld();p.setDead(false);p.setInvul(false);p.setSpawnProtection(false);p.spawnMe(83425,148585,-3406);
  p.setCurrentHp(p.getMaxHp()*0.6);p.setCurrentMp(p.getMaxMp()*0.5);p.setCurrentCp(p.getMaxCp()*0.4);
  SkillData.getInstance().getSkill(1204,1).applyEffects(p,p);
  return p;
 }
 static void sameResources(Player p,double hp,double mp,double cp,String context)
 {
  require(Math.abs(p.getCurrentHp()-hp)<0.001 && Math.abs(p.getCurrentMp()-mp)<0.001 && Math.abs(p.getCurrentCp()-cp)<0.001,context+" changed resources");
  require(p.isAffectedBySkill(1204),context+" removed buff");
 }
 @SuppressWarnings("unchecked")
 public static void agentmain(String directory,Instrumentation ignored)throws Exception
 {
  StringBuilder report=new StringBuilder();Player p=null,q=null;Object lobby=null;
  try
  {
   var handler=VoicedCommandHandler.getInstance().getHandler("salas");require(handler!=null,"Lobby missing");lobby=handler;
   Class<?> cls=lobby.getClass();Method tick=method(cls,"tick");
   Map<Integer,Object> visits=(Map<Integer,Object>)field(cls,"visits").get(lobby);
   Map<Integer,Location> returns=(Map<Integer,Location>)field(cls,"returns").get(lobby);
   Npc[] hosts=(Npc[])field(cls,"hosts").get(lobby);
   require(hosts.length==2 && hosts[0]!=null && hosts[1]!=null,"Two hosts missing");
   require(hosts[0].getId()==902600 && hosts[1].getZ()>11000,"Host placement mismatch");
   String html=(String)method(cls,"menu").invoke(lobby);require(html.contains("Quest PvpRooms elven"),"Menu bypass missing");
   var geo=org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance();
   for(int edge=0;edge<4;edge++)
   {
    int crossings=0;
    for(int along=0;along<7200;along+=64)
    {
     int x=edge<2?(edge==0?42000:49200):42000+along;
     int y=edge<2?46600+along:(edge==2?46600:54000);
     int ix=x+(edge==0?64:edge==1?-64:0),iy=y+(edge==2?64:edge==3?-64:0);
     int ox=x+(edge==0?-64:edge==1?64:0),oy=y+(edge==2?-64:edge==3?64:0);
     int iz=geo.getHeight(ix,iy,-3000),oz=geo.getHeight(ox,oy,-3000);
     if(iz>-3800 && iz<-2000 && oz>-3800 && oz<-2000 && geo.canMoveToTarget(ix,iy,iz,ox,oy,oz,0))crossings++;
    }
    report.append("Boundary edge "+edge+": "+crossings+" geodata crossings (sampled every 64 units).\n");
    require(crossings>0,"Boundary edge unreachable: "+edge);
   }
   report.append("PASS lobby NPCs at Giran + Gludio dock; menu Elven bypass.\n");
   p=player("ElvenBoundaryProbe");q=player("ElvenSecondProbe");
   synchronized(lobby)
   {
    double hp=p.getCurrentHp(),mp=p.getCurrentMp(),cp=p.getCurrentCp();
    VoicedCommandHandler.getInstance().getHandler("elvenpvp").onCommand("elvenpvp",p,"entrar");
    sameResources(p,hp,mp,cp,"Entry");
    require(p.getInstanceId()>0 && !p.isTeleportProtected() && !p.isTeleporting(),"Entry protection/loading state");
    int room=p.getInstanceId();
    q.setXYZ(hosts[1].getX(),hosts[1].getY(),hosts[1].getZ());
    method(cls,"onEvent",String.class,Npc.class,Player.class).invoke(lobby,"elven",hosts[1],q);
    require(q.getInstanceId()==room,"Dock NPC event failed or players entered separate rooms");
    report.append("PASS .elvenpvp delegates to lobby, shared room, entry preserves HP/MP/CP/buff; no protection.\n");
    p.setXYZ(45150,52100,-2792);tick.invoke(lobby);
    Object visit=visits.get(p.getObjectId());Class<?> visitClass=visit.getClass();
    Field timer=field(visitClass,"exitStarted");
    p.setXYZ(49240,52100,-2792);tick.invoke(lobby);
    require(timer.getLong(visit)>0,"Boundary did not start timer");
    require(!p.isInvul() && p.isSpawned(),"Boundary granted immunity/decayed player");
    require(timer.getLong(visits.get(q.getObjectId()))==0,"Second player's countdown affected");
    double before=p.getCurrentHp();p.getStatus().reduceHp(3,q,true,false,false,true);
    require(p.getCurrentHp()<before,"Could not damage during countdown");
    hp=p.getCurrentHp();mp=p.getCurrentMp();cp=p.getCurrentCp();
    p.setXYZ(49100,52100,-2792);tick.invoke(lobby);
    require(p.getX()==45150 && p.getY()==52100,"Cancel did not return to last interior position");
    require(timer.getLong(visit)==0 && p.isSpawned() && !p.isInvul() && !p.isTeleporting(),"Cancel state/protection");
    sameResources(p,hp,mp,cp,"Cancel return");
    before=p.getCurrentHp();p.getStatus().reduceHp(3,q,true,false,false,true);require(p.getCurrentHp()<before,"Could not damage after return");
    report.append("PASS boundary starts countdown; damage applied during countdown and after return; cancel restores position only, remains spawned/targetable; independent players.\n");
    p.setXYZ(49240,52100,-2792);tick.invoke(lobby);
    timer.setLong(visit,System.nanoTime()-3_800_000_000L);tick.invoke(lobby);require(p.getInstanceId()==room,"Exited before 4 seconds");
    timer.setLong(visit,System.nanoTime()-4_010_000_000L);
    hp=p.getCurrentHp();mp=p.getCurrentMp();cp=p.getCurrentCp();tick.invoke(lobby);
    require(p.getInstanceId()==0 && p.getX()==83425 && p.getY()==148585,"Deadline did not exit to Giran");
    sameResources(p,hp,mp,cp,"Exit");require(!visits.containsKey(p.getObjectId()),"Countdown survived exit");
    require(q.getInstanceId()==room,"Other player was ejected");
    require(returns.get(p.getObjectId()).getX()==45150,"Saved return point wrong");
    // The damage check started a combat stance; entry correctly rejects combat, so clear probe stance only.
    org.l2jmobius.gameserver.taskmanagers.AttackStanceTaskManager.getInstance().removeAttackStanceTask(p);
    handler.onCommand("salas",p,"elven");
    require(p.getInstanceId()==room && p.getX()==45150,"Re-entry did not use saved interior point");
    sameResources(p,hp,mp,cp,"Re-entry");
    visit=visits.get(p.getObjectId());timer=field(visit.getClass(),"exitStarted");require(timer.getLong(visit)==0,"Old timer resumed on re-entry");
    report.append("PASS no exit at 3.8 s, exit at >=4 s to Giran, retained state and saved-point re-entry, no stale timer/other-player exit.\n");
    handler.onCommand("salas",p,"salir");require(timer.getLong(visit)>0,"Manual command bypassed countdown");
    handler.onCommand("salas",p,"cancelar");require(timer.getLong(visit)==0,"Manual cancel failed");
    p.setXYZ(49240,52100,-2792);tick.invoke(lobby);p.setDead(true);tick.invoke(lobby);
    require(timer.getLong(visit)==0 && p.getInstanceId()==room,"Death did not cancel countdown");
    p.setDead(false);p.setXYZ(45150,52100,-2792);
    p.setCurrentHp(p.getMaxHp()*0.5);p.setCurrentMp(p.getMaxMp()*0.3);p.setCurrentCp(p.getMaxCp()*0.2);
    hp=p.getCurrentHp();mp=p.getCurrentMp();cp=p.getCurrentCp();
    Object old=VoicedCommandHandler.getInstance().getHandler("elvenpvp");
    var dead=(java.util.Set<Integer>)field(old.getClass(),"_deadPlayers").get(old);dead.add(p.getObjectId());
    method(old.getClass(),"tickArena").invoke(old);sameResources(p,hp,mp,cp,"Observed revival");
    visits.remove(p.getObjectId());p.setInstanceId(0);tick.invoke(lobby);require(!visits.containsKey(p.getObjectId()),"External departure retained visit");
    report.append("PASS command exit uses countdown, manual cancel, death cancellation, revival observer never heals, external departure cleanup.\n");
   }
   report.append("PASS server behavior only; client rendering/bar/visual perimeter not inspected. No persistent player/account created.\n");
  }
  catch(Throwable error){report.append("FAIL: "+error+"\n");throw error;}
  finally
  {
   for(Player probe:new Player[]{p,q})if(probe!=null)
   {
    if(lobby!=null){((Map<?,?>)field(lobby.getClass(),"visits").get(lobby)).remove(probe.getObjectId());((Map<?,?>)field(lobby.getClass(),"returns").get(lobby)).remove(probe.getObjectId());}
    var world=InstanceManager.getInstance().getWorld(probe.getInstanceId());if(world!=null)world.removeAllowed(probe);
    probe.abortAttack();probe.abortCast();probe.stopAllEffects();probe.deleteMe();probe.setOnlineStatus(false,false);
   }
   Files.writeString(Path.of(directory,"verification.txt"),report);
  }
 }
}
