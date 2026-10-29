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
 private final SiegeAgenda agenda=new SiegeAgenda();
 private Player controller;private Location origin;private boolean ownsSiege,claimed;private long started;private String mode="seguir";private int lastOwner;
 private GiranSiegeLab(){
  instance=this;VoicedCommandHandler.getInstance().registerHandler(this);ThreadPool.scheduleAtFixedRate(this::tick,1000,500);
  if(Boolean.getBoolean("lab.giran.install"))ThreadPool.schedule(this::installWhenReady,30000);
  LOG.info("GiranSiegeLab V8: threat-aware parties and temporary attacker ceasefires; Ares/Nyx patrol; throne shop/buffer.");
 }
 private void installWhenReady(){if(!NormalNpcRoster.isReady()){ThreadPool.schedule(this::installWhenReady,3000);return;}synchronized(this){try{GiranRoster.install();}catch(Exception e){LOG.log(Level.SEVERE,"GIRAN_ROSTER INSTALL FAILED",e);}}}
 public String[] getCommandList(){return new String[]{"giran","siegegiran"};}
 public boolean onCommand(String cmd,Player p,String args){
  if(!p.isGM()||!p.getName().equals("Hellkevin")){p.sendMessage("Giran: laboratorio de Hellkevin GM.");return true;}
  synchronized(this){try{
   String action=args==null||args.isBlank()?"panel":args.trim().toLowerCase(Locale.ROOT);
   switch(action){
    case "panel","estado" -> {}
    case "diagnostico" -> {p.sendMessage("Posicion servidor: "+p.getX()+","+p.getY()+","+p.getZ()+"; cliente: "+p.getClientX()+","+p.getClientY()+","+p.getClientZ());LOG.info("GIRAN_POSITION "+p.getName()+" server="+p.getX()+","+p.getY()+","+p.getZ()+" client="+p.getClientX()+","+p.getClientY()+","+p.getClientZ()+" last="+p.getLastServerPosition()+" ai="+p.getAI().getIntention()+" moving="+p.isMoving());for(Squad s:squads)for(Pilot a:s.members)LOG.info("GIRAN_PILOT "+a.p.getName()+" role="+a.role+" mode="+GiranOrders.effective(s,p,mode)+" xyz="+a.p.getX()+","+a.p.getY()+","+a.p.getZ()+" ai="+a.p.getAI().getIntention()+" focus="+(s.focus==null?"none":s.focus.getObjectId())+" HP="+(int)a.p.getCurrentHp()+" MP="+(int)a.p.getCurrentMp());}
    case "revivir" -> GiranGuardians.instance.revive(p);
    case "preparar" -> prepare(p);
    case "iniciar" -> start(p);
    case "seguir","asalto","retirada" -> {checkController(p);mode=action;int changed=0;for(Squad s:squads)for(Pilot a:s.members)if(a.bot&&GiranOrders.allied(a.p,p)){a.p.abortAttack();a.p.getAI().setIntentionIdle();changed++;}p.sendMessage("Orden para "+changed+" pilotos aliados: "+action+". Rivales conservan sus agendas.");}
    case "traer" -> {checkController(p);if(p.isDead()||p.isTeleporting())throw new IllegalStateException("Espera a estar vivo y en posicion.");int moved=0;for(Squad s:squads)for(Pilot a:s.members)if(GiranOrders.summonHere(a,p))moved++;mode="seguir";p.sendMessage("Traidos "+moved+" pilotos aliados vivos a tu posicion. No se movieron rivales ni guardianes.");}
    case "registrar" -> {if(controller!=null)throw new IllegalStateException("Finaliza la preparacion primero.");GiranRoster.registerAll();}
    case "cancelar","finalizar" -> {checkController(p);finish(true);}
    default -> throw new IllegalArgumentException("Usa .giran");
   }
   show(p);
  }catch(Exception e){p.sendMessage("Giran: "+e.getMessage());LOG.log(Level.WARNING,"Giran command "+args,e);}}
  return true;
 }
 // Four separate bases in Giran's native western HQ territory; all approaches stay outside the closed gate.
 static final int[][] CAMPS={{110700,145050},{110000,142000},{110000,146200},{111200,144100},{111700,147500}};
 static Location camp(int team,int slot){int[] base=CAMPS[team];return SiegeAgenda.safe(base[0]+(slot%2)*70,base[1]+(slot/2)*70,-2832);}
 static Location spawnPoint(Player p,int team,int slot){
  if(p.getClanId()==GiranRules.castle().getOwnerId()){var room=GiranRules.castle().getResidenceZone().getSpawnLoc();return SiegeAgenda.safe(room.getX()+slot*40,room.getY(),room.getZ());}
  var flags=GiranRules.castle().getSiege().getFlag(p.getClan());if(flags!=null)for(Npc flag:flags)if(!flag.isDead()&&flag.isSpawned())return SiegeAgenda.safe(flag.getX()+(slot%2)*70,flag.getY()+(slot/2)*70,flag.getZ()-50);
  return camp(team,slot);
 }
 static void move(Player p,Location to){
  if(p.getWorldRegion()==null){p.setInstanceId(0);p.spawnMe(to.getX(),to.getY(),to.getZ());p.revalidateZone(true);}
  else{p.teleToLocation(to.getX(),to.getY(),to.getZ(),0,0,false);if(p.getClient()==null)p.onTeleported();}
 }
 private void prepare(Player p)throws Exception{
  if(controller!=null)throw new IllegalStateException("Ya hay escuadrones preparados.");
  var castle=CastleManager.getInstance().getCastleById(3);
  if(!NormalNpcRoster.isReady())throw new IllegalStateException("Espera el roster completo.");
  if(castle.getSiege().isInProgress())throw new IllegalStateException("Finaliza el asedio activo primero.");
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
    for(Pilot a:s.members){if(a.bot){a.p.setLabControlled(true);a.p.setOnlineStatus(true,true);a.p.setEnteredWorld();a.p.setDead(false);reset(a);a.p.setInvul(true);a.p.setTitle("Escuadron "+GiranRoster.CLANS[s.id]);}move(a.p,spawnPoint(a.p,s.id,a.slot));}
   }
   p.sendMessage("Cinco escuadrones de4 preparados. NPC, puertas y Ares/Nyx se activan con Iniciar. No se inicio el siege.");
  }catch(Exception e){finish(false);throw e;}
 }
 private void checkController(Player p){if(controller!=p)throw new IllegalStateException("Usa Preparar primero.");}
 private void start(Player p)throws Exception{
  checkController(p);var castle=CastleManager.getInstance().getCastleById(3);if(ownsSiege)throw new IllegalStateException("Asedio ya iniciado.");
  if(castle.getSiege().isInProgress())throw new IllegalStateException("Cambio el estado del castillo.");
  castle.getSiege().startSiege();ownsSiege=castle.getSiege().isInProgress();if(!ownsSiege)throw new IllegalStateException("El motor no inicio el siege.");
  try{
   for(Squad s:squads)for(Pilot a:s.members){move(a.p,spawnPoint(a.p,s.id,a.slot));if(a.bot)a.p.setInvul(false);}
   if(castle.getOwnerId()!=0)castle.setFirstMidVictory(true); // Competitive laboratory: attackers also contest each other.
   GiranGuardians.instance.ensure();
   mode="asalto";lastOwner=castle.getOwnerId();agenda.clear();started=System.currentTimeMillis();for(Squad s:squads)s.launchAt=started+s.id*5000L;p.sendMessage("Giran iniciado: puerta exterior, patio, puerta interior, sala, pasillo y artefacto. Lider conquista; escolta protege. Seal of Ruler: 3 minutos,50MP,sin item.");LOG.info("GIRAN_SIEGE STARTED V6 owner="+lastOwner+"; staged assault, leader engraving and escort defense");
  }catch(Exception e){finish(true);throw e;}
 }
 static void reset(Pilot a){
  Player p=a.p;if(p.isDead())p.doRevive();p.abortAttack();p.abortCast();p.stopAllEffects();
  restoreExperience(a);
  rebuff(a);
  p.fullRestore();p.setRunning();a.summonAttempts=0;a.pursuit=null;a.pursuitOrigin=null;a.pursuitUntil=0;
  for(int[] stock:new int[][]{{5592,50},{728,30},{1539,30},{1467,4000},{3952,4000},{1345,4000},{2131,1200}})supply(p,stock[0],stock[1]);
  for(var skill:p.getAllSkills())if(!skill.isPassive()&&skill.getItemConsumeId()>0)supply(p,skill.getItemConsumeId(),Math.min(2000,Math.max(100,skill.getItemConsumeCount()*5)));
 }
 static void rebuff(Pilot a){for(int[][] set:new int[][][]{COMMON,a.magic()?MAGIC:PHYS})for(int[] b:set)SkillData.getInstance().getSkill(b[0],b[1]).applyEffects(a.p,a.p);}
 static void recoverRevival(Pilot a){if(!a.p.isDead()&&a.deadAt!=0){rebuff(a);a.deadAt=0;}}
 static void restoreExperience(Pilot a){if(a.bot){if(a.p.getExp()!=a.originalExp)a.p.getStat().setExp(a.originalExp);if(a.p.getLevel()!=80)a.p.getStat().setLevel((byte)80);if(a.p.getExpBeforeDeath()!=0)a.p.setExpBeforeDeath(0);}}
 static void supply(Player p,int item,int count){long have=p.getInventory().getInventoryItemCount(item,-1);if(have<count)p.getInventory().addItem(ItemProcessType.NONE,item,(int)(count-have),p,null);}
 private void tick(){synchronized(this){if(controller==null)return;try{
  if(controller.getClient()==null||!controller.isOnline()){finish(true);return;}
  var siege=CastleManager.getInstance().getCastleById(3).getSiege();
  if(ownsSiege&&!siege.isInProgress()){controller.sendMessage("El siege finalizo. Se conserva el resultado nativo del castillo.");ownsSiege=false;finish(false);return;}
  if(controller.getInstanceId()!=0||System.currentTimeMillis()-started>(ownsSiege?7300000:600000)){finish(true);return;}
  if(!ownsSiege)return;
  if(GiranRules.castle().getOwnerId()!=lastOwner){lastOwner=GiranRules.castle().getOwnerId();agenda.clear();for(Squad s:squads){s.step=0;s.seen=false;for(Pilot a:s.members)if(a.bot&&!GiranRules.castle().checkIfInZone(a.p.getX(),a.p.getY(),a.p.getZ()))move(a.p,spawnPoint(a.p,s.id,a.slot));}controller.sendMessage("Cambio el propietario de Giran. Guardianes y escuadrones cambian de bando.");}
  for(Squad s:squads){agenda.update(s,controller,mode);for(Pilot a:s.members)if(a.bot){
   restoreExperience(a);if(a.p.isDead()){
    if(a.deadAt==0)a.deadAt=System.currentTimeMillis();
    if(a.p.isReviveRequested()){a.p.reviveAnswer(1);recoverRevival(a);continue;}
    if(System.currentTimeMillis()-a.deadAt>=30000){reset(a);move(a.p,spawnPoint(a.p,s.id,a.slot));a.deadAt=0;}continue;
   }
   recoverRevival(a);restoreExperience(a);SiegeSquadBrain.act(a,controller,mode);
  }}
 }catch(Exception e){LOG.log(Level.SEVERE,"Giran squad tick",e);finish(true);}}}
 private void finish(boolean endSiege){
  Player op=controller;controller=null;
  for(Squad s:squads)for(Pilot a:s.members)try{a.p.abortAttack();a.p.abortCast();if(a.p.hasSummon()){a.p.getSummon().abortAttack();a.p.getSummon().abortCast();if(a.bot)a.p.getSummon().unSummon(a.p);else a.p.getSummon().setFollowStatus(true);}if(a.p.isInParty())a.p.leaveParty();}catch(Exception e){LOG.log(Level.SEVERE,"Pilot party cleanup "+a.p.getName(),e);}
  if(endSiege&&ownsSiege){try{CastleManager.getInstance().getCastleById(3).getSiege().endSiege();}catch(Exception e){LOG.log(Level.SEVERE,"Native end siege",e);}}
  for(Spawn spawn:bosses)try{spawn.stopRespawn();if(spawn.getLastSpawn()!=null)spawn.getLastSpawn().deleteMe();}catch(Exception e){LOG.log(Level.SEVERE,"Boss cleanup",e);}bosses.clear();
  for(Squad s:squads)for(Pilot a:s.members)if(a.bot)try{a.p.setInvul(a.originalInvul);a.p.setTitle(a.originalTitle);if(a.p.isDead())a.p.doRevive();restoreExperience(a);move(a.p,a.origin);a.p.storeMe();}catch(Exception e){LOG.log(Level.SEVERE,"Pilot restore "+a.p.getName(),e);}finally{try{GiranRoster.dispose(a.p);}catch(Exception e){LOG.log(Level.SEVERE,"Pilot disposal "+a.p.getName(),e);}}
  squads.clear();agenda.clear();ownsSiege=false;if(claimed){SoloArenaGauntlet.releasePilot();claimed=false;}
  if(op!=null&&origin!=null&&op.getClient()!=null&&op.isOnline())move(op,origin);origin=null;
  LOG.info("GIRAN_SIEGE SQUADS_CLEANED; castle ownership result preserved; persistent owner guardians retained");
 }
 private void show(Player p){
  var c=CastleManager.getInstance().getCastleById(3);StringBuilder h=new StringBuilder("<html><body><center><font color=LEVEL>Giran - Laboratorio de Siege</font><br>Ares: patrulla patio y acceso interior<br>Nyx: patrulla sala, pasillo y artefacto<br>Defienden al propietario actual<br>Duracion nativa: 120 minutos<br><br>");
  h.append("Ordenes solo para tus aliados actuales.<br>Bases separadas; rebuff al revivir.<br>Estado: ").append(c.getSiege().isInProgress()?"ASALTO ACTIVO":controller!=null?"ESCUADRONES LISTOS":"PREPARADO EN DATOS").append("<br>Orden aliados: ").append(mode).append("<br>");
  for(int t=0;t<5;t++){h.append("<font color=LEVEL>").append(GiranRoster.CLANS[t]).append("</font>: ").append(String.join(", ",GiranRoster.NAMES[t])).append("<br>");if(t<squads.size())h.append("Objetivo: ").append(squads.get(t).objective).append("<br>IA: ").append(SiegeTactics.status(squads.get(t))).append("<br>");}
  h.append("<br>Seal of Ruler:3minutos fijos,50MP,sin item.<br>Solo lider atacante, cerca y a altura del artefacto.<br>Lideres rivales pueden conquistar: 3 minutos. Se protegen o interrumpen al rival.<br><br>");
  if(controller==null)h.append(button("Reunir escuadrones","preparar")).append(button("Registrar atacantes","registrar"));
  else{if(!ownsSiege)h.append(button("Iniciar siege","iniciar"));h.append("<br><font color=LEVEL>Ordenes a pilotos aliados</font><br>").append(button("Aliados: seguirme","seguir")).append(button("Traer aliados vivos aqui","traer")).append(button("Aliados: objetivos del siege","asalto")).append(button("Aliados: retirada","retirada")).append("<br>Los rivales mantienen su estrategia.<br>").append(button(ownsSiege?"Finalizar siege":"Cancelar preparacion","finalizar"));}
  if(p.getClanId()==c.getOwnerId())h.append(button("Revivir guardianes caidos","revivir"));
  h.append(button("Actualizar","estado")).append(button("Diagnostico posicion e IA","diagnostico")).append("</center></body></html>");NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(h.toString());p.sendPacket(packet);
 }
 private static String button(String label,String action){return "<button value=\""+label+"\" action=\"bypass -h voice .giran "+action+"\" width=270 height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
 static final class Squad{final int id;final List<Pilot> members=new ArrayList<>();final SiegeTactics.State tactics=new SiegeTactics.State();Player leader;Creature focus;org.l2jmobius.gameserver.interfaces.ILocational goal;int step;boolean seen,conquest;String objective="Preparacion";long launchAt,rivalUntil,nextRivalSkirmish;Squad(int id){this.id=id;launchAt=System.currentTimeMillis()+id*5000L;}}
 static final class Pilot{
  final Player p;final Squad squad;final int slot;final String role;final boolean bot;final Location origin;final String originalTitle;final boolean originalInvul;
  final Map<Integer,Long> reuse=new HashMap<>();long deadAt,lastMove,pendingSummon,nextThink,lastProgress,nextHeadquarters,pursuitUntil;int summonAttempts,progressX,progressY;Location lastDestination,pursuitOrigin;Creature pursuit;final long originalExp;
  Pilot(Player p,Squad squad,int slot,String role,boolean bot){this.p=p;this.squad=squad;this.slot=slot;this.role=role;this.bot=bot;origin=new Location(p);originalTitle=p.getTitle();originalInvul=p.isInvul();originalExp=p.getExp();nextThink=System.currentTimeMillis()+java.util.concurrent.ThreadLocalRandom.current().nextInt(200,1200);lastProgress=System.currentTimeMillis();progressX=p.getX();progressY=p.getY();}
  boolean magic(){return Set.of("MAGE","HEALER","SUPPORT").contains(role);}
 }
 public static void main(String[] args){new GiranSiegeLab();}
}
