package custom.GiranSiegeLab;

import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.mechanics.siege.Castle;

/** Shared siege legality and observable coordination; never grants neutral-player aggression. */
public final class GiranRules {
 public static Castle castle(){return CastleManager.getInstance().getCastleById(3);}
 public static boolean defender(Player p){var c=castle();return p!=null&&(p.getClanId()==c.getOwnerId()&&c.getOwnerId()!=0||c.getSiege().checkIsDefender(p.getClan()));}
 public static boolean doorAllowed(Player p,Door d){var c=d.getCastle();return c!=null&&c.getSiege().isInProgress()&&c.getSiege().checkIsAttacker(p.getClan())&&p.getClanId()!=c.getOwnerId()&&!d.isWall()&&!d.isDead()&&!d.isOpen()&&d.isAutoAttackable(p);}
 static boolean hostile(Player p,Creature t){var c=castle();Player q=t==null?null:t.isSummon()?t.asSummon().getOwner():t.asPlayer();
  if(q==null||q==p||q.getClan()==null||p.getClan()==null||p.getClanId()==q.getClanId()||p.getAllyId()!=0&&p.getAllyId()==q.getAllyId())return false;
  if(!c.getSiege().isInProgress()||!c.checkIfInZone(q.getX(),q.getY(),q.getZ())||!c.checkIfInZone(p.getX(),p.getY(),p.getZ()))return false;
  return (c.getSiege().checkIsAttacker(p.getClan())||defender(p))&&(c.getSiege().checkIsAttacker(q.getClan())||defender(q))&&!p.isSiegeFriend(t)&&t.isAutoAttackable(p);
 }
 public static int doorSupport(Player p,Door d){if(!doorAllowed(p,d))return 0;int[] votes={0};
  World.forEachVisibleObjectInRange(p,Creature.class,1600,a->{Player ally=a.isSummon()?a.asSummon().getOwner():a.asPlayer();if(ally!=null&&doorAllowed(ally,d)&&a.hasAI()&&a.getAI().getAttackTarget()==d)votes[0]++;});return votes[0];
 }
 static Door sharedDoor(Player p){return castle().getDoors().stream().filter(d->doorAllowed(p,d)&&p.calculateDistance2D(d)<1600&&doorSupport(p,d)>0).max(Comparator.comparingDouble(d->doorSupport(p,d)*300-p.calculateDistance2D(d)*.1)).orElse(null);}
}
