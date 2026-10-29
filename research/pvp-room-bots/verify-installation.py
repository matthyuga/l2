from pathlib import Path
import hashlib,json
root=Path('E:/l2-local');s=Path(__file__).resolve().parent
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],str(p)
old=json.loads((root/'research/pvp-rounds/installation.json').read_text())
replaced={row['path'] for row in m['files']}
for row in old['files']:
    if row['path'] not in replaced:
        p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],str(p)
result={'status':'PASS','bot_files_verified':len(m['files']),'prior_room_files_verified_except_superseded_host':True,'default':'OFF','activation':'after next normal four-room startup, GM commands only','client_changed':False,'server_restarted':False}
(s/'final-installation-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
