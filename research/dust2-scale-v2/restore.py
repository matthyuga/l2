import pathlib,subprocess,json,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=ROOT/'research/dust2-integration';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True);assert not state.strip(),'Close client/GameServer'
m=json.loads((D/'installation.json').read_text());assert m['complete'] and not m.get('restored')
for row in m['files']:assert sha(row['target'])==row['after_sha256'] and sha(row['backup'])==row['before_sha256'],'Concurrent changes'
for row in reversed(m['files']):shutil.copy2(row['backup'],row['target'])
base=json.loads((OLD/'installation.json').read_text(encoding='utf-8'))
for row in m['files']:
 next(i for i in base['files'] if pathlib.Path(i['target'])==pathlib.Path(row['target']))['after_sha256']=row['before_sha256']
base['current_version']='pre-scale-v2';(OLD/'installation.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf-8');m['restored']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Restored prior large-scale layout, native floors and walls')
