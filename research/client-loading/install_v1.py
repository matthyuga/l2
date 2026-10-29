"""Convert generated assets to the client's bitmap/texture formats, with rollback."""
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
import struct,subprocess,json,hashlib,datetime,shutil
D=Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2';SYSTEM=CLIENT/'system-hud'
codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
image_source=Path('C:/Users/KEVIN/.codex/generated_images/01a13116-182b-7163-a05c-230eb529110e/exec-14825794-e5ac-47b4-bd9b-ab66bb1e56b5.png')
shutil.copy2(image_source,D/'startup-panel-v1.png')
rgba=Image.open(image_source).convert('RGBA');rgba.thumbnail((616,456),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(640,480),(0,0,0,0));canvas.paste(rgba,((640-rgba.width)//2,(480-rgba.height)//2));canvas.save(D/'startup-panel-640-v1.png')
assert canvas.getchannel('A').getextrema()==(0,255),'Expected actual alpha silhouette'
# Native 32-bit BMP stores BGRA in bottom-up rows. Pillow's BMP reader ignores alpha.
pixels=np.array(canvas);bgra=pixels[::-1,:,[2,1,0,3]].copy().tobytes();size=54+len(bgra)
header=struct.pack('<2sIHHI',b'BM',size,0,0,54)+struct.pack('<IiiHHIIiiII',40,640,480,1,32,0,len(bgra),2835,2835,0,0)
raw32=D/'startup-32-v1.bmp';raw32.write_bytes(header+bgra)
# Older 256-colour fallback reserves palette index 0 as the transparent black colour.
rgb=canvas.convert('RGB');pal=rgb.quantize(colors=255,method=Image.Quantize.MEDIANCUT)
palette=pal.getpalette();idx=np.array(pal,dtype=np.uint16)+1;idx[np.array(canvas.getchannel('A'))<128]=0
fallback=Image.fromarray(idx.astype(np.uint8),'P');fallback.putpalette([0,0,0]+palette[:255*3]);fallback.save(D/'startup-256-v1.bmp')
before=Image.open(D/'loading-square-v1.png').convert('RGBA')
after=Image.open(D/'verify/L2EpicLoadingV1-e/Texture/LoadingBackground01.png').convert('RGBA')
assert ImageChops.difference(before,after).getbbox() is None,'Native texture roundtrip changed pixels'
active=subprocess.run(['powershell.exe','-NoProfile','-Command','Get-Process L2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id; exit 0'],capture_output=True,text=True)
assert not active.stdout.strip(),'Client is open; do not replace files in use'
backup=ROOT/'backups'/('client-loading-v1-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest=dict(backup=str(backup),date=datetime.datetime.now().isoformat(),profile=str(SYSTEM),files=[],tested_ingame=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save_manifest():
 (backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 (D/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
def install(source,target):
 target=Path(target);relative=target.relative_to(CLIENT);saved=None
 if target.exists():
  saved=backup/'client'/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 entry=dict(relative=str(relative),target=str(target),backup=str(saved) if saved else None,before_sha256=sha(target) if target.exists() else None,installed_sha256=sha(source))
 manifest['files'].append(entry);save_manifest();shutil.copy2(source,target)
 assert sha(target)==entry['installed_sha256']
def encode(raw,output,protocol):
 r=subprocess.run([str(codec),'-c','encode','-p',str(protocol),'-f',output.name,'-o',str(output),str(raw)],input=b'\n',capture_output=True)
 assert r.returncode==0,r.stdout+r.stderr
 check=D/(output.name+'.decoded')
 r=subprocess.run([str(codec),'-o',str(check),str(output)],capture_output=True)
 assert r.returncode==0 and check.read_bytes()==raw.read_bytes(),output
prepared=D/'prepared';prepared.mkdir(exist_ok=True)
for i in range(1,12):
 for mode,raw in (('32b',raw32),('256',D/'startup-256-v1.bmp')):
  name=f'sp_{mode}_{i:02d}.bmp';target=CLIENT/'systextures'/name
  assert target.is_file(),'Missing original splash variant '+name
  output=prepared/name;encode(raw,output,121);install(output,target)
package=D/'L2EpicLoadingV1-e.utx';assert not (CLIENT/'systextures'/package.name).exists(),'Custom package already installed'
install(package,CLIENT/'systextures'/package.name)
config=SYSTEM/'Localization.ini'
r=subprocess.run([str(codec),'-o',str(D/'localization.before.raw'),str(config)],capture_output=True);assert r.returncode==0
raw=(D/'localization.before.raw').read_bytes();old=b'English_LoadingTexture=L2Font-e.loading02-e';new=b'English_LoadingTexture=L2EpicLoadingV1-e.Skins.LoadingBackground01'
assert raw.count(old)==1,'Loading configuration changed; inspect before proceeding'
(D/'localization.modified.raw').write_bytes(raw.replace(old,new))
encoded=prepared/'Localization.ini';encode(D/'localization.modified.raw',encoded,111);install(encoded,config)
manifest.update(dict(bitmap_variants=22,texture_roundtrip_exact=True,encoded_file_roundtrips=True,splash_alpha=True,loading_master='epic-arrival-v1.png',panel_master='startup-panel-v1.png'))
save_manifest();print(json.dumps(dict(backup=str(backup),installed_files=len(manifest['files']),checks='native texture pixels, 22 encoded bitmap roundtrips, localization roundtrip and installed hashes PASS',client_visual_check='pending next launch'),indent=2))
