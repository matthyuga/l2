"""Restore only this stage, with GameServer stopped and later-change checks."""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
ROOT=Path('E:/l2-local').resolve()
STAGE=Path(__file__).resolve().parent
m=json.loads((STAGE/'installation.json').read_text())
b=json.loads((STAGE/'baseline.json').read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(value):
    p=Path(value).resolve()
    p.relative_to(ROOT)
    return p
def main():
    r=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -match 'GameServer\\.jar' }).Count"],capture_output=True,text=True)
    if r.returncode or r.stdout.strip()!='0': raise SystemExit('Stop GameServer before restoring')
    for row in m['files']:
        p=checked(row['path'])
        if not p.exists() or digest(p)!=row['installed_sha256']: raise SystemExit('Later change detected: '+str(p))
        if row['existed'] and digest(checked(row['backup']))!=row['before_sha256']: raise SystemExit('Backup mismatch: '+str(p))
    jarrow=b['files'][0]
    jar=checked(jarrow['path']); previous=checked(jarrow['backup'])
    if digest(previous)!=jarrow['before_sha256']: raise SystemExit('Core backup mismatch')
    pending=checked(m['pending_patch'])
    expected={Path(row['path']).relative_to(pending).as_posix():checked(row['path']).read_bytes() for row in m['files'] if checked(row['path']).is_relative_to(pending)}
    if digest(jar)!=jarrow['before_sha256']:
        with zipfile.ZipFile(previous) as old, zipfile.ZipFile(jar) as current:
            allowed_dirs={str(parent).replace('\\','/')+'/' for name in expected for parent in Path(name).parents if str(parent)!='.'}
            if set(current.namelist())-set(old.namelist())-set(expected)-allowed_dirs: raise SystemExit('Unexpected core entries')
            if (set(old.namelist())|set(expected))-set(current.namelist()): raise SystemExit('Missing core entries')
            for name in current.namelist():
                wanted=expected[name] if name in expected else old.read(name) if name in old.namelist() else b''
                if current.read(name)!=wanted: raise SystemExit('Later core change: '+name)
    # All validation precedes mutation. Paths have been resolved within E:/l2-local.
    if digest(jar)!=jarrow['before_sha256']: shutil.copy2(previous,jar)
    for row in m['files']:
        p=checked(row['path'])
        if row['existed']: shutil.copy2(checked(row['backup']),p)
        else: p.unlink()
    (pending/'.applied').write_text('Restored; empty staging directory disabled.\n')
    print('Position synchronization stage restored. Start GameServer to load previous classes.')
if __name__=='__main__': main()
