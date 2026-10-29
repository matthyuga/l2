"""Undo this stage only. Requires stopped GameServer; refuses later changes."""
from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile,os
root=Path('E:/l2-local').resolve();s=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(value):
    p=Path(value).resolve();p.relative_to(root);return p
def main():
    m=json.loads((s/'installation.json').read_text());pending=checked(m['pending_patch'])
    r=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -match 'GameServer\\.jar' }).Count"],capture_output=True,text=True)
    if r.returncode or r.stdout.strip()!='0':raise SystemExit('Stop GameServer before restoring')
    for row in m['files']:
        p=checked(row['path'])
        if not p.exists() or sha(p)!=row['installed_sha256']:raise SystemExit('Later change: '+str(p))
        if row['existed'] and sha(checked(row['backup']))!=row['before_sha256']:raise SystemExit('Backup mismatch')
    jar=checked(m['core_baseline']['path']);baseline=checked(m['core_baseline']['backup'])
    if sha(baseline)!=m['core_baseline']['sha256']:raise SystemExit('Core backup mismatch')
    own={Path(row['path']).relative_to(pending).as_posix():checked(row['path']).read_bytes() for row in m['files'] if checked(row['path']).is_relative_to(pending)}
    prior={}
    sync=root/'server/pending-core-patches/20261015-elven-position-sync'
    for p in sync.rglob('*.class'):prior[p.relative_to(sync).as_posix()]=p.read_bytes()
    with zipfile.ZipFile(baseline) as old,zipfile.ZipFile(jar) as current:
        oldnames=set(old.namelist());names=set(current.namelist())
        if oldnames-names:raise SystemExit('Missing core entries')
        applied=any(n not in oldnames or current.read(n)!=old.read(n) for n in own if n in names)
        for n in names:
            data=current.read(n)
            allowed=[old.read(n)] if n in oldnames else [b''] if n.endswith('/') else []
            if n in prior:allowed.append(prior[n])
            if n in own:allowed.append(own[n])
            if data not in allowed:raise SystemExit('Later core change: '+n)
        if applied:
            tmp=jar.with_suffix('.rollback-tmp')
            with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
                for info in current.infolist():
                    if info.filename in own:
                        if info.filename in oldnames:out.writestr(info,old.read(info.filename))
                    else:out.writestr(info,current.read(info.filename))
    if applied:os.replace(tmp,jar)
    for row in m['files']:
        p=checked(row['path'])
        if row['existed']:shutil.copy2(checked(row['backup']),p)
        else:p.unlink()
    (pending/'.applied').write_text('Restored; staging disabled.\n')
    print('Round-room stage restored. Geodata retained for other uses; position-sync correction preserved.')
if __name__=='__main__':main()
