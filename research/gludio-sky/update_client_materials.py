from package_tools import *
import json,hashlib,subprocess,shutil
D=pathlib.Path(__file__).resolve().parent;CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id; exit 0"],text=True).strip(),'Client must be closed'
assert all(x['loaded'] for x in json.loads((D/'native-load-proof.json').read_text()))
m=json.loads((D/'installation.json').read_text());entries={e['target'].lower():e for e in m['files']}
proof=json.loads((D/'wrapper-proof.json').read_text())
for item in proof:
    source=D/'client'/item['relative'];target=CLIENT/item['relative'];e=entries[str(target).lower()]
    assert sha(target)==e['after_sha256'],'Installed file changed concurrently: '+str(target)
    assert sha(source)==item['sha256']
for item in proof:
    source=D/'client'/item['relative'];target=CLIENT/item['relative'];e=entries[str(target).lower()]
    if sha(target)!=sha(source):shutil.copy2(source,target)
    e['after_sha256']=sha(target)
m['material_conversion']='License37 native shader blocks converted to license28; mip pixels and tagged material graphs preserved.'
data=json.dumps(m,indent=2);(D/'installation.json').write_text(data);(pathlib.Path(m['backup'])/'manifest.json').write_text(data)
print('Corrected client material packages installed and rollback hashes updated; no server restart needed for textures.')
