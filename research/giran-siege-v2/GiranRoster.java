package custom.GiranSiegeLab;

import java.nio.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.data.sql.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.clan.Clan;
import org.l2jmobius.gameserver.entity.clan.enums.CrestType;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.managers.SiegeManager;

/** Persistent roster setup; live squads are created separately and only on request. */
public final class GiranRoster {
 public static final String[] CLANS={"Hellsing","Holly","Sacred","Fury","Waves"};
 public static final String[][] NAMES={{"Hellkevin","Vaelkor","Noctis","Selene"},{"Kaelis","Gorvak","Myrentha","Ignara"},{"Caelan","Arden","Zhurak","Morvain"},{"Riven","Eryndor","Korvash","Aelira"},{"Brunna","Lethiel","Sylira","Velith"}};
 public static final String[][] ROLES={{"MAGE","DAGGER","SUPPORT","HEALER"},{"ARCHER","FRONT","HEALER","MAGE"},{"ARCHER","FRONT","SUPPORT","MAGE"},{"DAGGER","ARCHER","SUPPORT","HEALER"},{"FRONT","HEALER","MAGE","MAGE"}};
 private static final Logger LOG=Logger.getLogger(GiranRoster.class.getName());
 private GiranRoster(){}
 static Player load(String name)throws Exception{
  if(name.equals("Hellkevin"))throw new IllegalArgumentException("Never load the user as an AI pilot.");
  int id;
  try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT c.charId,c.online,c.account_name,p.recipe_version FROM characters c JOIN lab_normal_npc_profiles p ON c.charId=p.char_id WHERE c.char_name=?")){
   q.setString(1,"Arena"+name);try(var rs=q.executeQuery()){
    if(!rs.next()||rs.getInt(2)!=0||!Set.of("telemetryarena1","telemetryarena2","telemetryarena3").contains(rs.getString(3))||!rs.getString(4).equals("normal-pvp-s4-hybrid-v2"))throw new IllegalStateException("Perfil ocupado o distinto: "+name);id=rs.getInt(1);
   }
  }
  if(World.getPlayer(id)!=null)throw new IllegalStateException("Perfil ya cargado: "+name);
  Player p=Player.load(id);if(p==null)throw new IllegalStateException("No se carga "+name);
  if(p.getClient()!=null||p.getLevel()!=80||p.getClassIndex()!=0||p.getSubClasses().size()!=3){dispose(p);throw new IllegalStateException("Perfil modificado: "+name);}
  if(p.getClan()!=null){var member=p.getClan().getClanMember(p.getObjectId());if(member==null){dispose(p);throw new IllegalStateException("Missing native clan member");}member.setPlayer(p);p.getClan().addSkillEffects(p);if(p.isClanLeader()&&p.getClan().getLevel()>=SiegeManager.getInstance().getSiegeClanMinLevel())SiegeManager.getInstance().addSiegeSkills(p);}
  return p;
 }
 static void dispose(Player p){if(p==null)return;Clan c=p.getClan();try{p.deleteMe();}finally{p.setOnlineStatus(false,true);p.setLabControlled(false);if(c!=null&&c.getClanMember(p.getObjectId())!=null)c.getClanMember(p.getObjectId()).setPlayer(null);}}
 static byte[] crest(String key,String kind)throws Exception{
  byte[] data=Files.readAllBytes(Path.of("data/lab/giran/"+key+"-"+kind+".dds"));ByteBuffer h=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);int w=kind.equals("clan")?16:8;
  if(data.length!=128+w*8||h.getInt(0)!=0x20534444||h.getInt(12)!=16||h.getInt(16)!=w||h.getInt(84)!=0x31545844)throw new IllegalStateException("Invalid power-of-two crest");return data;
 }
 static void install()throws Exception{
  var castle=CastleManager.getInstance().getCastleById(3);if(castle==null||castle.getOwnerId()!=0||castle.getSiege().isInProgress())throw new IllegalStateException("Giran debe estar sin propietario y sin asedio activo.");
  List<Player> loaded=new ArrayList<>();
  try{
   // Check all members and assets before creating anything persistent.
   for(int team=3;team<5;team++){
    if(ClanTable.getInstance().getClanByName(CLANS[team])!=null)throw new IllegalStateException("Clan nuevo ya existe; no se repite instalacion: "+CLANS[team]);
    crest(CLANS[team].toLowerCase(Locale.ROOT),"clan");crest(CLANS[team].toLowerCase(Locale.ROOT),"ally");
    for(String name:NAMES[team]){Player p=load(name);loaded.add(p);if(p.getClan()!=null)throw new IllegalStateException("Perfil ya tiene otro clan: "+name);}
   }
   for(int team=3;team<5;team++){
    List<Player> squad=loaded.subList((team-3)*4,(team-2)*4);Player leader=squad.get(0);Clan clan=ClanTable.getInstance().createClan(leader,CLANS[team]);if(clan==null)throw new IllegalStateException("No se creo clan.");
    // Store leader immediately: the native database cleaner requires a real membership.
    leader.storeMe();for(int i=1;i<4;i++){clan.addClanMember(squad.get(i));squad.get(i).storeMe();}
    clan.changeLevel(5);clan.setAllyId(clan.getId());clan.setAllyName(CLANS[team]);clan.updateClanInDB();String key=CLANS[team].toLowerCase(Locale.ROOT);
    var cc=CrestTable.getInstance().createCrest(crest(key,"clan"),CrestType.PLEDGE);var ac=CrestTable.getInstance().createCrest(crest(key,"ally"),CrestType.ALLY);
    if(cc==null||ac==null)throw new IllegalStateException("No se guardo crest.");clan.changeClanCrest(cc.getId());clan.changeAllyCrest(ac.getId(),true);
    LOG.info("GIRAN_ROSTER CREATED "+CLANS[team]+" clan="+clan.getId()+" leader="+leader.getName()+" members=4");
   }
  }finally{for(Player p:loaded)dispose(p);}
  registerAll();LOG.info("GIRAN_ROSTER INSTALLED: 5 clans x4,19 reserved pilots + Hellkevin,10 valid crests, all attackers Giran NPC; siege NOT started.");
 }
 static void registerAll()throws Exception{
  var castle=CastleManager.getInstance().getCastleById(3);var siege=castle.getSiege();if(castle.getOwnerId()!=0||siege.isInProgress())throw new IllegalStateException("Prueba requiere Giran NPC sin asedio activo.");
  for(int t=0;t<5;t++){
   Clan c=ClanTable.getInstance().getClanByName(CLANS[t]);if(c==null||c.getLevel()<4||c.getCastleId()!=0)throw new IllegalStateException("Clan no elegible: "+CLANS[t]);
   if(siege.checkIsDefender(c)||siege.checkIsDefenderWaiting(c))throw new IllegalStateException("Clan registrado de defensor: "+CLANS[t]);
   if(siege.checkIsAttacker(c))continue;
   Player proxy=load(NAMES[t][t==0?2:0]);try{if(proxy.getClan()!=c)throw new IllegalStateException("Membership mismatch");siege.registerAttacker(proxy,true);if(!siege.checkIsAttacker(c))throw new IllegalStateException("Registro fallido");}finally{dispose(proxy);}
  }
 }
}
