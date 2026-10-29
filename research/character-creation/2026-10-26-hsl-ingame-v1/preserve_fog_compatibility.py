from pathlib import Path
import hashlib,json,shutil
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((D/'installation.json').read_text());backup=Path(m['backup']);target=Path('E:/l2/system-hud/d3d9.dll');old=target.read_bytes()
assert sha(old)=='6779ad2afe4a52ff020ef4ad94cbbd17395ba1f2ea30a6ae5247ba0e928dddd7'
prior=bytes.fromhex('a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292');new=bytes.fromhex(sha(Path('E:/l2/system-hud/NWindow.dll').read_bytes()));assert old.count(prior)==1
patched=old.replace(prior,new);assert sum(a!=b for a,b in zip(old,patched))<=32
fogpath=P/'research/map-fog-render-v6/installation.json';fog=json.loads(fogpath.read_text());assert fog['after_sha256']==sha(old);fog.update(after_sha256=sha(patched),hsl_compatible_nwindow=new.hex(),hash_guard_only_update=True)
for f,data in [(target,patched),(fogpath,json.dumps(fog,indent=2).encode())]:
 saved=backup/(str(len(m['files']))+'-'+f.name);shutil.copy2(f,saved);before=sha(f.read_bytes());f.write_bytes(data);m['files'].append(dict(target=str(f),before_sha256=before,after_sha256=sha(data),backup=str(saved)))
m['map_fog_guard_preserved']=True
(D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2))
print('Preserved map fog compatibility: only its exact NWindow hash guard changed; renderer and settings unchanged.')
