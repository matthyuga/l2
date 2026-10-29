package org.l2jmobius.gameserver.mechanics;

import java.lang.ref.WeakReference;
import java.util.concurrent.TimeUnit;

import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.mechanics.skill.Skill;

/** Last accepted direct hit on a Player; never inferred from a mutable current target. */
public final class DirectThreat
{
	public static final long MAX_AGE_NANOS = TimeUnit.SECONDS.toNanos(30);
	private static final ThreadLocal<Context> CURRENT = new ThreadLocal<>();

	private record Context(Creature attacker, Creature primary) {}

	public record Entry(WeakReference<Creature> responsible, long time, int instanceId) {}

	public static final class Scope implements AutoCloseable
	{
		private final Context previous;

		private Scope(Context context)
		{
			previous = CURRENT.get();
			CURRENT.set(context);
		}

		@Override
		public void close()
		{
			if (previous == null)
			{
				CURRENT.remove();
			}
			else
			{
				CURRENT.set(previous);
			}
		}
	}

	private DirectThreat() {}

	public static Scope begin(Creature attacker, Creature primary, Skill skill)
	{
		// Explicit individually aimed skills, including areas centered on a selected enemy.
		if ((skill != null) && ((skill.getCastRange() < 0) || !hasIndividualTarget(skill)))
		{
			primary = null;
		}
		return new Scope(new Context(attacker, primary));
	}

	private static boolean hasIndividualTarget(Skill skill)
	{
		return switch (skill.getTargetType())
		{
			case ONE, AREA, AREA_UNDEAD, FRONT_AREA, BEHIND_AREA, UNDEAD, ENEMY_SUMMON -> true;
			default -> false;
		};
	}

	public static Creature responsible(Creature attacker)
	{
		if (attacker == null)
		{
			return null;
		}
		if (attacker.isPet())
		{
			return attacker.asPet().getOwner();
		}
		if (attacker.isSummon())
		{
			return attacker.asSummon().getOwner();
		}
		return attacker;
	}

	public static void onDamage(Player victim, Creature attacker, double damage, boolean dot, boolean consumption)
	{
		final Context context = CURRENT.get();
		if (dot || consumption || !Double.isFinite(damage) || (damage <= 0) || (context == null) ||
			(context.attacker() != attacker) || (context.primary() != victim) || victim.isAlikeDead())
		{
			return;
		}
		final Creature owner = responsible(attacker);
		if ((owner == null) || (owner == victim) || (owner.getInstanceId() != victim.getInstanceId()))
		{
			return;
		}
		victim.setLastDirectThreat(new Entry(new WeakReference<>(owner), System.nanoTime(), victim.getInstanceId()));
	}

	public static Creature last(Player victim)
	{
		final Entry entry = victim.getLastDirectThreat();
		if ((entry == null) || ((System.nanoTime() - entry.time()) > MAX_AGE_NANOS) || (entry.instanceId() != victim.getInstanceId()))
		{
			return null;
		}
		return entry.responsible().get();
	}
}
