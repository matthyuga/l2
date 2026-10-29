package custom.GiranSiegeLab;

import java.util.*;
import java.util.function.*;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import custom.GiranSiegeLab.GiranSiegeLab.*;
import custom.AmberContract.AmberScoutVerificationBridge;

/** Opt-in native fixture; patrols and real damage, never loads the human or completes conquest. */
final class GiranGuardianVerification {
 @FunctionalInterface interface Wait {void until(BooleanSupplier condition,String why,long timeout)throws Exception;}
 static void run(List<Squad> squads,BiConsumer<Boolean,String> check,Wait wait)throws Exception {
  var manager=GiranGuardians.instance;Player owner=squads.get(0).members.get(0).p,enemy=squads.get(1).members.get(0).p,rival=squads.get(2).members.get(0).p;
  try {
   for(Squad s:squads)for(Pilot p:s.members){p.p.abortAttack();p.p.abortCast();p.p.getAI().setIntentionIdle();p.p.setInvul(true);GiranSiegeLab.move(p.p,GiranSiegeLab.camp(s.id,p.slot));}
   // Both actual guardians walk their entire patrol with no enemy and no player orders.
   int[] starts=new int[2];for(int i=0;i<2;i++){var g=manager.actors.get(i);if(g.isDead())g.revive(false);GiranGuardianBrain.clear(g);g.holdingUntil=0;g.setInvul(false);g.returning=false;g.patrolIndex=0;g.teleToLocation(g.home.getX(),g.home.getY(),g.home.getZ(),0,0,false);starts[i]=g.patrolArrivals;}
   manager.verificationPaused=false;
   wait.until(()->{for(int i=0;i<2;i++){var g=manager.actors.get(i);if(g.patrolArrivals-starts[i]<GiranGuardianBrain.route(g).size()+1)return false;}return true;},"Both guardians walk a complete courtyard/passage/artifact patrol",150000);
   for(var g:manager.actors)check.accept(g.getAI() instanceof GiranGuardianAI&&g.focus==null,"Dedicated patrol AI without attack orders: "+g.getName());
   Logger.getLogger(GiranGuardianVerification.class.getName()).info("GIRAN_V7_PATROL_PASS Ares courtyard cycle; Nyx hall/passage/north-stairs/artifact cycle; native walking, no patrol teleport");
   manager.verificationPaused=true;
   for(var g:manager.actors){
    GiranGuardianBrain.clear(g);g.teleToLocation(g.home.getX(),g.home.getY(),g.home.getZ(),0,0,false);g.returning=false;g.patrolIndex=0;
    Location victim=SiegeAgenda.safe(g.home.getX()+180,g.home.getY(),g.home.getZ());GiranSiegeLab.move(enemy,victim);enemy.setInvul(false);enemy.fullRestore();
    GiranSiegeLab.move(owner,SiegeAgenda.safe(g.home.getX()+100,g.home.getY()+70,g.home.getZ()));owner.setInvul(false);owner.fullRestore();
    check.accept(!GiranGuardianBrain.enemy(g,owner)&&!g.isAutoAttackable(owner),"Current castle owner protected "+g.getName());
    check.accept(GiranGuardianBrain.engageable(g,enemy)&&GiranGuardianBrain.choose(g)==enemy,"Proactive unprovoked attacker acquired "+g.getName());
    double hp=enemy.getCurrentHp();int casts=g.casts;manager.verificationPaused=false;
    wait.until(()->enemy.getCurrentHp()<hp,"Unprovoked native combat damages attacker: "+g.getName(),22000);
    check.accept(g.casts>casts,"Guardian uses real native combat skills "+g.getName());
    manager.verificationPaused=true;GiranGuardianBrain.clear(g);enemy.abortAttack();enemy.abortCast();enemy.getAI().setIntentionIdle();enemy.setInvul(true);owner.setInvul(true);
    check.accept(owner.getCurrentHp()==owner.getMaxHp(),"Nearby owner receives no friendly damage "+g.getName());
    GiranSiegeLab.move(owner,GiranSiegeLab.camp(0,0));GiranSiegeLab.move(enemy,GiranSiegeLab.camp(1,0));
    Logger.getLogger(GiranGuardianVerification.class.getName()).info("GIRAN_V7_COMBAT_PASS "+g.getName()+" nativeDamage="+(hp-enemy.getCurrentHp())+" nativeCasts="+(g.casts-casts));
   }
   var nyx=manager.actors.get(1);var artifact=GiranRules.castle().getArtefacts().iterator().next();Location stand=SiegeAgenda.sealPosition(artifact);
   GiranGuardianBrain.clear(nyx);nyx.teleToLocation(117704,145064,-2528,0,0,false);GiranSiegeLab.move(enemy,stand);enemy.setInvul(false);enemy.fullRestore();
   GiranSiegeLab.move(rival,SiegeAgenda.safe(117740,145064,-2528));rival.setInvul(false);rival.fullRestore();
   enemy.setTarget(artifact);check.accept(enemy.useMagic(enemy.getKnownSkill(246),true,true)&&SiegeAgenda.engraving(enemy),"Real engraving fixture for Nyx priority");
   check.accept(GiranGuardianBrain.choose(nyx)==enemy,"Nyx prioritizes engraving over closer attacker");
   enemy.abortCast();nyx.focus=enemy;
   // Enemy summon resolves allegiance through its owner; no generic-NPC or neutral target scan.
   var pet=AmberScoutVerificationBridge.build(rival);pet.setInvul(false);pet.teleToLocation(117750,145064,-2528,0,0,false);
   check.accept(nyx.isAutoAttackable(pet)&&GiranGuardianBrain.enemy(nyx,pet),"Registered enemy summon accepted with owner allegiance");AmberScoutVerificationBridge.cleanup(rival);
   GiranSiegeLab.move(owner,SiegeAgenda.safe(117740,145130,-2528));owner.setInvul(false);rival.getAI().setIntentionAttack(owner);check.accept(GiranGuardianBrain.harmingDefender(rival),"Threat on owner is a protection priority");rival.abortAttack();rival.getAI().setIntentionIdle();owner.setInvul(true);GiranSiegeLab.move(owner,GiranSiegeLab.camp(0,0));
   GiranSiegeLab.move(enemy,GiranSiegeLab.camp(1,0));check.accept(!GiranGuardianBrain.engageable(nyx,enemy)&&GiranGuardianBrain.choose(nyx)!=enemy,"Castle guardians do not chase into camps");
   enemy.setInvul(true);rival.setInvul(true);GiranSiegeLab.move(rival,GiranSiegeLab.camp(2,0));
   // Only the revival lifecycle may leave the isolated native upper room using castle transport.
   var ares=manager.actors.get(0);ares.revive(true);Location room=new Location(ares);check.accept(ares.holdingUntil>System.currentTimeMillis()&&ares.isInvul(),"Residence-room ten-second hold preserved");
   int visits=ares.patrolArrivals,exits=ares.roomExits;ares.holdingUntil=System.currentTimeMillis()-1;manager.verificationPaused=false;
   wait.until(()->!ares.roomTransit&&ares.roomExits==exits+1,"Guardian exits isolated resurrection room by lifecycle transport",5000);
   check.accept(ares.getX()>115430&&GiranGuardianBrain.innerPost(ares),"Closed inner doors select the interior defense post");
   wait.until(()->!ares.returning&&ares.patrolArrivals>visits,"Guardian walks from room exit back into patrol behind closed inner gates",60000);
   check.accept(ares.calculateDistance3D(room)>100&&!ares.isInvul()&&ares.roomExits==exits+1,"Guardian resumes vulnerable patrol with no further transport");
   Logger.getLogger(GiranGuardianVerification.class.getName()).info("GIRAN_V7_GUARDIAN_PASS unprovoked combat/native skills,owner protection,engraver priority,enemy summon,leash,room hold/exit transport and walking return behind closed gates");
  }finally {manager.verificationPaused=true;for(var g:manager.actors){GiranGuardianBrain.clear(g);g.returning=true;}for(Squad s:squads)for(Pilot p:s.members){p.p.abortAttack();p.p.abortCast();p.p.getAI().setIntentionIdle();p.p.setInvul(true);GiranSiegeLab.move(p.p,GiranSiegeLab.camp(s.id,p.slot));}}
 }
}
