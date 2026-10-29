from pathlib import Path
import json,hashlib,subprocess,shutil
root=Path(__file__).resolve().parent
processes=subprocess.run(['tasklist.exe','/FI','IMAGENAME eq L2.exe','/FO','CSV','/NH'],capture_output=True,text=True,check=True).stdout
if '"l2.exe"' in processes.lower():raise SystemExit('Cerrar L2 antes de restaurar.')
m=json.loads((root/'installation.json').read_text());target=Path(m['target']);backup=Path(m['backup'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(target)==m['after_sha256'],'El archivo cambio desde V7; no sobrescribir.'
assert sha(backup)==m['before_sha256'],'Respaldo inesperado.'
shutil.copy2(backup,target)
m['state']='restored-v6';(root/'installation.json').write_text(json.dumps(m,indent=2))
print('Restaurado V6. Progreso de exploracion intacto.')
