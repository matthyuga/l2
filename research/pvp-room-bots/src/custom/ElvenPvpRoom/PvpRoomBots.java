package custom.ElvenPvpRoom;

import java.util.*;
import java.lang.reflect.Constructor;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import custom.ElvenPvpRoom.RoundState.*;

/** Opt-in GM laboratory. Only creates and operates its own transient players. */
public final class PvpRoomBots {
 public enum Profile { MAYORIA, EMPATE, PARCIAL, ABSTENCION, DUPLICADO, TARDIO }
 private static final Logger LOG=Logger.getLogger(PvpRoomBots.class.getName());
 private static final int MAX_PER_ROOM=12;
 private static int serial;
 private final PvpRoundRooms host;
 private final Map<Mode,Group> groups=new EnumMap<>(Mode.class);
 private static final class Bot {
  final Player player;final int slot;long round,deadSince;boolean attempted;long lateRound;
  Bot(Player player,int slot){this.player=player;this.slot=slot;}
 }
 private static final class Group {
  final Mode mode;final Profile profile;final List<Bot> bots=new ArrayList<>();long nextTick;int votesAccepted,votesRejected,abstentions,combatOrders,respawns;
  Group(Mode mode,Profile profile){this.mode=mode;this.profile=profile;}
 }
 PvpRoomBots(PvpRoundRooms host){this.host=host;}
 public void command(Player gm,String[] args){
  if(gm==null||!gm.isGM())return;
  try{
   if(args.length==0||args[0].equalsIgnoreCase("estado")){gm.sendMessage(status());return;}
   if(args[0].equalsIgnoreCase("parar")){
    if(args.length<2||args[1].equalsIgnoreCase("todas"))stopAll();else stop(mode(args[1]));
    gm.sendMessage("Bots retirados. "+status());return;
   }
   if(args[0].equalsIgnoreCase("iniciar")&&args.length>=3){
    Mode mode=mode(args[1]);int count=Integer.parseInt(args[2]);Profile profile=args.length>3?Profile.valueOf(args[3].toUpperCase(Locale.ROOT)):Profile.PARCIAL;
    start(mode,count,profile);gm.sendMessage("Bots iniciados. "+status());return;
   }
   gm.sendMessage(".salas bots iniciar libre|equipos|tres|arena 2..12 mayoria|empate|parcial|abstencion|duplicado|tardio; parar [modo|todas]; estado");
  }catch(Exception e){gm.sendMessage("Bots: "+e.getMessage());}
 }
 private static Mode mode(String name){return switch(name.toLowerCase(Locale.ROOT)){case "libre"->Mode.FREE;case "equipos"->Mode.TWO_TEAMS;case "tres"->Mode.THREE_TEAMS;case "arena"->Mode.ARENA;default->throw new IllegalArgumentException("Modo desconocido");};}
 void start(Mode mode,int count,Profile profile)throws Exception{
  if(count<2||count>MAX_PER_ROOM)throw new IllegalArgumentException("Usar de 2 a 12 bots por sala");
  if(groups.containsKey(mode))throw new IllegalStateException("Primero para los bots de esa sala");
  Group g=new Group(mode,profile);groups.put(mode,g);
  try{
   for(int i=0;i<count;i++){
    Player p=create();Bot bot=new Bot(p,i);g.bots.add(bot);
    if(!host.botJoin(p,mode))throw new IllegalStateException("Entrada del bot rechazada");
    if(World.getPlayer(p.getObjectId())!=p)throw new IllegalStateException("Bot no registrado en el mundo");
   }
   LOG.info("PvpRoomBots: started "+count+" bots in "+mode+" profile="+profile);
  }catch(Exception e){stop(mode);throw e;}
 }
 private Player create()throws Exception{
  var template=PlayerTemplateData.getInstance().getTemplate(0);
  Constructor<Player> ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,PlayerAppearance.class);ctor.setAccessible(true);
  Player p=ctor.newInstance(template,"hellgames-room-bots",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));
  p.setName("HGTest"+(++serial));p.setTitle("BOT DE PRUEBA");p.setLabControlled(true);p.setAccessLevel(0);p.setOnlineStatus(true,false);p.setEnteredWorld();
  p.getStat().setLevel((byte)80);p.setDead(false);p.setInvul(false);p.setSpawnProtection(false);p.fullRestore();
  // Do not spawn in Giran: normal room entry performs the first spawn in its own instance.
  p.setXYZInvisible(45150,52100,-2792);World.addObject(p);return p;
 }
 private void verifyOwned(Bot bot){
  if(!bot.player.isLabControlled()||bot.player.getClient()!=null||!bot.player.getAccountName().equals("hellgames-room-bots"))throw new IllegalStateException("Bot ownership invariant failed");
 }
 void tick(long now){
  for(Group g:new ArrayList<>(groups.values())){
   if(now<g.nextTick)continue;g.nextTick=now+500_000_000L;
   try{for(Bot bot:g.bots){verifyOwned(bot);Player p=bot.player;
    // A bot unexpectedly outside its room is retired instead of roaming another instance.
    if(!host.botParticipants(g.mode).contains(p)||!p.isOnline()){stop(g.mode);break;}
    vote(g,bot,now);
    if(p.isDead()){
     if(bot.deadSince==0)bot.deadSince=now;
     if(now-bot.deadSince>=10_000_000_000L){p.doRevive();p.fullRestore();host.botReposition(p);bot.deadSince=0;g.respawns++;}
     continue;
    }
    bot.deadSince=0;
    Player target=null;double nearest=Double.MAX_VALUE;
    // Default combat is bot vs bot, including when a real player enters to observe.
    for(Bot other:g.bots){Player q=other.player;
     if(q==p||q.getClient()!=null||!q.isLabControlled()||q.isDead()||!q.isOnline()||q.getInstanceId()!=p.getInstanceId()||RoomCombatRules.decision(p,q)!=1)continue;
     double dx=p.getX()-(double)q.getX(),dy=p.getY()-(double)q.getY(),distance=dx*dx+dy*dy;
     if(distance<nearest){nearest=distance;target=q;}
    }
    if(target!=null&&!p.isCastingNow()&&!p.isTeleporting()){
     p.setTarget(target);p.getAI().setIntentionAttack(target);g.combatOrders++;
    }
   }}catch(Exception e){LOG.warning("PvpRoomBots: stopping "+g.mode+": "+e);stop(g.mode);}
  }
 }
 private void vote(Group g,Bot bot,long now){
  RoundState state=host.botState(g.mode);long round=state.generation();
  if(bot.round!=round){bot.round=round;bot.attempted=false;}
  List<String> maps=state.maps();int current=maps.indexOf(state.current());String first=maps.get((current+1)%maps.size()),second=maps.get((current+2)%maps.size());
  if(g.profile==Profile.TARDIO){
   if(state.phase()==Phase.RESULT&&bot.lateRound!=round){bot.lateRound=round;cast(g,bot,round,first);}
   return;
  }
  if(state.phase()!=Phase.VOTING||bot.attempted)return;
  // With the current 60s ballot these staggered delays are 2..41 seconds after opening.
  long remaining=state.voteRemaining(now);long delay=2_000_000_000L+(bot.slot*7%40)*1_000_000_000L;
  if(remaining>Math.max(0,host.botVoteDuration()-delay))return;
  bot.attempted=true;
  if(g.profile==Profile.ABSTENCION || g.profile==Profile.PARCIAL&&bot.slot%2==1 || g.profile==Profile.EMPATE&&g.bots.size()%2==1&&bot.slot==g.bots.size()-1){g.abstentions++;return;}
  String map=g.profile==Profile.EMPATE&&bot.slot%2==1?second:first;
  cast(g,bot,round,map);if(g.profile==Profile.DUPLICADO)cast(g,bot,round,second);
 }
 private void cast(Group g,Bot bot,long round,String map){
  RoundState state=host.botState(g.mode);int before=state.tally().values().stream().mapToInt(Integer::intValue).sum();
  // Same command handler as a player's HTML vote; no direct writes to tally or winner.
  host.onCommand("salas",bot.player,"votar "+round+" "+map);
  int after=state.tally().values().stream().mapToInt(Integer::intValue).sum();
  if(after==before+1)g.votesAccepted++;else g.votesRejected++;
 }
 void stop(Mode mode){
  Group g=groups.remove(mode);if(g==null)return;
  for(Bot bot:g.bots){verifyOwned(bot);Player p=bot.player;host.botForget(p);p.abortAttack();p.abortCast();p.stopMove(null);p.stopAllEffects();
   if(!p.isOnline())p.setOnlineStatus(true,false);p.deleteMe();p.setOnlineStatus(false,false);
  }
  LOG.info("PvpRoomBots: stopped "+mode);
 }
 void stopAll(){for(Mode mode:new ArrayList<>(groups.keySet()))stop(mode);}
 public String status(){
  if(groups.isEmpty())return "Bots apagados.";
  StringJoiner result=new StringJoiner(" | ");for(Group g:groups.values())result.add(g.mode+": "+g.bots.size()+" "+g.profile+" votos="+g.votesAccepted+" rechazados="+g.votesRejected+" abstenciones="+g.abstentions+" ataques="+g.combatOrders+" respawns="+g.respawns);
  return result.toString();
 }
}
