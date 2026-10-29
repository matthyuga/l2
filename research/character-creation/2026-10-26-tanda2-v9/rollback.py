from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');m=json.loads((D/'installation.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert m['live_installed'] and not m.get('rolled_back')
ps=['powershell','-NoProfile','-Command'];assert not subprocess.check_output(ps+["if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client first'
for item in m['files']:
 assert sha(Path(item['target']).read_bytes())==item['after_sha256'],('Later modification; review before rollback',item['target'])
 if item['backup']:assert sha(Path(item['backup']).read_bytes())==item['before_sha256']
pid=subprocess.check_output(ps+["Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"],text=True).strip()
assert pid.isdigit(),'Start GameServer to restore its live validator'
subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(D.parent/'2026-10-24/integration/reload-appearance.jar'),str(D/'rollback-live')],check=True,timeout=60)
assert (D/'rollback-live/server-reload-proof.txt').exists()
for item in reversed(m['files']):
 target=Path(item['target'])
 if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
 else:target.unlink()
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8')
print('RESTORED: pre-Tanda 2 files and live hair limits. No characters changed; Tanda 2 indices remain saved for reinstall.')
