from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;m=json.loads((D/'installation.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert m['live_installed'] and not m.get('rolled_back')
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close Lineage II'
for x in m['files']:
 assert sha(x['target'])==x['after_sha256'],('Later change requires review',x['target'])
 if x['backup']:assert sha(x['backup'])==x['before_sha256']
for x in reversed(m['files']):
 p=Path(x['target'])
 if x['backup']:p.write_bytes(Path(x['backup']).read_bytes())
 else:p.unlink()
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8')
print('Restored pre-v13 files. Warning: pre-v13 custom Orc head had a reported crash; review before enabling those faces.')
