from pathlib import Path
from datetime import datetime
import hashlib,json
root=Path('E:/l2-local').resolve();s=Path(__file__).resolve().parent
if (s/'installation.json').exists():raise SystemExit('Already installed')
old=json.loads((root/'research/pvp-room-bots/installation.json').read_text());known={r['path']:r for r in old['files']}
backup=root/'backups'/('pvp-siege-bots-'+datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
def sha(b):return hashlib.sha256(b).hexdigest()
base=Path('L2J_Mobius_CT_0_Interlude')
for prefix in [root/'server',root/'source'/base/'dist',root/'cloud-repo/mobius-overlay'/base/'dist']:
    folder=prefix/'game/data/scripts/custom/ElvenPvpRoom'
    for name in ['PvpRoomBots.java','PvpSiegeRoster.java','PvpSiegeBrain.java']:
        p=(folder/name).resolve();p.relative_to(root);before=p.read_bytes() if p.exists() else None
        if name=='PvpRoomBots.java':assert sha(before)==known[str(p)]['installed_sha256'],'Later bot controller change'
        else:assert before is None,'Existing helper'
        data=(s/'src/custom/ElvenPvpRoom'/name).read_bytes();saved=backup/p.relative_to(root)
        changes.append({'path':str(p),'existed':before is not None,'backup':str(saved) if before is not None else None,'before_sha256':sha(before) if before is not None else None,'installed_sha256':sha(data),'previous':before,'data':data})
for row in changes:
    if row['previous'] is not None:
        p=Path(row['backup']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['previous'])
for row in changes:
    p=Path(row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['data']);row.pop('data');row.pop('previous')
(s/'installation.json').write_text(json.dumps({'backup':str(backup),'files':changes,'activation':'live bot controller hot replacement and next normal startup','client_changed':False,'core_changed':False,'source_profiles':'native offline lab profiles temporarily reserved; class/subclass/clan recipe untouched'},indent=2))
print(json.dumps({'backup':str(backup),'files':len(changes)}))
