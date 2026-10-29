package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Defender;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.taskmanagers.DecayTaskManager;

/** Persistent castle guardians with separate patrol/combat agendas and current-owner allegiance. */
public class GiranGuardians extends Script {
 private static final Logger LOG=Logger.getLogger(GiranGuardians.class.getName());
 static GiranGuardians instance;final List<Guardian> actors=new ArrayList<>();private int lastOwner=-1;volatile boolean verificationPaused;
 public GiranGuardians(){instance=this;ThreadPool.scheduleAtFixedRate(this::tick,12000,1000);}
 synchronized void ensure(){if(!actors.isEmpty())return;for(int[] d:new int[][]{{903200,114174,145058,-2752},{903201,117400,145064,-2640}}){
  var home=SiegeAgenda.safe(d[1],d[2],d[3]);Guardian g=new Guardian(NpcData.getInstance().getTemplate(d[0]),home);actors.add(g);g.fullRestore();g.setHeading(32768);g.setRunning();g.spawnMe(home.getX(),home.getY(),home.getZ());g.revalidateZone(true);
 }LOG.info("GIRAN_GUARDIANS V7 spawned patrol defenders; current-owner allegiance");}
 synchronized void revive(Player p){if(p.getClanId()!=GiranRules.castle().getOwnerId())throw new IllegalStateException("Solo el propietario actual revive a sus guardianes.");for(Guardian g:actors)if(g.isDead())g.revive(false);}
 private synchronized void tick(){try{
  var c=GiranRules.castle();if(c==null)return;
  if(c.getOwnerId()==0&&!c.getSiege().isInProgress()){for(Guardian g:actors){DecayTaskManager.getInstance().cancel(g);g.deleteMe();}actors.clear();return;}
  ensure();long now=System.currentTimeMillis();
  if(lastOwner!=c.getOwnerId()){lastOwner=c.getOwnerId();for(Guardian g:actors){GiranGuardianBrain.clear(g);if(!g.isDead()&&now>=g.holdingUntil)g.getAI().setIntentionActive();}LOG.info("GIRAN_GUARDIANS owner="+lastOwner+"; old combat cleared");}
  for(Guardian g:actors){
   if(g.isDead()){if(now-g.deadAt>=60000)g.revive(true);continue;}
   if(now<g.holdingUntil)continue;
   if(g.holdingUntil!=0){g.holdingUntil=0;g.setInvul(false);
    // Native residence spawn is an isolated upper-room island in this geodata. Only the respawn lifecycle may transport out.
    if(g.roomTransit){Location exit=SiegeAgenda.safe(116650,145095,-2560);g.teleToLocation(exit.getX(),exit.getY(),exit.getZ(),0,0,false);g.roomTransit=false;g.roomExits++;}
    g.getAI().setIntentionActive();}
   if(!verificationPaused)GiranGuardianBrain.act(g,now);
  }
 }catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"Giran guardians",e);}}
 static final class Guardian extends Defender {
  final Location home;long deadAt,holdingUntil,lastMove,nextSkill,pauseUntil;boolean returning,roomTransit;
  int patrolIndex,patrolArrivals,casts,lastSkill,roomExits;Creature focus;Location destination;
  Guardian(NpcTemplate template,Location home){super(template);this.home=home;setXYZ(home.getX(),home.getY(),home.getZ());}
  @Override protected org.l2jmobius.gameserver.ai.CreatureAI initAI(){return new GiranGuardianAI(this);}
  @Override public boolean isAutoAttackable(Creature attacker){Player p=attacker==null?null:attacker.isSummon()?attacker.asSummon().getOwner():attacker.asPlayer();return p!=null&&!GiranRules.defender(p)&&GiranRules.castle().checkIfInZone(p.getX(),p.getY(),p.getZ())&&System.currentTimeMillis()>=holdingUntil&&super.isAutoAttackable(p);}
  @Override public void addDamageHate(Creature attacker,long damage,long aggro){if(GiranGuardianBrain.enemy(this,attacker))super.addDamageHate(attacker,damage,aggro);}
  @Override public void returnHome(){returning=true;}
  @Override public boolean doDie(Creature killer){if(!super.doDie(killer))return false;deadAt=System.currentTimeMillis();DecayTaskManager.getInstance().cancel(this);return true;}
  void revive(boolean inRoom){DecayTaskManager.getInstance().cancel(this);doRevive();fullRestore();GiranGuardianBrain.clear(this);deadAt=0;
   if(inRoom){Location room=GiranRules.castle().getResidenceZone().getSpawnLoc();teleToLocation(room.getX(),room.getY(),room.getZ(),0,0,false);holdingUntil=System.currentTimeMillis()+10000;setInvul(true);returning=true;roomTransit=true;getAI().setIntentionIdle();}
   else {holdingUntil=0;setInvul(false);returning=false;roomTransit=false;getAI().setIntentionActive();}
   LOG.info("GIRAN_GUARDIAN revived "+getName()+" room="+inRoom+" owner="+GiranRules.castle().getOwnerId());
  }
 }
 public static void main(String[] args){new GiranGuardians();}
}
