"""Backed-up hash-guarded install; client and GameServer must be closed."""
import pathlib,sys,json,hashlib,shutil,subprocess,datetime,struct,zlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2';stage=D/'stage';encoded=D/'client';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
if '--wrap' in sys.argv:
 for rel in ['StaticMeshes/HGDust2Arena.usx','Maps/24_19.unr']:
  p=stage/rel;q=encoded/rel;q.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f',p.name,'-o',str(q),str(p)],check=True,capture_output=True,timeout=60)
  raw=p.read_bytes();enc=q.read_bytes();key=sum(map(ord,p.name.lower()))&255
  assert enc[:28].decode('utf-16le')=='Lineage2Ver121' and enc[28:-20].translate(bytes(x^key for x in range(256)))==raw
  assert struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20])
 print('Client encryption and CRC verified');sys.exit(0)
assert not (D/'installation.json').exists(),'Already installed; inspect manifest'
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True)
assert not state.strip(),'Client/GameServer still active: '+state
build=json.loads((D/'build-audit.json').read_text());geo=json.loads((D/'geodata-audit.json').read_text())
assert sha(CLIENT/'maps/24_19.unr')==build['source_map_sha256'],'Client map changed concurrently'
assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==geo['source_sha256'],'Geodata changed concurrently'
assert geo['reachable_layers']>10000 and build['native_objects_loaded']==105
configs=json.loads((D/'server-source-hashes.json').read_text())
for i in configs:assert sha(i['target'])==i['sha256'],'Server config changed concurrently'
files=[(CLIENT/r,encoded/r) for r in ['Maps/24_19.unr','StaticMeshes/HGDust2Arena.usx']]+[(ROOT/'server/game/data/geodata/24_19.l2j',stage/'Geodata/24_19.l2j')]
files.extend((pathlib.Path(i['target']),pathlib.Path(i['stage'])) for i in configs)
assert not (CLIENT/'StaticMeshes/HGDust2Arena.usx').exists()
for p in (stage/'server').rglob('*'):
 if p.is_file():
  rel=p.relative_to(stage/'server')
  if str(rel).replace('\\','/')=='config/Custom/WorldContent.ini':continue
  for root in [ROOT/'server/game',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:files.append((root/rel,p))
backup=ROOT/'backups'/('dust2-integration-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest=dict(backup=str(backup),files=[],client_visual_verified=False,exploration_only=True)
def record():
 text=json.dumps(manifest,indent=2);(D/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
record()
try:
 for target,source in files:
  existed=target.exists();saved=backup/('client' if target.is_relative_to(CLIENT) else 'project')/(target.relative_to(CLIENT) if target.is_relative_to(CLIENT) else target.relative_to(ROOT))
  if existed:saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  manifest['files'].append(dict(target=str(target),existed=existed,backup=str(saved) if existed else None,before_sha256=sha(target) if existed else None,after_sha256=sha(source)));record()
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==sha(source)
except Exception:
 for i in reversed(manifest['files']):
  p=pathlib.Path(i['target'])
  if i['existed']:shutil.copy2(i['backup'],p)
  elif p.exists():p.unlink()
 manifest['rolled_back']=True;record();raise
manifest['complete']=True;record();print('DUST2_INSTALLED',len(files),'files; backup',backup)
