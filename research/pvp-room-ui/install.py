from pathlib import Path
from datetime import datetime
import hashlib,json
root=Path('E:/l2-local').resolve();s=Path(__file__).resolve().parent
if (s/'installation.json').exists():raise SystemExit('Already installed; preserve backup')
previous=json.loads((root/'research/pvp-room-bots/installation.json').read_text())
known={row['path']:row for row in previous['files']}
backup=root/'backups'/('pvp-room-ui-'+datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
def sha(data):return hashlib.sha256(data).hexdigest()
base=Path('L2J_Mobius_CT_0_Interlude')
for prefix in [root/'server',root/'source'/base/'dist',root/'cloud-repo/mobius-overlay'/base/'dist']:
    folder=prefix/'game/data/scripts/custom/ElvenPvpRoom'
    for name in ['PvpRoundRooms.java','PvpRoomUi.java']:
        path=(folder/name).resolve();path.relative_to(root);before=path.read_bytes() if path.exists() else None
        if name=='PvpRoundRooms.java':assert sha(before)==known[str(path)]['installed_sha256'],'Later host change: '+str(path)
        else:assert before is None,'Existing UI module'
        data=(s/'src/custom/ElvenPvpRoom'/name).read_bytes();saved=backup/path.relative_to(root)
        changes.append({'path':str(path),'existed':before is not None,'backup':str(saved) if before is not None else None,'before_sha256':sha(before) if before is not None else None,'installed_sha256':sha(data),'previous':before,'data':data})
for row in changes:
    if row['previous'] is not None:
        p=Path(row['backup']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['previous'])
for row in changes:
    p=Path(row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['data']);row.pop('data');row.pop('previous')
(s/'installation.json').write_text(json.dumps({'backup':str(backup),'files':changes,'activation':'next normal four-room startup; no active client or server restart','client_changed':False,'core_changed':False,'exit_cancel':'native Cancel returns to last interior position, explicitly requested by user'},indent=2))
print(json.dumps({'backup':str(backup),'files':len(changes),'client_changed':False,'restart':False}))
