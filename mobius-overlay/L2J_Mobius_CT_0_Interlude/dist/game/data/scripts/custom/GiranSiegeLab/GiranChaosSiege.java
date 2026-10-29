package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.clan.Clan;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Two native siege sides. Random party agendas do not change character recipes or PvP legality. */
final class GiranChaosSiege {
 static final Logger LOG=Logger.getLogger(GiranChaosSiege.class.getName());
 static GiranChaosSiege instance;
 static final String CLAN="Raiders";
 static final String[][] ATTACK={
  {"Darion","Valerian","Seraphine","Mazhura","Nysera"},
  {"Malrik","Lucien","Nerys"},{"Darius","Thalion","Elowen"},
  {"Draven","Saevra"},{"Zareth","Faelith"},{"Dagna","Borin"},
  {"Rhogar"},{"Urkan"},{"Veyron"}
 };
 static final String[][] ROLES={
  {"FRONT","FRONT","SUPPORT","SUPPORT","FRONT"},
  {"FRONT","SUMMONER","HEALER"},{"FRONT","FRONT","SUPPORT_PHYS"},
  {"FRONT","HEALER"},{"SUMMONER","SUMMONER"},{"FRONT","FRONT"},
  {"FRONT"},{"FRONT"},{"ARCHER"}
 };
 final List<Squad> squads=new ArrayList<>();
 final Map<Squad,GiranChaosAgenda.Route> routes=new HashMap<>();
 final GiranChaosAgenda agenda=new GiranChaosAgenda();
 final GiranChaosMachinery machines=new GiranChaosMachinery();
 Player controller;Location humanOrigin;boolean claimed,ownsSiege;long began;int initialOwner;
 String orders="defensa";
 GiranChaosSiege(){instance=this;ThreadPool.scheduleAtFixedRate(this::tick,1500,500);if(Boolean.getBoolean("lab.giran.chaos.verify"))ThreadPool.schedule(()->new GiranChaosVerification(this).whenReady(),55000);LOG.info("GIRAN_CHAOS V9 available: 20 Raiders without crests,19 defenders + operator,parties5/3/3/2/2/2 and3solo;native machinery");}
 static List<String> attackers(){return Arrays.stream(ATTACK).flatMap(Arrays::stream).toList();}
 static boolean machineCarrier(Player p){return instance!=null&&instance.member(p)&&(p.getName().equals("ArenaDagna")||p.getName().equals("ArenaBorin"));}
 boolean member(Player p){return squads.stream().flatMap(s->s.members.stream()).anyMatch(a->a.p==p);}
 synchronized boolean command(Player human,String args){
  try{
   String action=args==null||args.isBlank()?"panel":args.trim().toLowerCase(Locale.ROOT);
   if(action.startsWith("caos"))action=action.substring(4).trim();
   switch(action){
    case "","panel","estado" -> {}
    case "preparar" -> prepare(human);
    case "registrar" -> {if(!squads.isEmpty())throw new IllegalStateException("Finaliza la preparacion primero.");setupSides();}
    case "iniciar" -> {require(human);start();}
    case "seguir","asalto","defensa","retirada" -> {require(human);orders=action.equals("asalto")?"defensa":action;human.sendMessage("Orden defensora: "+orders+". Los20 atacantes conservan sus agendas.");}
    case "traer" -> {require(human);int n=0;for(Squad s:squads)for(Pilot a:s.members)if(GiranOrders.summonHere(a,human))n++;human.sendMessage("Defensores aliados traidos: "+n);}
    case "revivir" -> GiranGuardians.instance.revive(human);
    case "cancelar","finalizar" -> {require(human);finish(true);}
    case "diagnostico" -> {for(Squad s:squads)LOG.info("GIRAN_CHAOS_GROUP "+s.id+" "+s.objective+" "+s.members.stream().map(a->a.p.getName()+":"+(int)a.p.getCurrentHp()).toList());}
    default -> throw new IllegalArgumentException("Usa .giran");
   }
  }catch(Exception e){human.sendMessage("Giran caos: "+e.getMessage());LOG.log(Level.WARNING,"Giran chaos command",e);}
  show(human);return true;
 }
 private void require(Player p){if(controller!=p)throw new IllegalStateException("Usa Preparar primero.");}
 /** Idempotent setup limited to the twenty reserved additions; existing clans/crests stay intact. */
 static void setupSides()throws Exception{
  var castle=GiranRules.castle();Clan owner=ClanTable.getInstance().getClanByName("Hellsing");
  if(owner==null||castle.getOwnerId()!=owner.getId()||castle.getSiege().isInProgress())throw new IllegalStateException("Este escenario requiere Giran de Hellsing y sin siege activo.");
  List<Player> loaded=new ArrayList<>();Clan clan=ClanTable.getInstance().getClanByName(CLAN);
  try{
   for(String name:attackers()){Player p=GiranRoster.load(name);loaded.add(p);if(p.getClan()!=null&&p.getClan()!=clan)throw new IllegalStateException("Clan ajeno en "+name);}
   if(clan!=null&&(clan.getLeaderId()!=loaded.get(0).getObjectId()||clan.getCrestId()!=0||clan.getAllyId()!=0||clan.getAllyCrestId()!=0||clan.getMembers().stream().anyMatch(m->!loaded.stream().anyMatch(p->p.getObjectId()==m.getObjectId()))))throw new IllegalStateException("Clan Raiders ajeno o editado; no se sobrescribe.");
   if(clan==null){clan=ClanTable.getInstance().createClan(loaded.get(0),CLAN);if(clan==null)throw new IllegalStateException("No se creo Raiders");clan.changeLevel(5);loaded.get(0).storeMe();}
   for(Player p:loaded)if(p.getClan()==null){clan.addClanMember(p);p.storeMe();}
   clan.updateClanInDB();if(clan.getMembersCount()!=20)throw new IllegalStateException("Raiders requiere exactamente20 perfiles");
  }finally{for(Player p:loaded)GiranRoster.dispose(p);}
  var siege=castle.getSiege();
  for(int t=1;t<5;t++){
   Clan c=ClanTable.getInstance().getClanByName(GiranRoster.CLANS[t]);if(c==null||c.getCastleId()!=0)throw new IllegalStateException("Clan defensor no elegible");
   if(siege.checkIsDefender(c))continue;
   siege.removeSiegeClan(c.getId());Player proxy=GiranRoster.load(GiranRoster.NAMES[t][0]);
   try{siege.registerDefender(proxy,true);siege.approveSiegeDefenderClan(c.getId());if(!siege.checkIsDefender(c))throw new IllegalStateException("Registro defensor fallido");}finally{GiranRoster.dispose(proxy);}
  }
  siege.removeSiegeClan(owner.getId());
  Clan raid=ClanTable.getInstance().getClanByName(CLAN);
  if(!siege.checkIsAttacker(raid)){siege.removeSiegeClan(raid.getId());Player p=GiranRoster.load("Darion");try{siege.registerAttacker(p,true);if(!siege.checkIsAttacker(raid))throw new IllegalStateException("Registro atacante fallido");}finally{GiranRoster.dispose(p);}}
  LOG.info("GIRAN_CHAOS SIDES_READY:5 defender clans,20 Raiders;crest=0,ally=0;castle owner preserved");
 }
 private void prepare(Player human)throws Exception{
  if(!NormalNpcRoster.isReady())throw new IllegalStateException("Espera el roster39 completo.");
  if(!squads.isEmpty())throw new IllegalStateException("Ya hay grupos preparados.");
  if(human.isInParty()||human.isDead()||human.isInCombat()||human.isCastingNow()||human.getInstanceId()!=0||human.isInvul())throw new IllegalStateException("Sal de party/combate/evento y desactiva invulnerabilidad GM.");
  if(human.getClan()!=ClanTable.getInstance().getClanByName("Hellsing")||!human.isClanLeader())throw new IllegalStateException("Debes ser lider de Hellsing.");
  setupSides();prepareTeams(human);human.sendMessage("19 bots defensores + vos;20 atacantes en6 parties y3solos. Todavia no se inicio.");
 }
 void prepareTeams(Player human)throws Exception{
  if(!squads.isEmpty())throw new IllegalStateException("Hay grupos activos.");
  if(!SoloArenaGauntlet.tryClaimPilot())throw new IllegalStateException("Finaliza .arena/.ia/.agite/otro siege primero.");claimed=true;
  controller=human;humanOrigin=human==null?null:new Location(human);began=System.currentTimeMillis();orders="defensa";
  try{
   for(int t=0;t<5;t++){
    Squad s=new Squad(t);squads.add(s);
    for(int i=0;i<4;i++){if(t==0&&i==0&&human==null)continue;Player p=t==0&&i==0?human:GiranRoster.load(GiranRoster.NAMES[t][i]);s.members.add(new Pilot(p,s,i,GiranRoster.ROLES[t][i],p!=human));}
   }
   for(int t=0;t<ATTACK.length;t++){
    Squad s=new Squad(t+5);squads.add(s);for(int i=0;i<ATTACK[t].length;i++){Player p=GiranRoster.load(ATTACK[t][i]);s.members.add(new Pilot(p,s,i,ROLES[t][i],true));}
   }
   for(Squad s:squads){
    if(s.members.stream().anyMatch(a->a.p.isInParty()))throw new IllegalStateException("Perfil con party previa");
    if(s.members.size()>1){Player lead=s.members.get(0).p;Party party=new Party(lead,PartyDistributionType.FINDERS_KEEPERS);lead.setParty(party);for(int i=1;i<s.members.size();i++)s.members.get(i).p.joinParty(party);}
    for(Pilot a:s.members){if(a.bot){a.p.setLabControlled(true);a.p.setOnlineStatus(true,true);a.p.setEnteredWorld();GiranSiegeLab.reset(a);a.p.setInvul(true);a.p.setTitle(s.id<5?"Defensor / "+GiranRoster.CLANS[s.id]:"Atacante / "+(s.members.size()==1?"solo":"grupo"));}a.nextHeadquarters=Long.MAX_VALUE;GiranSiegeLab.move(a.p,spawnPoint(a.p,s.id,a.slot));}
    s.leader=SiegeAgenda.captain(s);routes.put(s,new GiranChaosAgenda.Route(s));
   }
  }catch(Exception e){finish(false);throw e;}
 }
 static Location attackerCamp(int group,int slot){int lane=(group-5)%3;int x=110950+((group-5)/3)*200,y=144250+lane*600; if(group==10){x=111700;y=145350;}return SiegeAgenda.safe(x+(slot%2)*95,y+(slot/2)*95,-2832);}
 static final int[][] POSTS={{116650,145095,-2560},{114174,145058,-2648},{115700,145035,-2560},{116650,145095,-2560},{117400,145064,-2640}};
 Location spawnPoint(Player p,int group,int slot){if(group>=5)return attackerCamp(group,slot);int[] xyz=POSTS[group];return SiegeAgenda.safe(xyz[0]+(slot%2)*70,xyz[1]+(slot/2)*70,xyz[2]);}
 void start(){
  var c=GiranRules.castle();if(ownsSiege||c.getSiege().isInProgress())throw new IllegalStateException("Asedio ya activo");initialOwner=c.getOwnerId();
  c.getSiege().startSiege();ownsSiege=c.getSiege().isInProgress();if(!ownsSiege)throw new IllegalStateException("El motor no inicio el siege");began=System.currentTimeMillis();
  for(Squad s:squads){s.launchAt=began+(s.id<5?0:java.util.concurrent.ThreadLocalRandom.current().nextInt(0,18000));for(Pilot a:s.members){GiranSiegeLab.move(a.p,spawnPoint(a.p,s.id,a.slot));if(a.bot)a.p.setInvul(false);a.p.revalidateZone(true);}}
  GiranGuardians.instance.ensure();machines.deploy(squads);LOG.info("GIRAN_CHAOS START:20 attackers,19 defenders+human,6 mixed parties,3 solos,random schedules,native sides;owner="+initialOwner);
 }
 void battleTick(){
  long now=System.currentTimeMillis();
  for(Squad s:squads){agenda.update(s,routes.get(s),controller,orders,now);for(Pilot a:s.members)if(a.bot){
   GiranSiegeLab.restoreExperience(a);
   if(a.p.isDead()){if(a.deadAt==0)a.deadAt=now;if(a.p.isReviveRequested()){a.p.reviveAnswer(1);GiranSiegeLab.recoverRevival(a);}else if(now-a.deadAt>=30000){GiranSiegeLab.reset(a);GiranSiegeLab.move(a.p,spawnPoint(a.p,s.id,a.slot));a.deadAt=0;}continue;}
   GiranSiegeLab.recoverRevival(a);GiranSiegeLab.restoreExperience(a);SiegeSquadBrain.act(a,controller,orders);
  }}
  machines.act(squads);
 }
 private synchronized void tick(){if(controller==null||squads.isEmpty())return;try{
  if(controller.getClient()==null||!controller.isOnline()||controller.getInstanceId()!=0||System.currentTimeMillis()-began>(ownsSiege?7300000:600000)){finish(true);return;}
  if(!ownsSiege)return;
  if(!GiranRules.castle().getSiege().isInProgress()){finish(false);return;}
  if(GiranRules.castle().getOwnerId()!=initialOwner){controller.sendMessage("Giran conquistado. Se conserva el resultado nativo.");finish(true);return;}
  battleTick();
 }catch(Exception e){LOG.log(Level.SEVERE,"Giran chaos tick",e);finish(true);}}
 void finish(boolean endSiege){
  Player human=controller;controller=null;
  for(Squad s:squads)for(Pilot a:s.members)try{a.p.abortAttack();a.p.abortCast();if(a.p.hasSummon()){if(a.bot)a.p.getSummon().unSummon(a.p);else{a.p.getSummon().abortAttack();a.p.getSummon().abortCast();a.p.getSummon().setFollowStatus(true);}}if(a.p.isInParty())a.p.leaveParty();}catch(Exception e){LOG.log(Level.SEVERE,"Chaos party cleanup",e);}
  try{if(endSiege&&ownsSiege&&GiranRules.castle().getSiege().isInProgress())GiranRules.castle().getSiege().endSiege();}catch(Exception e){LOG.log(Level.SEVERE,"Chaos native siege end",e);}
  for(Squad s:squads)for(Pilot a:s.members)if(a.bot)try{if(a.p.isDead())a.p.doRevive();GiranSiegeLab.restoreExperience(a);a.p.setTitle(a.originalTitle);a.p.setInvul(a.originalInvul);GiranSiegeLab.move(a.p,a.origin);a.p.storeMe();}catch(Exception e){LOG.log(Level.SEVERE,"Chaos restore",e);}finally{GiranRoster.dispose(a.p);}
  squads.clear();routes.clear();machines.clear();ownsSiege=false;SiegeTactics.reset();if(claimed){SoloArenaGauntlet.releasePilot();claimed=false;}
  if(human!=null&&humanOrigin!=null&&human.getClient()!=null&&human.isOnline())GiranSiegeLab.move(human,humanOrigin);humanOrigin=null;
  LOG.info("GIRAN_CHAOS CLEANED:all pilots offline,parties/summons removed;guardian patrol and castle result preserved");
 }
 private void show(Player p){
  StringBuilder h=new StringBuilder("<html><body><center><font color=LEVEL>Giran: defensa contra20 atacantes</font><br>Defensores: Hellsing,Holly,Sacred,Fury,Waves<br>Ares y Nyx: guardianes en patrulla<br>Raiders: sin logo; bando atacante nativo<br>Grupos5/3/3/2/2/2 y3solos<br>Golem + Wild Hog Cannon: maquinaria del lab<br>");
  h.append("Estado: ").append(ownsSiege?"ACTIVO":squads.isEmpty()?"LISTO PARA PREPARAR":"GRUPOS PREPARADOS").append("<br>Orden defensora: ").append(orders).append("<br>");
  for(int i=0;i<ATTACK.length;i++){h.append("<font color=LEVEL>").append(ATTACK[i].length==1?"Solo":"Grupo"+(i+1)).append("</font>: ").append(String.join(",",ATTACK[i])).append("<br>");if(squads.size()>i+5)h.append(squads.get(i+5).objective).append("<br>");}
  if(squads.isEmpty())h.append(button("Preparar defensa y atacantes","preparar"));else{if(!ownsSiege)h.append(button("Iniciar siege","iniciar"));h.append(button("Defensores: patrullar y combatir","defensa")).append(button("Defensores: seguirme","seguir")).append(button("Traer defensores vivos aqui","traer")).append(button("Defensores: retirada","retirada")).append(button(ownsSiege?"Finalizar siege":"Cancelar preparacion","finalizar"));}
  h.append(button("Revivir guardianes","revivir")).append(button("Actualizar","estado")).append("</center></body></html>");NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(h.toString());p.sendPacket(packet);
 }
 private static String button(String label,String action){return "<button value=\""+label+"\" action=\"bypass -h voice .giran "+action+"\" width=270 height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
}
