from pathlib import Path
from datetime import datetime
import hashlib,json
root=Path('E:/l2-local').resolve();s=Path(__file__).resolve().parent
if (s/'installation.json').exists():raise SystemExit('Already installed; preserve original backup')
backup=root/'backups'/('pvp-room-bots-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
previous=json.loads((root/'research/pvp-rounds/installation.json').read_text())
known={row['path']:row for row in previous['files']}
changes=[]
def sha(data):return hashlib.sha256(data).hexdigest()
base=Path('L2J_Mobius_CT_0_Interlude')
for prefix in [root/'server',root/'source'/base/'dist',root/'cloud-repo/mobius-overlay'/base/'dist']:
    folder=prefix/'game/data/scripts/custom/ElvenPvpRoom'
    for name in ['PvpRoundRooms.java','PvpRoomBots.java']:
        path=(folder/name).resolve();path.relative_to(root)
        before=path.read_bytes() if path.exists() else None
        if name=='PvpRoundRooms.java':assert sha(before)==known[str(path)]['installed_sha256'],'Later host changes: '+str(path)
        else:assert before is None,'Existing bots module: '+str(path)
        data=(s/'src/custom/ElvenPvpRoom'/name).read_bytes();saved=backup/path.relative_to(root)
        changes.append({'path':str(path),'existed':before is not None,'backup':str(saved) if before is not None else None,'before_sha256':sha(before) if before is not None else None,'installed_sha256':sha(data),'previous':before,'data':data})
for row in changes:
    if row['previous'] is not None:
        p=Path(row['backup']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['previous'])
for row in changes:
    p=Path(row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['data']);row.pop('previous');row.pop('data')
(s/'installation.json').write_text(json.dumps({'backup':str(backup),'files':changes,'activation':'next normal startup of four-room lobby; bots remain off until GM command','core_changed':False,'client_changed':False},indent=2))
print(json.dumps({'backup':str(backup),'files':len(changes),'auto_start_bots':False}))
