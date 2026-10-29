from pathlib import Path
import hashlib, json, shutil
r=Path(__file__).resolve().parents[1]
s=r/'research/giran-assault-v6'
b=r/'backups/giran-assault-v6-2026-10-11'
assert not s.exists(), 'Stage already exists'
(s/'GiranSiegeLab').mkdir(parents=True)
(b/'GiranSiegeLab').mkdir(parents=True)
manifest={}
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    shutil.copy2(p,s/'GiranSiegeLab'/p.name)
    shutil.copy2(p,b/'GiranSiegeLab'/p.name)
    manifest['GiranSiegeLab/'+p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest['GameServer.jar']=hashlib.sha256((r/'server/libs/GameServer.jar').read_bytes()).hexdigest()
(s/'baseline.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for name in ['install.ps1','state.js']:
    t=(r/'research/giran-orders-v5'/name).read_text(encoding='utf-8-sig').replace('giran-orders-v5-2026-10-11','giran-assault-v6-2026-10-11')
    (s/name).write_text(t,encoding='utf-8')
(s/'sources.txt').write_text('\n'.join(p.as_posix() for p in (s/'GiranSiegeLab').glob('*.java')),encoding='utf-8')
(s/'classes').mkdir()
t=(s/'GiranSiegeLab/GiranDefenseVerification.java').read_text().replace('GIRAN_V5_VERIFY','GIRAN_V6_VERIFY').replace('GIRAN_V3_VERIFY FAILED readiness','GIRAN_V6_VERIFY FAILED readiness')
(s/'GiranSiegeLab/GiranDefenseVerification.java').write_text(t,encoding='utf-8')
print('V6 isolated stage and baseline ready; runtime untouched.')
