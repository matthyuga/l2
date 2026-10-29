from pathlib import Path
import subprocess,json,hashlib,shutil
from datetime import datetime
s=Path(__file__).resolve().parent;root=s.parents[4];client=root.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((s/'verification.json').read_text());assert not proof['installed']
p=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){exit 1}"],capture_output=True)
assert p.returncode==0,'Cierra L2 antes de instalar.'
assert sha(client/'HellgamesLabelsV1.u')==proof['before_sha256'],'Paquete modificado despues de preparar'
assert not (client/'HGLabelArtV3.u').exists()
log=(s/'verify.log').read_bytes();text=log.decode('utf-16' if log.startswith(b'\xff\xfe') else 'utf-8-sig')
assert 'PASS: EventGold.Label' in text and 'PASS: EventGold.Motes' in text
backup=root/'backups'/('hellgames-label-compact-v3-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
shutil.copy2(client/'HellgamesLabelsV1.u',backup/'HellgamesLabelsV1.u')
info=json.loads((s.parent/'installed.json').read_text());manifestpath=Path(info['backup'])/'manifest.json'
shutil.copy2(manifestpath,backup/'original-manifest.json');manifest=json.loads(manifestpath.read_text(encoding='utf-8-sig'))
for name in ['HellgamesLabelsV1.u','HGLabelArtV3.u']:
 shutil.copy2(s/name,client/name);assert sha(client/name)==sha(s/name)
 if name=='HellgamesLabelsV1.u':next(r for r in manifest if Path(r['target'])==client/name)['installed']=sha(client/name)
 else:manifest.append(dict(target=str(client/name),previous=None,before=None,installed=sha(client/name)))
manifestpath.write_text(json.dumps(manifest,indent=2),encoding='utf-8');proof.update(installed=True,backup=str(backup));(s/'verification.json').write_text(json.dumps(proof,indent=2))
print('Compact transparent label installed, protected rollback updated. Ingame review pending.')
