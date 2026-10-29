"""Restore native L2 envelopes on renamed texture/mesh packages, with roundtrip checks."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime,zlib,struct
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];CLIENT=PROJECT.parent/'l2';OUT=ROOT/'asset-envelope-fix';OUT.mkdir(exist_ok=True)
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True,timeout=60)
 if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace'))
manifest=json.loads((ROOT/'installation.json').read_text());changes=[]
for f in manifest['files']:
 target=Path(f['target'])
 if target.suffix.lower() not in ('.utx','.ukx','.usx') or not target.stem.startswith('EB'):continue
 assert sha(target)==f['after'],'Concurrent asset modification: '+str(target)
 source=Path(f['stage']);raw=source.read_bytes();assert raw[:4]==bytes.fromhex('c1832a9e'),source
 protocol=121 if target.suffix.lower()=='.utx' else 111
 out=OUT/target.name
 run([CODEC,'-c','encode','-p',protocol,'-f',target.name,'-o',out,source])
 check=OUT/(target.name+'.check.raw');run([CODEC,'-f',target.name,'-o',check,out]);assert check.read_bytes()==raw,target
 # Verify filename-based XOR independently from the codec.
 encoded=out.read_bytes();assert encoded[:28]==('Lineage2Ver'+str(protocol)).encode('utf-16le')
 assert zlib.crc32(encoded[:-20])==struct.unpack_from('<I',encoded,len(encoded)-20+12)[0],target
 key=sum(target.name.lower().encode('ascii'))&255 if protocol==121 else 172
 table=bytes.maketrans(bytes(range(256)),bytes(v^key for v in range(256)))
 assert encoded[28:28+len(raw)].translate(table)==raw
 check.unlink()
 changes.append({'target':str(target),'stage':str(out),'raw_source':str(source),'protocol':protocol,'before':f['after'],'after':sha(out),'raw_sha256':sha(source)})
 print('PREPARED',target.name,flush=True)
assert subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2 -ErrorAction SilentlyContinue){exit 5}'],capture_output=True).returncode==0,'Client is running; close it before replacing package files'
backup=PROJECT/'backups'/('equipment-asset-envelope-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for f in changes:
 target=Path(f['target']);assert sha(target)==f['before'],'Concurrent edit: '+str(target)
 saved=backup/target.name;shutil.copy2(target,saved);f['backup']=str(saved)
(backup/'files.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
written=[]
try:
 for f in changes:shutil.copy2(f['stage'],f['target']);written.append(f)
 for f in changes:assert sha(f['target'])==f['after']
except Exception:
 for f in reversed(written):
  if sha(f['target'])==f['after']:shutil.copy2(f['backup'],f['target'])
 raise
shutil.copy2(ROOT/'installation.json',backup/'installation-before.json')
lookup={f['target']:f for f in changes}
for entry in manifest['files']:
 if entry['target'] in lookup:
  fix=lookup[entry['target']];entry.update(after=fix['after'],stage=fix['stage'],raw_stage=fix['raw_source'],protocol=fix['protocol'])
(ROOT/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'installation.json').write_text(json.dumps({'status':'installed','backup':str(backup),'files':changes,'raw_package_payload_preserved':True,'in_client_check':'pending'},indent=2),encoding='utf-8')
print('INSTALLED',len(changes),'encrypted packages;',backup,flush=True)
