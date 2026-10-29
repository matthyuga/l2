package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import custom.ElvenPvpRoom.RoundState.*;
import custom.ElvenPvpRoom.PvpRoomBots.Profile;
public class SiegeBotCheck {
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 static String fingerprint()throws Exception{
  StringBuilder b=new StringBuilder();
  try(var c=DatabaseFactory.getConnection()){
   String ids="SELECT char_id FROM lab_normal_npc_profiles UNION SELECT char_id FROM lab_real_human_pilots";
   for(String sql:new String[]{"SELECT charId,char_name,classid,base_class,clanid,race FROM characters WHERE charId IN ("+ids+") ORDER BY charId","SELECT * FROM character_subclasses WHERE charId IN ("+ids+") ORDER BY charId,class_index","SELECT * FROM character_skills WHERE charId IN ("+ids+") ORDER BY charId,class_index,skill_id","SELECT owner_id,item_id,SUM(count),MAX(enchant_level),loc FROM items WHERE owner_id IN ("+ids+") GROUP BY owner_id,item_id,loc ORDER BY owner_id,item_id,loc"}){
    try(var q=c.createStatement();var rs=q.executeQuery(sql)){while(rs.next()){for(int i=1;i<=rs.getMetaData().getColumnCount();i++)b.append(rs.getString(i)).append('|');b.append('\n');}}
   }
  }
  return b.toString();
 }
 public static void run(String directory)throws Exception{
  Path dir=Path.of(directory);StringBuilder b=new StringBuilder();PvpRoundRooms host=null;String before=fingerprint();
  try{
   var config=new PvpRoomConfig(Path.of("E:/l2-local/server/game/config/Custom/PvpRooms.properties"));
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object prior=loading.get(null);check(prior==null,"Script loader busy");
   try{loading.set(null,dir.resolve("src/custom/ElvenPvpRoom/SiegeBotCheck.java"));host=new PvpRoundRooms(config,System::nanoTime,0,false);}finally{loading.set(null,prior);}
   PvpRoomBots bots=(PvpRoomBots)field(host,"bots");bots.start(Mode.TWO_TEAMS,6,Profile.PARCIAL);
   List<Player> players=host.botParticipants(Mode.TWO_TEAMS);Set<Integer> classes=new HashSet<>(),parties=new HashSet<>();int clan=0,solo=0;
   Map<Integer,int[]> origins=new HashMap<>();Set<Integer> moved=new HashSet<>();
   for(Player p:players){check(p.getClient()==null&&p.getSubClasses().size()==3&&p.getAllSkills().size()>80&&p.getActiveWeaponItem()!=null,"Incomplete siege profile");classes.add(p.getPlayerClass().getId());if(p.getClan()!=null)clan++;else solo++;if(p.isInParty())parties.add(p.getParty().getLeaderObjectId());origins.put(p.getObjectId(),new int[]{p.getX(),p.getY()});b.append(p.getName()).append(" class=").append(p.getPlayerClass()).append(" clan=").append(p.getClanId()).append(" party=").append(p.isInParty()?p.getParty().getLeaderObjectId():0).append(" subs=").append(p.getSubClasses().size()).append(" skills=").append(p.getAllSkills().size()).append('\n');}
   check(clan>0&&solo>0&&classes.size()>=3&&parties.size()>=2,"Roster/party diversity missing");
   for(Player p:players)if(p.isInParty())for(Player mate:p.getParty().getMembers())check(host.botState(Mode.TWO_TEAMS).team(p.getObjectId())==host.botState(Mode.TWO_TEAMS).team(mate.getObjectId()),"Mixed team party");
   for(Player p:World.getPlayers())if(p.getClient()!=null)check(p.getInstanceId()!=players.get(0).getInstanceId(),"Test shares user instance");
   for(int tick=0;tick<30;tick++){host.tick();Thread.sleep(500);for(Player p:players){int[] o=origins.get(p.getObjectId());if(Math.hypot(p.getX()-o[0],p.getY()-o[1])>100)moved.add(p.getObjectId());}}
   check(moved.size()>=4,"Actual movement insufficient: "+moved.size()+"/6");
   b.append("PASS native siege roster, three subclasses/skills/weapons, clan and clanless actors, class variety, random same-team parties; ").append(moved.size()).append("/6 bots moved >100 units under native movement.\n");
   bots.stopAll();check(players.stream().noneMatch(p->World.getPlayer(p.getObjectId())!=null),"Borrowed profile remained online");
   check(before.equals(fingerprint()),"Original class/subclass/skills/clan/equipment quantities changed");
   b.append("PASS borrowed actors released; original class, subclasses, learned skills, clans and equipment quantities preserved.\n");
  }catch(Throwable t){b.append("FAIL ").append(t).append('\n');throw t;}
  finally{if(host!=null)host.closeForVerification();Files.writeString(dir.resolve("verification.txt"),b);}
 }
}

