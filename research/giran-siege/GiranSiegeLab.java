package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.entity.item.enums.*;
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;

/** Manual siege laboratory: native Giran siege; real Player squads; no automatic start. */
public class GiranSiegeLab extends Script implements IVoicedCommandHandler {
 private static final Logger LOG=Logger.getLogger(GiranSiegeLab.class.getName());
 static GiranSiegeLab instance;
 static final int[][] COMMON={{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
 static final int[][] PHYS={{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},{271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
 static final int[][] MAGIC={{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},{273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};
 private final List<Squad> squads=new ArrayList<>();private final List<Spawn> bosses=new ArrayList<>();
 private Player controller;private Location origin;private boolean ownsSiege,claimed;private long started;private String mode="seguir";
 private GiranSiegeLab(){
  instance=this;VoicedCommandHandler.getInstance().registerHandler(this);ThreadPool.scheduleAtFixedRate(this::tick,1000,500);
  if(Boolean.getBoolean("lab.giran.install"))ThreadPool.schedule(this::installWhenReady,30000);
  LOG.info("GiranSiegeLab: .giran / .siegegiran manual panel; prepare/start/follow/assault/end. Boss special AI pending; native base combat only.");
 }
 private void installWhenReady(){if(!NormalNpcRoster.isReady()){ThreadPool.schedule(this::installWhenReady,3000);return;}synchronized(this){try{GiranRoster.install();}catch(Exception e){LOG.log(Level.SEVERE,"GIRAN_ROSTER INSTALL FAILED",e);}}}
 public String[] getCommandList(){return new String[]{"giran","siegegiran"};}
 public boolean onCommand(String cmd,Player p,String args){
  if(!p.isGM()||!p.getName().equals("Hellkevin")){p.sendMessage("Giran: laboratorio de Hellkevin GM.");return true;}
  synchronized(this){try{
   String action=args==null||args.isBlank()?"panel":args.trim().toLowerCase(Locale.ROOT);
   switch(action){
    case "panel","estado" -> {}
    case "preparar" -> prepare(p);
    case "iniciar" -> start(p);
    case "seguir","asalto","retirada" -> {checkController(p);mode=action;for(Squad s:squads)for(Pilot a:s.members)if(a.bot){a.p.abortAttack();a.p.getAI().setIntentionIdle();}p.sendMessage("Orden escuadrones: "+action);}
    case "registrar" -> {if(controller!=null)throw new IllegalStateException("Finaliza la preparacion primero.");GiranRoster.registerAll();}
    case "cancelar","finalizar" -> {checkController(p);finish(true);}
    default -> throw new IllegalArgumentException("Usa .giran");
   }
   show(p);
  }catch(Exception e){p.sendMessage("Giran: "+e.getMessage());LOG.log(Level.WARNING,"Giran command "+args,e);}}
  return true;
 }
 static Location camp(int team,int slot){int x=110700+slot*65,y=144450+team*260;int z=GeoEngine.getInstance().getHeight(x,y,-2800);return new Location(x,y,z);}
 static void move(Player p,Location to){
  if(p.getWorldRegion()==null){p.setInstanceId(0);p.spawnMe(to.getX(),to.getY(),to.getZ());p.revalidateZone(true);}
  else{p.teleToLocation(to.getX(),to.getY(),to.getZ(),0,0,false);if(p.getClient()==null)p.onTeleported();}
 }
 private void prepare(Player p)throws Exception{
  if(controller!=null)throw new IllegalStateException("Ya hay escuadrones preparados.");
  var castle=CastleManager.getInstance().getCastleById(3);
  if(!NormalNpcRoster.isReady())throw new IllegalStateException("Espera el roster completo.");
  if(castle.getOwnerId()!=0||castle.getSiege().isInProgress())throw new IllegalStateException("Prueba NPC requiere Giran sin propietario ni asedio activo.");
  if(p.isInParty()||p.isDead()||p.isInCombat()||p.isCastingNow()||p.getInstanceId()!=0)throw new IllegalStateException("Sal de party, combate y evento antes de preparar.");
  if(p.isInvul())throw new IllegalStateException("Desactiva invulnerabilidad GM para probar el asedio.");
  if(p.getClan()!=ClanTable.getInstance().getClanByName("Hellsing")||!p.isClanLeader())throw new IllegalStateException("Debes ser lider de Hellsing.");
  GiranRoster.registerAll();
  if(!SoloArenaGauntlet.tryClaimPilot())throw new IllegalStateException("Finaliza .arena/.ia/.agite primero.");claimed=true;controller=p;origin=new Location(p);started=System.currentTimeMillis();mode="seguir";
  try{
   // Load and validate all19 before making parties or teleporting the operator.
   for(int t=0;t<5;t++){
    Squad squad=new Squad(t);squads.add(squad);var clan=ClanTable.getInstance().getClanByName(GiranRoster.CLANS[t]);
    for(int i=0;i<4;i++){
     Player actor=t==0&&i==0?p:GiranRoster.load(GiranRoster.NAMES[t][i]);Pilot a=new Pilot(actor,squad,i,GiranRoster.ROLES[t][i],actor!=p);squad.members.add(a);
     if(actor.getClan()!=clan||actor.isInParty())throw new IllegalStateException("Clan/party incorrectos: "+actor.getName());
    }
   }
   for(Squad s:squads){Player leader=s.members.get(0).p;Party party=new Party(leader,PartyDistributionType.FINDERS_KEEPERS);leader.setParty(party);for(int i=1;i<4;i++)s.members.get(i).p.joinParty(party);
    for(Pilot a:s.members){if(a.bot){a.p.setLabControlled(true);a.p.setOnlineStatus(true,true);a.p.setEnteredWorld();a.p.setDead(false);reset(a);a.p.setInvul(true);a.p.setTitle("Escuadron "+GiranRoster.CLANS[s.id]);}move(a.p,camp(s.id,a.slot));}
   }
   p.sendMessage("Cinco escuadrones de4 preparados. NPC, puertas y Ares/Nyx se activan con Iniciar. No se inicio el siege.");
  }catch(Exception e){finish(false);throw e;}
 }
 private void checkController(Player p){if(controller!=p)throw new IllegalStateException("Usa Preparar primero.");}
 private void start(Player p)throws Exception{
  checkController(p);var castle=CastleManager.getInstance().getCastleById(3);if(ownsSiege)throw new IllegalStateException("Asedio ya iniciado.");
  if(castle.getOwnerId()!=0||castle.getSiege().isInProgress())throw new IllegalStateException("Cambio el estado del castillo.");
  castle.getSiege().startSiege();ownsSiege=castle.getSiege().isInProgress();if(!ownsSiege)throw new IllegalStateException("El motor no inicio el siege.");
  try{
   for(Squad s:squads)for(Pilot a:s.members){move(a.p,camp(s.id,a.slot));if(a.bot)a.p.setInvul(false);}
   for(int[] data:new int[][]{{903200,114174,145058,-2751},{903201,117700,145150,-2544}}){
    Spawn spawn=new Spawn(data[0]);spawn.setXYZ(data[1],data[2],GeoEngine.getInstance().getHeight(data[1],data[2],data[3]));spawn.setHeading(32768);spawn.setRespawnDelay(0);spawn.stopRespawn();Npc n=spawn.doSpawn(false);bosses.add(spawn);n.setRunning();
   }
   mode="seguir";started=System.currentTimeMillis();p.sendMessage("Siege nativo de Giran iniciado (120 minutos). Escuadrones en modo Seguir; Asalto habilita objetivos automaticos. Ares/Nyx usan combate base, IAespecial pendiente.");LOG.info("GIRAN_SIEGE STARTED by "+p.getObjectId()+";5parties20players,2guardians,NPCowner");
  }catch(Exception e){finish(true);throw e;}
 }
 static void reset(Pilot a){
  Player p=a.p;if(p.isDead())p.doRevive();p.abortAttack();p.abortCast();p.stopAllEffects();
  for(int[][] set:new int[][][]{COMMON,a.magic()?MAGIC:PHYS})for(int[] b:set)SkillData.getInstance().getSkill(b[0],b[1]).applyEffects(p,p);
  p.fullRestore();p.setRunning();a.summonAttempts=0;
  for(int[] stock:new int[][]{{5592,50},{728,30},{1539,30},{1467,4000},{3952,4000},{1345,4000}})supply(p,stock[0],stock[1]);
  for(var skill:p.getAllSkills())if(!skill.isPassive()&&skill.getItemConsumeId()>0)supply(p,skill.getItemConsumeId(),Math.min(2000,Math.max(100,skill.getItemConsumeCount()*5)));
 }
 static void supply(Player p,int item,int count){long have=p.getInventory().getInventoryItemCount(item,-1);if(have<count)p.getInventory().addItem(ItemProcessType.NONE,item,(int)(count-have),p,null);}
 private void tick(){synchronized(this){if(controller==null)return;try{
  if(controller.getClient()==null||!controller.isOnline()){finish(true);return;}
  var siege=CastleManager.getInstance().getCastleById(3).getSiege();
  if(ownsSiege&&!siege.isInProgress()){controller.sendMessage("El siege finalizo. Se conserva el resultado nativo del castillo.");ownsSiege=false;finish(false);return;}
  if(controller.getInstanceId()!=0||System.currentTimeMillis()-started>(ownsSiege?7300000:600000)){finish(true);return;}
  if(!ownsSiege)return;
  for(Squad s:squads)for(Pilot a:s.members)if(a.bot){
   if(a.p.isDead()){
    if(a.p.isReviveRequested()){a.p.reviveAnswer(1);continue;}
    if(a.deadAt==0)a.deadAt=System.currentTimeMillis();
    if(System.currentTimeMillis()-a.deadAt>=30000){reset(a);move(a.p,camp(s.id,a.slot));a.deadAt=0;}continue;
   }
   a.deadAt=0;SiegeSquadBrain.act(a,controller,mode);
  }
 }catch(Exception e){LOG.log(Level.SEVERE,"Giran squad tick",e);finish(true);}}}
 private void finish(boolean endSiege){
  Player op=controller;controller=null;
  for(Squad s:squads)for(Pilot a:s.members)try{a.p.abortAttack();a.p.abortCast();if(a.p.hasSummon()){a.p.getSummon().abortAttack();a.p.getSummon().abortCast();if(a.bot)a.p.getSummon().unSummon(a.p);else a.p.getSummon().setFollowStatus(true);}if(a.p.isInParty())a.p.leaveParty();}catch(Exception e){LOG.log(Level.SEVERE,"Pilot party cleanup "+a.p.getName(),e);}
  if(endSiege&&ownsSiege){try{CastleManager.getInstance().getCastleById(3).getSiege().endSiege();}catch(Exception e){LOG.log(Level.SEVERE,"Native end siege",e);}}
  for(Spawn spawn:bosses)try{spawn.stopRespawn();if(spawn.getLastSpawn()!=null)spawn.getLastSpawn().deleteMe();}catch(Exception e){LOG.log(Level.SEVERE,"Boss cleanup",e);}bosses.clear();
  for(Squad s:squads)for(Pilot a:s.members)if(a.bot)try{a.p.setInvul(a.originalInvul);a.p.setTitle(a.originalTitle);if(a.p.isDead())a.p.doRevive();move(a.p,a.origin);a.p.storeMe();}catch(Exception e){LOG.log(Level.SEVERE,"Pilot restore "+a.p.getName(),e);}finally{try{GiranRoster.dispose(a.p);}catch(Exception e){LOG.log(Level.SEVERE,"Pilot disposal "+a.p.getName(),e);}}
  squads.clear();ownsSiege=false;if(claimed){SoloArenaGauntlet.releasePilot();claimed=false;}
  if(op!=null&&origin!=null&&op.getClient()!=null&&op.isOnline())move(op,origin);origin=null;
  LOG.info("GIRAN_SIEGE SQUADS_CLEANED; castle ownership result preserved; no boss spawns remain");
 }
 private void show(Player p){
  var c=CastleManager.getInstance().getCastleById(3);StringBuilder h=new StringBuilder("<html><body><center><font color=LEVEL>Giran - Laboratorio de Siege</font><br>Defensa inicial: NPC + Ares/Nyx<br>IA especial de bosses: pendiente<br>Duracion nativa: 120 minutos<br><br>");
  h.append("Estado: ").append(c.getSiege().isInProgress()?"ASALTO ACTIVO":controller!=null?"ESCUADRONES LISTOS":"PREPARADO EN DATOS").append("<br>Orden: ").append(mode).append("<br>");
  for(int t=0;t<5;t++){h.append("<font color=LEVEL>").append(GiranRoster.CLANS[t]).append("</font>: ").append(String.join(", ",GiranRoster.NAMES[t])).append("<br>");}
  h.append("<br>Guardias, puertas, torres y captura nativos.<br>Solo lideres usan Seal of Ruler sobre artefacto.<br>No hay conquista automatica de los pilotos.<br><br>");
  if(controller==null)h.append(button("Reunir escuadrones","preparar")).append(button("Registrar atacantes","registrar"));
  else{if(!ownsSiege)h.append(button("Iniciar siege","iniciar"));h.append(button("Seguir y asistir","seguir")).append(button("Asalto automatico","asalto")).append(button("Retirada al campamento","retirada")).append(button(ownsSiege?"Finalizar siege":"Cancelar preparacion","finalizar"));}
  h.append(button("Actualizar","estado")).append("</center></body></html>");NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(h.toString());p.sendPacket(packet);
 }
 private static String button(String label,String action){return "<button value=\""+label+"\" action=\"bypass -h voice .giran "+action+"\" width=270 height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
 static final class Squad{final int id;final List<Pilot> members=new ArrayList<>();Squad(int id){this.id=id;}}
 static final class Pilot{
  final Player p;final Squad squad;final int slot;final String role;final boolean bot;final Location origin;final String originalTitle;final boolean originalInvul;
  final Map<Integer,Long> reuse=new HashMap<>();long deadAt,lastMove,pendingSummon;int summonAttempts;
  Pilot(Player p,Squad squad,int slot,String role,boolean bot){this.p=p;this.squad=squad;this.slot=slot;this.role=role;this.bot=bot;origin=new Location(p);originalTitle=p.getTitle();originalInvul=p.isInvul();}
  boolean magic(){return Set.of("MAGE","HEALER","SUPPORT").contains(role);}
 }
 public static void main(String[] args){new GiranSiegeLab();}
}
