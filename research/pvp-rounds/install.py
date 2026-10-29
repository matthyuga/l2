from pathlib import Path
from datetime import datetime
import json,hashlib,shutil,zipfile
root=Path('E:/l2-local').resolve();s=Path(__file__).resolve().parent
manifest=s/'installation.json'
if manifest.exists():raise SystemExit('Already installed; inspect manifest rather than overwriting backup')
backup=root/'backups'/('pvp-rounds-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
pending=root/'server/pending-core-patches/20261015-pvp-rounds'
changes=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def add(target,data):
    target=target.resolve();rel=target.relative_to(root);old=target.read_bytes() if target.exists() else None
    saved=backup/rel
    changes.append({'path':str(target),'existed':old is not None,'backup':str(saved) if old is not None else None,'before_sha256':sha(old) if old is not None else None,'installed_sha256':sha(data),'data':data,'previous':old})
base=Path('L2J_Mobius_CT_0_Interlude')
for src in (s/'src/org').rglob('*.java'):
    rel=src.relative_to(s/'src');data=src.read_bytes()
    add(root/'source'/base/'java'/rel,data)
    add(root/'cloud-repo/mobius-overlay'/base/'java'/rel,data)
for prefix in [root/'server',root/'source'/base/'dist',root/'cloud-repo/mobius-overlay'/base/'dist']:
    scripts=prefix/'game/data/scripts/custom/ElvenPvpRoom'
    for src in (s/'src/custom/ElvenPvpRoom').glob('*.java'):add(scripts/src.name,src.read_bytes())
    old=scripts/'PvpRooms.java';text=old.read_text()
    before='public static void main(String[] args) { new PvpRooms(); }'
    assert text.count(before)==1,str(old)
    add(old,text.replace(before,'public static void main(String[] args) { /* Replaced by PvpRoundRooms.main. Legacy implementation retained for rollback. */ }').encode())
    add(prefix/'game/config/Custom/PvpRooms.properties',(s/'PvpRooms.properties').read_bytes())
    xml='''<?xml version="1.0" encoding="UTF-8"?>
<instance id="3060" allowRandomWalk="false" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../xsd/instance.xsd">
 <allowSummon val="true" />
 <PvPInstance val="true" />
 <spawnPoints startPosType="FIXED"><Location x="45150" y="52100" z="-2792" /></spawnPoints>
 <exitPoint x="83425" y="148585" z="-3406" />
</instance>
'''
    target=prefix/'game/data/instances/custom/hellgames_pvp_rounds.xml'
    assert not target.exists(),'Template already exists'
    add(target,xml.encode())
core=['entity/actor/Player.class','entity/actor/Creature.class','entity/actor/status/PlayerStatus.class','entity/actor/status/SummonStatus.class','mechanics/skill/Skill.class','managers/RoomCombatRules.class','managers/RoomCombatRules$Member.class']
for rel in core:
    p=Path('org/l2jmobius/gameserver')/rel
    assert not (pending/p).exists(),'Pending file already exists'
    add(pending/p,(s/'compiled'/p).read_bytes())
# Include only class entries actually changed. Nested switch-map classes retain their original code.
jar=root/'server/libs/GameServer.jar';jar_backup=backup/'server/libs/GameServer.jar';jar_backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(jar,jar_backup)
for row in changes:
    if row['previous'] is not None:
        p=Path(row['backup']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['previous'])
for row in changes:
    p=Path(row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['data'])
    row.pop('data');row.pop('previous')
result={'backup':str(backup),'files':changes,'pending_patch':str(pending),'core_baseline':{'path':str(jar),'backup':str(jar_backup),'sha256':sha(jar_backup.read_bytes())},'activation':'next normal server startup; current user/session untouched','geodata':json.loads((s/'geodata-sources.json').read_text())}
manifest.write_text(json.dumps(result,indent=2))
print(json.dumps({'backup':str(backup),'files':len(changes),'pending_core_classes':len(core)}))
