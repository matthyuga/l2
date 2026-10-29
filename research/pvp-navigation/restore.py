from pathlib import Path
import hashlib,json,subprocess
s=Path(__file__).resolve().parent;r=Path('E:/l2-local')
pidfile=r/'run/game.pid'
if pidfile.exists():
 pid=int(pidfile.read_text().strip())
 check=subprocess.run(['powershell.exe','-NoProfile','-Command',f'if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 1}}'],capture_output=True)
 assert check.returncode==0,'Stop bots normally, then stop GameServer first'
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
 p=Path(row['path']).resolve();p.relative_to(r.resolve());assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'],'Later change: '+str(p)
 if row['backup']:assert hashlib.sha256(Path(row['backup']).read_bytes()).hexdigest()==row['before_sha256']
for row in m['files']:
 p=Path(row['path'])
 if row['backup']:p.write_bytes(Path(row['backup']).read_bytes())
 else:p.unlink()
print('Combat stage sources restored. Start using the normal launcher.')
