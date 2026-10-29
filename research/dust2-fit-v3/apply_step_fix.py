from pathlib import Path
import json,shutil,hashlib,subprocess
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True);assert not state.strip(),state
m=json.loads((D/'installation.json').read_text());changed=[]
for row in m['files']:
 if row['target'].endswith('24_19.unr'):source=D/'client/Maps/24_19.unr'
 elif row['target'].endswith('24_19.l2j'):source=D/'stage/Geodata/24_19.l2j'
 else:continue
 assert sha(row['target'])==row['after_sha256'],'Concurrent change '+row['target']
 backup=Path(m['backup'])/'intermediate-v3'/Path(row['target']).name;backup.parent.mkdir(exist_ok=True);shutil.copy2(row['target'],backup)
 changed.append(dict(target=row['target'],before=row['after_sha256'],intermediate_backup=str(backup),after=sha(source)))
 shutil.copy2(source,row['target']);row['after_sha256']=sha(source)
m['step_fix']=changed;m['layer_merge']=8.1
for p in [D/'installation.json',Path(m['backup'])/'manifest.json']:p.write_text(json.dumps(m,indent=2),encoding='utf-8')
for p in [D.parent/'dust2-integration/installation.json',D.parent/'dust2-scale-v2/installation.json']:
 parent=json.loads(p.read_text(encoding='utf-8'))
 for row in parent['files']:
  for new in changed:
   if Path(row['target'])==Path(new['target']):row['after_sha256']=new['after']
 parent['fit_v3']=m
 for target in [p,Path(parent['backup'])/'manifest.json']:target.write_text(json.dumps(parent,ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied 8u layer equality fix to',len(changed),'files, with intermediate backup and synchronized manifests')
