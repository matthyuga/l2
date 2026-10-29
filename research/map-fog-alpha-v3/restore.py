from pathlib import Path
import hashlib,json,subprocess
base=Path(__file__).resolve().parent
m=json.loads((base/'installation.json').read_text(encoding='utf8'))
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('Cierra L2 para restaurar.')
target=base.parents[2]/'l2/system-hud/d3d9.dll'
if str(target)!=m['target']:raise SystemExit('Destino inesperado.')
sha=lambda b:hashlib.sha256(b).hexdigest()
if sha(target.read_bytes())!=m['after_sha256']:raise SystemExit('La DLL cambio; no se sobrescribe.')
before=Path(m['backup']).read_bytes()
assert sha(before)==m['before_sha256']
target.write_bytes(before);m['state']='restored-to-v2'
(base/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8')
print('Restaurado V2. Si se desea retirar todo, restaurar despues V2 y luego V1.')
