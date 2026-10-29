"""Restore this installation only when every current file still matches its installed hash."""
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parent;m=json.loads((ROOT/'installation.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2,java -ErrorAction SilentlyContinue){exit 5}'],capture_output=True).returncode==0,'Close client/server first'
for f in m['files']:assert Path(f['target']).is_file() and sha(f['target'])==f['after'],'File changed since install: '+f['target']
for f in reversed(m['files']):
 if f['before']:shutil.copy2(f['backup'],f['target'])
 else:Path(f['target']).unlink()
m['status']='rolled_back';(ROOT/'installation.json').write_text(json.dumps(m,indent=2));print('Restored all previous files; removed only unchanged files created by this installation.')
