from pathlib import Path
import hashlib,json,subprocess,shutil,sys
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent
backup=root/'backups/skill-groups-v3-2026-10-10'
original=json.loads((backup/'original-hashes.json').read_text());client=root.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
offline=subprocess.run(['powershell','-NoProfile','-Command',"if((Get-Process -Name L2 -ErrorAction SilentlyContinue) -or (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue)){exit 1}"],capture_output=True)
assert offline.returncode==0,'L2 is still open or a player connected'
targets=[(client/n,stage/n) for n in ('Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat')]
targets.append((root/'server/libs/GameServer.jar',stage/'GameServer.jar'))
texture=root.parent/'l2/systextures/SkillGroupsV3.utx';assert not texture.exists(),'Concurrent texture package'
for target,source in targets:
    assert sha(target)==original[str(target)],'Concurrent edit: '+str(target)
    assert source.stat().st_size>100
assert (stage/'callback-verification.txt').read_text(encoding='utf-8-sig').rstrip().endswith('PASS: fresh native final dispatch matches stock callers; every VM branch boundary and zero-ID click guard valid.')
assert json.loads((stage/'assets-verification.json').read_text())['texture_wrapper']=='121 checksum and decode PASS'
assert json.loads((stage/'jar-verification.json').read_text())['all_other_entries_identical']
if '--check' in sys.argv:print('PASS: prepared build verified; client offline and original file guards match.');sys.exit()
listen=subprocess.run(['powershell','-NoProfile','-Command',"if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){exit 1}"],capture_output=True)
assert listen.returncode==0,'Stop the empty GameServer before replacing its JAR'
for target,source in targets:shutil.copy2(source,target)
shutil.copy2(stage/texture.name,texture)
proof={str(p):sha(p) for p,_ in targets};proof[str(texture)]=sha(texture)
(stage/'installed-hashes.json').write_text(json.dumps(proof,indent=2))
print('PASS: native grouped catalog installed offline; other client assets and core modules preserved.')
