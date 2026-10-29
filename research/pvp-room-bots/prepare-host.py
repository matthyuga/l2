from pathlib import Path
s=Path(__file__).resolve().parent
src=Path('E:/l2-local/server/game/data/scripts/custom/ElvenPvpRoom/PvpRoundRooms.java').read_text()
src=src.replace(' private long lastUi;',' private long lastUi;\n private final PvpRoomBots bots;')
src=src.replace('  if(live){','  bots=new PvpRoomBots(this);\n  if(live){',1)
src=src.replace('   case "entrar", "elven"','   case "bots" -> { if(!p.isGM())p.sendMessage("Comando reservado a GM.");else bots.command(p,Arrays.copyOfRange(args,1,args.length)); }\n   case "entrar", "elven"',1)
src=src.replace('   }\n  }catch(Exception e){LOG.log(Level.SEVERE,"PvP room tick failed",e);}', '   }\n   bots.tick(now);\n  }catch(Exception e){LOG.log(Level.SEVERE,"PvP room tick failed",e);}')
src=src.replace(' public synchronized void closeForVerification(){',' public synchronized void closeForVerification(){bots.stopAll();')
api='''
 // Package-scoped bot bridge. Every caller runs under this controller's monitor.
 RoundState botState(Mode mode){return rooms.get(mode).state;}
 long botNow(){return clock.getAsLong();}
 long botVoteDuration(){return config.voteNanos;}
 List<Player> botParticipants(Mode mode){List<Player> result=new ArrayList<>();for(Visit v:visits.values())if(v.room==rooms.get(mode))result.add(v.player);return result;}
 boolean botJoin(Player p,Mode mode){enter(p,mode);return visits.containsKey(p.getObjectId());}
 void botForget(Player p){Visit v=visits.get(p.getObjectId());if(v!=null)cleanup(v);returns.keySet().removeIf(k->k.startsWith(p.getObjectId()+":"));}
 void botReposition(Player p){
  Visit v=visits.get(p.getObjectId());if(v==null)throw new IllegalStateException("Bot has no visit");
  int team=v.room.state.team(p.getObjectId());Location destination=map(v.room).safe(map(v.room).spawns().get(team));
  v.lastInside=destination;v.pendingMapTravel=false;v.exitStarted=0;v.commandExit=false;v.shown=-1;
  travel(p,destination,instance(v.room).getId());
 }
'''
src=src.replace(' public synchronized void closeForVerification(){',api+' public synchronized void closeForVerification(){')
dest=s/'src/custom/ElvenPvpRoom/PvpRoundRooms.java';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(src)
print('Bot controller bridge prepared without touching active lobby.')
