import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.zone.type.FlagPvPZone;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import l2jorion.game.model.zone.type.L2RandomZone;
import l2jorion.game.model.actor.instance.L2PcInstance;
import l2jorion.game.model.base.ClassId;
public class ReviewHarness {
 static class N extends FlagPvPZone{N(int id){super(id);}void enter(Creature c){onEnter(c);}void exit(Creature c){onExit(c);}}
 static class O extends L2RandomZone{O(){super(1);}void enter(l2jorion.game.model.L2Character c){onEnter(c);}void exit(l2jorion.game.model.L2Character c){onExit(c);}}
 static int checks=0;static void check(boolean b,String s){if(!b)throw new AssertionError(s);checks++;System.out.println("PASS "+s);}
 public static void main(String[] args){
  N n=new N(1);Player p=new Player();n.enter(p);check(p.flag==1,"Mobius entering sets flag");
  n.exit(p);check(p.flag==0,"Mobius leaving clears flag immediately");
  p.flag=1;n.onDieInside(p);check(p.flag==0,"Mobius death clears flag via exit");
  n.onReviveInside(p);check(p.flag==1,"Mobius revive sets flag");
  N second=new N(2);second.enter(p);n.exit(p);check(p.flag==0,"Mobius overlapping-zone exit has no ownership guard");
  n.enter(p);p.until=1;PvpFlagTaskManager.getInstance().add(p);PvpFlagTaskManager.getInstance().run();check(p.flag==0,"Mobius existing expired combat timer can clear flag while inside");
  O o=new O();o.setParameter("autoPvpFlag","true");L2PcInstance q=new L2PcInstance();
  o.enter(q);check(!q.inside && q.flag==0,"Orion inactive zone ignores entry");
  o.setActiveZone(true);q.instance=0;o.enter(q);check(!q.inside && q.flag==0,"Orion entry requires configured instance already assigned");
  q.instance=3051;o.enter(q);check(q.inside && q.flag==1 && q.stops==1,"Orion entry stops old flag task and sets forced flag");
  o.exit(q);check(q.instance==0 && !q.inside && q.normalTimerStarts==1,"Orion geometric exit immediately resets instance and requests normal flag timer");
  L2PcInstance healer=new L2PcInstance();healer.cls=ClassId.cardinal;o.enter(healer);check(healer.ejected,"Orion healer restriction ejects cardinal when enabled");
  o.onDieInside(q);o.onReviveInside(q);check(q.instance==0 && q.normalTimerStarts==1,"Orion death/revive callbacks perform no action");
  O empty=new O();boolean rejected=false;try{empty.getLoc();}catch(RuntimeException e){rejected=true;}check(rejected,"Orion empty spawn list fails at selection");
  o.setParameter("locs","10,20,30;40,50,60;");check(o.getLoc().x()==10,"Orion configured spawn list parses trailing separator");
  boolean centerMissing=false;try{o.getCenterLoc();}catch(IndexOutOfBoundsException e){centerMissing=true;}check(centerMissing,"Orion fence center missing fails at access");
  System.out.println("TOTAL "+checks);
 }
}