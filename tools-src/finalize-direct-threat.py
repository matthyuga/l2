from pathlib import Path
import shutil

root=Path('E:/l2-local')
src=root/'source/L2J_Mobius_CT_0_Interlude'
overlay=root/'cloud-repo/mobius-overlay'
backup=root/'backups/direct-threat-2026-10-12'
files=[
 'java/org/l2jmobius/gameserver/mechanics/DirectThreat.java',
 'java/org/l2jmobius/gameserver/entity/actor/Creature.java',
 'java/org/l2jmobius/gameserver/entity/actor/Player.java',
 'java/org/l2jmobius/gameserver/entity/actor/status/PlayerStatus.java',
 'java/org/l2jmobius/gameserver/entity/actor/tasks/creature/HitTask.java',
 'java/org/l2jmobius/gameserver/entity/actor/tasks/creature/MagicUseTask.java',
 'dist/game/data/scripts/handlers/MasterHandler.java',
 'dist/game/data/scripts/handlers/chat/commands/voiced/ThreatCommand.java']
for f in files:
    dest=overlay/'L2J_Mobius_CT_0_Interlude'/f
    saved=backup/dest.relative_to(root)
    if dest.exists() and not saved.exists():
        saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(dest,saved)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src/f,dest)
    misplaced=overlay/f
    misplaced_backup=backup/misplaced.relative_to(root)
    if misplaced.exists():
        assert misplaced.read_bytes()==(src/f).read_bytes(), misplaced
        if misplaced_backup.exists(): shutil.copy2(misplaced_backup,misplaced)
        else:
            misplaced.unlink()
            parent=misplaced.parent
            while parent != overlay and not any(parent.iterdir()):
                parent.rmdir()
                parent=parent.parent
print('Overlay synchronized in existing project hierarchy.')
