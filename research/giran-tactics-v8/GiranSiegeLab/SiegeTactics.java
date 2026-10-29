package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Per-party perception and temporary bilateral ceasefires. Native clans, alliances and PvP legality stay intact. */
final class SiegeTactics {
 private static final Logger LOG=Logger.getLogger(SiegeTactics.class.getName());
 private static final Map<Integer,Squad> PARTIES=new HashMap<>();private static final Map<Long,Pact> PACTS=new HashMap<>();private static final Map<Long,Long> COOLDOWNS=new HashMap<>();
 static final class State {long assessAt,seenAt;double ownForce,defenderForce;int defenders,alive;boolean pressured;String stance="Avanzar";}
 private record Pact(int first,int second,long until){}
 static synchronized void reset(){PARTIES.clear();PACTS.clear();COOLDOWNS.clear();}
 private static long key(int a,int b){return ((long)Math.min(a,b)<<32)|(Math.max(a,b)&0xffffffffL);}
 private static Player captain(Squad s){return s.leader!=null&&!s.leader.isDead()?s.leader:SiegeAgenda.captain(s);}
 private static boolean attacker(Player p){var c=GiranRules.castle();return p!=null&&p.getClan()!=null&&c.getSiege().isInProgress()&&c.getSiege().checkIsAttacker(p.getClan())&&!GiranRules.defender(p);}
 static boolean defenderTarget(Creature t){return t instanceof Defender||t!=null&&t.isPlayable()&&GiranRules.defender(SiegeAgenda.owner(t));}
 static boolean visible(Player p,Creature t,int range){return SiegeSquadBrain.allowed(t,p)&&!t.isInvul()&&!t.isInvisible()&&p.calculateDistance2D(t)<=range&&GeoEngine.getInstance().canSeeTarget(p,t);}
 static synchronized void update(Squad s){Player lead=captain(s);if(lead==null)return;long now=System.currentTimeMillis();State state=s.tactics;state.seenAt=now;PARTIES.put(lead.getClanId(),s);if(now<state.assessAt)return;state.assessAt=now+1000;
  state.ownForce=0;state.alive=0;double hp=0;
  for(Pilot a:s.members)if(!a.p.isAlikeDead()&&a.p.calculateDistance2D(lead)<=1500){state.alive++;hp+=SiegeSquadBrain.hp(a.p);state.ownForce+=(.25+.75*SiegeSquadBrain.hp(a.p))*(a.magic()?.5+.5*a.p.getCurrentMp()/Math.max(1,a.p.getMaxMp()):1);}
  Set<Creature> threats=new HashSet<>();for(Pilot a:s.members)if(!a.p.isAlikeDead()&&a.p.calculateDistance2D(lead)<=1500)World.forEachVisibleObjectInRange(a.p,Creature.class,1300,t->{if(defenderTarget(t)&&visible(a.p,t,1300))threats.add(t);});
  state.defenders=threats.size();state.defenderForce=threats.stream().mapToDouble(t->(t instanceof GiranGuardians.Guardian?2:1)*(.3+.7*SiegeSquadBrain.hp(t))).sum();
  state.pressured=state.defenders>0&&(state.defenderForce>=Math.max(.5,state.ownForce)*.8||state.alive<=2||hp/Math.max(1,state.alive)<.45);
  state.stance=state.defenders>0?(state.pressured?"Presion defensora; buscar tregua":"Despejar defensores"):(s.conquest?"Llegar y proteger conquista":"Avanzar por objetivos");
  expire(now);if(!attacker(lead))return;
  for(Squad other:new ArrayList<>(PARTIES.values())){Player q=captain(other);if(other==s||!attacker(q)||now-other.tactics.seenAt>3000||lead.calculateDistance2D(q)>1600||!GeoEngine.getInstance().canSeeTarget(lead,q))continue;
   long pair=key(lead.getClanId(),q.getClanId());if(now<COOLDOWNS.getOrDefault(pair,0L)||SiegeAgenda.engraving(lead)||SiegeAgenda.engraving(q))continue;
   if(state.pressured||other.tactics.pressured&&state.defenders>0){
    Pact old=PACTS.get(pair);if(old==null){PACTS.put(pair,new Pact(lead.getClanId(),q.getClanId(),now+20000));cease(s,q.getClanId());cease(other,lead.getClanId());LOG.info("GIRAN_V8_TRUCE BEGIN "+lead.getClan().getName()+" + "+q.getClan().getName()+";20s;defenders="+state.defenders+" own="+state.alive);}
    else if(old.until-now<5000)PACTS.put(pair,new Pact(old.first,old.second,now+20000));
   }
  }
 }
 private static void cease(Squad s,int clan){if(s.focus!=null&&SiegeAgenda.owner(s.focus)!=null&&SiegeAgenda.owner(s.focus).getClanId()==clan)s.focus=null;
  for(Pilot a:s.members)if(a.bot){Creature attack=a.p.getAI().getAttackTarget(),cast=a.p.getAI().getCastTarget();boolean hostile=belongs(attack,clan)||belongs(cast,clan)&&!SiegeAgenda.engraving(a.p);
   if(hostile){a.p.abortAttack();a.p.abortCast();a.p.getAI().setIntentionActive();}if(a.pursuit!=null&&belongs(a.pursuit,clan))a.pursuit=null;
   if(a.p.hasSummon()&&belongs(a.p.getSummon().getAI().getAttackTarget(),clan)){a.p.getSummon().abortAttack();a.p.getSummon().setFollowStatus(true);}}
 }
 private static boolean belongs(Creature t,int clan){return t!=null&&SiegeAgenda.owner(t)!=null&&SiegeAgenda.owner(t).getClanId()==clan;}
 private static boolean betrayal(Squad s,int clan){return s!=null&&s.members.stream().anyMatch(a->a.p.hasAI()&&(belongs(a.p.getAI().getAttackTarget(),clan)||belongs(a.p.getAI().getCastTarget(),clan))||a.p.hasSummon()&&belongs(a.p.getSummon().getAI().getAttackTarget(),clan));}
 private static void expire(long now){for(var e:new ArrayList<>(PACTS.entrySet())){Pact p=e.getValue();Squad a=PARTIES.get(p.first),b=PARTIES.get(p.second);Player first=a==null?null:captain(a),second=b==null?null:captain(b);
   boolean betrayal=betrayal(a,p.second)||betrayal(b,p.first),capture=first!=null&&SiegeAgenda.engraving(first)||second!=null&&SiegeAgenda.engraving(second);
   if(now>=p.until||!attacker(first)||!attacker(second)||capture||betrayal){PACTS.remove(e.getKey());if(capture||betrayal)COOLDOWNS.put(e.getKey(),now+15000);LOG.info("GIRAN_V8_TRUCE END "+p.first+"/"+p.second+" reason="+(capture?"capture":betrayal?"betrayal":"expired/side changed"));}}
 }
 static synchronized boolean truce(Player p,Creature t){Player q=t==null?null:SiegeAgenda.owner(t);if(q==null||p.getClanId()==q.getClanId())return false;expire(System.currentTimeMillis());return PACTS.containsKey(key(p.getClanId(),q.getClanId()));}
 static synchronized String status(Squad s){Player p=captain(s);if(p==null)return s.tactics.stance;expire(System.currentTimeMillis());List<String> names=new ArrayList<>();for(Pact pact:PACTS.values())if(pact.first==p.getClanId()||pact.second==p.getClanId()){Squad other=PARTIES.get(pact.first==p.getClanId()?pact.second:pact.first);Player q=other==null?null:captain(other);if(q!=null)names.add(q.getClan().getName());}return s.tactics.stance+(names.isEmpty()?"":" / Tregua: "+String.join(", ",names));}
 static boolean engage(Pilot a,Creature t,long now){return !truce(a.p,t)&&(defenderTarget(t)||SiegeAgenda.engraving(t)||SiegeAgenda.attackingParty(t,a.squad)||now>=a.squad.nextRivalSkirmish);}
 static Creature localTarget(Pilot a){Player p=a.p;long now=System.currentTimeMillis();List<Creature> choices=new ArrayList<>();
  World.forEachVisibleObjectInRange(p,Creature.class,1400,t->{if(!(t instanceof Door)&&visible(p,t,1400)&&engage(a,t,now)&&(defenderTarget(t)||SiegeAgenda.engraving(t)||SiegeAgenda.attackingParty(t,a.squad)||a.squad.conquest&&p.calculateDistance2D(t)<700))choices.add(t);});
  Creature pick=choices.stream().max(Comparator.comparingDouble(t->score(a,t))).orElse(null);
  boolean kept=a.pursuit!=null&&now<a.pursuitUntil&&visible(p,a.pursuit,1500)&&engage(a,a.pursuit,now)&&a.pursuitOrigin!=null&&a.pursuit.calculateDistance2D(a.pursuitOrigin)<1600;
  if(kept&&(pick==null||score(a,a.pursuit)+150>=score(a,pick)))return a.pursuit;
  if(pick!=null){a.pursuit=pick;a.pursuitOrigin=new Location(p);a.pursuitUntil=now+10000;return pick;}a.pursuit=null;return null;
 }
 private static double score(Pilot a,Creature t){return (SiegeAgenda.engraving(t)?6000:0)+(SiegeAgenda.attackingLeader(t,a.squad)?3000:0)+(attacking(t,a.p)?2500:0)
  +(SiegeAgenda.attackingParty(t,a.squad)?1800:0)+(defenderTarget(t)?1400:0)+250*(1-SiegeSquadBrain.hp(t))-a.p.calculateDistance2D(t)*.4;}
 static boolean attacking(Creature t,Player p){return t.hasAI()&&(t.getAI().getAttackTarget()==p||t.getAI().getCastTarget()==p);}
 static boolean leaderMustFight(Pilot a,Creature t){return t!=null&&(attacking(t,a.p)||SiegeAgenda.attackingParty(t,a.squad)||SiegeAgenda.engraving(t)||defenderTarget(t)&&a.p.calculateDistance2D(t)<=850);}
 static boolean unsafeArea(Pilot a,Skill skill,Creature target){if(!skill.hasNegativeEffect()||skill.getAffectRange()<=0||skill.getTargetType().toString().equals("ONE"))return false;
  Creature center=skill.getTargetType().toString().contains("AURA")?a.p:target;
  return World.getFirstVisibleObjectInRange(center,Creature.class,skill.getAffectRange()+200,t->t.isPlayable()&&truce(a.p,t))!=null;}
 static boolean escortBusy(Squad s){Player lead=captain(s);return lead!=null&&s.members.stream().anyMatch(a->a.p!=lead&&!a.p.isAlikeDead()&&a.p.calculateDistance2D(lead)<=1800&&a.p.hasAI()&&visible(a.p,a.p.getAI().getAttackTarget()!=null?a.p.getAI().getAttackTarget():a.p.getAI().getCastTarget(),1400)&&defenderTarget(a.p.getAI().getAttackTarget()!=null?a.p.getAI().getAttackTarget():a.p.getAI().getCastTarget()));}
}
