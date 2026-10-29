from pathlib import Path
import hashlib,json
r=Path('E:/l2-local');s=Path(__file__).resolve().parent
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
 p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],'Concurrent change: '+str(p)
for row in m['files']:
 p=Path(row['path']);data=(s/'src/custom/ElvenPvpRoom'/p.name).read_bytes();p.write_bytes(data);row['installed_sha256']=hashlib.sha256(data).hexdigest()
(s/'installation.json').write_text(json.dumps(m,indent=2))
current={}
for stage in ['pvp-rounds','pvp-room-bots','pvp-room-ui','pvp-siege-bots','pvp-bot-combat']:
 for row in json.loads((r/'research'/stage/'installation.json').read_text())['files']:current[row['path']]=row
for row in current.values():assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['installed_sha256'],row['path']
result=dict(status='PASS',current_chain_files_verified=len(current),client_changed=False,core_changed=False)
(s/'installation-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
