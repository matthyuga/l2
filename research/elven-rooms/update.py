from pathlib import Path
import json,hashlib,re
root=Path('E:/l2-local');stage=root/'research/elven-rooms'
manifest=json.loads((stage/'installation.json').read_text())
for file in manifest['files']:
    path=Path(file['path'])
    if path.name=='PvpRooms.java':path.write_text((stage/'PvpRooms.java').read_text(encoding='utf8'),encoding='utf8')
    if path.name=='ElvenPvpRoom.java':
        data=path.read_text(encoding='utf8')
        data=re.sub(r'\tprivate static void prepareArenaPlayer\(Player player\)\n\t\{.*?\n\t\}\n', '\tprivate static void prepareArenaPlayer(Player player)\n\t{\n\t\t// No resource or effect restoration. Method retained for running-class compatibility.\n\t}\n',data,flags=re.S)
        path.write_text(data,encoding='utf8')
    file['installed_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
(stage/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
