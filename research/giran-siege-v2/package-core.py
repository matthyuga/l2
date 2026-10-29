from pathlib import Path
import zipfile,hashlib,json
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent
old=r/'backups/giran-siege-v2-2026-10-11/GameServer-before.jar';stage=s/'GameServer-staged.jar'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(old.read_bytes())==sha((r/'backups/giran-siege-v2-2026-10-11/GameServer-before.jar').read_bytes()),'Concurrent core edit'
prefix='org/l2jmobius/gameserver/geoengine/pathfinding/'
entries={prefix+'PathFinding.class',prefix+'PathFinding$SingletonHolder.class','org/l2jmobius/gameserver/entity/clan/ClanMember.class'}
with zipfile.ZipFile(old) as z,zipfile.ZipFile(stage,'w') as out:
 for info in z.infolist():out.writestr(info,(s/'core-classes'/info.filename).read_bytes() if info.filename in entries else z.read(info.filename))
with zipfile.ZipFile(old) as a,zipfile.ZipFile(stage) as b:
 assert a.namelist()==b.namelist();changed=[n for n in a.namelist() if a.read(n)!=b.read(n)];assert set(changed)<=entries and prefix+'PathFinding.class' in changed
proof={'old':sha(old.read_bytes()),'new':sha(stage.read_bytes()),'entries_changed':changed,'all_other_entries_identical':True}
(s/'core-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
