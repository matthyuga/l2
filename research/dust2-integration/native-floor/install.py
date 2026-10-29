import pathlib,sys,json,hashlib,subprocess,shutil,datetime
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id;exit 0"],text=True).strip(),'Client must stay closed'
assert not (D/'installation.json').exists(),'Already installed'
a=json.loads((D/'audit.json').read_text());target=CLIENT/'Maps/24_19.unr';assert sha(target)==a['source_map_sha256'];assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==a['source_geodata_sha256'];assert a['reachable_layers']==61234 and a['floor_actors']==1591
backup=ROOT/'backups'/('dust2-native-floor-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);shutil.copy2(target,backup/'24_19.unr')
report=dict(backup=str(backup),target=str(target),before_sha256=sha(target),after_sha256=sha(D/'client/Maps/24_19.unr'),audit=a,client_physics_verified=False)
(backup/'manifest.json').write_text(json.dumps(report,indent=2));(D/'installation.json').write_text(json.dumps(report,indent=2));shutil.copy2(D/'client/Maps/24_19.unr',target);assert sha(target)==report['after_sha256']
m=json.loads((BASE/'installation.json').read_text())
for r in m['files']:
 if pathlib.Path(r['target'])==target:r['after_sha256']=report['after_sha256']
m['native_floor_support']=report;(BASE/'installation.json').write_text(json.dumps(m,indent=2));(pathlib.Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2))
print('NATIVE_FLOOR_INSTALLED',a['floor_actors'],'actors; backup',backup)
