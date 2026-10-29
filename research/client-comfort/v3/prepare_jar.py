from pathlib import Path
import json,hashlib,zipfile
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent
original=json.loads((root/'backups/skill-groups-v3-2026-10-10/original-hashes.json').read_text())
jar=root/'server/libs/GameServer.jar';assert hashlib.sha256(jar.read_bytes()).hexdigest()==original[str(jar)]
prefix='org/l2jmobius/gameserver/network/serverpackets/'
names=['SkillList.class','SkillCatalogView.class','SkillCatalogView$Model.class']
replacements={prefix+n:(root/'build/client-comfort-v3'/prefix/n).read_bytes() for n in names}
extra='org/l2jmobius/gameserver/network/clientpackets/RequestBypassToServer.class'
replacements[extra]=(root/'build/client-comfort-v3'/extra).read_bytes()
with zipfile.ZipFile(jar) as src,zipfile.ZipFile(stage/'GameServer.jar','w',compression=zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():dst.writestr(info,replacements.pop(info.filename,src.read(info.filename)))
    for name,data in replacements.items():dst.writestr(name,data)
with zipfile.ZipFile(jar) as src,zipfile.ZipFile(stage/'GameServer.jar') as dst:
    assert src.namelist()==dst.namelist()
    changed=[name for name in src.namelist() if src.read(name)!=dst.read(name)]
    assert set(changed)==set([*(prefix+n for n in names),extra]),changed
(stage/'jar-verification.json').write_text(json.dumps({'changed_entries':changed,'all_other_entries_identical':True},indent=2))
print('PASS: only SkillList, SkillCatalogView/Model and exact native bypass dispatch changed; all other core entries identical.')
