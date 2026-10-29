"""Hash-guarded, backed-up installation. Requires client and GameServer closed."""
import pathlib,sys,json,hashlib,shutil,subprocess,datetime,struct,zlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
stage=D/'stage';encoded=D/'client';codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
if '--wrap' in sys.argv:
 for rel in ['StaticMeshes/HGSkyAirship.usx','Maps/24_19.unr']:
  p=stage/rel;q=encoded/rel;q.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run([str(codec),'-c','encode','-p','121','-f',p.name,'-o',str(q),str(p)],check=True,capture_output=True,timeout=60)
  raw=p.read_bytes();enc=q.read_bytes();key=sum(map(ord,p.name.lower()))&255
  assert enc[:28].decode('utf-16le')=='Lineage2Ver121' and enc[28:-20].translate(bytes(x^key for x in range(256)))==raw
  assert struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20])
 print('Encoded client packages verified, full payload and CRC.');sys.exit(0)
assert not (D/'installation.json').exists(),'Already installed or partially applied: inspect manifest'
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){Write-Output 'CLIENT'};if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){Write-Output 'SERVER'};exit 0"],text=True)
assert not state.strip(),'Close client/GameServer: '+state
build=json.loads((D/'build-audit.json').read_text());geo=json.loads((D/'geodata-audit.json').read_text())
assert sha(CLIENT/'maps/24_19.unr')==build['source_map_sha256'],'Map changed concurrently'
assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==geo['source_sha256'],'Geodata changed concurrently'
for item in json.loads((D/'server-source-hashes.json').read_text()):assert sha(ROOT/'server/game'/item['relative'])==item['sha256'],'Server source changed concurrently'
checks=json.loads((D/'verification.json').read_text());assert checks['native_load'] and checks['map_preserved'] and checks['geo_spawn_valid']
files=[(CLIENT/rel,encoded/rel) for rel in ['Maps/24_19.unr','StaticMeshes/HGSkyAirship.usx']]
assert not (CLIENT/'StaticMeshes/HGSkyAirship.usx').exists(),'New package name already exists'
files.append((ROOT/'server/game/data/geodata/24_19.l2j',stage/'Geodata/24_19.l2j'))
for p in (stage/'server').rglob('*'):
 if p.is_file():
  rel=p.relative_to(stage/'server')
  for root in [ROOT/'server/game',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:files.append((root/rel,p))
backup=ROOT/'backups'/('airship-integration-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest=dict(backup=str(backup),files=[],stationary=True,client_visual_verified=False)
def record():
 text=json.dumps(manifest,indent=2);(D/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
record()
for target,source in files:
 existed=target.exists();saved=backup/('client' if target.is_relative_to(CLIENT) else 'project')/(target.relative_to(CLIENT) if target.is_relative_to(CLIENT) else target.relative_to(ROOT))
 if existed:saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 manifest['files'].append(dict(target=str(target),existed=existed,backup=str(saved) if existed else None,before_sha256=sha(target) if existed else None,after_sha256=sha(source)));record();target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==sha(source)
print('INSTALLED',len(files),'files; backup',backup)
