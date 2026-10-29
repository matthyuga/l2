from pathlib import Path
import hashlib,json,subprocess
base=Path(__file__).resolve().parent;root=base.parent.parent;client=root.parent/'l2/system-hud'
m=json.loads((base/'installation.json').read_text(encoding='utf8'))
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('Cierra L2 primero. Tambien hay que detener GameServer antes de retirar sus scripts.')
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('GameServer sigue abierto; detenerlo antes de restaurar.')
for item in m['files']:
    path=Path(item['path']);resolved=path.resolve()
    if root.resolve() not in resolved.parents and resolved.parent!=client.resolve():raise SystemExit('Destino inesperado.')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=item['after_sha256']:raise SystemExit('Archivo cambiado: '+str(path))
for item in reversed(m['files']):
    path=Path(item['path'])
    if 'backup' in item:
        data=Path(item['backup']).read_bytes();assert hashlib.sha256(data).hexdigest()==item['before_sha256'];path.write_bytes(data)
    else:path.unlink()
m['state']='restored-to-v3';(base/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8')
print('Restaurado V3; datos de exploracion nuevos conservados.')
