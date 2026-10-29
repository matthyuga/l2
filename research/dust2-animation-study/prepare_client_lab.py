import pathlib,subprocess,shutil,re,struct,zlib,hashlib,json
root=pathlib.Path(r'E:\l2-local\research\dust2-animation-study')
source=pathlib.Path(r'E:\l2\system-hud'); dest=root/'client-lab/system';dest.mkdir(parents=True,exist_ok=True)
manifest=[]
for p in source.iterdir():
 if p.is_file():
  q=dest/p.name
  if q.exists():raise RuntimeError('Refusing overwrite of existing lab profile: '+str(q))
  shutil.copy2(p,q)
  manifest.append({'name':p.name,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size})
text=subprocess.check_output([r'E:\l2-local\tools\node-portable\node.exe',r'E:\l2-local\l2ini-local.js','decrypt',str(source/'l2.ini')]).decode('utf-8')
def pathline(m):
 value=m.group(1).strip(); old=(source/value).resolve()
 return 'Paths='+str(old).replace('\\','/')
text=re.sub(r'^Paths=(.*)$',pathline,text,flags=re.M)
# New animation override before all original paths; original system.u path is retained.
text=re.sub(r'(?m)^Paths=', 'Paths='+str((root/'client-lab/animations').resolve()).replace('\\','/')+'/*.ukx\nPaths=',text,count=1)
for key,folder in [('SavePath','Save'),('CachePath','Cache')]:
 target=root/'client-lab'/folder;target.mkdir(exist_ok=True)
 text=re.sub(r'(?m)^'+key+r'=.*$',key+'='+str(target).replace('\\','/'),text)
plain=text.encode('utf8');body='Lineage2Ver111'.encode('utf-16-le')+bytes(v^0xac for v in plain);tail=bytearray(20);struct.pack_into('<I',tail,12,zlib.crc32(body)&0xffffffff)
(dest/'l2.ini').write_bytes(body+tail)
assert bytes(v^0xac for v in (dest/'l2.ini').read_bytes()[28:-20])==plain
(root/'client-lab/profile-manifest.json').write_text(json.dumps({'source':str(source),'copied_files':manifest,'ini_override':text,'runtime_validated':False},indent=2),encoding='utf8')
print('Isolated profile copied:',len(manifest),'files.',round(sum(x['bytes'] for x in manifest)/1048576),'MiB. Original untouched.')
