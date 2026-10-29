package org.l2jmobius.gameserver.entity.zone;
import org.l2jmobius.gameserver.entity.actor.Creature;
public abstract class ZoneType {public ZoneType(int id){} protected abstract void onEnter(Creature c);protected abstract void onExit(Creature c); public abstract void onDieInside(Creature c);public abstract void onReviveInside(Creature c);}