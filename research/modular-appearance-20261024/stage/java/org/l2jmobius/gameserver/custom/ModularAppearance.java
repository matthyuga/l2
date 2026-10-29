package org.l2jmobius.gameserver.custom;

import java.util.Arrays;
import java.util.function.Supplier;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.util.ConfigReader;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;

/** Independent body/sex contributions; never mutates shared templates or professions. */
public final class ModularAppearance {
 public static final String ENABLED="MODULAR_APPEARANCE_V1",BODY="MODULAR_BODY_V1",SNAPSHOT="MODULAR_BEFORE_V1";
 private static final int[] ROOTS={0,10,18,25,31,38,44,49,53};
 private static final String[] NAMES={"Humano Fighter","Humano Mystic","Elfo Fighter","Elfo Mystic","Elfo oscuro Fighter","Elfo oscuro Mystic","Orco Fighter","Orco Mystic","Enano"};
 private static final int[][] DEFAULTS={{1,0,1,-1,-1,0},{-1,0,-1,1,1,0},{-1,2,-1,0,0,0},{-1,0,-1,0,2,0},{2,0,-1,0,0,-1},{-1,0,-1,2,0,0},{1,-1,2,-1,-1,0},{0,-1,1,0,-1,1},{0,-1,2,-1,0,0}};
 private static final ConfigReader CONFIG=new ConfigReader("./config/Custom/ModularAppearance.ini");
 public static final boolean ACTIVE=CONFIG.getBoolean("Enabled",true),NEW_CHARACTERS=CONFIG.getBoolean("EnableForNewCharacters",true);
 private static final int[][] BONUSES=new int[9][];
 private static final int[] MALE;
 private record Context(Player player,Profile profile){}
 private static final ThreadLocal<Context> PREVIEW=new ThreadLocal<>();
 static {
  for(int i=0;i<9;i++)BONUSES[i]=parse(CONFIG.getString("BodyBonus"+i,join(DEFAULTS[i])),2);
  MALE=parse(CONFIG.getString("MaleBonus","1,-1,1,1,-1,-1"),1);
 }
 private ModularAppearance(){}
 public record Profile(boolean enabled,int body,boolean female) {
  public Profile {if(body<0||body>8)throw new IllegalArgumentException("Cuerpo invalido");}
 }
 private static String join(int[] values){return String.join(",",Arrays.stream(values).mapToObj(Integer::toString).toList());}
 private static int[] parse(String value,int max){int[] a=Arrays.stream(value.split(",")).map(String::trim).mapToInt(Integer::parseInt).toArray();if(a.length!=6||Arrays.stream(a).sum()!=0||Arrays.stream(a).anyMatch(i->Math.abs(i)>max))throw new IllegalStateException("Invalid zero-sum modular stat configuration");return a;}
 public static int root(int body){return ROOTS[new Profile(true,body,false).body()];}
 public static String name(int body){return NAMES[new Profile(true,body,false).body()];}
 public static Race bodyRace(int body){return PlayerClass.getPlayerClass(root(body)).getRace();}
 public static int origin(Race race,boolean mage){return race==Race.DWARF?8:race.ordinal()*2+(mage?1:0);}
 public static int nativeBody(Player p){return origin(p.getRace(),PlayerClass.getPlayerClass(p.getBaseClass()).getRootClass().isMage());}
 public static Profile current(Player p){
  Context context=PREVIEW.get();if(context!=null&&context.player()==p)return context.profile();
  if(p.getAppearance()==null)return new Profile(false,nativeBody(p),false);
  return new Profile(ACTIVE&&p.getVariables().getBoolean(ENABLED,false),p.getVariables().getInt(BODY,nativeBody(p)),p.getAppearance().isFemale());
 }
 public static int bonus(Profile value,int index){if(index<0||index>=6)throw new IllegalArgumentException("Atributo invalido");return ACTIVE&&value.enabled()?BONUSES[value.body()][index]+(value.female()?-MALE[index]:MALE[index]):0;}
 public static int[] bodyBonuses(int body){return BONUSES[new Profile(true,body,false).body()].clone();}
 public static int[] sexBonuses(boolean female){return Arrays.stream(MALE).map(v->female?-v:v).toArray();}
 public static int base(Player p,int index){
  PlayerTemplate t=p.getRacialBaseTemplate();int value=switch(index){case 0->t.getBaseSTR();case 1->t.getBaseDEX();case 2->t.getBaseCON();case 3->t.getBaseINT();case 4->t.getBaseWIT();case 5->t.getBaseMEN();default->throw new IllegalArgumentException("Atributo invalido");};
  if(!ACTIVE)return value;
  Context context=PREVIEW.get();
  if(context!=null&&context.player()==p)return Math.max(1,Math.min(99,value+bonus(context.profile(),index)));
  // Combat's common path performs no allocations and never modifies variables.
  if(p.getAppearance()==null||!p.getVariables().getBoolean(ENABLED,false))return value;
  int body=p.getVariables().getInt(BODY,nativeBody(p));if(body<0||body>8)throw new IllegalStateException("Cuerpo guardado invalido");
  return Math.max(1,Math.min(99,value+BONUSES[body][index]+(p.getAppearance().isFemale()?-MALE[index]:MALE[index])));
 }
 public static <T>T preview(Player p,Race race,boolean mage,Profile value,Supplier<T> action){Context old=PREVIEW.get();PREVIEW.set(new Context(p,value));try{return p.previewRacialStats(race,mage,action);}finally{if(old==null)PREVIEW.remove();else PREVIEW.set(old);}}
 public static int displayClass(Player p){Profile value=current(p);return value.enabled()?root(value.body()):p.getBaseClass();}
 public static PlayerTemplate displayTemplate(Player p){Profile value=current(p);return value.enabled()?PlayerTemplateData.getInstance().getTemplate(root(value.body())):p.getBaseTemplate();}
 /** Selection-screen lookup only, once per character in the account list. */
 public static int displayClass(int objectId,int fallback){
  if(!ACTIVE)return fallback;
  try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT var,val FROM character_variables WHERE charId=? AND var IN ('MODULAR_APPEARANCE_V1','MODULAR_BODY_V1')")){
   ps.setInt(1,objectId);boolean enabled=false;int body=-1;
   try(var rs=ps.executeQuery()){while(rs.next()){if(ENABLED.equals(rs.getString(1)))enabled=Boolean.parseBoolean(rs.getString(2));else body=Integer.parseInt(rs.getString(2));}}
   return enabled&&body>=0&&body<9?root(body):fallback;
  }catch(Exception e){throw new IllegalStateException("Cannot resolve saved modular body",e);}
 }
 public static void initialize(Player p){if(ACTIVE&&NEW_CHARACTERS){p.getVariables().set(BODY,nativeBody(p));p.getVariables().set(ENABLED,true);p.getVariables().saveNow();}}
 /** Compact rollback state; classes/equipment/progress are deliberately absent. */
 public static String state(Player p){Profile c=current(p);return p.getRace().ordinal()+","+p.getRacialStatRace().ordinal()+","+p.isRacialMage()+","+p.getAppearance().isFemale()+","+p.getAppearance().getFace()+","+p.getAppearance().getHairStyle()+","+p.getAppearance().getHairColor()+","+c.enabled()+","+c.body();}
 private static void restoreState(Player p,String state){
  String[] a=state.split(",");if(a.length!=9)throw new IllegalArgumentException("Respaldo invalido");
  p.setAppearanceRace(Race.values()[Integer.parseInt(a[0])]);p.setRacialStatsOrigin(Race.values()[Integer.parseInt(a[1])],Boolean.parseBoolean(a[2]));
  if(Boolean.parseBoolean(a[3]))p.getAppearance().setFemale();else p.getAppearance().setMale();
  p.getAppearance().setFace(Integer.parseInt(a[4]));p.getAppearance().setHairStyle(Integer.parseInt(a[5]));p.getAppearance().setHairColor(Integer.parseInt(a[6]));
  p.getVariables().set(ENABLED,Boolean.parseBoolean(a[7]));p.getVariables().set(BODY,Integer.parseInt(a[8]));p.getVariables().saveNow();p.storeMe();
 }
 public static void apply(Player p,Race statRace,boolean mage,Profile value){
  if(!ACTIVE)throw new IllegalStateException("Sistema modular desactivado");
  if(statRace.ordinal()>4||statRace==Race.DWARF&&mage)throw new IllegalArgumentException("Origen invalido");
  String old=state(p);double hp=p.getCurrentHp(),mp=p.getCurrentMp(),cp=p.getCurrentCp();
  if(!p.getVariables().hasVariable(SNAPSHOT))p.getVariables().set(SNAPSHOT,old);
  try{
   boolean changed=p.getRace()!=bodyRace(value.body())||current(p).body()!=value.body()||p.getAppearance().isFemale()!=value.female();
   p.setAppearanceRace(bodyRace(value.body()));p.setRacialStatsOrigin(statRace,mage);
   if(value.female())p.getAppearance().setFemale();else p.getAppearance().setMale();
   p.getVariables().set(BODY,value.body());p.getVariables().set(ENABLED,value.enabled());p.getVariables().saveNow();
   if(changed){p.getAppearance().setFace(0);p.getAppearance().setHairStyle(0);p.getAppearance().setHairColor(0);}
   p.setCurrentHp(Math.min(hp,p.getMaxHp()));p.setCurrentMp(Math.min(mp,p.getMaxMp()));p.setCurrentCp(Math.min(cp,p.getMaxCp()));p.storeMe();verifySaved(p);
  }catch(RuntimeException e){restoreState(p,old);p.setCurrentHp(hp);p.setCurrentMp(mp);p.setCurrentCp(cp);throw e;}
 }
 public static boolean canRestore(Player p){return p.getVariables().hasVariable(SNAPSHOT);}
 public static void restore(Player p){
  String before=p.getVariables().getString(SNAPSHOT,null);if(before==null)throw new IllegalStateException("No hay cambio anterior guardado");
  String old=state(p);double hp=p.getCurrentHp(),mp=p.getCurrentMp(),cp=p.getCurrentCp();
  try{restoreState(p,before);p.setCurrentHp(Math.min(hp,p.getMaxHp()));p.setCurrentMp(Math.min(mp,p.getMaxMp()));p.setCurrentCp(Math.min(cp,p.getMaxCp()));p.storeMe();verifySaved(p);p.getVariables().remove(SNAPSHOT);p.getVariables().saveNow();}
  catch(RuntimeException e){restoreState(p,old);throw e;}
 }
 private static void verifySaved(Player p){
  try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT race,sex,base_class,classid FROM characters WHERE charId=?")){
   ps.setInt(1,p.getObjectId());try(var rs=ps.executeQuery()){if(!rs.next()||rs.getInt(1)!=p.getRace().ordinal()||rs.getInt(2)!=(p.getAppearance().isFemale()?1:0)||rs.getInt(3)!=p.getBaseClass()||rs.getInt(4)!=p.getPlayerClass().getId())throw new IllegalStateException("No se confirmo el guardado modular");}
   try(var vars=con.prepareStatement("SELECT var,val FROM character_variables WHERE charId=? AND var IN ('MODULAR_APPEARANCE_V1','MODULAR_BODY_V1','RACIAL_STAT_RACE','RACIAL_PROFILE')")){
    vars.setInt(1,p.getObjectId());java.util.Map<String,String> saved=new java.util.HashMap<>();try(var rs=vars.executeQuery()){while(rs.next())saved.put(rs.getString(1),rs.getString(2));}
    Profile value=current(p);if(!Boolean.toString(value.enabled()).equals(saved.get(ENABLED))||!Integer.toString(value.body()).equals(saved.get(BODY))||!Integer.toString(p.getRacialStatRace().ordinal()).equals(saved.get("RACIAL_STAT_RACE"))||!(p.isRacialMage()?"MYSTIC":"FIGHTER").equals(saved.get("RACIAL_PROFILE")))throw new IllegalStateException("No se confirmaron los atributos y el cuerpo guardados");
   }
  }catch(java.sql.SQLException e){throw new IllegalStateException("No se pudo verificar el guardado",e);}
 }
}
