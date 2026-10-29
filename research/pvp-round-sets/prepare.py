from pathlib import Path
import shutil
r=Path('E:/l2-local');s=Path(__file__).resolve().parent;src=s/'src/custom/ElvenPvpRoom';runtime=r/'server/game/data/scripts/custom/ElvenPvpRoom'
for p in runtime.glob('*.java'):shutil.copy2(p,src/p.name)
p=src/'PvpSiegeRoster.java';t=p.read_text().replace(' public static synchronized Player acquire()throws Exception{',' public static synchronized Player acquire()throws Exception{\n  Player prepared=PvpRoundSets.prepared();if(prepared!=null){if(!owned(prepared))throw new IllegalStateException("Prepared bot no longer owned");return prepared;}');p.write_text(t)
p=src/'PvpRoomBots.java';t=p.read_text().replace('   try{PvpSiegeBrain.regroup(host,g.mode,g);','   try{PvpRoundSets.warm(this,g.mode,g.bots.size(),g.profile);PvpSiegeBrain.regroup(host,g.mode,g);')
t=t.replace('  Group g=groups.remove(mode);if(g==null)return;','  PvpRoundSets.cancel(this,mode);Group g=groups.remove(mode);if(g==null)return;')
t=t.replace('  return result.toString();','  return result.toString()+PvpRoundSets.status(this);');p.write_text(t)
p=src/'PvpRoundRooms.java';t=p.read_text();a=t.index(' private void roundFinished(');b=t.index('\n private String score(',a);old=t[a:b]
new=old.replace('  r.state.restart(now);','  PvpRoundSets.Batch nextBatch=PvpRoundSets.beforeRound(bots,r.state.mode);\n  r.state.restart(now);\n  List<Visit> shuffled=new ArrayList<>();for(Visit v:visits.values())if(v.room==r)shuffled.add(v);Collections.shuffle(shuffled);')
new=new.replace('  for(Visit v:visits.values())if(v.room==r){','  for(Visit v:shuffled){')
new=new.replace('\n }','\n  PvpRoundSets.afterRound(bots,nextBatch);\n }')
assert new!=old and 'afterRound' in new;t=t[:a]+new+t[b:];p.write_text(t)
print('Prepared shuffled round admission and asynchronous distinct bot batches.')
