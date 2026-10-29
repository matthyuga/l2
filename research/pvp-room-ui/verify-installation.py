from pathlib import Path
import hashlib,json
root=Path('E:/l2-local');s=Path(__file__).resolve().parent
stages=['pvp-rounds','pvp-room-bots','pvp-room-ui'];current={}
for name in stages:
    m=json.loads((root/'research'/name/'installation.json').read_text())
    for row in m['files']:current[row['path']]=row
for row in current.values():
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],str(p)
result={'status':'PASS','current_chain_files_verified':len(current),'active_lobby':'previous Elven lobby','activation':'next normal startup','native_confirm_message_id':1983,'client_changed':False,'core_changed_in_this_stage':False,'rendering_verified':False}
(s/'final-installation-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
