from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
overlay=root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'
source=root/'source/L2J_Mobius_CT_0_Interlude'
for name in ('SkillList.java','SkillCatalogView.java'):
    rel=Path('java/org/l2jmobius/gameserver/network/serverpackets')/name
    (overlay/rel).parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/rel,overlay/rel)
for file in (root/'server/game/data/scripts/custom/SkillCatalog').glob('*.java'):
    rel=Path('dist/game/data/scripts/custom/SkillCatalog')/file.name
    for base in (source,overlay):
        (base/rel).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(file,base/rel)
shutil.copy2(root/'Start-L2Local.ps1',root/'cloud-repo/ops/windows/Start-L2Local.ps1')
print('PASS: only catalog sources and startup flag mirrored; other modules untouched.')
