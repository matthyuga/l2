import pathlib,json,hashlib,subprocess,shutil,datetime
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id;exit 0"],text=True).strip(),'Client must be closed'
assert not (D/'installation.json').exists(),'Already installed'
a=json.loads((D/'audit.json').read_text());v=json.loads((D/'verification.json').read_text());assert v['upper_storey_wall_conflicts']==0 and v['native_walls_verified']==a['native_wall_actors'] and v['native_walls_verified']>1000
target=CLIENT/'Maps/24_19.unr';assert sha(target)==a['source_map_sha256'];assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==a['source_geodata_sha256']
backup=ROOT/'backups'/('dust2-native-walls-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);shutil.copy2(target,backup/'24_19.unr')
report=dict(backup=str(backup),target=str(target),before_sha256=sha(target),after_sha256=sha(D/'client/Maps/24_19.unr'),audit=a,verification=v,client_physics_verified=False)
(backup/'manifest.json').write_text(json.dumps(report,indent=2));(D/'installation.json').write_text(json.dumps(report,indent=2));shutil.copy2(D/'client/Maps/24_19.unr',target);assert sha(target)==report['after_sha256']
m=json.loads((BASE/'installation.json').read_text())
for row in m['files']:
 if pathlib.Path(row['target'])==target:row['after_sha256']=report['after_sha256']
m['native_wall_support']=report;(BASE/'installation.json').write_text(json.dumps(m,indent=2));(pathlib.Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2));print('NATIVE_WALLS_INSTALLED',v['native_walls_verified'],'actors; backup',backup)
