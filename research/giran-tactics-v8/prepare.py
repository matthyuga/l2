from pathlib import Path
s=Path(__file__).resolve().parent
p=s/'GiranSiegeLab/GiranDefenseVerification.java';t=p.read_text()
t=t.replace('rival.getAI().setIntentionAttack(leader);entrance.rivalUntil=0;','leader.setInvul(false);rival.setInvul(false);rival.getAI().setIntentionAttack(leader);entrance.rivalUntil=0;')
t=t.replace('rival.getAI().setIntentionIdle();GiranSiegeLab.move(leader,GiranSiegeLab.camp(1,0));','rival.getAI().setIntentionIdle();leader.setInvul(true);rival.setInvul(true);GiranSiegeLab.move(leader,GiranSiegeLab.camp(1,0));')
t=t.replace('guardians;human not loaded','guardians,all16attackers/threat damage,tactical truces,throne services;human not loaded')
t=t.replace('if(claimed)SoloArenaGauntlet.releasePilot();','SiegeTactics.reset();if(claimed)SoloArenaGauntlet.releasePilot();')
p.write_text(t,encoding='utf-8')
(s/'sources.txt').write_text('\n'.join(p.as_posix() for p in (s/'GiranSiegeLab').glob('*.java')),encoding='utf-8')
print('V8 native fixtures ready; no runtime mutation.')
