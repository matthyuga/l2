package custom.ClanLab;

import java.sql.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.data.xml.SkillTreeData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.clan.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;

/** Opt-in real clan persistence/effect test; reserved offline owner and disposable clan only. */
public class ClanLabVerification extends Script
{
    private static final Logger LOG=Logger.getLogger(ClanLabVerification.class.getName());
    private static final int TEST_CLAN=-19010;
    private int checks;
    public ClanLabVerification(){if(Boolean.getBoolean("lab.clanlab.verify"))ThreadPool.schedule(this::verify,30000);}
    private void check(boolean b,String label){if(!b)throw new IllegalStateException(label);checks++;}
    private interface Attempt{void run()throws Exception;}
    private void rejects(Attempt fn,String label)throws Exception{boolean rejected=false;try{fn.run();}catch(IllegalArgumentException e){rejected=true;}check(rejected,label);}
    private long scalar(String sql)throws Exception{try(Connection c=DatabaseFactory.getConnection();Statement q=c.createStatement();var r=q.executeQuery(sql)){check(r.next(),"Scalar query returns row");return r.getLong(1);}}
    private Map<Integer,String> liveClanSnapshot(){Map<Integer,String> result=new TreeMap<>();for(Clan c:ClanTable.getInstance().getClans())result.put(c.getId(),c.getName()+":"+c.getLevel()+":"+c.getReputationScore()+":"+c.getCrestId()+":"+c.getAllyCrestId()+":"+c.getSkills().size());return result;}
    private void verify(){
        Player p=null;Clan fixture=null,oldClan=null;String title=null;int pledge=0;Map<Integer,Skill> original=new HashMap<>();boolean created=false;
        Map<Integer,String> realClans=liveClanSnapshot();
        try{
            int id;
            try(Connection db=DatabaseFactory.getConnection();PreparedStatement q=db.prepareStatement("SELECT charId,online,clanid FROM characters WHERE char_name='AmberOwnerProbe' AND account_name='ambercontracttest'")){try(var rs=q.executeQuery()){check(rs.next()&&rs.getInt(2)==0&&rs.getInt(3)==0,"Reserved offline clanless probe");id=rs.getInt(1);check(World.getPlayer(id)==null,"Probe not loaded in World");}}
            p=Player.load(id);check(p!=null,"Probe loads");p.fullRestore();final Player actor=p;
            oldClan=p.getClan();title=p.getTitle();pledge=p.getPledgeClass();for(Skill s:p.getAllSkills())original.put(s.getId(),s);
            long rep=scalar("SELECT SUM(reputation_score) FROM clan_data");
            check(scalar("SELECT COUNT(*) FROM clan_data WHERE clan_id="+TEST_CLAN)==0,"Disposable clan ID unused");
            try(Connection db=DatabaseFactory.getConnection();PreparedStatement q=db.prepareStatement("INSERT INTO clan_data(clan_id,clan_name,clan_level,leader_id) VALUES(?,?,?,?)")){q.setInt(1,TEST_CLAN);q.setString(2,"ClanLabProbe");q.setInt(3,4);q.setInt(4,id);q.executeUpdate();created=true;}
            fixture=new Clan(TEST_CLAN,"ClanLabProbe");fixture.setLeader(new ClanMember(fixture,p));p.setClan(fixture);fixture.changeLevel(4);ClanLab.refresh(fixture,p);final Clan c=fixture;
            check(p.isClanLeader()&&!ClanLab.authorized(p),"Named probe denied personal GM panel even if leader");
            var handler=org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().getHandler("clanlab");check(handler instanceof ClanLab,"Panel registered in native voice handler");handler.onCommand("clanlab",p,"level 8");check(c.getLevel()==4,"Unauthorized command cannot mutate");
            rejects(()->ClanLab.upgrade(actor,c,0,4,5),"Forged clan ID rejected");
            rejects(()->ClanLab.upgrade(actor,c,TEST_CLAN,3,5),"Stale level rejected");
            rejects(()->ClanLab.upgrade(actor,c,TEST_CLAN,4,9),"Above Interlude max rejected");
            rejects(()->ClanLab.upgrade(actor,c,TEST_CLAN,4,3),"Downgrade rejected");
            rejects(()->ClanLab.learn(actor,c,TEST_CLAN,370,0,1),"Level5 skill locked at clan4");
            check(ClanLab.catalog(0).size()==22,"Native22skill catalog");
            check(ClanLab.catalog(0).stream().mapToInt(s->s.getSkillLevel()).sum()==64,"Catalog exposes all64native skill ranks, not only first rank");
            for(int f=0;f<=8;f++){
                check(ClanLab.skills(p,f,0).getBytes(java.nio.charset.StandardCharsets.UTF_8).length<8000,"Paginated HTML fits native limit "+f);
                check(ClanLab.skills(p,f,99).contains("bypass -h voice .clanlab"),"Final page has functional voice bypass "+f);
            }
            check(ClanLab.levels(p).contains("level 8")&&ClanLab.home(p).contains("skills 0 0"),"Both panel routes exposed");
            double hp=p.getMaxHp();
            for(int level=5;level<=8;level++){
                int previous=c.getLevel();ClanLab.upgrade(p,c,TEST_CLAN,previous,level);
                check(scalar("SELECT clan_level FROM clan_data WHERE clan_id="+TEST_CLAN)==level,"Level persisted "+level);
                check(p.getPledgeClass()==ClanMember.calculatePledgeClass(p),"Member rank refreshed after level "+level);
                if(level==5){
                    rejects(()->ClanLab.learn(actor,c,TEST_CLAN,370,0,3),"Cannot skip skill ranks");
                    rejects(()->ClanLab.learn(actor,c,TEST_CLAN,378,0,1),"Future level8 skill rejected");
                    rejects(()->ClanLab.learn(actor,c,TEST_CLAN,999999,0,1),"Unknown skill rejected");
                }
                for(var row:ClanLab.catalog(level)){
                    for(int next=1;next<=row.getSkillLevel();next++){
                        int old=ClanLab.known(c,row.getSkillId());ClanLab.learn(p,c,TEST_CLAN,row.getSkillId(),old,next);
                        check(ClanLab.known(c,row.getSkillId())==next,"Clan learns sequentially "+row.getSkillId()+":"+next);
                        check(scalar("SELECT skill_level FROM clan_skills WHERE clan_id="+TEST_CLAN+" AND sub_pledge_id=-2 AND skill_id="+row.getSkillId())==next,"Skill stored "+row.getSkillId()+":"+next);
                        boolean eligible=row.getSocialClass()==null||p.getPledgeClass()+1>=row.getSocialClass().ordinal();
                        check(p.getKnownSkill(row.getSkillId())!=null==eligible,"Leader receives effect iff rank eligible "+row.getSkillId());
                    }
                }
                check(c.getReputationScore()==0,"Free GM learning keeps reputation "+level);
            }
            check(p.getMaxHp()>hp,"Passive clan HP bonus changes real stats");
            check(c.getSkills().size()==22,"All native clan skills learned at final level8");
            check(c.getAllSkills().stream().mapToInt(Skill::getLevel).sum()==64,"All22skills reach native maximum rank");
            rejects(()->ClanLab.learn(actor,c,TEST_CLAN,370,0,1),"Stale skill level rejected");
            rejects(()->ClanLab.learn(actor,c,TEST_CLAN,370,3,4),"Skill above native max rejected");
            rejects(()->ClanLab.upgrade(actor,c,TEST_CLAN,8,8),"Repeated level does not mutate");
            // Reload a standalone Clan from DB: runtime caches alone cannot make this pass.
            Clan restored=new Clan(TEST_CLAN);check(restored.getLevel()==8&&restored.getSkills().size()==22,"Reload preserves level and22skills");
            for(Skill s:c.getAllSkills())check(restored.getSkills().get(s.getId()).getLevel()==s.getLevel(),"Reload skill rank "+s.getId());
            check(liveClanSnapshot().equals(realClans),"Real Hellsing/Holly/Sacred runtime untouched");
            check(scalar("SELECT SUM(reputation_score) FROM clan_data WHERE clan_id<>"+TEST_CLAN)==rep,"Real clan reputation unchanged");
            LOG.info("ClanLabVerification SUCCESS: "+checks+" checks; real upgrade/skill persistence and reload,22skills, rank gating/passive stats, invalid requests, HTML routes/limits; real clans untouched.");
        }catch(Exception e){LOG.log(Level.SEVERE,"ClanLabVerification FAILED after "+checks+" checks",e);}
        finally{
            if(p!=null){
                if(fixture!=null)fixture.removeSkillEffects(p);
                for(Skill s:new ArrayList<>(p.getAllSkills()))if(!original.containsKey(s.getId()))p.removeSkill(s.getId(),false);
                for(Skill s:original.values())p.addSkill(s,false);
                p.setClan(oldClan);if(title!=null)p.setTitle(title);p.setPledgeClass(pledge);p.setOnlineStatus(true,false);p.deleteMe();
            }
            if(created)try(Connection db=DatabaseFactory.getConnection();Statement q=db.createStatement()){q.executeUpdate("DELETE FROM clan_skills WHERE clan_id="+TEST_CLAN);q.executeUpdate("DELETE FROM clan_data WHERE clan_id="+TEST_CLAN);}catch(Exception e){LOG.log(Level.SEVERE,"Disposable clan cleanup failed",e);}
        }
    }
    public static void main(String[] args){new ClanLabVerification();}
}
