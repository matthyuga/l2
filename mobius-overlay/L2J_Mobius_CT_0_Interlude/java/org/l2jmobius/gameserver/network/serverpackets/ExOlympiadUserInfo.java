/*
 * This file is part of the L2J Mobius project.
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
package org.l2jmobius.gameserver.network.serverpackets;

import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.network.GameClient;
import org.l2jmobius.gameserver.network.ServerPackets;

/**
 * @author godson
 */
public class ExOlympiadUserInfo extends ServerPacket
{
	private final int _side;
	private final int _objectId;
	private final String _name;
	private final int _classId;
	private final int _currentHp;
	private final int _maxHp;
	private final int _currentCp;
	private final int _maxCp;
	
	public ExOlympiadUserInfo(Player player, int side)
	{
		_side = side;
		_objectId = player.getObjectId();
		_name = player.getName();
		_classId = player.getPlayerClass().getId();
		_currentHp = (int) player.getCurrentHp();
		_maxHp = player.getMaxHp();
		_currentCp = (int) player.getCurrentCp();
		_maxCp = player.getMaxCp();
	}
	
	/**
	 * Reuses the native Olympiad target HUD for a fake player.
	 * @param npc fake player NPC
	 * @param side target slot (normally 1)
	 */
	public ExOlympiadUserInfo(Npc npc, int side)
	{
		_side = side;
		_objectId = npc.getObjectId();
		_name = npc.getName();
		_classId = npc.getTemplate().getFakePlayerInfo().getPlayerClass().getId();
		_currentHp = (int) npc.getCurrentHp();
		_maxHp = npc.getMaxHp();
		_currentCp = (int) npc.getCurrentCp();
		_maxCp = npc.getMaxCp();
	}
	
	@Override
	public void writeImpl(GameClient client, WriteBuffer buffer)
	{
		ServerPackets.EX_OLYMPIAD_USER_INFO.writeId(this, buffer);
		buffer.writeByte(_side);
		buffer.writeInt(_objectId);
		buffer.writeString(_name);
		buffer.writeInt(_classId);
		buffer.writeInt(_currentHp);
		buffer.writeInt(_maxHp);
		buffer.writeInt(_currentCp);
		buffer.writeInt(_maxCp);
	}
}
