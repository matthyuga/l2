from pathlib import Path
root=Path('E:/l2-local');s=Path(__file__).resolve().parent
text=(root/'server/game/data/scripts/custom/ElvenPvpRoom/PvpRoundRooms.java').read_text()
text=text.replace(' private final PvpRoomBots bots;',' private final PvpRoomBots bots;\n private final PvpRoomUi ui;')
text=text.replace('  bots=new PvpRoomBots(this);','  bots=new PvpRoomBots(this);ui=new PvpRoomUi(this);')
text=text.replace('   case "votar" -> {','''   case "elegir" -> {
    Visit v=visits.get(p.getObjectId());
    if(v!=null&&args.length==3&&p.getInstanceId()==instance(v.room).getId())try{
     long token=Long.parseLong(args[1]);RoundState state=v.room.state;long now=clock.getAsLong();state.advance(now);
     if(token==state.generation()&&state.phase()==Phase.VOTING&&!state.hasVoted(p.getObjectId())&&config.maps.containsKey(args[2]))ui.choose(p,token,args[2],config.maps.get(args[2]).name(),now,now+state.voteRemaining(now));
    }catch(NumberFormatException ignored){}
   }
   case "votar" -> {''')
text=text.replace('v.votePanel=true;v.scorePanel=false;showVote(v);\n    }','v.votePanel=true;v.scorePanel=false;showVote(v);\n    }',1)
text=text.replace('  listen(v);','  listen(v);ui.attach(p);',1)
text=text.replace('v.commandExit=true;v.exitStarted=clock.getAsLong();v.shown=-1;', 'v.commandExit=true;beginExit(v,clock.getAsLong());')
text=text.replace(' private void returnInside(Visit v){',''' private void beginExit(Visit v,long now){v.exitStarted=now;v.shown=-1;ui.exit(v.player,now,now+EXIT);}
 void uiCancelExit(Player p){
  Visit v=visits.get(p.getObjectId());if(v==null||v.exitStarted==0||p.isDead()||p.isTeleporting())return;
  if(clock.getAsLong()-v.exitStarted>=EXIT)return;
  returnInside(v);
 }
 private void returnInside(Visit v){''')
text=text.replace('  v.exitStarted=0;v.commandExit=false;v.shown=-1;screen(p,"Salida cancelada"','  ui.invalidate(p,PvpRoomUi.Kind.EXIT);v.exitStarted=0;v.commandExit=false;v.shown=-1;screen(p,"Salida cancelada"')
text=text.replace('  victim.exitStarted=0;','  ui.invalidate(victim.player,PvpRoomUi.Kind.EXIT);victim.exitStarted=0;')
text=text.replace('  visits.remove(v.player.getObjectId());','  ui.detach(v.player);visits.remove(v.player.getObjectId());')
# No text-based bars remain. Vote choices use a genuine timed native confirmation.
start=text.index(' private String bar(');end=text.index('\n private static String escape',start)
text=text[:start]+text[end:]
text=text.replace('b.append(bar(s.voteRemaining(now),config.voteNanos))','b.append(PvpRoomUi.progress(s.voteRemaining(now),config.voteNanos))')
text=text.replace('"votar "+s.generation()+" "+entry.getKey()','"elegir "+s.generation()+" "+entry.getKey()')
text=text.replace('   v.lastInside=map(r).safe(map(r).spawns().get(team));','   ui.invalidate(v.player,PvpRoomUi.Kind.EXIT);ui.invalidate(v.player,PvpRoomUi.Kind.VOTE);v.lastInside=map(r).safe(map(r).spawns().get(team));')
text=text.replace('if(p.isDead()){v.exitStarted=0;', 'if(p.isDead()){ui.invalidate(p,PvpRoomUi.Kind.EXIT);v.exitStarted=0;')
old='else {int segments=(int)((left*16+EXIT-1)/EXIT);if(segments!=v.shown){v.shown=segments;screen(p,"Saliendo "+bar(left,EXIT)+" "+String.format(Locale.ROOT,"%.1f",left/1e9)+" s",ExShowScreenMessage.BOTTOM_CENTER,600);}}'
assert old in text
text=text.replace(old,'// Native ConfirmDlg animates its own countdown; never resend it per tick.')
text=text.replace('else {v.exitStarted=now;v.shown=-1;}','else beginExit(v,now);')
assert '"|".repeat' not in text and '".".repeat' not in text
text=text.replace('PvpRoomUi ui;', 'PvpRoomUi roomUi;').replace('ui=new PvpRoomUi(this);','roomUi=new PvpRoomUi(this);').replace('ui.', 'roomUi.')
target=s/'src/custom/ElvenPvpRoom/PvpRoundRooms.java';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
print('Prepared native exit confirmation and graphical vote panel without client edits.')
