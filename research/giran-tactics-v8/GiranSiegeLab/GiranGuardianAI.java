package custom.GiranSiegeLab;

import org.l2jmobius.gameserver.ai.AttackableAI;
import org.l2jmobius.gameserver.entity.WorldObject;
import custom.GiranSiegeLab.GiranGuardians.Guardian;

/** Native attack/cast/reuse/movement events, with a guarded target policy instead of generic mob retargeting. */
final class GiranGuardianAI extends AttackableAI {
 private final Guardian guardian;
 GiranGuardianAI(Guardian g){super(g);guardian=g;}
 @Override protected void thinkActive(){/* Patrol is scheduled once per second by the guardian manager. */}
 @Override protected void thinkAttack(){GiranGuardianBrain.fight(guardian,System.currentTimeMillis());}
 @Override public synchronized void setIntentionAttack(WorldObject t){if(t!=null&&GiranGuardianBrain.engageable(guardian,t.asCreature()))super.setIntentionAttack(t);}
 @Override public void notifyActionAggression(WorldObject t,int hate){if(t!=null&&GiranGuardianBrain.engageable(guardian,t.asCreature()))super.notifyActionAggression(t,hate);}
}
