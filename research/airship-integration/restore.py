"""Restore this integration before any older dock rollback; client/server closed."""
import pathlib,subprocess,json,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id;Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess;exit 0"],text=True).strip(),'Client and GameServer must be closed'
m=json.loads((D/'installation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for i in m['files']:
 p=pathlib.Path(i['target']);assert p.is_relative_to(ROOT) or p.is_relative_to(CLIENT);assert p.exists() and sha(p)==i['after_sha256'],'Changed since install: '+str(p)
 if i['existed']:assert sha(pathlib.Path(i['backup']))==i['before_sha256']
for i in reversed(m['files']):
 p=pathlib.Path(i['target'])
 if i['existed']:shutil.copy2(i['backup'],p)
 else:p.unlink()
m['restored']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Restored pre-airship map, geodata, commands and zone; dock preserved.')
