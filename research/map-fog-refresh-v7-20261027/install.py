from pathlib import Path
import hashlib,json,shutil,subprocess,datetime

root=Path(__file__).resolve().parent
target=Path(r'E:\l2\system-hud\d3d9.dll')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='08d8cd491a0f0a89d4f126291f249ebc2c9b1471e200ac12c88ad33ee25f3d4f'
processes=subprocess.run(['tasklist.exe','/FI','IMAGENAME eq L2.exe','/FO','CSV','/NH'],capture_output=True,text=True,check=True).stdout
if '"l2.exe"' in processes.lower():raise SystemExit('Cerrar L2 antes de instalar. No se cambio ningun archivo.')
if sha(target)!=expected:raise SystemExit('El proxy actual difiere de la base V6 revisada. No se sobrescribe.')
nwindow=Path(r'E:\l2\system-hud\NWindow.dll')
if sha(nwindow)!='a4de43d5d31241daae7dac072134c011abdd036b0d1ee291eead0bb5e9c6ca7d':raise SystemExit('NWindow cambio; revisar compatibilidad antes de instalar.')
source=root/'build/d3d9.dll'
if not source.exists():raise SystemExit('Compilar y verificar V7 antes de instalar.')
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=Path(r'E:\l2-local\backups')/('map-fog-refresh-v7-'+stamp);backup.mkdir()
shutil.copy2(target,backup/'d3d9.dll')
log=target.parent/'NexusMapFog.log'
if log.exists():shutil.copy2(log,backup/'NexusMapFog-before.log')
manifest={'state':'installed-awaiting-in-game-validation','target':str(target),'backup':str(backup/'d3d9.dll'),'before_sha256':expected,'after_sha256':sha(source),'nwindow_sha256':sha(nwindow),'server_changed':False,'exploration_data_changed':False,'client_closed_at_install':True}
shutil.copy2(source,target)
assert sha(target)==manifest['after_sha256']
(root/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(backup/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('INSTALLED V7. Solo se reemplazo d3d9.dll; visitas, configuracion, servidor y HSL conservados.')
print('Backup:',backup)
