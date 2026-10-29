from pathlib import Path
import datetime
import hashlib
import json
import subprocess
base=Path(__file__).resolve().parent;root=base.parent.parent;client=root.parent/'l2/system-hud'
sha=lambda data:hashlib.sha256(data).hexdigest()
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('L2 sigue abierto. Correccion preparada; cerrar cliente antes de instalar.')
v2=json.loads((base.parent/'map-fog-giran-v2/installation.json').read_text(encoding='utf8'))
previous=next(x for x in v2['files'] if Path(x['path']).name=='d3d9.dll')
target=client/'d3d9.dll';before=target.read_bytes()
if sha(before)!=previous['after_sha256']:raise SystemExit('La DLL cambio desde V2; se cancela.')
if sha((client/'NWindow.dll').read_bytes())!=v2['client_original_nwindow_sha256']:raise SystemExit('NWindow no coincide.')
backup=root/'backups'/('map-fog-alpha-v3-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
(backup/'d3d9.dll').write_bytes(before)
after=(base/'build/d3d9.dll').read_bytes();target.write_bytes(after)
assert target.read_bytes()==after
manifest={'state':'installed-pending-client-launch','target':str(target),'backup':str(backup/'d3d9.dll'),
          'before_sha256':sha(before),'after_sha256':sha(after),'visual_validation':'pending',
          'assets_changed':False,'server_changed':False}
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(base/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('INSTALADO V3: opacidad de niebla aislada del foco de otras ventanas. Backup:',backup)
