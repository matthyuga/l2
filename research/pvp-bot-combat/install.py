from pathlib import Path
from datetime import datetime
import hashlib,json
r=Path('E:/l2-local');s=Path(__file__).resolve().parent
assert not (s/'installation.json').exists(),'Already installed'
backup=r/'backups'/('pvp-bot-combat-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
old=json.loads((r/'research/pvp-siege-bots/installation.json').read_text());known={row['path']:row for row in old['files']}
rows=[]
for prefix in [r/'server',r/'source/L2J_Mobius_CT_0_Interlude/dist',r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist']:
 for name in ['PvpSiegeBrain.java','PvpSiegeRoster.java','PvpSiegeCombat.java']:
  p=prefix/'game/data/scripts/custom/ElvenPvpRoom'/name;before=p.read_bytes() if p.exists() else None
  if before is not None:assert hashlib.sha256(before).hexdigest()==known[str(p)]['installed_sha256'],'Concurrent change: '+str(p)
  data=(s/'src/custom/ElvenPvpRoom'/name).read_bytes();saved=backup/p.relative_to(r)
  rows.append(dict(path=str(p),backup=str(saved) if before is not None else None,before_sha256=hashlib.sha256(before).hexdigest() if before else None,installed_sha256=hashlib.sha256(data).hexdigest(),before=before,data=data))
for row in rows:
 if row['before'] is not None:
  p=Path(row['backup']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['before'])
for row in rows:
 Path(row['path']).write_bytes(row.pop('data'));row.pop('before')
(s/'installation.json').write_text(json.dumps(dict(backup=str(backup),files=rows,client_changed=False,core_changed=False),indent=2))
print('Installed nine mirrored files with backup: '+str(backup))
