from pathlib import Path
import hashlib,json,re,subprocess,datetime
base=Path(__file__).resolve().parent;root=base.parent.parent;native=base.parent/'map-fog-walking-v4';client=root.parent/'l2/system-hud'
sha=lambda b:hashlib.sha256(b).hexdigest()
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('Cierra L2 antes de instalar V4.')
v3=json.loads((base.parent/'map-fog-alpha-v3/installation.json').read_text(encoding='utf8'))
if sha((client/'d3d9.dll').read_bytes())!=v3['after_sha256']:raise SystemExit('La DLL instalada ya no es V3; se cancela.')
if sha((client/'NWindow.dll').read_bytes())!='a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292':raise SystemExit('NWindow cambio.')
files={client/'d3d9.dll':(native/'build/d3d9.dll').read_bytes()}
for name in ['NexusMapFogV4.u','NexusFogFieldV4.bin']:
    target=client/name
    if target.exists():raise SystemExit('Ya existe: '+str(target))
    files[target]=(native/'build'/name).read_bytes()
for prefix in [root/'server/game',root/'source/L2J_Mobius_CT_0_Interlude/dist/game']:
    for source in (base/'server/custom/ExplorationWalking').glob('*.java'):
        target=prefix/'data/scripts/custom/ExplorationWalking'/source.name
        if target.exists():raise SystemExit('Ya existe: '+str(target))
        files[target]=source.read_bytes()
    cfg=prefix/'config/Custom/WorldContent.ini';text=cfg.read_bytes().decode('utf8')
    m=re.search(r'(?m)^CustomScriptFolders\s*=\s*([^\r\n]*)',text)
    if not m or 'ExplorationWalking' in m.group(1).split(';'):raise SystemExit('Whitelist no reconocida: '+str(cfg))
    text=text[:m.end(1)]+';ExplorationWalking'+text[m.end(1):];files[cfg]=text.encode('utf8')
backup=root/'backups'/('exploration-walking-v4-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
records=[]
for i,(path,data) in enumerate(files.items()):
    old=path.read_bytes() if path.exists() else None
    item={'path':str(path),'before_sha256':sha(old) if old is not None else None,'after_sha256':sha(data)}
    if old is not None:
        saved=backup/(str(i)+'-'+path.name);saved.write_bytes(old);item['backup']=str(saved)
    records.append(item)
(backup/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
written=[]
try:
    for (path,data),item in zip(files.items(),records):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);written.append(item)
        assert sha(path.read_bytes())==item['after_sha256']
except Exception:
    for item in reversed(written):
        path=Path(item['path'])
        if 'backup' in item:path.write_bytes(Path(item['backup']).read_bytes())
        else:path.unlink(missing_ok=True)
    raise
manifest={'state':'installed-pending-gameserver-restart','backup':str(backup),'files':records,'runtime_visual_validation':'pending','gm_only':True}
(base/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('INSTALADO V4: cliente y scripts preparados. Reiniciar solo GameServer con cliente cerrado. Backup:',backup)
