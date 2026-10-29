from pathlib import Path
import shutil,hashlib,json,datetime
ROOT=Path('E:/l2-local'); STAGE=Path(__file__).resolve().parent
manifest=STAGE/'baseline.json'
if manifest.exists():raise SystemExit('Baseline already exists; refusing overwrite')
backup=ROOT/'backups'/('elven-autoflag-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
rels=['java/org/l2jmobius/gameserver/entity/actor/Player.java','java/org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager.java','java/org/l2jmobius/gameserver/entity/zone/type/FlagPvPZone.java']
targets=[ROOT/'server/libs/GameServer.jar']
for base in [ROOT/'source/L2J_Mobius_CT_0_Interlude',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude']:
    targets.extend(base/r for r in rels)
for base in [ROOT/'server/game',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
    targets.append(base/'data/scripts/custom/ElvenPvpRoom/PvpRooms.java')
rows=[]
for p in targets:
    b=backup/p.relative_to(ROOT)
    if p.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    rows.append({'path':str(p),'existed':p.exists(),'backup':str(b),'before_sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None})
(STAGE/'baseline.json').write_text(json.dumps({'backup':str(backup),'files':rows},indent=2),encoding='utf-8')
for r in rels:
    p=STAGE/'src'/r;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'source/L2J_Mobius_CT_0_Interlude'/r,p)
shutil.copy2(ROOT/'server/game/data/scripts/custom/ElvenPvpRoom/PvpRooms.java',STAGE/'PvpRooms.java')
print('Baseline saved:',backup)
