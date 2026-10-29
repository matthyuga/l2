import custom.ElvenPvpRoom.RoomTacticalPolicy;
import custom.ElvenPvpRoom.RoomTacticalPolicy.*;
import java.util.*;
import java.nio.file.*;
public final class RoomTacticalPolicyCheck {
 private static int checks;
 private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
 private static Self self(Role role){return new Self(1,300002,role,false,false,.5,.5);}
 private static Option option(Kind kind,int skill,int target,int instance,int priority,double urgency){return new Option(kind,skill,target,instance,priority,urgency,true,true,true,true,true,true,true,false,false);}
 private static Option flags(Option o,boolean known,boolean ready,boolean resources,boolean nativeAllowed,boolean legal,boolean range,boolean visible,boolean dead,boolean pending){return new Option(o.kind(),o.skill(),o.target(),o.instance(),o.priority(),o.urgency(),known,ready,resources,nativeAllowed,legal,range,visible,dead,pending);}
 public static void main(String[] args)throws Exception{
  Option nuke=option(Kind.OFFENSE,1239,2,300002,50,.1),heal=option(Kind.HEAL,1401,3,300002,10,.8),defense=option(Kind.DEFENSE,110,1,300002,0,.9);
  check(RoomTacticalPolicy.choose(self(Role.MAGE),List.of(nuke,heal,defense)).skill()==110,"critical defense precedes damage");
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(nuke,heal)).target()==3,"heal precedes damage");
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(heal,option(Kind.HEAL,1401,4,300002,10,.95))).target()==4,"lowest HP receives same-priority heal");
  for(int flag=0;flag<7;flag++){
   boolean[] valid={true,true,true,true,true,true,true};valid[flag]=false;
   Option blocked=flags(nuke,valid[0],valid[1],valid[2],valid[3],valid[4],valid[5],valid[6],false,false);
   check(RoomTacticalPolicy.choose(self(Role.MAGE),List.of(blocked)).kind()==null,"invalid condition index "+flag);
  }
  check(RoomTacticalPolicy.choose(self(Role.MAGE),List.of(option(Kind.OFFENSE,1239,2,300003,1,1))).kind()==null,"different instance blocked");
  check(RoomTacticalPolicy.choose(new Self(1,300002,Role.MAGE,true,false,0,1),List.of(nuke)).kind()==null,"dead bot never acts");
  check(RoomTacticalPolicy.choose(new Self(1,300002,Role.MAGE,false,true,1,1),List.of(nuke)).kind()==null,"casting bot never restarts action");
  Option basic=option(Kind.ATTACK,0,2,300002,100,0);
  for(Role role:List.of(Role.MAGE,Role.HEALER,Role.BUFFER,Role.SUMMONER))check(RoomTacticalPolicy.choose(self(role),List.of(basic)).kind()==null,"no physical fallback "+role);
  check(RoomTacticalPolicy.choose(self(Role.WARRIOR),List.of(basic)).kind()==Kind.ATTACK,"warrior native attack allowed");
  Option res=option(Kind.RESURRECT,1016,3,300002,25,1);
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(res)).kind()==null,"cannot resurrect living target");
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(flags(res,true,true,true,true,true,true,true,true,false))).kind()==Kind.RESURRECT,"valid corpse can be resurrected");
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(flags(res,true,true,true,true,true,true,true,true,true))).kind()==null,"do not duplicate pending revive");
  check(RoomTacticalPolicy.choose(self(Role.HEALER),List.of(flags(heal,true,true,true,true,true,true,true,true,false))).kind()==null,"cannot heal corpse");
  check(RoomTacticalPolicy.role("CARDINAL","DAGGER",true)==Role.HEALER,"hybrid healer retains assigned role");
  check(RoomTacticalPolicy.role("MYSTIC_MUSE","BOW",true)==Role.ARCHER,"equipped bow resolves hybrid weapon role");
  check(RoomTacticalPolicy.role("SPECTRAL_MASTER","SWORD",true)==Role.SUMMONER,"summoner stays summoner");
  check(RoomTacticalPolicy.role("SPECTRAL_DANCER","DUAL",false)==Role.SUPPORT,"dancer support role");
  check(RoomTacticalPolicy.role("HELL_KNIGHT","SWORD",false)==Role.TANK,"tank role");
  int[] kite=RoomTacticalPolicy.retreat(500,500,400,500,0,1000,0,1000,200);
  check(kite!=null&&kite[0]==700&&kite[1]==500,"retreat increases distance");
  check(RoomTacticalPolicy.retreat(900,500,800,500,0,1000,0,1000,200)==null,"retreat cannot leave room");
  check(RoomTacticalPolicy.retreat(500,500,500,500,0,1000,0,1000,100)!=null,"coincident actors produce finite retreat");
  String result="PASS "+checks+" decision scenarios; native API compilation separate. No live combat behavior activated.\n";
  Files.writeString(Path.of(args[0]),result);System.out.print(result);
 }
}
