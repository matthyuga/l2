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
package org.l2jmobius.gameserver.entity.actor.status;

import org.l2jmobius.gameserver.entity.actor.Attackable;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.network.serverpackets.ExOlympiadUserInfo;

public class AttackableStatus extends NpcStatus
{
	private double _currentCp;
	
	public AttackableStatus(Attackable activeChar)
	{
		super(activeChar);
	}
	
	@Override
	public void reduceCp(int value)
	{
		if (getActiveChar().isFakePlayer())
		{
			setCurrentCp(_currentCp - value);
		}
	}
	
	@Override
	public double getCurrentCp()
	{
		return getActiveChar().isFakePlayer() ? _currentCp : 0;
	}
	
	@Override
	public void setCurrentCp(double newCp)
	{
		final Attackable attackable = getActiveChar();
		if (attackable.isFakePlayer())
		{
			_currentCp = Math.max(0, Math.min(newCp, attackable.getMaxCp()));
		}
	}
	
	@Override
	public void reduceHp(double value, Creature attacker)
	{
		reduceHp(value, attacker, true, false, false);
	}
	
	@Override
	public void reduceHp(double value, Creature attacker, boolean awake, boolean isDOT, boolean isHpConsumption)
	{
		final Attackable attackable = getActiveChar();
		if (attackable.isDead())
		{
			return;
		}
		
		// Fake players use a real CP reserve, just like player characters.
		double hpDamage = value;
		if ((value > 0) && attackable.isFakePlayer() && !isHpConsumption && (attacker != null) && (attacker != attackable) && (attacker.isPlayable() || attacker.isFakePlayer()) && !(attackable.isInvul() && !isDOT))
		{
			final double currentCp = getCurrentCp();
			if (currentCp >= hpDamage)
			{
				setCurrentCp(currentCp - hpDamage);
				hpDamage = 0;
			}
			else
			{
				hpDamage -= currentCp;
				setCurrentCp(0);
			}
		}
		
		if (hpDamage > 0)
		{
			if (attackable.isOverhit())
			{
				attackable.setOverhitValues(attacker, hpDamage);
			}
			else
			{
				attackable.overhitEnabled(false);
			}
		}
		else
		{
			attackable.overhitEnabled(false);
		}
		
		super.reduceHp(hpDamage, attacker, awake, isDOT, isHpConsumption);
		
		// Refresh the native CP/HP target panel for every player currently targeting this fake player.
		if (attackable.isFakePlayer() && (value > 0))
		{
			for (Creature listener : attackable.getStatus().getStatusListener())
			{
				if ((listener != null) && listener.isPlayer() && (listener.getTarget() == attackable))
				{
					listener.sendPacket(new ExOlympiadUserInfo(attackable, 1));
				}
			}
		}
		
		if (!attackable.isDead())
		{
			// And the attacker's hit didn't kill the mob, clear the over-hit flag.
			attackable.overhitEnabled(false);
		}
	}
	
	@Override
	public Attackable getActiveChar()
	{
		return super.getActiveChar().asAttackable();
	}
}
