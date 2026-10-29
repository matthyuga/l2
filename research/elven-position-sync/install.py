from pathlib import Path
import json,hashlib,shutil
R=Path('E:/l2-local');S=Path(__file__).resolve().parent
if (S/'installation.json').exists():raise SystemExit('Already installed')
m=json.loads((S/'baseline.json').read_text());rows=[]
for row in m['files']:
    p=Path(row['path'])
    if p.exists()!=row['existed'] or (p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=row['before_sha256']):raise RuntimeError('Concurrent change: '+str(p))
for row in m['files']:
    p=Path(row['path'])
    if p.name=='GameServer.jar':continue
    if p.name=='PvpRooms.java':src=S/'PvpRooms.java'
    elif p.name=='RoomTeleportSync.java':src=S/'RoomTeleportSync.java'
    else:src=S/'src'/p.as_posix().split('L2J_Mobius_CT_0_Interlude/',1)[1]
    p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p);rows.append({**row,'installed_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
pending=R/'server/pending-core-patches/20261015-elven-position-sync'
if pending.exists():raise RuntimeError('Pending patch already exists')
for src in (S/'compiled/org').rglob('*.class'):
    p=pending/src.relative_to(S/'compiled');p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p)
    rows.append({'path':str(p),'existed':False,'backup':None,'installed_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(S/'installation.json').write_text(json.dumps({'backup':m['backup'],'files':rows,'runtime_jar_unchanged_until_next_start':True,'pending_patch':str(pending)},indent=2),encoding='utf-8')
print('Installed source/scripts and staged persistent core patch for next startup')
