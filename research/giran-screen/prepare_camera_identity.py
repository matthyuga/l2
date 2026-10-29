"""Give only the camera executable its own original Interlude splash paths."""
from pathlib import Path
import hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent
root=D.parents[1]; client=root.parent/'l2'
exe=client/'system-camera-online/L2.exe'
backup=root/'backups/giran-screen-20261016/source/L2.exe'
sha=lambda b:hashlib.sha256(b).hexdigest()
b=exe.read_bytes(); before=sha(b)
assert before=='790d9068796714389d82a400d14d26dcb9e6ecdfc6c2b5eba92ebd1a441b10ee',before
if not backup.exists():shutil.copy2(exe,backup)
changes=[]
for enc in ['ascii','utf-16le']:
 for variant in ['256','32b']:
  old=('..\\SysTextures\\sp_'+variant+'_%02d.bmp').encode(enc)
  new=('..\\camtextures\\sp_'+variant+'_%02d.bmp').encode(enc)
  assert len(old)==len(new) and b.count(old)==1
  changes.append({'offset':b.index(old),'length':len(old),'encoding':enc,'variant':variant})
  b=b.replace(old,new)
target=client/'camtextures';target.mkdir(exist_ok=True)
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
assets=[]
for original in sorted((root/'research/client-loading').glob('sp_*.bmp.decoded')):
 name=original.name.removesuffix('.decoded'); output=target/name
 result=subprocess.run([str(codec),'-c','encode','-p','121','-f',name,'-o',str(output),str(original)],capture_output=True,check=True)
 check=D/(name+'.check')
 subprocess.run([str(codec),'-f',name,'-o',str(check),str(output)],capture_output=True,check=True)
 assert check.read_bytes()==original.read_bytes();check.unlink()
 assets.append({'name':name,'sha256':sha(output.read_bytes())})
assert len(assets)==22
original=exe.read_bytes(); allowed=set()
for c in changes:allowed.update(range(c['offset'],c['offset']+c['length']))
assert len(b)==len(original) and all(i in allowed for i,(x,y) in enumerate(zip(original,b)) if x!=y)
exe.write_bytes(b)
(D/'camera-identity.json').write_text(json.dumps({'before':before,'after':sha(b),'changes':changes,'assets':assets,'backup':str(backup)},indent=2))
print('PASS camera-only original splash paths, 22 encrypted BMP roundtrips; executable length and all other bytes preserved')
