from pathlib import Path
ROOT=Path('E:/l2-local');S=Path(__file__).resolve().parent
p=(ROOT/'research/elven-rooms/VerifyElvenV2.java').read_text()
p=p.replace('public class VerifyElvenV2','public class VerifyElvenFlagV3')
p=p.replace('SkillData.getInstance().getSkill(1204,1).applyEffects(p,p);','''SkillData.getInstance().getSkill(1204,1).applyEffects(p,p);
  // Test fixture: install a real continuous debuff deterministically, without a combat success roll.
  var weakness=SkillData.getInstance().getSkill(1164,19);
  var weaknessInfo=new org.l2jmobius.gameserver.mechanics.skill.BuffInfo(p,p,weakness);
  weakness.applyEffectScope(org.l2jmobius.gameserver.mechanics.skill.EffectScope.GENERAL,weaknessInfo,false,true);
  p.getEffectList().add(weaknessInfo);
  require(p.isAffectedBySkill(1164),"Fixture failed to install debuff before entry");''')
p=p.replace('p.setCurrentHp(p.getMaxHp()*0.6);', 'p.addTimeStamp(SkillData.getInstance().getSkill(1204,1),120000);\n  p.setCurrentHp(p.getMaxHp()*0.6);')
p=p.replace('require(p.isAffectedBySkill(1204),context+" removed buff");','''require(p.isAffectedBySkill(1204),context+" removed buff");
  long remaining=p.getSkillRemainingReuseTime(SkillData.getInstance().getSkill(1204,1).getReuseHashCode());
  require(p.isAffectedBySkill(1164),context+" removed debuff");
  require(remaining>110000 && remaining<=120000,context+" reset/removed cooldown");''')
p=p.replace('int room=p.getInstanceId();','''require(p.getPvpFlag()==1,"Entry missing forced flag");
    var flags=org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager.getInstance();
    p.setPvpFlagLasts(1);flags.add(p);flags.run();
    require(p.getPvpFlag()==1,"Combat timer cleared room flag");
    p.updatePvPFlag(0);require(p.getPvpFlag()==1,"Direct flag clear bypassed ownership");
    p.updatePvPFlag(2);require(p.getPvpFlag()==1,"Forced flag blinked");
    report.append("PASS forced flag on entry; expired timer/direct clear/blink cannot remove it.\\n");
    int room=p.getInstanceId();''')
p=p.replace('VoicedCommandHandler.getInstance().getHandler("elvenpvp").onCommand("elvenpvp",p,"entrar");','''long entryDeadline=System.currentTimeMillis()+120000;
    p.setPvpFlagLasts(entryDeadline);p.startPvPFlag();
    VoicedCommandHandler.getInstance().getHandler("elvenpvp").onCommand("elvenpvp",p,"entrar");
    require(p.getPvpFlagLasts()==entryDeadline,"Entry changed previous combat deadline");''')
p=p.replace('require(timer.getLong(visit)>0,"Boundary did not start timer");','require(timer.getLong(visit)>0,"Boundary did not start timer");require(p.getPvpFlag()==1,"Boundary lost flag");')
p=p.replace('sameResources(p,hp,mp,cp,"Cancel return");','sameResources(p,hp,mp,cp,"Cancel return");require(p.getPvpFlag()==1,"Cancel lost flag");')
p=p.replace('sameResources(p,hp,mp,cp,"Exit");require(!visits.containsKey', '''sameResources(p,hp,mp,cp,"Exit");require(!flags.isForced(p),"Exit retained room ownership");require(p.getPvpFlag()==0,"Expired combat flag survived final exit");require(!visits.containsKey''')
p=p.replace('visits.remove(p.getObjectId());p.setInstanceId(0);tick.invoke(lobby);require(!visits.containsKey(p.getObjectId()),"External departure retained visit");','''require(p.getPvpFlag()==1,"Death/revive observation lost flag");
    long futureDeadline=System.currentTimeMillis()+90000;
    p.setPvpFlagLasts(futureDeadline);flags.add(p);
    p.setInstanceId(0);tick.invoke(lobby);
    require(!visits.containsKey(p.getObjectId()) && !flags.isForced(p),"External departure retained visit/ownership");
    require(p.getPvpFlag()==1 && p.getPvpFlagLasts()==futureDeadline,"External departure erased/reset existing combat deadline");
    p.setPvpFlagLasts(1);flags.run();require(p.getPvpFlag()==0,"Normal flag no longer expires outside room");
    report.append("PASS boundary/cancel/death/revive keep flag; exit releases ownership; external exit preserves original combat deadline; normal expiry works.\\n");
    verifyOwners(p,report);''')
p=p.replace('probe.abortAttack();probe.abortCast();probe.stopAllEffects();probe.deleteMe();probe.setOnlineStatus(false,false);','''var flags=org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager.getInstance();
    flags.release(probe,"hellgames:elven-room:3051");flags.release(probe,"test:first");flags.release(probe,"test:second");
    probe.abortAttack();probe.abortCast();probe.stopAllEffects();probe.deleteMe();probe.setOnlineStatus(false,false);flags.run();''')
idx=p.index(' @SuppressWarnings("unchecked")')
p=p[:idx]+''' static void verifyOwners(Player p,StringBuilder report)throws Exception
 {
  var flags=org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager.getInstance();
  p.setPvpFlagLasts(0);p.stopPvPFlag();
  flags.force(p,"test:first");flags.force(p,"test:first");flags.force(p,"test:second");
  flags.release(p,"unknown");flags.release(p,"test:first");require(flags.isForced(p) && p.getPvpFlag()==1,"One owner cleared another");
  flags.release(p,"test:second");require(!flags.isForced(p) && p.getPvpFlag()==0,"Idempotent owner was counted twice");
  flags.force(p,"test:first");
  var failure=new java.util.concurrent.atomic.AtomicReference<Throwable>();
  Thread worker=new Thread(()->{try{for(int i=0;i<200;i++){flags.force(p,"test:second");flags.release(p,"test:second");}}catch(Throwable t){failure.set(t);}});
  worker.start();for(int i=0;i<200;i++){p.updatePvPFlag(0);require(p.getPvpFlag()==1,"Concurrent owner clear removed forced flag");}
  worker.join(5000);require(!worker.isAlive() && failure.get()==null,"Concurrent owner operation failed/stalled");flags.release(p,"test:first");
  report.append("PASS concurrent owner changes and flag-clear attempts preserve anchor ownership.\\n");
  var a=new org.l2jmobius.gameserver.entity.zone.type.FlagPvPZone(990001);
  var b=new org.l2jmobius.gameserver.entity.zone.type.FlagPvPZone(990002);
  var enter=method(a.getClass(),"onEnter",org.l2jmobius.gameserver.entity.actor.Creature.class);
  var exit=method(a.getClass(),"onExit",org.l2jmobius.gameserver.entity.actor.Creature.class);
  enter.invoke(a,p);enter.invoke(b,p);exit.invoke(a,p);require(p.getPvpFlag()==1,"Native overlapping zones lost flag");
  exit.invoke(b,p);require(p.getPvpFlag()==0,"Last native zone did not release flag");
  flags.force(p,"test:first");enter.invoke(a,p);exit.invoke(a,p);require(p.getPvpFlag()==1,"Native zone exit cleared room owner");
  long deadline=System.currentTimeMillis()+90000;p.setPvpFlagLasts(deadline);flags.release(p,"test:first");
  require(p.getPvpFlag()==1 && p.getPvpFlagLasts()==deadline,"Owner release changed normal combat deadline");
  p.setPvpFlagLasts(1);flags.run();require(p.getPvpFlag()==0,"Normal combat flag expiry after forced release failed");
  flags.force(p,"test:first");p.setOnlineStatus(false,false);flags.run();
  require(!flags.isForced(p) && p.getPvpFlag()==0,"Logout leaked ownership");p.setOnlineStatus(true,false);
  report.append("PASS independent/idempotent owners, native zone overlap, room+zone overlap, combat deadline preservation and offline cleanup.\\n");
 }
''' + p[idx:]
(S/'VerifyElvenFlagV3.java').write_text(p,encoding='utf-8')
(S/'verify-state-v3.mf').write_text('Manifest-Version: 1.0\nAgent-Class: VerifyElvenFlagV3\n\n')
print('Prepared live transient-character verification')
