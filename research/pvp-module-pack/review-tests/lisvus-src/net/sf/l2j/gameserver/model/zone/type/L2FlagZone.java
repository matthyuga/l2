/*
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program. If not, see <http://www.gnu.org/licenses/>.
 */
/** * PvP Flag Zone * @author JMD */
package net.sf.l2j.gameserver.model.zone.type;

import net.sf.l2j.gameserver.model.L2Character;
import net.sf.l2j.gameserver.model.actor.instance.L2PcInstance;
import net.sf.l2j.gameserver.model.zone.L2ZoneSpawn;

public class L2FlagZone extends L2ZoneSpawn
{
	public L2FlagZone(int id)
	{
		super(id);
	}
	
	@Override
	protected void onEnter(L2Character character)
	{
		if (character instanceof L2PcInstance)
		{
			((L2PcInstance) character).updatePvPFlag(1);
			((L2PcInstance) character).sendMessage("You have entered a flag zone.");
			((L2PcInstance) character).broadcastUserInfo();
		}
	}
	
	@Override
	protected void onExit(L2Character character)
	{
		if (character instanceof L2PcInstance)
		{
			((L2PcInstance) character).updatetPvPFlag(0);
			((L2PcInstance) character).sendMessage("You have left a flag zone.");
			((L2PcInstance) character).broadcastUserInfo();
		}
	}
	
	public void onDieInside(L2Character character)
	{
		onEnter(character);
	}
	
	public void onReviveInside(L2Character character)
	{
		onEnter(character);
	}
}