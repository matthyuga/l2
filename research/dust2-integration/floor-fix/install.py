import pathlib,sys,json,hashlib,subprocess,shutil,datetime
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id;exit 0"],text=True).strip(),'Client must remain closed'
assert not (D/'installation.json').exists(),'Repair already installed'
audit=json.loads((D/'audit.json').read_text());assert sha(CLIENT/'Maps/24_19.unr')==audit['source_map_sha256'];assert sha(CLIENT/'StaticMeshes/HGDust2Arena.usx')==audit['source_mesh_sha256']
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Edit
old=Edit(CLIENT/'Maps/24_19.unr');new=Edit(D/'stage/Maps/24_19.unr');preserved=0
assert len(old.exports)==len(new.exports)
for a,b in zip(old.exports,new.exports):
 if a['name'].startswith('HGDust2Arena'):continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
for e in new.exports:
 if e['name'].startswith('HGDust2Arena'):
  p=new.props(e);assert p['bWorldGeometry'] and p['bStatic'] and not p['bUseCylinderCollision']
backup=ROOT/'backups'/('dust2-collision-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(backup=str(backup),files=[],preserved_map_payloads=preserved,client_physics_verified=False)
m=json.loads((BASE/'installation.json').read_text())
for rel in ['StaticMeshes/HGDust2Arena.usx','Maps/24_19.unr']:
 target=CLIENT/rel;source=D/'client'/rel;saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(source)))
(backup/'manifest.json').write_text(json.dumps(report,indent=2));(D/'installation.json').write_text(json.dumps(report,indent=2))
for row in report['files']:
 target=pathlib.Path(row['target']);assert sha(target)==row['before_sha256'];shutil.copy2(D/'client'/target.relative_to(CLIENT),target);assert sha(target)==row['after_sha256']
 for item in m['files']:
  if pathlib.Path(item['target'])==target:item['after_sha256']=row['after_sha256']
m['collision_format_fix']=report;(BASE/'installation.json').write_text(json.dumps(m,indent=2));(pathlib.Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2));print('COLLISION_FIX_INSTALLED',backup,'map payloads preserved',preserved)
