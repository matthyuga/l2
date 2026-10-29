from pathlib import Path
root=Path('E:/l2-local');s=Path(__file__).resolve().parent
text=(root/'server/game/data/scripts/custom/ElvenPvpRoom/PvpRoomBots.java').read_text()
a=text.index(' private Player create()');b=text.index('\n private void verifyOwned',a)
text=text[:a]+''' private Player create()throws Exception{return PvpSiegeRoster.acquire();}
'''+text[b:]
a=text.index(' private void verifyOwned');b=text.index('\n void tick',a)
text=text[:a]+''' private void verifyOwned(Bot bot){if(!PvpSiegeRoster.owned(bot.player))throw new IllegalStateException("Bot no reservado por esta sala");}
'''+text[b:]
text=text.replace('   LOG.info("PvpRoomBots: started', '   PvpSiegeBrain.regroup(host,mode,g);\n   LOG.info("PvpRoomBots: started')
text=text.replace('   try{for(Bot bot:g.bots)', '   try{PvpSiegeBrain.regroup(host,g.mode,g);for(Bot bot:g.bots)')
text=text.replace('p.doRevive();p.fullRestore();host.botReposition(p);','p.doRevive();PvpSiegeRoster.prepare(p);host.botReposition(p);')
a=text.index('    Player target=null;');b=text.index('\n   }}catch(Exception e)',a)
text=text[:a]+'''    List<Player> opponents=new ArrayList<>();
    for(Bot other:g.bots){Player q=other.player;if(q!=p&&!q.isDead()&&q.isOnline()&&q.getClient()==null&&PvpSiegeRoster.owned(q)&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1)opponents.add(q);}
    Player target=PvpSiegeBrain.target(p,opponents);
    if(target!=null&&!p.isCastingNow()&&!p.isTeleporting()){PvpSiegeBrain.act(p,target);g.combatOrders++;}
'''+text[b:]
a=text.index('  for(Bot bot:g.bots){verifyOwned(bot);Player p=bot.player;host.botForget(p);')
b=text.index('\n  LOG.info("PvpRoomBots: stopped',a)
text=text[:a]+'''  PvpSiegeBrain.clearGroup(g);
  for(Bot bot:g.bots){verifyOwned(bot);Player p=bot.player;host.botForget(p);PvpSiegeRoster.release(p);}
'''+text[b:]
dest=s/'src/custom/ElvenPvpRoom/PvpRoomBots.java';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
print('Prepared same-schema bot controller and dedicated native roster/brain helpers.')
