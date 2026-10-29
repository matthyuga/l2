from pathlib import Path
import json,hashlib
s=Path(__file__).resolve().parent;root=Path('E:/l2-local')
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
    p=Path(row['path'])
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],'Later change: '+str(p)
for row in m['files']:
    if Path(row['path']).name=='PvpSiegeBrain.java':
        data=(s/'src/custom/ElvenPvpRoom/PvpSiegeBrain.java').read_bytes();Path(row['path']).write_bytes(data);row['installed_sha256']=hashlib.sha256(data).hexdigest()
(s/'installation.json').write_text(json.dumps(m,indent=2))
print('Final brain sources synchronized; manifest updated with owned-player-only party filter.')
