from pathlib import Path
import json,hashlib,subprocess,shutil
root=Path('E:/l2-local').resolve();stage=root/'research/elven-rooms'
manifest=json.loads((stage/'installation.json').read_text(encoding='utf8'))
check=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { $_.CommandLine -like '*GameServer.jar*' } | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
if check.stdout.strip():raise SystemExit('Close GameServer before restoring. This prevents a runtime/source mismatch.')
for record in manifest['files']:
    path=Path(record['path']).resolve()
    if not path.is_relative_to(root):raise SystemExit('Target outside project: '+str(path))
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['installed_sha256']:
        raise SystemExit('File changed after installation; refusing to overwrite: '+str(path))
    if record['existed'] and not Path(record['backup']).is_file():raise SystemExit('Missing backup: '+record['backup'])
for record in manifest['files']:
    path=Path(record['path'])
    if record['existed']:shutil.copy2(record['backup'],path)
    else:path.unlink()
print('Restored the Elven room files in runtime, source and overlay. Restart GameServer to load the previous version.')
