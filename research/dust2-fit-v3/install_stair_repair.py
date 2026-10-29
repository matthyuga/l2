from pathlib import Path
import datetime,json,hashlib,shutil
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=json.loads((D/'stairs-repair-audit.json').read_text());target=R/'server/game/data/geodata/24_19.l2j';assert sha(target)==a['before_sha256'],'Concurrent geodata change'
backup=R/'backups'/('dust2-stairs-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);shutil.copy2(target,backup/'24_19.l2j')
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3']:shutil.copy2(D.parent/name/'installation.json',backup/(name+'-installation.json'))
shutil.copy2(D/'stairs-repaired.l2j',target);assert sha(target)==a['after_sha256']
a.update(backup=str(backup),target=str(target),installed=True,server_probe_pending=True)
(D/'stairs-repair-installation.json').write_text(json.dumps(a,indent=2));print('Installed with backup',backup)
