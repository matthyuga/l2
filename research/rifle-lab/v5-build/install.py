from pathlib import Path
import subprocess,json,hashlib,shutil,datetime
R=Path(__file__).parent;m=json.loads((R/'stage-manifest.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-Process -Name L2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True);assert p.stdout.strip()=='0','Close L2 from game before installing'
assert sha(m['client_catalog'])==m['before_sha256'],'Concurrent NPC catalog changes; stop and review'
assert sha(m['source'])==m['after_sha256'];assert not(R/'installation.json').exists(),'Already installed'
for f in m['files']:assert sha(f['source'])==f['sha256'] and not Path(f['target']).exists()
backup=R/'installation-backup';backup.mkdir(exist_ok=False);shutil.copy2(m['client_catalog'],backup/'npcgrp.before.dat')
for f in m['files']:shutil.copy2(f['source'],f['target']);assert sha(f['target'])==f['sha256']
shutil.copy2(m['source'],m['client_catalog']);assert sha(m['client_catalog'])==m['after_sha256']
m.update(installed=True,backup=str(backup),no_server_file_changes=True,no_AI_changes=True,no_server_restart=True,runtime_validated=False);(R/'installation.json').write_text(json.dumps(m,indent=2));print('INSTALLED_V5 clientLab only, fixed feet/gaze/hair, continuous cycle')

