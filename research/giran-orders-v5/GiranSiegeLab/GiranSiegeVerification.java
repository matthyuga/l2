package custom.GiranSiegeLab;

import java.sql.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import custom.NormalNpcRoster.NormalNpcRoster;

/** One-shot live-data checks. Does not start a siege, load the human or change castle ownership. */
public class GiranSiegeVerification extends Script {
 private static final Logger LOG=Logger.getLogger(GiranSiegeVerification.class.getName());
 private int checks,waits;
 public GiranSiegeVerification(){if(Boolean.getBoolean("lab.giran.verify"))ThreadPool.schedule(this::whenReady,40000);}
 private void check(boolean ok,String why){if(!ok)throw new IllegalStateException(why);checks++;}
 private long scalar(String sql)throws Exception{try(Connection c=DatabaseFactory.getConnection();Statement s=c.createStatement();var rs=s.executeQuery(sql)){check(rs.next(),"SQL row");return rs.getLong(1);}}
 private void whenReady(){if(!NormalNpcRoster.isReady()||ClanTable.getInstance().getClanByName("Waves")==null){if(++waits<100)ThreadPool.schedule(this::whenReady,3000);else LOG.severe("GIRAN_VERIFY FAILED readiness timeout");return;}verify();}
 private void verify(){synchronized(GiranSiegeLab.instance){verifyLocked();}}
 private void verifyLocked(){List<Player> loaded=new ArrayList<>();try{
  var c=CastleManager.getInstance().getCastleById(3);check(c!=null&&c.getOwnerId()==0&&!c.getSiege().isInProgress(),"NPC castle, siege not started");
  check(c.getZone()!=null&&!c.getDoors().isEmpty()&&!c.getArtefacts().isEmpty(),"Native siege zone, doors and capture artifact");
  check(VoicedCommandHandler.getInstance().getHandler("giran") instanceof GiranSiegeLab,"Manual panel registered");
  check(scalar("SELECT COUNT(*) FROM castle_siege_guards WHERE castleId=3")==382,"382 configured guard positions");
  check(scalar("SELECT COUNT(*) FROM siege_clans WHERE castle_id=3")==5,"Five persistent siege attacker registrations");
  for(int t=0;t<5;t++){
   var clan=ClanTable.getInstance().getClanByName(GiranRoster.CLANS[t]);check(clan!=null&&clan.getLevel()>=4,"Eligible clan "+t);check(clan.getMembersCount()==4,"Four members "+t);check(c.getSiege().checkIsAttacker(clan),"Live attacker registration "+t);
   check(clan.getCrestId()>0&&clan.getAllyCrestId()>0,"Clan and alliance emblems "+t);
   var restored=new org.l2jmobius.gameserver.entity.clan.Clan(clan.getId());check(restored.getMembersCount()==4&&restored.getLeaderId()==clan.getLeaderId()&&restored.getCrestId()==clan.getCrestId()&&restored.getAllyCrestId()==clan.getAllyCrestId(),"Persistent native clan reload "+t);
   for(int i=0;i<4;i++){
    var loc=GiranSiegeLab.camp(t,i);check(GeoEngine.getInstance().hasGeo(loc.getX(),loc.getY()),"Real Giran geodata, not fallback height "+t+":"+i);check(loc.getZ()>-4000&&loc.getZ()<-1500&&c.checkIfInZone(loc.getX(),loc.getY(),loc.getZ()),"Camp floor/zone "+t+":"+i);
    if(t==0&&i==0)continue;
    Player p=GiranRoster.load(GiranRoster.NAMES[t][i]);loaded.add(p);check(p.getClan()==clan,"Native clan membership "+p.getName());check(p.getSubClasses().size()==3&&p.getClassIndex()==0&&p.getLevel()==80,"Main and three subclasses "+p.getName());
    check(!SiegeSquadBrain.allowed(p,p),"Player targets refused "+p.getName());check(!SiegeSquadBrain.allowed(c.getArtefacts().iterator().next(),p),"Capture artifact never autoattacked");
    for(var door:c.getDoors())check(!SiegeSquadBrain.allowed(door,p),"No AI door attack before native siege");
    check(p.getKnownSkill(246)!=null==p.isClanLeader(),"Native Seal of Ruler only clan leaders "+p.getName());
   }
  }
  // Construct actual native parties using only the reserved nineteen pilots.
  for(int t=0;t<5;t++){
   final var clan=ClanTable.getInstance().getClanByName(GiranRoster.CLANS[t]);var members=loaded.stream().filter(p->p.getClan()==clan).toList();Party party=new Party(members.get(0),PartyDistributionType.FINDERS_KEEPERS);members.get(0).setParty(party);
   for(int i=1;i<members.size();i++)members.get(i).joinParty(party);
   for(Player p:members)check(p.getParty()==party,"Native squad party "+p.getName());
  }
  for(String name:new String[]{"fury","waves"})for(String kind:new String[]{"clan","ally"})check(GiranRoster.crest(name,kind).length>128,"Power-of-two DDS "+name+kind);
  for(int[] ids:new int[][]{{900200,903200},{900201,903201}}){var src=NpcData.getInstance().getTemplate(ids[0]);var dst=NpcData.getInstance().getTemplate(ids[1]);check(dst!=null,"Isolated boss template");check(dst.getBaseHpMax()==src.getBaseHpMax()&&dst.getBasePAtk()==src.getBasePAtk()&&dst.getBaseMAtk()==src.getBaseMAtk(),"Base boss stats preserved, no new special AI claimed");check(dst.getExp()==0&&dst.getSP()==0,"No repeatable EXP/SP from lab bosses");}
  check(!c.getSiege().isInProgress()&&c.getOwnerId()==0,"No siege start or ownership mutation during verification");
  LOG.info("GIRAN_VERIFY PASS checks="+checks+";19 real Players,5 native squads,5 attacker clans,valid DDS,382 guards configured,isolated bosses; siege NOT started. Combat/pathfinding/balance await user trial.");
 }catch(Exception e){LOG.log(Level.SEVERE,"GIRAN_VERIFY FAILED checks="+checks,e);}finally{for(Player p:loaded){try{if(p.isInParty())p.leaveParty();GiranRoster.dispose(p);}catch(Exception e){LOG.log(Level.SEVERE,"Verification cleanup",e);}}}}
 public static void main(String[] args){new GiranSiegeVerification();}
}
