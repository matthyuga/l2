from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((D/'installation.json').read_text())
assert m['live_installed'] and not m.get('rolled_back')
ps=['powershell','-NoProfile','-Command'];assert not subprocess.check_output(ps+["if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client'
for x in m['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256'],('Changed since installation',x['target'])
pid=subprocess.check_output(ps+["Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"],text=True).strip()
if pid:
 assert pid==m['game_server_pid'],'Server restarted: original runtime definitions require a controlled server restart instead of old live rollback capture'
 result=subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(D/'reload-hsl.jar'),str(D)+'|rollback'],capture_output=True,text=True,timeout=60)
 assert result.returncode==0 and (D/'live-rollback-proof.txt').exists(),result.stdout+result.stderr
for x in reversed(m['files']):
 target=Path(x['target'])
 if x['backup']:target.write_bytes(Path(x['backup']).read_bytes());assert sha(target.read_bytes())==x['before_sha256']
 else:target.unlink()
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Restored complete pre-HSL client/server state; custom RGB variables remain harmless metadata.')
