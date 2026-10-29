from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3]
backup=root/'backups/skill-groups-v3-2026-10-10'
paths=[root.parent/'l2/system-hud'/n for n in ('Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat')]
paths += [root/'server/libs/GameServer.jar']
paths += list((root/'server/game/data/scripts/custom/SkillCatalog').glob('*.java'))
paths += [root/'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/network/serverpackets'/n for n in ('SkillList.java','SkillCatalogView.java')]
assert not backup.exists(), 'Backup already exists; do not overwrite'
backup.mkdir(parents=True)
report={}
for i,p in enumerate(paths):
    shutil.copy2(p,backup/(str(i)+'-'+p.name))
    report[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(backup/'original-hashes.json').write_text(json.dumps(report,indent=2))
print('Backed up',len(paths),'current files.')
