/*
 * Copyright (c) 2013 L2jMobius
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
 * IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
package org.l2jmobius.gameserver.taskmanagers;

import java.util.Set;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Player;

/**
 * @author Mobius
 */
public class PvpFlagTaskManager implements Runnable
{
	private static final Set<Player> PLAYERS = ConcurrentHashMap.newKeySet();
	/** Independent, idempotent owners: releasing one room/zone cannot clear another. */
	private static final Map<Player, Set<String>> FORCED = new ConcurrentHashMap<>();
	private static boolean _working = false;
	
	protected PvpFlagTaskManager()
	{
		ThreadPool.schedulePriorityTaskAtFixedRate(this, 1000, 1000);
	}
	
	@Override
	public void run()
	{
		if (_working)
		{
			return;
		}
		
		_working = true;
		
		try
		{
			// Logout may remove a player from the world before its room observes departure.
			for (Player player : FORCED.keySet())
			{
				synchronized (player)
				{
					if (!player.isOnline())
					{
						FORCED.remove(player);
						PLAYERS.remove(player);
						player.updatePvPFlag(0);
					}
				}
			}
			final long currentTime = System.currentTimeMillis();
			for (Player player : PLAYERS)
			{
				if (isForced(player))
				{
					continue;
				}
				if (currentTime > player.getPvpFlagLasts())
				{
					player.stopPvPFlag();
				}
				else if (currentTime > (player.getPvpFlagLasts() - 20000))
				{
					player.updatePvPFlag(2);
				}
				else
				{
					player.updatePvPFlag(1);
				}
			}
		}
		finally
		{
			_working = false;
		}
	}

	public boolean isForced(Player player)
	{
		final Set<String> owners = FORCED.get(player);
		return (owners != null) && !owners.isEmpty();
	}

	/** Never changes the existing combat deadline or any character resources. */
	public void force(Player player, String owner)
	{
		if ((owner == null) || owner.isBlank())
		{
			throw new IllegalArgumentException("A forced PvP flag needs an owner");
		}
		synchronized (player)
		{
			FORCED.computeIfAbsent(player, key -> ConcurrentHashMap.newKeySet()).add(owner);
			player.updatePvPFlag(1);
		}
	}

	/** Only the last owner releases the flag; a still-live combat deadline is preserved. */
	public void release(Player player, String owner)
	{
		synchronized (player)
		{
			final Set<String> owners = FORCED.get(player);
			if ((owners == null) || !owners.remove(owner) || !owners.isEmpty())
			{
				return;
			}
			FORCED.remove(player);
			if (player.isOnline() && (player.getPvpFlagLasts() > System.currentTimeMillis()))
			{
				// Do not call updatePvPStatus: it replaces the deadline and ignores PvP zones.
				player.startPvPFlag();
			}
			else
			{
				PLAYERS.remove(player);
				player.updatePvPFlag(0);
			}
		}
	}
	
	public void add(Player player)
	{
		PLAYERS.add(player);
	}
	
	public void remove(Player player)
	{
		PLAYERS.remove(player);
	}
	
	public static PvpFlagTaskManager getInstance()
	{
		return SingletonHolder.INSTANCE;
	}
	
	private static class SingletonHolder
	{
		protected static final PvpFlagTaskManager INSTANCE = new PvpFlagTaskManager();
	}
}
