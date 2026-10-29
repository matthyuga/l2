"""Restore only this installation, refusing later changes. Client/server must be stopped."""
from package_tools import *
import json,hashlib,subprocess,shutil
D=pathlib.Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
check=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){Write-Output 'CLIENT'}; if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){Write-Output 'SERVER'}"],text=True)
assert not check.strip(),'Close client and GameServer before restoration'
m=json.loads((D/'installation.json').read_text());client=(ROOT.parent/'l2').resolve();workspace=ROOT.resolve()
for e in m['files']:
    target=pathlib.Path(e['target']).resolve();assert target.is_relative_to(client) or target.is_relative_to(workspace),'Path outside intended workspace'
    assert target.exists() and sha(target)==e['after_sha256'],'Changed after installation: '+str(target)
    if e['existed']:assert sha(e['backup'])==e['before_sha256'],'Backup hash mismatch'
for e in reversed(m['files']):
    target=pathlib.Path(e['target'])
    if e['existed']:shutil.copy2(e['backup'],target)
    else:target.unlink()
(D/'restored.json').write_text(json.dumps({'restored':True,'backup':m['backup']},indent=2));print('Previous maps, geodata and spawn settings restored. Existing character positions are not rewritten.')
