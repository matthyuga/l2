"""Restore Dust2 first, before any older airship/dock rollback."""
import pathlib,subprocess,json,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True)
assert not state.strip(),'Client/GameServer must be closed'
m=json.loads((D/'installation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for i in m['files']:
 p=pathlib.Path(i['target']);assert p.is_relative_to(ROOT) or p.is_relative_to(CLIENT);assert p.exists() and sha(p)==i['after_sha256'],'Changed since install: '+str(p)
 if i['existed']:assert sha(pathlib.Path(i['backup']))==i['before_sha256']
for i in reversed(m['files']):
 p=pathlib.Path(i['target'])
 if i['existed']:shutil.copy2(i['backup'],p)
 else:p.unlink()
m['restored']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Dust2 removed. Previous airship/dock/client map preserved.')
