from pathlib import Path
import json,hashlib,subprocess,shutil
from datetime import datetime
s=Path(__file__).resolve().parent;root=s.parents[4];client=root.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((s/'verification.json').read_text());assert not proof['installed']
p=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){exit 1}"],capture_output=True)
assert p.returncode==0,'L2 sigue abierto; cerrar antes de instalar.'
for name,digest in proof['before'].items():assert sha(client/name)==digest,'Archivo modificado: '+name
for name in ['HGLabelNpcV2.u','HGLabelNpcV2.int']:assert not (client/name).exists()
buildlog=(s.parent/'npc-hook-build.log').read_bytes()
buildtext=buildlog.decode('utf-16' if buildlog.startswith(b'\xff\xfe') else 'utf-8-sig')
assert 'PASS native object reads: Npc.Destroyed' in buildtext
backup=root/'backups'/('hellgames-label-npc-hook-v2-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
info=json.loads((s.parent/'installed.json').read_text());manifestpath=Path(info['backup'])/'manifest.json'
manifest=json.loads(manifestpath.read_text(encoding='utf-8-sig'));shutil.copy2(manifestpath,backup/'original-manifest.json')
shutil.copy2(client/'npcgrp.dat',backup/'npcgrp.dat')
for name in ['npcgrp.dat','HGLabelNpcV2.u','HGLabelNpcV2.int']:
 shutil.copy2(s/name,client/name);assert sha(client/name)==sha(s/name)
 if name=='npcgrp.dat':next(r for r in manifest if Path(r['target'])==client/name)['installed']=sha(client/name)
 else:manifest.append(dict(target=str(client/name),previous=None,before=None,installed=sha(client/name)))
manifestpath.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
proof.update(installed=True,backup=str(backup));(s/'verification.json').write_text(json.dumps(proof,indent=2))
print('Installed explicit NPC lifecycle hook. NPC/display/stats/server unchanged; visual verification pending.')
