from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path('E:/l2-local');STAGE=Path(__file__).resolve().parent
m=json.loads((STAGE/'installation.json').read_text())
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -match 'GameServer\\.jar' }).Count"],capture_output=True,text=True)
if r.returncode or r.stdout.strip()!='0':raise SystemExit('Stop GameServer before restoring')
for row in m['files']:
    p=Path(row['path']);p.resolve().relative_to(ROOT.resolve())
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['installed_sha256']:raise SystemExit('Later change detected: '+str(p))
for row in m['files']:
    p=Path(row['path'])
    if row['existed']:shutil.copy2(row['backup'],p)
    else:p.unlink()
print('Previous runtime/source/overlay restored. Start GameServer to load it.')
