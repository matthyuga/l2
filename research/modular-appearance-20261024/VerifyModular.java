import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.custom.ModularAppearance;
import org.l2jmobius.gameserver.custom.ModularAppearance.Profile;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;

/** Actual formula tests on detached objects, plus one clearly reserved offline probe. */
public class VerifyModular {
 private static int checks;
 private static void check(boolean yes,String message){if(!yes)throw new IllegalStateException(message);checks++;}
 private static int[] attrs(Player p){return new int[]{p.getSTR(),p.getDEX(),p.getCON(),p.getINT(),p.getWIT(),p.getMEN()};}
 private static int[] template(PlayerTemplate t){return new int[]{t.getBaseSTR(),t.getBaseDEX(),t.getBaseCON(),t.getBaseINT(),t.getBaseWIT(),t.getBaseMEN()};}
 public static void run(Path directory)throws Exception {
  var constructor=Player.class.getDeclaredConstructor(int.class,PlayerTemplate.class,String.class,PlayerAppearance.class);constructor.setAccessible(true);
  var templates=PlayerTemplateData.getInstance();List<Player> detached=new ArrayList<>();Map<Integer,int[]> original=new HashMap<>();
  for(int i=0;i<9;i++)original.put(i,template(templates.getTemplate(ModularAppearance.root(i))));
  int total=0;Player probe=null,loaded=null;
  try{
   for(int profession:new int[]{0,27,46,48}){
    Player p=constructor.newInstance(2147483000+total++,templates.getTemplate(profession),"_detached_modular",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));p.stopVitalityTask();p.setBaseClass(profession);detached.add(p);
    int baseClass=p.getBaseClass(),activeClass=p.getPlayerClass().getId();int[] baseline=attrs(p);
    for(int origin=0;origin<9;origin++)for(int body=0;body<9;body++)for(boolean female:new boolean[]{false,true}){
     Profile profile=new Profile(true,body,female);int o=origin;
     ModularAppearance.preview(p,ModularAppearance.bodyRace(origin),origin<8&&origin%2==1,profile,()->{
      int[] actual=attrs(p),race=original.get(o);
      for(int i=0;i<6;i++)check(actual[i]==Math.max(1,Math.min(99,race[i]+ModularAppearance.bonus(profile,i))),"Native formula mismatch");
      check(ModularAppearance.displayClass(p)==ModularAppearance.root(profile.body()),"Visual body class mismatch");
      check(p.getBaseClass()==baseClass&&p.getPlayerClass().getId()==activeClass,"Profession changed during preview");
      check(Double.isFinite(p.getMaxHp())&&Double.isFinite(p.getMAtkSpd())&&p.getMaxHp()>0&&p.getMAtkSpd()>0,"Invalid derived stat");
      return null;
     });
     check(Arrays.equals(attrs(p),baseline),"Preview leaked into real player state");
    }
    try{ModularAppearance.preview(p,ModularAppearance.bodyRace(1),true,new Profile(true,1,true),()->{throw new IllegalArgumentException("expected");});throw new AssertionError("Exception swallowed");}catch(IllegalArgumentException expected){}
    check(Arrays.equals(attrs(p),baseline),"Exception did not clean preview context");
   }
   for(int i=0;i<9;i++)check(Arrays.equals(original.get(i),template(templates.getTemplate(ModularAppearance.root(i)))),"Shared template changed");
   for(int body=0;body<9;body++){
    check(Arrays.stream(ModularAppearance.bodyBonuses(body)).sum()==0,"Unbalanced body point budget");
    for(int i=0;i<6;i++)check(ModularAppearance.bonus(new Profile(true,body,false),i)-ModularAppearance.bonus(new Profile(true,body,true),i)==2*ModularAppearance.sexBonuses(false)[i],"Sex contribution incorrect");
   }
   // Guard both identity and ownership; never loads a user's character.
   int id=0;
   try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name='BodySexProbe'")){
    try(var rs=ps.executeQuery()){if(rs.next()){id=rs.getInt(1);check("modular-test".equals(rs.getString(2))&&rs.getInt(3)==0&&World.getPlayer(id)==null,"Reserved persistence probe unavailable");}}
   }
   probe=id==0?Player.create(templates.getTemplate(0),"modular-test","BodySexProbe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false)):Player.load(id);
   check(probe!=null,"Persistence probe creation/load failed");probe.stopVitalityTask();
   if(ModularAppearance.canRestore(probe))ModularAppearance.restore(probe);
   probe.getVariables().set(ModularAppearance.ENABLED,false);probe.getVariables().set(ModularAppearance.BODY,0);probe.getVariables().saveNow();
   String before=ModularAppearance.state(probe);int baseClass=probe.getBaseClass(),activeClass=probe.getPlayerClass().getId();
   Profile chosen=new Profile(true,1,true);ModularAppearance.apply(probe,ModularAppearance.bodyRace(2),false,chosen);
   check(ModularAppearance.current(probe).equals(chosen),"Applied profile differs");check(ModularAppearance.displayClass(probe)==10,"Human Mystic body not selected");
   check(probe.getRacialStatRace()==ModularAppearance.bodyRace(2)&&!probe.isRacialMage(),"Attribute origin did not remain independent");
   loaded=Player.load(probe.getObjectId());check(loaded!=null,"Reload failed");loaded.stopVitalityTask();
   check(ModularAppearance.state(loaded).equals(ModularAppearance.state(probe)),"Profile did not persist across reload");
   check(Arrays.equals(attrs(probe),attrs(loaded)),"Reloaded stats differ");check(ModularAppearance.displayClass(loaded.getObjectId(),baseClass)==10,"Selection-screen persistence failed");
   check(loaded.getBaseClass()==baseClass&&loaded.getPlayerClass().getId()==activeClass,"Applied profession changed");
   ModularAppearance.restore(loaded);check(ModularAppearance.state(loaded).equals(before),"Personal rollback did not restore original state");
   check(!ModularAppearance.canRestore(loaded),"Rollback snapshot not cleared");
   // No object is spawned, online, or added to a user account.
   for(Player p:detached)check(World.getPlayer(p.getObjectId())==null,"Detached probe entered world");
   Files.writeString(directory.resolve("engine-verification.txt"),"PASS: "+checks+" real-engine checks; 648 race/body/sex/profession combinations; preview cleanup; unchanged shared templates; reserved offline BodySexProbe persistence/reload/rollback. User characters unchanged.\n");
  }finally{for(Player p:detached)p.stopVitalityTask();if(probe!=null)probe.stopVitalityTask();if(loaded!=null)loaded.stopVitalityTask();}
 }
}
