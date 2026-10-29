from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists()
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close Lineage II'
assert json.loads((D/'verification.json').read_text())['native_materials_loaded']==144
assets=json.loads((D/'assets-manifest.json').read_text());items=[]
def add(target,data):
 target=Path(target);items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()),after_sha256=sha(data)))
for f in assets['files']:
 target=Path(f['target']);assert sha(target.read_bytes())==f['before_sha256'];data=(D/'stage'/target.name).read_bytes();assert sha(data)==f['after_sha256'];add(target,data)
for relative in ['2026-10-26-tanda2-v9','2026-10-26-appearance-v12','2026-10-24/hair-native121-v6']:
 manifest=D.parent/relative/'installation.json';m=json.loads(manifest.read_text());changed=False
 for item in m.get('files',[]):
  for new in assets['files']:
   if item.get('target')==new['target']:
    assert item['after_sha256']==new['before_sha256'];item['after_sha256']=new['after_sha256'];changed=True
 if changed:
  m['hair_alpha_v3']=str(D/'installation.json');data=json.dumps(m,indent=2).encode();add(manifest,data);backupManifest=Path(m['backup'])/'manifest.json'
  if backupManifest.exists():add(backupManifest,data)
backup=P/'backups'/('hair-alpha-v3-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
m=dict(backup=str(backup),live_installed=False,files=[],materials=144,only_framebuffer_blending_changed=True,mesh_texture_pixels_alpha_unchanged=True,hsl_dll_server_unchanged=True,visual_validation='pending')
for i,item in enumerate(items):
 saved=backup/(str(i)+'-'+Path(item['target']).name);shutil.copy2(item['target'],saved);m['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved)))
def save():
 (D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2))
save()
try:
 for item in items:
  target=Path(item['target']);assert sha(target.read_bytes())==item['before_sha256'];target.write_bytes(item['data'])
 for x in m['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256']
 m['live_installed']=True;save()
except Exception:
 for x in reversed(m['files']):Path(x['target']).write_bytes(Path(x['backup']).read_bytes())
 m['failed_and_restored']=True;save();raise
print('Installed hair material cutout fix in shared SysTextures for both profiles; original files backed up:',backup)
