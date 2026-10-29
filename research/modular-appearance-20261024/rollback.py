from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;P=D.parents[1];m=json.loads((D/'installation.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert m['live_installed'] and not m.get('rolled_back'),'Not an active installation'
for i in m['files']:
 target=Path(i['target']);assert target.exists() and sha(target.read_bytes())==i['after_sha256'],('Later modifications require review',target)
 if i['backup']:assert sha(Path(i['backup']).read_bytes())==i['before_sha256']
pid=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"],text=True).strip()
assert pid,'Start GameServer first so saved modular profiles can be restored safely'
subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(D/'rollback-agent.jar'),str(D)],check=True)
assert (D/'live-rollback-proof.txt').exists()
for i in reversed(m['files']):
 target=Path(i['target'])
 if i['backup']:target.write_bytes(Path(i['backup']).read_bytes())
 else:target.unlink()
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('RESTORED: original files, live classes and legacy profiles. Hair correction preserved.')
