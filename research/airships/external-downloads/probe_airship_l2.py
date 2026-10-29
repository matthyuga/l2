"""Geometry-only L2/UE2 conversion probe. Never writes the live client."""
import pathlib,struct,re,shutil,subprocess,json,time,sys
from PIL import Image
D=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship';optimized='--optimized' in sys.argv;P=D/('l2-probe-optimized' if optimized else 'l2-probe');P.mkdir(exist_ok=True)
base=D.parents[2]/'giran-editor-test/compiler'
S=P/'system';S.mkdir(exist_ok=True)
for p in base.iterdir():
 if p.is_file() and p.suffix.lower() in ('.exe','.dll','.int','.u','.ini') and p.name not in ('HGStatueProbe.u','trial.u'):shutil.copy2(p,S/p.name)
verts=[];uvs=[];groups=[];group=None;mat='Default'
for line in (D/'airship-probe-optimized.obj' if optimized else D/'airship02obj/airship02obj.obj').open():
 s=line.split()
 if not s:continue
 if s[0]=='v':verts.append(tuple(map(float,s[1:4])))
 elif s[0]=='vt':uvs.append(tuple(map(float,s[1:3])))
 elif s[0]=='o':group=dict(name=s[1],faces=[]);groups.append(group)
 elif s[0]=='usemtl':mat=s[1]
 elif s[0]=='f':
  face=[tuple(int(i) if i else 0 for i in t.split('/')) for t in s[1:]]
  for i in range(1,len(face)-1):group['faces'].append((mat,[face[0],face[i],face[i+1]]))
def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def st(s):
 b=s.encode()+b'\0';return b+(b'\0' if len(b)%2 else b'')
def vx(i):return struct.pack('>H',i) if i<65280 else bytes([255])+i.to_bytes(3,'big')
materials=sorted(set(m for g in groups for m,f in g['faces']));matnames={m:'Mat'+str(i) for i,m in enumerate(materials)}
assets=P/'assets';assets.mkdir(exist_ok=True);cmds=[]
for m in materials:
 n=matnames[m];Image.new('RGB',(8,8),(155,130,90)).save(assets/(n+'.tga'));cmds.append(f'#exec TEXTURE IMPORT NAME={n} FILE="{(assets/(n+".tga")).as_posix()}" MIPS=ON')
info=[]
for j,g in enumerate(groups):
 if not g['faces']:continue
 points=[];uv=[];faces=[];mats=[];lookup={}
 for m,f in g['faces']:
  ids=[];mats.append(materials.index(m))
  for v,t,*_ in f:
   k=(v,t)
   if k not in lookup:lookup[k]=len(points);points.append(verts[v-1]);uv.append(uvs[t-1] if t else (0,0))
   ids.append(lookup[k])
  faces.append(ids)
 # OBJ has Y-up axes; LWO importer transforms X,Y,Z -> X,-Z,Y.
 data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',*(x*100 for x in v)) for v in points))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>H',3)+b''.join(vx(i) for i in f) for f in faces))+chunk(b'TAGS',b''.join(st(matnames[m]) for m in materials))+chunk(b'PTAG',b'SURF'+b''.join(vx(i)+struct.pack('>H',m) for i,m in enumerate(mats)))
 data+=chunk(b'VMAP',b'TXUV'+struct.pack('>H',2)+st('Texture')+b''.join(vx(i)+struct.pack('>ff',u,1-v) for i,(u,v) in enumerate(uv)))
 data+=chunk(b'VMAD',b'TXUV'+struct.pack('>H',2)+st('Texture')+b''.join(vx(v)+vx(i)+struct.pack('>ff',uv[v][0],1-uv[v][1]) for i,f in enumerate(faces) for v in f))
 for m in materials:
  mapping=sub(b'IMAP',st('1')+sub(b'CHAN',b'COLR')+sub(b'ENAB',struct.pack('>H',1)))+sub(b'PROJ',struct.pack('>H',5))+sub(b'VMAP',st('Texture'))
  data+=chunk(b'SURF',st(matnames[m])+st('')+sub(b'COLR',struct.pack('>fffH',1,1,1,0))+sub(b'SIDE',struct.pack('>H',1))+sub(b'BLOK',mapping))
 n='Part'+str(j).zfill(2);path=assets/(n+'.lwo');path.write_bytes(b'FORM'+struct.pack('>I',len(data))+data);cmds.append(f'#exec STATICMESH IMPORT NAME={n} FILE="{path.as_posix()}"');info.append(dict(name=n,source=g['name'],triangles=len(faces)))
classes=P/'HGAirshipProbe/Classes';classes.mkdir(parents=True,exist_ok=True);(classes/'AirshipProbe.uc').write_text('class AirshipProbe extends Actor;\n'+'\n'.join(cmds)+'\n')
ini=(S/'UT2003.ini').read_text()+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=HGAirshipProbe\n';(S/'AirshipProbe.ini').write_text(ini)
if (S/'HGAirshipProbe.u').exists():shutil.move(S/'HGAirshipProbe.u',P/('trial-'+str(time.time_ns())+'.u'))
with (P/'compile.log').open('w') as log:r=subprocess.run([str(S/'UCC.exe'),'make','-Silent','-NoBind','ini=AirshipProbe.ini','-unattended'],cwd=S,stdout=log,stderr=subprocess.STDOUT,timeout=120)
print('COMPILE',r.returncode,flush=True);out=P/'roundtrip';out.mkdir(exist_ok=True)
if r.returncode==0:
 with (P/'reload.log').open('w') as log:r=subprocess.run([str(S/'UCC.exe'),'batchexport',str(S/'HGAirshipProbe.u'),'StaticMesh','t3d',str(out),'ini=AirshipProbe.ini','-unattended'],cwd=S,stdout=log,stderr=subprocess.STDOUT,timeout=60)
 print('RELOAD',r.returncode,flush=True)
 for row in info:
  f=out/(row['name']+'.t3d')
  if f.exists():
   text=f.read_text();row['reloaded_triangles']=text.count('Begin Triangle');coords=re.findall(r'Vertex \d+ [-\d.]+ [-\d.]+ [-\d.]+ ([-\d.]+) ([-\d.]+)',text);row['nonzero_uv']=sum(abs(float(u))+abs(float(v))>1e-6 for u,v in coords)
(P/'proof.json').write_text(json.dumps(dict(parts=info,geometry_only=True,textures_are_placeholders=True,in_game_verified=False),indent=2))
print('PARTS',len(info),'TRIANGLES',sum(i['triangles'] for i in info),'RELOADED',sum(i.get('reloaded_triangles',0) for i in info),flush=True)
