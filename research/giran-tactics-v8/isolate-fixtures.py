from pathlib import Path
p=Path(__file__).resolve().parent/'GiranSiegeLab/GiranDefenseVerification.java';t=p.read_text()
t=t.replace('private Player scout;','private Player scout;private final Map<Npc,CreatureAI> guardAIs=new HashMap<>();private final Map<Npc,Boolean> guardInvul=new HashMap<>();')
t=t.replace('GiranGuardians.instance.verificationPaused=true;', '''GiranGuardians.instance.verificationPaused=true;
  // Opt-in fixtures isolate the tested player/route; production native guards and V7 guardians keep their AI.
  for(WorldObject o:World.getVisibleObjects())if(o instanceof Npc n&&SiegeSquadBrain.GUARDS.contains(n.getId())&&c.checkIfInZone(n.getX(),n.getY(),n.getZ())){
   guardInvul.put(n,n.isInvul());n.abortAttack();n.abortCast();if(n instanceof Attackable mob)mob.clearAggroList();n.setInvul(true);
   if(!(n instanceof GiranGuardians.Guardian)){guardAIs.put(n,n.getAI());n.setAI(new CreatureAI(n));}
  }''',1)
t=t.replace('GiranTacticsVerification.run(squads,','for(var g:GiranGuardians.instance.actors)g.setInvul(true);GiranTacticsVerification.run(squads,')
t=t.replace('SiegeTactics.reset();if(claimed)', 'for(var row:guardInvul.entrySet())if(row.getKey().isSpawned())row.getKey().setInvul(row.getValue());for(var row:guardAIs.entrySet())if(row.getKey().isSpawned()){row.getKey().setAI(row.getValue());row.getKey().getAI().setIntentionActive();}SiegeTactics.reset();if(claimed)')
p.write_text(t,encoding='utf-8')
print('Native unrelated guards isolated only inside opt-in fixtures and restored at cleanup.')
