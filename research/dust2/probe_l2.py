"""Native resource feasibility probe only; no writes to installed L2 files."""
import pathlib,struct,subprocess,shutil,json
from PIL import Image
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];P=D/'l2-probe';P.mkdir(exist_ok=True);S=P/'compiler';S.mkdir(exist_ok=True)
base=ROOT/'research/airship-integration/compiler'
for p in base.iterdir():
 if p.is_file() and (p.suffix.lower() in ('.exe','.dll','.ini','.int') or p.name in ('Core.u','Engine.u','Editor.u','Fire.u','UnrealEd.u')):shutil.copy2(p,S/p.name)
verts=[];uv=[];groups={};mat=None
for line in (D/'Dust2-CS16.obj').open():
 s=line.split()
 if not s:continue
 if s[0]=='v':verts.append(tuple(map(float,s[1:4])))
 elif s[0]=='vt':uv.append(tuple(map(float,s[1:3])))
 elif s[0]=='usemtl':mat=s[1];groups.setdefault(mat,[])
 elif s[0]=='f':
  face=[tuple(int(v) if v else 0 for v in item.split('/')) for item in s[1:]]
  for i in range(1,len(face)-1):groups[mat].append([face[0],face[i],face[i+1]])
def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def st(s):
 b=s.encode()+b'\0';return b+(b'\0' if len(b)%2 else b'')
def vx(i):return struct.pack('>H',i) if i<65280 else b'\xff'+i.to_bytes(3,'big')
commands=[];parts=[];resized=[];assets=P/'assets';assets.mkdir(exist_ok=True)
for mi,(material,faces) in enumerate(groups.items()):
 name='DustTex'+str(mi).zfill(2);image=Image.open(D/'textures'/(material.lower()+'.png')).convert('RGB');original=image.size;target=tuple(1<<(n-1).bit_length() for n in original)
 if original!=target:image=image.resize(target,Image.Resampling.LANCZOS);resized.append(dict(material=material,original=original,converted=target))
 image.save(assets/(name+'.tga'));commands.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{(assets/(name+".tga")).as_posix()}" MIPS=ON')
 for start in range(0,len(faces),1400):
  fs=faces[start:start+1400];points=[];uvs=[];ids=[];lookup={}
  for face in fs:
   out=[]
   for vi,ti,*_ in face:
    key=(vi,ti)
    if key not in lookup:lookup[key]=len(points);points.append(verts[vi-1]);uvs.append(uv[ti-1])
    out.append(lookup[key])
   ids.append(out)
  data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',*(x*100 for x in v)) for v in points))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>H',3)+b''.join(vx(i) for i in f) for f in ids))+chunk(b'TAGS',st(name))+chunk(b'PTAG',b'SURF'+b''.join(vx(i)+b'\0\0' for i in range(len(ids))))
  data+=chunk(b'VMAD',b'TXUV'+struct.pack('>H',2)+st('Texture')+b''.join(vx(v)+vx(i)+struct.pack('>ff',uvs[v][0],1-uvs[v][1]) for i,f in enumerate(ids) for v in f))
  mapping=sub(b'IMAP',st('1')+sub(b'CHAN',b'COLR')+sub(b'ENAB',struct.pack('>H',1)))+sub(b'PROJ',struct.pack('>H',5))+sub(b'VMAP',st('Texture'))
  data+=chunk(b'SURF',st(name)+st('')+sub(b'COLR',struct.pack('>fffH',1,1,1,0))+sub(b'SIDE',struct.pack('>H',1))+sub(b'BLOK',mapping))
  mesh='DustPart'+str(len(parts)).zfill(2);path=assets/(mesh+'.lwo');path.write_bytes(b'FORM'+struct.pack('>I',len(data))+data);commands.append(f'#exec STATICMESH IMPORT NAME={mesh} FILE="{path.as_posix()}"');parts.append(dict(name=mesh,texture=name,source_material=material,triangles=len(ids)))
C=P/'HGDust2Probe/Classes';C.mkdir(parents=True,exist_ok=True);(C/'Dust2Asset.uc').write_text('class Dust2Asset extends Actor;\n'+'\n'.join(commands)+'\n')
ini=(S/'UT2003.ini').read_text()+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=HGDust2Probe\n';(S/'Dust2Probe.ini').write_text(ini)
assert not (S/'HGDust2Probe.u').exists(),'Probe already compiled; inspect previous proof'
with (P/'compile.log').open('w') as log:r=subprocess.run([str(S/'UCC.exe'),'make','-Silent','-NoBind','ini=Dust2Probe.ini','-unattended'],cwd=S,stdout=log,stderr=subprocess.STDOUT,timeout=120)
assert r.returncode==0,(P/'compile.log').read_text()[-2000:]
out=P/'roundtrip';out.mkdir(exist_ok=True)
with (P/'roundtrip.log').open('w') as log:r=subprocess.run([str(S/'UCC.exe'),'batchexport',str(S/'HGDust2Probe.u'),'StaticMesh','t3d',str(out),'ini=Dust2Probe.ini','-unattended'],cwd=S,stdout=log,stderr=subprocess.STDOUT,timeout=40)
assert r.returncode==0
for part in parts:
 text=(out/(part['name']+'.t3d')).read_text();part['reloaded_triangles']=text.count('Begin Triangle');assert part['reloaded_triangles']==part['triangles']
loaded=[];reader=ROOT/'research/amber-l2/tools/umodel.exe';logs=P/'native-load';logs.mkdir(exist_ok=True)
for name in [p['name'] for p in parts]+['DustTex'+str(i).zfill(2) for i in range(len(groups))]:
 r=subprocess.run([str(reader),'-dump','-game=l2','-path='+str(S),'HGDust2Probe.u',name],capture_output=True,text=True,errors='replace',timeout=20);t=r.stdout+r.stderr;(logs/(name+'.log')).write_text(t);assert r.returncode==0 and '*** ERROR' not in t and 'Unable to load' not in t;loaded.append(name)
report=dict(parts=parts,triangles=sum(p['triangles'] for p in parts),textures=len(groups),native_objects_loaded=len(loaded),resized_textures=resized,installed_in_l2=False,geodata_built=False,client_visual_verified=False)
(P/'proof.json').write_text(json.dumps(report,indent=2));print('DUST2_NATIVE_PROBE_PASS',report['triangles'],'triangles',len(parts),'meshes',len(groups),'textures',flush=True)
