from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parents[3];b=r/'backups/summon-buffs-2026-10-10'
paths=[r/'server/libs/GameServer.jar',r/'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/actor/instance/SchemeBuffer.java',r/'server/game/data/html/mods/SchemeBuffer/50008.htm']
assert not b.exists(),'Do not overwrite backup'
b.mkdir(parents=True);report={}
for p in paths:shutil.copy2(p,b/p.name);report[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(b/'original-hashes.json').write_text(json.dumps(report,indent=2))
print('Backed up current buffer source, menu and GameServer.')
