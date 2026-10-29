"""Restore this installation only. Requires the client and server to be stopped."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((ROOT/'installation.json').read_text(encoding='utf8'))
profile_fix=ROOT/'camera-profile-fix/installation.json'
if profile_fix.exists():
 m['files']+=json.loads(profile_fix.read_text(encoding='utf8'))['files']
assert not (ROOT/'rollback-complete.json').exists(),'Already rolled back'
r=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2,java -ErrorAction SilentlyContinue){exit 5}'],capture_output=True)
assert r.returncode==0,'Stop client and server before rollback (templates are loaded in memory)'
# Refuse to overwrite later work; check every target and backup before touching any file.
for c in m['files']:
 assert sha(c['target'])==c['after'],('Later edit detected; manual reconciliation required',c['target'])
 if c['before']:assert sha(c['backup'])==c['before'],('Backup changed',c['backup'])
for c in reversed(m['files']):
 dst=Path(c['target'])
 if c['before']:shutil.copy2(c['backup'],dst)
 else:dst.unlink()
(ROOT/'rollback-complete.json').write_text(json.dumps({'status':'restored','backup':m['backup']},indent=2),encoding='utf8')
print('Restored',len(m['files']),'files. Restart server to load original data.')
