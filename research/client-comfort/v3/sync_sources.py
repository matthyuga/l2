from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent
backup=root/'backups/skill-groups-v3-2026-10-10';old=json.loads((backup/'original-hashes.json').read_text())
source=root/'source/L2J_Mobius_CT_0_Interlude';cloud=root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[]
for name in ('SkillList.java','SkillCatalogView.java'):
    rel=Path('java/org/l2jmobius/gameserver/network/serverpackets')/name
    pairs.append((source/rel,cloud/rel,old[str(source/rel)]))
rel=Path('java/org/l2jmobius/gameserver/network/clientpackets/RequestBypassToServer.java')
target=cloud/rel
if target.exists():assert target.read_text()==(backup/'RequestBypassToServer.before.java').read_text() or target.read_text()==(source/rel).read_text(),'Concurrent bypass mirror change'
pairs.append((source/rel,target,sha(target) if target.exists() else None))
for name in ('SkillCatalog.java','SkillCatalogVerification.java'):
    runtime=root/'server/game/data/scripts/custom/SkillCatalog'/name
    rel=Path('dist/game/data/scripts/custom/SkillCatalog')/name
    for base in (source,cloud):pairs.append((runtime,base/rel,old[str(runtime)]))
for src,dst,expected in pairs:
    if dst.exists():assert sha(dst) in (expected,sha(src)),'Concurrent mirror edit: '+str(dst)
for src,dst,expected in pairs:
    if dst.exists():
        saved=backup/'mirrors'/dst.relative_to(root);saved.parent.mkdir(parents=True,exist_ok=True)
        if not saved.exists():shutil.copy2(dst,saved)
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
mirror=root/'cloud-repo/research/client-comfort/v3';mirror.mkdir(parents=True,exist_ok=True)
for p in stage.iterdir():
    if p.suffix in ('.py','.groovy','.json') or p.name in ('callback-verification.txt','restart_server.ps1'):shutil.copy2(p,mirror/p.name)
print('PASS:',len(pairs),'catalog/bypass sources mirrored with original-file guards; other modules untouched.')
