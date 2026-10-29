package org.l2jmobius.gameserver.entity.actor;
public class Creature { public boolean isPlayer(){return this instanceof Player;} public Player asPlayer(){return (Player)this;} }