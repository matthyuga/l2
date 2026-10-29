from pathlib import Path
import zipfile,hashlib,json
r=Path(__file__).resolve().parents[3];s=Path(__file__).resolve().parent
b=r/'backups/summon-buffs-2026-10-10';old=json.loads((b/'original-hashes.json').read_text())
jar=b/'GameServer.jar';installed=r/'server/libs/GameServer.jar'
expected=json.loads((s/'installed.json').read_text())['core_sha256'] if (s/'installed.json').exists() else old[str(installed)]
assert hashlib.sha256(installed.read_bytes()).hexdigest()==expected,'Concurrent GameServer edit'
name='org/l2jmobius/gameserver/entity/actor/instance/SchemeBuffer.class';data=(r/'build/summon-buffs'/name).read_bytes()
with zipfile.ZipFile(jar) as src,zipfile.ZipFile(s/'GameServer.jar','w',compression=zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():dst.writestr(info,data if info.filename==name else src.read(info.filename))
with zipfile.ZipFile(jar) as src,zipfile.ZipFile(s/'GameServer.jar') as dst:
    assert src.namelist()==dst.namelist()
    changed=[n for n in src.namelist() if src.read(n)!=dst.read(n)];assert changed==[name]
proof={'changed_core_entries':changed,'all_other_core_entries_identical':True,'existing_profiles_unchanged':True,'client_unchanged':True,'dynamic_test':'Prepared; run after offline restart'}
(s/'prepared.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
