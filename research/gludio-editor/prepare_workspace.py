from pathlib import Path
import sys,struct,json,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'gludio-sky'))
from package_tools import Edit,change_props
work=ROOT/'Working';work.mkdir(exist_ok=True)
dst=work/'24_19.unr'
if dst.exists():raise SystemExit('Working map already exists; refusing to overwrite edits.')
p=Edit(ROOT/'Packages/24_19.unr')
e=next(e for e in p.exports if e['name']=='LevelInfo0')
changes={
 'CameraLocationDynamic':p.vector('CameraLocationDynamic',(149000,42500,14700)),
 'CameraRotationDynamic':p.prop('CameraRotationDynamic',10,struct.pack('<3i',-5000,16384,0),'Rotator'),
 'CameraLocationTop':p.vector('CameraLocationTop',(149000,46700,45000)),
 'CameraLocationFront':p.vector('CameraLocationFront',(149000,46700,12000)),
 'CameraLocationSide':p.vector('CameraLocationSide',(149000,46700,12000)),
}
p.replace(e,change_props(p,e,changes));p.save(dst)
manifest=json.loads((ROOT/'snapshot.json').read_text())
unchanged=all(hashlib.sha256(Path(f['source']).read_bytes()).hexdigest()==f['sha256']==hashlib.sha256(Path(f['backup']).read_bytes()).hexdigest() for f in manifest['files'])
if not unchanged:raise RuntimeError('Live client changed since snapshot; review required.')
(ROOT/'workspace-proof.json').write_text(json.dumps({'live_and_backups_match':unchanged,'working_map':str(dst),'only_changed_export':'LevelInfo0','camera_position':[149000,42500,14700],'packages':len(manifest['files']),'ready_for_install':False},indent=2))
print('Working map prepared; originals verified unchanged.')
