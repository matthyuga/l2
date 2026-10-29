from pathlib import Path
import json, hashlib, shutil, subprocess
from datetime import datetime
stage=Path(__file__).resolve().parent
root=stage.parents[4]
client=root.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((stage/'verification.json').read_text())
p=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){exit 1}"],capture_output=True)
assert p.returncode==0,'Cierra L2 antes de instalar'
assert not proof['installed'],'Control already installed'
for name,before in proof['before'].items():assert sha(client/name)==before,'Concurrent change: '+name
backup=root/'backups'/('hellgames-label-load-control-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
info=json.loads((stage.parent/'installed.json').read_text())
manifestpath=Path(info['backup'])/'manifest.json'
shutil.copy2(manifestpath,backup/'original-manifest.json')
manifest=json.loads(manifestpath.read_text(encoding='utf-8-sig'))
for name in proof['before']:
    shutil.copy2(client/name,backup/name)
    shutil.copy2(stage/name,client/name)
    assert sha(client/name)==sha(stage/name)
    entry=next(x for x in manifest if Path(x['target'])==client/name)
    entry['installed']=sha(client/name)
manifestpath.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
proof.update(installed=True,backup=str(backup))
(stage/'verification.json').write_text(json.dumps(proof,indent=2))
print('Installed native halo control and encoded custom package. Reopen L2; no GS restart needed.')
