package custom.ElvenPvpRoom;

import java.nio.file.Path;
import java.util.*;
import java.util.function.LongSupplier;
import java.util.concurrent.ThreadLocalRandom;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Team;
import org.l2jmobius.gameserver.entity.instancezone.*;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDeath;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.network.serverpackets.*;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import custom.ElvenPvpRoom.RoundState.*;
import custom.ElvenPvpRoom.PvpRoomConfig.ArenaMap;

/** Four independent rooms. No automatic resurrection, restoration or teleport immunity. */
public class PvpRoundRooms extends Script implements IVoicedCommandHandler {
 public static void main(String[] args){new PvpRoundRooms();}
 private static final Logger LOG=Logger.getLogger(PvpRoundRooms.class.getName());
 private static final String OWNER="hellgames:pvp-round-rooms";
 private static final long EXIT=4_000_000_000L;
 private static final int NPC=902600;
 private final PvpRoomConfig config;
 private final LongSupplier clock;
 private final int template;
 private final Map<Mode,Room> rooms=new EnumMap<>(Mode.class);
 private final Map<Integer,Visit> visits=new HashMap<>();
 private final Map<String,Location> returns=new HashMap<>();
 private long lastUi;
 private final PvpRoomBots bots;
 private final PvpRoomUi roomUi;
 private static final class Room {
  final RoundState state; Instance instance;
  Room(RoundState state){this.state=state;}
 }
 private static final class Visit {
  final Player player; final Room room; final int originalColor,originalTitleColor; final String originalTitle; final Team originalTeam;
  Location lastInside; long exitStarted; boolean commandExit,votePanel,scorePanel,pendingMapTravel; int shown=-1;
  ConsumerEventListener deathListener;
  Visit(Player p,Room r,Location l){player=p;room=r;lastInside=l;originalColor=p.getAppearance().getNameColor();originalTeam=p.getTeam();originalTitle=p.getAppearance().getVisibleTitle();originalTitleColor=p.getAppearance().getTitleColor();}
 }
 public PvpRoundRooms(){this(loadConfig(),System::nanoTime,3060,true);}
 private static PvpRoomConfig loadConfig(){try{return new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));}catch(Exception e){throw new IllegalStateException("PvP rooms configuration invalid",e);}}
 // Isolated server verification supplies a clock and empty template 0, no NPC, handler or scheduler.
 public PvpRoundRooms(PvpRoomConfig config,LongSupplier clock,int template,boolean live){
  this.config=config;this.clock=clock;this.template=template;
  for(Mode mode:Mode.values())rooms.put(mode,new Room(new RoundState(mode,new ArrayList<>(config.maps.keySet()),"elven",clock.getAsLong(),config.roundNanos,config.voteLeadNanos,config.voteNanos,ThreadLocalRandom.current())));
  bots=new PvpRoomBots(this);roomUi=new PvpRoomUi(this);
  if(live){
   addStartNpc(NPC);addTalkId(NPC);addFirstTalkId(NPC);
   addSpawn(NPC,83480,148120,-3406,32768,false,0,false,0);
   addSpawn(NPC,149160,46700,12016,32768,false,0,false,0);
   VoicedCommandHandler.getInstance().registerHandler(this);
   ThreadPool.scheduleAtFixedRate(this::tick,100,100);
   LOG.info("PvpRoundRooms: four independent modes, three maps, 5m/60s vote and vulnerable exits.");
  }
 }
 @Override public String[] getCommandList(){return new String[]{"salas"};}
 @Override public synchronized boolean onCommand(String command,Player p,String params){
  if(p==null)return false;
  String[] args=(params==null?"":params.trim()).split("\\s+");
  switch(args[0].toLowerCase(Locale.ROOT)){
   case "bots" -> { if(!p.isGM())p.sendMessage("Comando reservado a GM.");else bots.command(p,Arrays.copyOfRange(args,1,args.length)); }
   case "entrar", "elven" -> enter(p,Mode.FREE);
   case "libre" -> enter(p,Mode.FREE);
   case "equipos" -> enter(p,Mode.TWO_TEAMS);
   case "tres" -> enter(p,Mode.THREE_TEAMS);
   case "arena" -> enter(p,Mode.ARENA);
   case "salir" -> requestExit(p);
   case "cancelar" -> {Visit v=visits.get(p.getObjectId());if(v!=null&&v.commandExit&&!p.isDead()&&map(v.room).inside(new Location(p))){if(clock.getAsLong()-v.exitStarted>=EXIT)leave(v);else returnInside(v);}}
   case "elegir" -> {
    Visit v=visits.get(p.getObjectId());
    if(v!=null&&args.length==3&&p.getInstanceId()==instance(v.room).getId())try{
     long token=Long.parseLong(args[1]);RoundState state=v.room.state;long now=clock.getAsLong();state.advance(now);
     if(token==state.generation()&&state.phase()==Phase.VOTING&&!state.hasVoted(p.getObjectId())&&config.maps.containsKey(args[2]))roomUi.choose(p,token,args[2],config.maps.get(args[2]).name(),now,now+state.voteRemaining(now));
    }catch(NumberFormatException ignored){}
   }
   case "votar" -> {
    Visit v=visits.get(p.getObjectId());if(v!=null&&p.getInstanceId()==instance(v.room).getId()){
     if(args.length==3){try{if(!v.room.state.vote(p.getObjectId(),Long.parseLong(args[1]),args[2],clock.getAsLong()))p.sendMessage("Voto no aceptado: ya votaste, la votacion termino o el panel es anterior.");}catch(NumberFormatException e){p.sendMessage("Votacion invalida.");}}
     v.votePanel=true;v.scorePanel=false;showVote(v);
    }
   }
   case "cerrar" -> {Visit v=visits.get(p.getObjectId());if(v!=null){v.votePanel=false;v.scorePanel=false;}p.sendPacket(new NpcHtmlMessage("<html><body>Panel cerrado. .salas votar para abrirlo.</body></html>"));}
   case "top" -> {Visit v=visits.get(p.getObjectId());if(v!=null){v.votePanel=false;v.scorePanel=true;showTop(v);}}
   default -> p.sendPacket(new NpcHtmlMessage(menu()));
  }
  return true;
 }
 @Override public String onFirstTalk(Npc npc,Player p){return menu();}
 @Override public String onTalk(Npc npc,Player p){return menu();}
 @Override public synchronized String onEvent(String event,Npc npc,Player p){
  if(npc==null||npc.getId()!=NPC||npc.getInstanceId()!=p.getInstanceId()||!p.isInsideRadius2D(npc,250)||Math.abs(p.getZ()-npc.getZ())>200)return null;
  onCommand("salas",p,event);return null;
 }
 private String button(String label,String action){return "<button value=\""+label+"\" action=\"bypass -h voice .salas "+action+"\" width=230 height=24 back=\"L2UI_CT1.Button_DF_Down\" fore=\"L2UI_CT1.Button_DF\">";}
 private String menu(){
  StringBuilder b=new StringBuilder("<html><body><center><font color=LEVEL>HELLGAMES - Salas PvP</font><br>");
  String[] actions={"libre","equipos","tres","arena"};int i=0;
  for(Room r:rooms.values()){b.append(button(r.state.mode.label,actions[i++])).append(map(r).name()).append(" | ").append(r.state.participants()).append(" jugadores<br>");}
  return b.append("<br>Salida vulnerable: 4 segundos.<br>Entrar conserva tu estado y efectos.<br>.salas votar / .salas top</center></body></html>").toString();
 }
 private ArenaMap map(Room r){return config.maps.get(r.state.current());}
 private Instance instance(Room r){
  if(r.instance==null){
   r.instance=InstanceManager.getInstance().createDynamicInstance(template);r.instance.setPvP(true);
   InstanceWorld w=new InstanceWorld();w.setInstance(r.instance);InstanceManager.getInstance().addWorld(w);
  }
  return r.instance;
 }
 private String returnKey(Player p,Room r){return p.getObjectId()+":"+r.state.mode+":"+r.state.current();}
 private synchronized void enter(Player p,Mode mode){
  if(visits.containsKey(p.getObjectId())){p.sendMessage("Primero sal de tu sala actual.");return;}
  if(p.isDead()||p.isInCombat()||p.isTeleporting()||p.isMounted()||p.isFlying()||p.isInVehicle()||p.isInOlympiadMode()||p.isInDuel()||p.isOnEvent()||p.getInstanceId()!=0){p.sendMessage("Debes estar vivo, desmontado, fuera de combate, eventos e instancias.");return;}
  Room r=rooms.get(mode);int team=r.state.join(p.getObjectId(),p.getName());
  ArenaMap m=map(r);Location loc=m.safe(returns.getOrDefault(returnKey(p,r),m.spawns().get(team)));
  Visit v=new Visit(p,r,loc);visits.put(p.getObjectId(),v);
  listen(v);roomUi.attach(p);
  PvpFlagTaskManager.getInstance().force(p,OWNER);
  InstanceWorld w=InstanceManager.getInstance().getWorld(instance(r).getId());if(w!=null)w.addAllowed(p);
  travel(p,loc,instance(r).getId());applyTeam(v,team);
  if(r.state.phase()==Phase.VOTING||r.state.phase()==Phase.RESULT){v.votePanel=true;showVote(v);}
  if(mode==Mode.ARENA){v.scorePanel=true;v.votePanel=false;showTop(v);}
  p.sendMessage(mode.label+" - "+m.name()+". Salida: 4 segundos. .salas votar / .salas top");
 }
 private void applyTeam(Visit v,int team){
  Player p=v.player;RoomCombatRules.join(p,team,config.friendlyFire);
  p.setTeam(team==1?Team.RED:team==2?Team.BLUE:Team.NONE);
  // Team title remains visible even if violet PvP name color takes precedence.
  if(team>0){int color=team==1?0x4040FF:team==2?0xFF8040:0x40FF40;p.getAppearance().setNameColor(color);p.getAppearance().setTitleColor(color);p.getAppearance().setVisibleTitle(team==1?"ROJOS":team==2?"AZULES":"VERDES");}
  p.broadcastInfo();
 }
 private static void travel(Player p,Location l,int instance){
  RoomTeleportSync.arm(p,instance);p.teleToLocation(l.getX(),l.getY(),l.getZ(),l.getHeading(),instance,false);
  p.setClientX(p.getX());p.setClientY(p.getY());p.setClientZ(p.getZ());p.setCursorKeyMovement(false);p.onTeleported();p.setTeleportProtection(false);
 }
 private void requestExit(Player p){Visit v=visits.get(p.getObjectId());if(v!=null&&!p.isDead()&&!p.isTeleporting()&&v.exitStarted==0){v.commandExit=true;beginExit(v,clock.getAsLong());}}
 private void beginExit(Visit v,long now){v.exitStarted=now;v.shown=-1;roomUi.exit(v.player,now,now+EXIT);}
 void uiCancelExit(Player p){
  Visit v=visits.get(p.getObjectId());if(v==null||v.exitStarted==0||p.isDead()||p.isTeleporting())return;
  if(clock.getAsLong()-v.exitStarted>=EXIT)return;
  returnInside(v);
 }
 private void returnInside(Visit v){
  Player p=v.player;Location l=map(v.room).safe(v.lastInside);
  p.stopMove(null);p.abortAttack();p.abortCast();p.setTarget(null);p.getAI().setIntentionActive();RoomTeleportSync.arm(p,p.getInstanceId());
  p.setXYZ(l.getX(),l.getY(),l.getZ());p.setHeading(l.getHeading());p.setClientX(p.getX());p.setClientY(p.getY());p.setClientZ(p.getZ());p.setCursorKeyMovement(false);p.setBlinkActive(true);
  p.setLastServerPosition(p.getX(),p.getY(),p.getZ());p.revalidateZone(true);p.broadcastPacket(new TeleportToLocation(p,p.getX(),p.getY(),p.getZ(),p.getHeading()));p.broadcastInfo();
  if(p.getSummon()!=null)p.getSummon().teleToLocation(p.getLocation(),false);
  roomUi.invalidate(p,PvpRoomUi.Kind.EXIT);v.exitStarted=0;v.commandExit=false;v.shown=-1;screen(p,"Salida cancelada",ExShowScreenMessage.BOTTOM_CENTER,1500);
 }
 private void listen(Visit v){
  if(v.deathListener!=null)v.player.removeListener(v.deathListener);
  long generation=v.room.state.generation();
  v.deathListener=new ConsumerEventListener(v.player,EventType.ON_CREATURE_DEATH,(OnCreatureDeath event)->death(event,generation),this);v.player.addListener(v.deathListener);
 }
 private synchronized void death(OnCreatureDeath event,long generation){
  if(event.getTarget()==null||!event.getTarget().isPlayer())return;
  Visit victim=visits.get(event.getTarget().getObjectId());if(victim==null||victim.room.state.generation()!=generation||victim.player.getInstanceId()!=instance(victim.room).getId())return;
  Player killer=event.getAttacker()==null?null:event.getAttacker().asPlayer();Visit attacker=killer==null?null:visits.get(killer.getObjectId());
  victim.room.state.death(attacker!=null&&attacker.room==victim.room?killer.getObjectId():0,victim.player.getObjectId());
  roomUi.invalidate(victim.player,PvpRoomUi.Kind.EXIT);victim.exitStarted=0;victim.commandExit=false;victim.shown=-1;
 }
 private void leave(Visit v){
  returns.put(returnKey(v.player,v.room),map(v.room).safe(v.lastInside));
  InstanceWorld w=InstanceManager.getInstance().getWorld(v.player.getInstanceId());if(w!=null)w.removeAllowed(v.player);
  travel(v.player,new Location(83425,148585,-3406),0);cleanup(v);
 }
 private void cleanup(Visit v){
  roomUi.detach(v.player);visits.remove(v.player.getObjectId());v.room.state.leave(v.player.getObjectId());RoomCombatRules.leave(v.player);
  if(v.deathListener!=null)v.player.removeListener(v.deathListener);
  v.player.setTeam(v.originalTeam);v.player.getAppearance().setNameColor(v.originalColor);v.player.getAppearance().setTitleColor(v.originalTitleColor);v.player.getAppearance().setVisibleTitle(v.originalTitle);v.player.broadcastInfo();PvpFlagTaskManager.getInstance().release(v.player,OWNER);
 }
 private static void screen(Player p,String text,int position,int millis){p.sendPacket(new ExShowScreenMessage(text,position,millis,1,false,false));}

 private static String escape(String text){return text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}
 private void showVote(Visit v){
  RoundState s=v.room.state;long now=clock.getAsLong();s.advance(now);
  StringBuilder b=new StringBuilder("<html><body><center><font color=LEVEL>Siguiente mapa - "+s.mode.label+"</font><br>");
  if(s.phase()==Phase.VOTING)b.append(PvpRoomUi.progress(s.voteRemaining(now),config.voteNanos)).append(" ").append((s.voteRemaining(now)+999999999)/1000000000).append(" s<br>");
  else if(s.phase()==Phase.BEFORE_VOTE)b.append("Abre cuando faltan 5 minutos.<br>");
  else b.append("Votacion cerrada. Siguiente: ").append(escape(config.maps.get(s.next()).name())).append("<br>");
  for(var entry:s.tally().entrySet()){
   b.append(escape(config.maps.get(entry.getKey()).name())).append(": ").append(entry.getValue()).append(" votos<br>");
   if(s.phase()==Phase.VOTING&&!s.hasVoted(v.player.getObjectId()))b.append(button("Votar", "elegir "+s.generation()+" "+entry.getKey()));
  }
  b.append("<br>Un voto por personaje y ronda.<br>Sin votos: al azar. Empate: sorteo.<br>").append(button("Cerrar", "cerrar")).append("</center></body></html>");
  v.player.sendPacket(new NpcHtmlMessage(b.toString()));
 }
 private void showTop(Visit v){
  StringBuilder b=new StringBuilder("<html><body><center><font color=LEVEL>Top 10 de la ronda</font><br><table width=260><tr><td># / Jugador</td><td>Bajas</td><td>Muertes</td></tr>");int rank=0;
  for(Standing s:v.room.state.top10())b.append("<tr><td>").append(++rank).append(". ").append(escape(s.name())).append("</td><td>").append(s.kills()).append("</td><td>").append(s.deaths()).append("</td></tr>");
  b.append("</table><br>").append(button("Cerrar", "cerrar")).append("</center></body></html>");v.player.sendPacket(new NpcHtmlMessage(b.toString()));
 }
 private void roundFinished(Room r,long now){
  for(Visit v:visits.values())if(v.room==r)screen(v.player,"Fin de ronda. "+score(r),ExShowScreenMessage.TOP_CENTER,5000);
  r.state.restart(now);
  for(Visit v:visits.values())if(v.room==r){
   int team=r.state.join(v.player.getObjectId(),v.player.getName());v.exitStarted=0;v.commandExit=false;v.shown=-1;v.votePanel=false;v.scorePanel=r.state.mode==Mode.ARENA;
   roomUi.invalidate(v.player,PvpRoomUi.Kind.EXIT);roomUi.invalidate(v.player,PvpRoomUi.Kind.VOTE);v.lastInside=map(r).safe(map(r).spawns().get(team));
   // A dead player is moved only after a normal revive, never revived by this controller.
   v.pendingMapTravel=v.player.isDead();if(!v.pendingMapTravel)travel(v.player,v.lastInside,instance(r).getId());
   applyTeam(v,team);listen(v);
  }
 }
 private String score(Room r){
  if(r.state.mode.teams>0)return "Rojos "+r.state.teamScore(1)+" | Azules "+r.state.teamScore(2)+(r.state.mode.teams==3?" | Verdes "+r.state.teamScore(3):"");
  List<Standing> top=r.state.top10();return top.isEmpty()?"Sin bajas":("Lider: "+top.get(0).name()+" - "+top.get(0).kills()+" bajas");
 }
 public synchronized void tick(){
  try{
   long now=clock.getAsLong();boolean ui=now-lastUi>=1_000_000_000L;if(ui)lastUi=now;
   for(Room r:rooms.values()){
    Phase before=r.state.phase(),after=r.state.advance(now);
    if(after==Phase.FINISHED){roundFinished(r,now);continue;}
    if(before!=after&&(after==Phase.VOTING||after==Phase.RESULT))for(Visit v:visits.values())if(v.room==r){v.votePanel=true;v.scorePanel=false;showVote(v);}
   }
   for(Visit v:new ArrayList<>(visits.values())){
    Player p=v.player;
    if(!p.isOnline()||World.getPlayer(p.getObjectId())!=p||p.getInstanceId()!=instance(v.room).getId()){cleanup(v);continue;}
    PvpFlagTaskManager.getInstance().force(p,OWNER);
    if(p.isDead()){roomUi.invalidate(p,PvpRoomUi.Kind.EXIT);v.exitStarted=0;v.commandExit=false;v.shown=-1;}
    else if(!p.isTeleporting()){
     if(v.pendingMapTravel){travel(p,v.lastInside,instance(v.room).getId());v.pendingMapTravel=false;}
     v.room.state.alive(p.getObjectId());
     if(v.exitStarted!=0){long left=EXIT-(now-v.exitStarted);
      if(left<=0){leave(v);continue;}
      if(!v.commandExit&&map(v.room).inside(new Location(p)))returnInside(v);
      // Native ConfirmDlg animates its own countdown; never resend it per tick.
     }else if(map(v.room).inside(new Location(p))){p.setBlinkActive(false);v.lastInside=new Location(p);}
     else beginExit(v,now);
    }
    if(ui){
     screen(p,v.room.state.mode.label+" | "+score(v.room)+" | "+(v.room.state.remaining(now)/60_000_000_000L)+":"+String.format(Locale.ROOT,"%02d",v.room.state.remaining(now)/1_000_000_000L%60),ExShowScreenMessage.TOP_CENTER,1200);
     if(v.votePanel&&(v.room.state.phase()==Phase.VOTING||v.room.state.phase()==Phase.RESULT))showVote(v);else if(v.scorePanel)showTop(v);
    }
   }
   bots.tick(now);
  }catch(Exception e){LOG.log(Level.SEVERE,"PvP room tick failed",e);}
 }

 // Package-scoped bot bridge. Every caller runs under this controller's monitor.
 RoundState botState(Mode mode){return rooms.get(mode).state;}
 long botNow(){return clock.getAsLong();}
 long botVoteDuration(){return config.voteNanos;}
 List<Player> botParticipants(Mode mode){List<Player> result=new ArrayList<>();for(Visit v:visits.values())if(v.room==rooms.get(mode))result.add(v.player);return result;}
 boolean botJoin(Player p,Mode mode){enter(p,mode);return visits.containsKey(p.getObjectId());}
 void botForget(Player p){Visit v=visits.get(p.getObjectId());if(v!=null)cleanup(v);returns.keySet().removeIf(k->k.startsWith(p.getObjectId()+":"));}
 void botReposition(Player p){
  Visit v=visits.get(p.getObjectId());if(v==null)throw new IllegalStateException("Bot has no visit");
  int team=v.room.state.team(p.getObjectId());Location destination=map(v.room).safe(map(v.room).spawns().get(team));
  v.lastInside=destination;v.pendingMapTravel=false;v.exitStarted=0;v.commandExit=false;v.shown=-1;
  travel(p,destination,instance(v.room).getId());
 }
 public synchronized void closeForVerification(){bots.stopAll();for(Visit v:new ArrayList<>(visits.values()))cleanup(v);for(Room r:rooms.values())if(r.instance!=null)InstanceManager.getInstance().destroyInstance(r.instance.getId());}
}
