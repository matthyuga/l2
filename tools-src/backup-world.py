"""Create and verify a private pre-empty-world server snapshot; never changes live content."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,zipfile,shutil

root=Path(__file__).resolve().parent.parent
stamp=datetime.now().strftime('%Y-%m-%d_%H%M%S')
backup=root/'backups'/('mundo-completo-antes-vaciado-'+stamp)
backup.mkdir(parents=True,exist_ok=False)
cfg=json.loads((root/'lab-panel/config.json').read_text(encoding='utf-8-sig'))['database']
client=backup/'.dump-client.cnf'
def esc(v):return '"'+str(v).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
client.write_text('[client]\n'+''.join(f'{k}={esc(cfg[k])}\n' for k in ['host','port','user','password'])+'default-character-set=utf8mb4\n',encoding='utf-8')
dump=root/'tools/mariadb-11.8.9-winx64/bin/mariadb-dump.exe'
try:
 for filename,args in [('database.sql',['--single-transaction','--quick','--hex-blob','--routines','--events','--triggers',cfg['database']])]:
  with (backup/filename).open('wb') as out:
   result=subprocess.run([str(dump),'--defaults-extra-file='+str(client),*args],stdout=out,stderr=subprocess.PIPE)
  if result.returncode:
   (backup/(filename+'.error.txt')).write_bytes(result.stderr)
   raise RuntimeError('SQL backup failed; private error file recorded')
 cli=root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'
 result=subprocess.run([str(cli),'--defaults-extra-file='+str(client),'--batch','--skip-column-names','--raw','--execute=SHOW GRANTS FOR CURRENT_USER'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
 user="'"+str(cfg['user']).replace("'","''")+"'@'127.0.0.1'"
 secret="'"+str(cfg['password']).replace('\\','\\\\').replace("'","''")+"'"
 grants='CREATE USER IF NOT EXISTS '+user+' IDENTIFIED BY '+secret+';\n'+''.join(line.rstrip(';')+';\n' for line in result.stdout.decode('utf-8').splitlines())
 (backup/'database-users.sql').write_text(grants,encoding='utf-8')
finally:client.unlink(missing_ok=True)
print('SQL backups complete',flush=True)

trees=['server','source','lab-panel','tools-src','cloud-repo/mobius-overlay',
       'tools/jdk-25.0.4.1+1','tools/mariadb-11.8.9-winx64','tools/node-portable','tools/apache-ant-1.10.18']
files=[]
for folder in trees:
 for file in (root/folder).rglob('*'):
  if file.is_file() and not any(p in {'logs','log','.git','__pycache__'} for p in file.relative_to(root/folder).parts):files.append(file)
files += [p for p in root.iterdir() if p.is_file() and p.suffix.lower() in {'.ps1','.cmd','.bat','.md','.json','.ini','.properties'}]
files += [root/'database/my.ini']
manifest=[]
with zipfile.ZipFile(backup/'servidor-y-codigo.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as archive:
 for i,file in enumerate(sorted(set(files))):
  before=file.stat();rel=file.relative_to(root).as_posix();data=file.read_bytes();after=file.stat()
  if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('File changed during backup: '+rel)
  archive.writestr(rel,data);manifest.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  if i%1000==0:print('Archived files:',i,flush=True)
print('Archive complete; checking every member',flush=True)
with zipfile.ZipFile(backup/'servidor-y-codigo.zip') as archive:
 if archive.testzip() is not None:raise RuntimeError('Archive CRC failure')
 for entry in manifest:
  if hashlib.sha256(archive.read(entry['path'])).hexdigest()!=entry['sha256']:raise RuntimeError('Archive SHA mismatch: '+entry['path'])

ref=backup/'referencia-clasica'
for folder in ['spawns','stats','zones','mapregion','teleporters','buylists','multisell']:
 shutil.copytree(root/'server/game/data'/folder,ref/folder)
(backup/'manifest-files.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
meta={'created_local':stamp,'created_utc':datetime.now(timezone.utc).isoformat(),'root':str(root),'database':cfg['database'],
      'archive_files':len(manifest),'archive_original_bytes':sum(v['bytes'] for v in manifest),'archive_verified':True,
      'contains':trees,'excluded':'Live MariaDB physical data, running process files, logs, external client E:/l2. Database restored from logical SQL.'}
(backup/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
def sha(file):
 h=hashlib.sha256()
 with file.open('rb') as inp:
  for data in iter(lambda:inp.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
(backup/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in [backup/'servidor-y-codigo.zip',backup/'database.sql',backup/'database-users.sql',backup/'manifest-files.json',backup/'metadata.json']),encoding='utf-8')
print('BACKUP_READY '+str(backup),flush=True)
