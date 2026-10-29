from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((D/'installation.json').read_text());assert m['live_installed'] and not m.get('rolled_back')
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client'
for x in m['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256'],x['target']
for x in reversed(m['files']):Path(x['target']).write_bytes(Path(x['backup']).read_bytes())
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Restored HSL v1; full removal remains available via v1 rollback.')
