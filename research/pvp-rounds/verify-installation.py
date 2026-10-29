from pathlib import Path
import json,hashlib,zipfile
s=Path(__file__).resolve().parent;root=Path('E:/l2-local')
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],str(p)
for row in m['geodata']:
    p=root/'server/game/data/geodata'/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
core=Path(m['core_baseline']['path']);assert hashlib.sha256(core.read_bytes()).hexdigest()==m['core_baseline']['sha256'],'Unexpected runtime core mutation'
patches={}
for stage in ['20261015-elven-position-sync','20261015-pvp-rounds']:
    pending=root/'server/pending-core-patches'/stage
    for p in pending.rglob('*.class'):patches[p.relative_to(pending).as_posix()]=p.read_bytes()
with zipfile.ZipFile(core) as old,zipfile.ZipFile(s/'next-start-core.jar','w',zipfile.ZIP_DEFLATED) as out:
    for info in old.infolist():out.writestr(info,patches.pop(info.filename,old.read(info.filename)))
    for name,data in patches.items():out.writestr(name,data)
result={'status':'PASS','installed_files_verified':len(m['files']),'geodata_regions_verified':2,'active_lobby':'previous Elven lobby','next_start_lobby':'four-mode PvpRoundRooms','cold_start':'pending; server deliberately not restarted with client open','visual_checks':'pending at home'}
(s/'final-installation-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
