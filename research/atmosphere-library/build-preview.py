"""Local web previews; source archives and client packages are never modified."""
import audioop,hashlib,json,pathlib,re,struct,wave,zipfile
import numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'preview';OUT.mkdir(exist_ok=True)
items=[];errors=[]
def save_catalog(preparing=True):
 available=items
 if preparing and (ROOT/'preview-catalog.json').exists():
  previous=json.loads((ROOT/'preview-catalog.json').read_text(encoding='utf8'))
  available=list({item['id']:item for item in previous['items']+items}.values())
 catalog={'items':available,'errors':errors,'preparing':preparing,'audioNote':'Fragmentos mono de hasta 12 segundos de los ZIP de Sonniss ya terminados. Freesound pendiente de login.'}
 temp=ROOT/'preview-catalog.tmp';temp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(ROOT/'preview-catalog.json')
def ident(path):return hashlib.sha1(str(path).replace('\\','/').encode()).hexdigest()[:20]
def emit_image(p,kind,provider,source,frames=1):
 key=ident(p.relative_to(ROOT));dest=OUT/(key+('.jpg' if kind=='sky' else '.png'));thumb=OUT/(key+'-thumb.jpg')
 with Image.open(p) as im:
  size=list(im.size)
  if kind=='sky':im.draft('RGB',(2048,1024))
  if not dest.exists():
   copy=im.convert('RGB' if kind=='sky' else 'RGBA');copy.thumbnail((2048,1024) if kind=='sky' else (4096,512));copy.save(dest,quality=90)
  if not thumb.exists():
   copy=im.crop((0,0,im.width//frames,im.height)).convert('RGBA');copy.thumbnail((300,150))
   bg=Image.new('RGB',copy.size,'#303a43');bg.paste(copy,mask=copy.getchannel('A'));bg.save(thumb,quality=82)
 title=p.stem.replace('_',' ').replace('-',' ')
 items.append(dict(id=key,type=kind,title=title,provider=provider,url='/atmosphere/'+dest.name,thumbnail='/atmosphere/'+thumb.name,frames=frames,dimensions=size,source=source,original=p.relative_to(ROOT).as_posix()))
 if len(items)%16==0:save_catalog()
def audio_preview(z,info):
 key=ident(z.filename+'::'+info.filename);dest=OUT/(key+'.wav');meta=OUT/(key+'.json')
 if meta.exists() and dest.exists():items.append(json.loads(meta.read_text(encoding='utf8')));return
 # Read RIFF chunks explicitly to support PCM, IEEE float and WAVE extensible.
 with z.open(info) as f:
  if f.read(4)!=b'RIFF':raise ValueError('Not RIFF')
  f.read(4)
  if f.read(4)!=b'WAVE':raise ValueError('Not WAVE')
  fmt=None
  while True:
   head=f.read(8)
   if len(head)!=8:raise ValueError('Missing WAVE data')
   chunk,n=struct.unpack('<4sI',head)
   if chunk==b'fmt ':fmt=f.read(n)
   elif chunk==b'data':
    if fmt is None:raise ValueError('Missing WAVE format')
    code,channels,rate,_,block,bits=struct.unpack('<HHIIHH',fmt[:16])
    if code==65534 and len(fmt)>=40:code=struct.unpack('<H',fmt[24:26])[0]
    raw=f.read(min(n,rate*block*12));break
   else:
    remaining=n
    while remaining:
     skip=f.read(min(remaining,1024*1024))
     if not skip:raise ValueError('Truncated WAVE')
     remaining-=len(skip)
   if n%2:f.read(1)
 if channels<1 or channels>16 or rate<1000 or block!=channels*(bits//8):raise ValueError('Unsupported format')
 raw=raw[:len(raw)//block*block]
 if code==3 and bits in (32,64):
  a=np.frombuffer(raw,dtype='<f4' if bits==32 else '<f8').reshape(-1,channels).mean(axis=1)
  raw=(np.nan_to_num(a).clip(-1,1)*32767).astype('<i2').tobytes()
 elif code==1 and bits in (8,16,24,32):
  width=bits//8
  if width==1:raw=audioop.bias(raw,1,-128)
  raw=audioop.lin2lin(raw,width,2)
  if channels>1:raw=np.frombuffer(raw,dtype='<i2').reshape(-1,channels).mean(axis=1).astype('<i2').tobytes()
 else:raise ValueError(f'Unsupported codec {code}/{bits}')
 raw=audioop.ratecv(raw,2,1,rate,22050,None)[0]
 temp=dest.with_suffix('.tmp')
 with wave.open(str(temp),'wb') as out:out.setparams((1,2,22050,0,'NONE','not compressed'));out.writeframes(raw)
 temp.replace(dest)
 item=dict(id=key,type='audio',title=pathlib.PurePosixPath(info.filename).stem,provider='Sonniss',url='/atmosphere/'+dest.name,duration=round(len(raw)/44100,2),source='https://sonniss.com/gameaudiogdc/',original=pathlib.Path(z.filename).name+' :: '+info.filename,license='Sonniss GDC Bundle')
 meta.write_text(json.dumps(item,ensure_ascii=False),encoding='utf8');items.append(item)
if __name__=='__main__':
 import msvcrt
 lock=(ROOT/'preview-build.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
 try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 except OSError:print('Preview builder already running',flush=True);raise SystemExit(0)
 for p in sorted((ROOT/'polyhaven').glob('*/*.jpg')):
  emit_image(p,'sky','Poly Haven','https://polyhaven.com/a/'+p.parent.name)
 for p in sorted((ROOT/'cloudy').glob('extracted/*/Panorama/*.png')):
  emit_image(p,'sky','Screaming Brain Studios','https://opengameart.org/content/cloudy-skyboxes-0')
 for p in sorted((ROOT/'kenney-sky').glob('extracted/*/Skyboxes/*.png')):
  emit_image(p,'sky','Kenney','https://kenney.nl/assets/skyboxes')
 for folder,provider,url in [('kenney-particles','Kenney','https://kenney.nl/assets/particle-pack'),('kenney-smoke','Kenney','https://kenney.nl/assets/smoke-particles'),('spritepilot','SpritePilot','https://spritepilot.com/free-game-assets/weather')]:
  for p in sorted((ROOT/folder/'extracted').rglob('*.png')):
   if folder=='kenney-particles' and 'PNG (Transparent)' not in p.parts:continue
   if folder=='kenney-smoke' and 'PNG' not in p.parts:continue
   if folder=='spritepilot' and '32px' not in p.parts:continue
   frames=int(re.search(r'_strip(\d+)',p.stem)[1]) if re.search(r'_strip(\d+)',p.stem) else 1
   emit_image(p,'particle',provider,url,frames)
 print('Images prepared:',len(items),flush=True)
 save_catalog()
 for sidecar in sorted((ROOT/'sonniss').glob('*.zip.source.json')):
  archive=pathlib.Path(str(sidecar).removesuffix('.source.json'))
  with zipfile.ZipFile(archive) as z:
   for info in z.infolist():
    name=pathlib.PurePosixPath(info.filename).name.lower()
    if not name.endswith('.wav') or not re.search(r'rain|wind|thunder|storm|forest|bird|river|waves?|water|fire|ambien',name):continue
    try:audio_preview(z,info)
    except Exception as e:errors.append({'file':archive.name+' :: '+info.filename,'error':str(e)})
  print('Indexed',archive.name,flush=True)
  save_catalog()
 save_catalog(False)
 print('FINISHED',len(items),'resources;',len(errors),'unsupported audio files',flush=True)
