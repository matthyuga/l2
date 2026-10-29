from pathlib import Path
import json,hashlib,subprocess,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];m=json.loads((S/'installation.json').read_text())
assert not m.get('rolled_back') and not m.get('files_restored_after_failure'),'Not an active installation'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'Cierra L2 antes de restaurar'}; if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay jugadores conectados'}"],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
for item in m['files']:assert sha(Path(item['target']))==item['after_sha256'],'Later change: '+item['target']
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"],capture_output=True,text=True)
pid=r.stdout.strip()
if pid:
    assert pid.isdigit() and int((R/'run/game.pid').read_text(encoding='utf-8-sig').strip())==int(pid),'Wrong GameServer PID'
    subprocess.run([str(R/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(S/'agent'),'AttachStickers',pid,str(S/'DeactivateStickers.jar'),str(S)],check=True,capture_output=True,timeout=60)
for item in reversed(m['files']):
    p=Path(item['target'])
    if item['backup']:shutil.copy2(item['backup'],p);assert sha(p)==item['before_sha256']
    else:p.unlink()
m['rolled_back']=True
(S/'installation.json').write_text(json.dumps(m,indent=2));(Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2))
print('RESTORED: sticker files, configuration and live handler reverted.')
