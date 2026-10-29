package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.entity.actor.holders.creature.TimeStamp;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.mechanics.skill.*;

/** Temporarily borrows only verified offline lab actors; never edits their builds or clan membership. */
public final class PvpSiegeRoster {
 private record Effect(Skill skill,long expires){}
 private record Saved(Location location,int instance,String title,double hp,double mp,double cp,long exp,int level,int pvps,int pks,int karma,List<Effect> effects,Map<Integer,TimeStamp> cooldowns,Map<Integer,Long> items){}
 private static final Map<Player,Saved> OWNED=new IdentityHashMap<>();
 private static final int[][] COMMON={{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
 private static final int[][] PHYS={{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1}};
 private static final int[][] MAGIC={{1085,3},{1059,3},{1078,6},{1303,2},{1355,1}};
 private static int cursor;
 public static synchronized Player acquire()throws Exception{
  Player prepared=PvpRoundSets.prepared();if(prepared!=null){if(!owned(prepared))throw new IllegalStateException("Prepared bot no longer owned");return prepared;}
  List<int[]> clan=new ArrayList<>(),solo=new ArrayList<>();
  try(var c=DatabaseFactory.getConnection();var q=c.createStatement();var rs=q.executeQuery("SELECT c.charId,c.clanid,c.classid FROM characters c WHERE c.online=0 AND c.account_name LIKE 'telemetry%' AND c.char_name<>'Hellkevin' AND (EXISTS(SELECT 1 FROM lab_normal_npc_profiles p WHERE p.char_id=c.charId AND p.recipe_version='normal-pvp-s4-hybrid-v2') OR EXISTS(SELECT 1 FROM lab_real_human_pilots p WHERE p.char_id=c.charId AND p.recipe_version IN ('human-pilots-v3-hybrid-third','human-pilots-v2-active-slot'))) ORDER BY c.classid,c.charId")){
   while(rs.next())if(World.getPlayer(rs.getInt(1))==null)(rs.getInt(2)==0?solo:clan).add(new int[]{rs.getInt(1),rs.getInt(3)});
  }
  Collections.shuffle(clan);Collections.shuffle(solo);List<int[]> candidates=new ArrayList<>();
  boolean wantSolo=cursor++%3==2;
  candidates.addAll(wantSolo&&!solo.isEmpty()?solo:clan);candidates.addAll(wantSolo&&!solo.isEmpty()?clan:solo);
  for(int[] candidate:candidates){
   int id=candidate[0];
   try(var c=DatabaseFactory.getConnection();var q=c.prepareStatement("UPDATE characters SET online=2 WHERE charId=? AND online=0")){q.setInt(1,id);if(q.executeUpdate()!=1)continue;}
   Player p=null;
   try{
    if(World.getPlayer(id)!=null)throw new IllegalStateException("Perfil ocupado durante la reserva");
    p=Player.load(id);
    if(p==null||p.getClient()!=null||p.getAccessLevel().getLevel()!=0||p.getLevel()!=80||p.getSubClasses().size()!=3)throw new IllegalStateException("Perfil incompleto/ocupado: "+id);
    List<Effect> effects=new ArrayList<>();for(BuffInfo buff:p.getEffectList().getEffects())if(!buff.getSkill().isPassive())effects.add(new Effect(buff.getSkill(),System.currentTimeMillis()+Math.max(1,buff.getTime())*1000L));
    Map<Integer,Long> items=new HashMap<>();for(var item:p.getInventory().getItems())items.merge(item.getId(),(long)item.getCount(),Long::sum);
    Saved snapshot=new Saved(new Location(p),p.getInstanceId(),p.getTitle(),p.getCurrentHp(),p.getCurrentMp(),p.getCurrentCp(),p.getExp(),p.getLevel(),p.getPvpKills(),p.getPkKills(),p.getKarma(),effects,new HashMap<>(p.getSkillReuseTimeStamps()),items);
    OWNED.put(p,snapshot);p.setLabControlled(true);p.setOnlineStatus(true,true);p.setEnteredWorld();p.setDead(false);p.setInvul(false);p.setSpawnProtection(false);p.setRunning();
    if(p.getClan()!=null){var member=p.getClan().getClanMember(id);if(member==null)throw new IllegalStateException("Clan sin miembro nativo");member.setPlayer(p);p.getClan().addSkillEffects(p);}
    p.setInstanceId(0);p.setXYZInvisible(45150,52100,-2792);World.addObject(p);prepare(p);return p;
   }catch(Exception error){
    if(p!=null&&OWNED.containsKey(p))release(p);else if(p!=null){p.setOnlineStatus(true,false);p.deleteMe();}
    try(var c=DatabaseFactory.getConnection();var q=c.prepareStatement("UPDATE characters SET online=0 WHERE charId=? AND online=2")){q.setInt(1,id);q.executeUpdate();}
    throw error;
   }
  }
  throw new IllegalStateException("No quedan perfiles de laboratorio libres con tres subclases");
 }
 public static synchronized boolean owned(Player p){return OWNED.containsKey(p)&&p.isLabControlled()&&p.getClient()==null;}
 public static void prepare(Player p){
  if(!owned(p))throw new IllegalStateException("No es un bot reservado");
  for(int[][] set:new int[][][]{COMMON,p.isMageClass()?MAGIC:PHYS})for(int[] buff:set){var s=SkillData.getInstance().getSkill(buff[0],buff[1]);if(s!=null)s.applyEffects(p,p);}
  PvpSiegeCombat.stock(p);p.fullRestore();p.setRunning();
 }
 public static synchronized void release(Player p){
  Saved before=OWNED.get(p);if(before==null||p.getClient()!=null)throw new IllegalStateException("No se puede liberar perfil ajeno");
  try{
   PvpSiegeBrain.forget(p);p.abortAttack();p.abortCast();p.stopMove(null);if(p.isInParty())p.leaveParty();
   if(p.hasSummon())p.getSummon().unSummon(p);
   var world=InstanceManager.getInstance().getWorld(p.getInstanceId());if(world!=null)world.removeAllowed(p);
   p.decayMe();p.setTeleporting(false);p.setInstanceId(before.instance());p.setXYZInvisible(before.location().getX(),before.location().getY(),before.location().getZ());p.setHeading(before.location().getHeading());
   if(p.isDead())p.doRevive();p.setTitle(before.title());p.getStat().setExp(before.exp());p.getStat().setLevel((byte)before.level());p.setPvpKills(before.pvps());p.setPkKills(before.pks());p.setKarma(before.karma());
   p.stopAllEffects();for(Effect effect:before.effects()){
    int seconds=(int)((effect.expires()-System.currentTimeMillis())/1000L);if(seconds<=0)continue;
    BuffInfo info=new BuffInfo(p,p,effect.skill());info.setAbnormalTime(seconds);effect.skill().applyEffectScope(EffectScope.GENERAL,info,false,true);p.getEffectList().add(info);
   }
   p.getSkillReuseTimeStamps().clear();p.getSkillReuseTimeStamps().putAll(before.cooldowns());
   Map<Integer,Long> current=new HashMap<>();for(var item:p.getInventory().getItems())current.merge(item.getId(),(long)item.getCount(),Long::sum);
   Set<Integer> ids=new HashSet<>(current.keySet());ids.addAll(before.items().keySet());
   for(int id:ids){long have=current.getOrDefault(id,0L),wanted=before.items().getOrDefault(id,0L);if(have<wanted)p.getInventory().addItem(ItemProcessType.NONE,id,Math.toIntExact(wanted-have),p,null);else if(have>wanted)p.getInventory().destroyItemByItemId(ItemProcessType.NONE,id,Math.toIntExact(have-wanted),p,null);}
   p.setCurrentHp(before.hp());p.setCurrentMp(before.mp());p.setCurrentCp(before.cp());p.stopPvPFlag();
   p.storeMe();
  }finally{
   try{if(!p.isOnline())p.setOnlineStatus(true,false);p.deleteMe();}finally{p.setOnlineStatus(false,true);p.setLabControlled(false);OWNED.remove(p);}
  }
 }
}

