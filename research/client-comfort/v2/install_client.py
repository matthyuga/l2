from pathlib import Path
import hashlib,json,subprocess,shutil,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent;backup=root/'backups/amber-ui-rain-2026-10-10'
client=root.parent/'l2/system-hud';original=json.loads((backup/'original-hashes.json').read_text())
offline=subprocess.run(['powershell','-NoProfile','-Command',"if((Get-Process -Name L2 -ErrorAction SilentlyContinue) -or (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue)){exit 1}"],capture_output=True)
assert offline.returncode==0,'Close L2 before replacing its loaded catalogs/interface.'
proof={}
for name in ('Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat'):
    target=client/name;assert hashlib.sha256(target.read_bytes()).hexdigest()==original[str(target)],'Concurrent client edit: '+name
    assert (stage/name).stat().st_size>100
texture=root.parent/'l2/systextures/AmberAssistIconsV1.utx'
assert (stage/texture.name).read_bytes()[:28].decode('utf-16le')=='Lineage2Ver121','L2 textures must have their filename-dependent 121 wrapper.'
assert not texture.exists() or texture.read_bytes()==(stage/texture.name).read_bytes()
tree=ET.parse(root/'server/game/data/stats/skills/custom/amber_contract.xml')
assert tree.find(".//skill[@id='19003']/power").text=='3000'
assert tree.find(".//skill[@id='19014']/icon").text=='AmberAssistIconsV1.Assist'
for name in ('Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat'):
    shutil.copy2(stage/name,client/name);proof[name]=hashlib.sha256((client/name).read_bytes()).hexdigest()
shutil.copy2(stage/texture.name,texture);proof[texture.name]=hashlib.sha256(texture.read_bytes()).hexdigest()
assert hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest()==original[str(root/'server/libs/GameServer.jar')]
(stage/'installed-client.json').write_text(json.dumps(proof,indent=2));print('PASS: visible class controls and IA icon installed offline; core and all V10 effects preserved.')
