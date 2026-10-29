"""Install the generated HELL GAMES startup art, keeping both V1 and original backups."""
from pathlib import Path
from PIL import Image
import numpy as np
import subprocess,json,hashlib,shutil,struct,datetime,sys
D=Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
source=Path(sys.argv[1]);assert source.is_file()
active=subprocess.run(['powershell.exe','-NoProfile','-Command','Get-Process L2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id; exit 0'],capture_output=True,text=True)
assert not active.stdout.strip(),'Client open: do not replace splash files in use'
manifest_path=D/'installation.json';original=json.loads(manifest_path.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
entries=[e for e in original['files'] if Path(e['target']).name.startswith('sp_')]
assert len(entries)==22
for e in entries:assert sha(e['target'])==e['installed_sha256'],'Splash changed concurrently: '+e['target']
backup=ROOT/'backups'/('client-loading-hellgames-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(manifest_path,backup/'previous-full-installation.json')
shutil.copy2(source,D/'startup-hellgames-v2.png')
rgba=Image.open(source).convert('RGBA');rgba.thumbnail((616,456),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(640,480),(0,0,0,0));canvas.paste(rgba,((640-rgba.width)//2,(480-rgba.height)//2));canvas.save(D/'startup-hellgames-640-v2.png')
assert canvas.getchannel('A').getextrema()==(0,255),'No actual alpha silhouette'
pixels=np.array(canvas);bgra=pixels[::-1,:,[2,1,0,3]].copy().tobytes();size=54+len(bgra)
header=struct.pack('<2sIHHI',b'BM',size,0,0,54)+struct.pack('<IiiHHIIiiII',40,640,480,1,32,0,len(bgra),2835,2835,0,0)
raw32=D/'startup-hellgames-32-v2.bmp';raw32.write_bytes(header+bgra)
pal=canvas.convert('RGB').quantize(colors=255,method=Image.Quantize.MEDIANCUT);idx=np.array(pal,dtype=np.uint16)+1
idx[np.array(canvas.getchannel('A'))<128]=0
fallback=Image.fromarray(idx.astype(np.uint8),'P');fallback.putpalette([0,0,0]+pal.getpalette()[:765]);raw256=D/'startup-hellgames-256-v2.bmp';fallback.save(raw256)
prepared=D/'prepared-hellgames';prepared.mkdir(exist_ok=True)
codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
changes=[]
for e in entries:
 target=Path(e['target']);output=prepared/target.name;raw=raw32 if '32b' in target.name else raw256
 r=subprocess.run([str(codec),'-c','encode','-p','121','-f',target.name,'-o',str(output),str(raw)],input=b'\n',capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 decoded=prepared/(target.name+'.decoded');r=subprocess.run([str(codec),'-o',str(decoded),str(output)],capture_output=True)
 assert r.returncode==0 and decoded.read_bytes()==raw.read_bytes(),target
 saved=backup/'client'/target.relative_to(CLIENT);saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 changes.append(dict(relative=str(target.relative_to(CLIENT)),target=str(target),backup=str(saved),before_sha256=sha(target),installed_sha256=sha(output)))
report=dict(brand='HELL GAMES',backup=str(backup),date=datetime.datetime.now().isoformat(),files=changes,master='startup-hellgames-v2.png',alpha=True,encoded_roundtrips=True,tested_ingame=False)
(D/'hellgames-installation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(backup/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
# All outputs and backups are ready before replacing any active file.
for e in entries:
 target=Path(e['target']);shutil.copy2(prepared/target.name,target);e['installed_sha256']=sha(target)
original.update(brand='HELL GAMES',panel_master='startup-hellgames-v2.png',brand_backup=str(backup))
manifest_path.write_text(json.dumps(original,indent=2),encoding='utf-8')
Path(original['backup'],'manifest.json').write_text(json.dumps(original,indent=2),encoding='utf-8')
for e in original['files']:assert sha(e['target'])==e['installed_sha256'],e['target']
print(json.dumps(dict(brand='HELL GAMES',installed_splash_files=len(entries),backup=str(backup),verified_total_files=len(original['files']),ingame_visual_check='pending next client launch'),indent=2))
