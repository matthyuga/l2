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
package org.l2jmobius.gameserver.network.serverpackets;

import java.util.ArrayList;
import java.util.List;

import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.gameserver.network.GameClient;
import org.l2jmobius.gameserver.network.ServerPackets;
import org.l2jmobius.gameserver.entity.actor.Player;

public class SkillList extends ServerPacket
{
	private final List<Skill> _skills = new ArrayList<>();
	
	public SkillList()
	{
	}
	
	public void addSkill(int id, int level, boolean passive, boolean disabled)
	{
		_skills.add(new Skill(id, level, passive, disabled));
	}
	
	@Override
	public void writeImpl(GameClient client, WriteBuffer buffer)
	{
		writeForPlayer(client==null?null:client.getPlayer(),buffer);
	}
	public void writeForPlayer(Player player,WriteBuffer buffer)
	{
		ServerPackets.SKILL_LIST.writeId(this, buffer);
		List<Skill> visible=wireEntries(player);
		buffer.writeInt(visible.size());
		for (Skill temp : visible)
		{
			buffer.writeInt(temp.passive);
			buffer.writeInt(temp.level);
			buffer.writeInt(temp.id);
			buffer.writeByte(temp.disabled);
		}
	}
	/** Exposes the same presentation as the wire writer for read-only verification. */
	public List<Integer> presentedSkillIds(Player player){return presented(player).stream().map(s->s.id).toList();}
	public List<Integer> wireSkillIds(Player player){return wireEntries(player).stream().map(s->s.id).toList();}
	private List<Skill> wireEntries(Player player)
	{
		List<Skill> skills=presented(player);
		if(player==null)return skills;
		var model=SkillCatalogView.model(player);
		int filter=SkillCatalogView.filter(player);
		List<Skill> result=new ArrayList<>();
		int[] lastGroup={-1,-1},columns={0,0};
		for(Skill skill:skills)
		{
			int type=skill.passive?1:0;
			int group=filter==SkillCatalogView.ALL?model.group(skill.id):filter;
			if(group!=lastGroup[type])
			{
				while(columns[type]%SkillCatalogView.COLUMNS!=0)
				{
					result.add(new Skill(SkillCatalogView.PADDING,1,skill.passive,true));columns[type]++;
				}
				for(int tile=0;tile<SkillCatalogView.COLUMNS;tile++)
					result.add(new Skill(SkillCatalogView.HEADER_BASE+group*SkillCatalogView.COLUMNS+tile,1,skill.passive,true));
				columns[type]+=SkillCatalogView.COLUMNS;lastGroup[type]=group;
			}
			result.add(skill);columns[type]++;
		}
		return result;
	}
	private List<Skill> presented(Player player)
	{
		List<Skill> visible=_skills;
		if(player!=null)
		{
			var model=SkillCatalogView.model(player);
			int filter=SkillCatalogView.filter(player);
			visible=_skills.stream().filter(s->model.visible(s.id,filter)).sorted(java.util.Comparator
				.comparingInt((Skill s)->model.rank(s.id))
				.thenComparing(s->{var known=player.getKnownSkill(s.id);return known==null?"":known.getName();},String.CASE_INSENSITIVE_ORDER)
				.thenComparingInt(s->s.id)).toList();
		}
		return visible;
	}
	
	private static class Skill
	{
		public int id;
		public int level;
		public boolean passive;
		public boolean disabled;
		
		Skill(int pId, int pLevel, boolean pPassive, boolean pDisabled)
		{
			id = pId;
			level = pLevel;
			passive = pPassive;
			disabled = pDisabled;
		}
	}
}
