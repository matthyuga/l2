from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parents[1];s=r/'research/giran-tactics-v8';b=r/'backups/giran-tactics-v8-2026-10-11'
assert not s.exists(), 'Stage already exists'
(s/'GiranSiegeLab').mkdir(parents=True);(b/'GiranSiegeLab').mkdir(parents=True)
m={}
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    shutil.copy2(p,s/'GiranSiegeLab'/p.name);shutil.copy2(p,b/'GiranSiegeLab'/p.name);m['GiranSiegeLab/'+p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
for k,p in {'GameServer.jar':r/'server/libs/GameServer.jar','geodata/23_22.l2j':r/'server/game/data/geodata/23_22.l2j','npcs/giran_lab_guardians.xml':r/'server/game/data/stats/npcs/custom/giran_lab_guardians.xml'}.items():m[k]=hashlib.sha256(p.read_bytes()).hexdigest()
(s/'baseline.json').write_text(json.dumps(m,indent=2))
for name in ['install.ps1','state.js']:(s/name).write_text((r/'research/giran-guardians-v7'/name).read_text(encoding='utf-8-sig').replace('giran-guardians-v7-2026-10-11','giran-tactics-v8-2026-10-11'),encoding='utf-8')
t=(s/'GiranSiegeLab/GiranDefenseVerification.java').read_text().replace('GIRAN_V7_VERIFY','GIRAN_V8_VERIFY')
t=t.replace('GiranGuardianVerification.run(squads, this::check, (condition,why,timeout)->waitFor(condition,why,timeout));','GiranTacticsVerification.run(squads, this::check, (condition,why,timeout)->waitFor(condition,why,timeout));')
t=t.replace('Siege of', 'Siege of')
(s/'GiranSiegeLab/GiranDefenseVerification.java').write_text(t,encoding='utf-8');(s/'classes').mkdir()
print('V8 stage and baseline saved; runtime unchanged.')
