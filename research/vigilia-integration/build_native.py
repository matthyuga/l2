"""Compile baked ship with installed UE2 toolchain; stage against current map."""
import pathlib,sys,struct,shutil,subprocess,json,time,hashlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'research/gludio-sky'))
from package_tools import *
base=ROOT/'research/giran-editor-test/compiler';S=D/'compiler';S.mkdir(exist_ok=True)
for p in base.iterdir():
 if p.is_file() and (p.suffix.lower() in ('.exe','.dll','.int','.ini') or p.name in ('Core.u','Engine.u','Editor.u','UnrealEd.u','Fire.u')):shutil.copy2(p,S/p.name)
verts=[];uv=[];faces=[]
for l in (D/'HGVigilia.obj').open():
 s=l.split()
 if not s:continue
 if s[0]=='v':verts.append(tuple(map(float,s[1:4])))
 elif s[0]=='vt':uv.append(tuple(map(float,s[1:3])))
 elif s[0]=='f':
  f=[tuple(int(i) if i else 0 for i in t.split('/')) for t in s[1:]]
  for i in range(1,len(f)-1):faces.append([f[0],f[i],f[i+1]])
points=[];texcoords=[];triangles=[];lookup={};dropped=0
for face in faces:
 a,b,c=[verts[f[0]-1] for f in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 if sum(x*x for x in cross)<1e-16:dropped+=1;continue
 ids=[]
 for vi,ti,*_ in face:
  key=(vi,ti)
  if key not in lookup:lookup[key]=len(points);points.append(verts[vi-1]);texcoords.append(uv[ti-1])
  ids.append(lookup[key])
 triangles.append(ids)
def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def st(s):
 b=s.encode()+b'\0';return b+(b'\0' if len(b)%2 else b'')
def vx(i):return struct.pack('>H',i) if i<65280 else b'\xff'+i.to_bytes(3,'big')
assert len(points)<200000
mapping=sub(b'IMAP',st('1')+sub(b'CHAN',b'COLR')+sub(b'ENAB',struct.pack('>H',1)))+sub(b'PROJ',struct.pack('>H',5))+sub(b'VMAP',st('Texture'))
parts=[];commands=[]
for start in range(0,len(triangles),1800):
 fs=triangles[start:start+1800];used=sorted({v for f in fs for v in f});lookup={v:i for i,v in enumerate(used)};fs=[[lookup[v] for v in f] for f in fs];vs=[points[i] for i in used];uvs=[texcoords[i] for i in used]
 data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',v[0]*100,v[2]*100,-v[1]*100) for v in vs))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>H',3)+b''.join(vx(i) for i in t) for t in fs))+chunk(b'TAGS',st('VigiliaAtlas'))+chunk(b'PTAG',b'SURF'+b''.join(vx(i)+b'\0\0' for i in range(len(fs))))
 data+=chunk(b'VMAD',b'TXUV'+struct.pack('>H',2)+st('Texture')+b''.join(vx(v)+vx(i)+struct.pack('>ff',uvs[v][0],uvs[v][1]) for i,f in enumerate(fs) for v in f))
 data+=chunk(b'SURF',st('VigiliaAtlas')+st('')+sub(b'COLR',struct.pack('>fffH',1,1,1,0))+sub(b'SIDE',struct.pack('>H',1))+sub(b'BLOK',mapping))
 name='Vigilia'+str(len(parts)).zfill(2);path=D/(name+'.lwo');path.write_bytes(b'FORM'+struct.pack('>I',len(data))+data);parts.append(name);commands.append(f'#exec STATICMESH IMPORT NAME={name} FILE="{path.as_posix()}"')
C=D/'HGVigilia/Classes';C.mkdir(parents=True,exist_ok=True)
(C/'VigiliaAsset.uc').write_text(f'''class VigiliaAsset extends Actor;
#exec TEXTURE IMPORT NAME=VigiliaAtlas FILE="{(D/'VigiliaAtlas.tga').as_posix()}" MIPS=ON
{chr(10).join(commands)}
''')
ini=(S/'UT2003.ini').read_text()+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=HGVigilia\n';(S/'Vigilia.ini').write_text(ini)
if (S/'HGVigilia.u').exists():shutil.move(S/'HGVigilia.u',D/('trial-'+str(time.time_ns())+'.u'))
with (D/'compile.log').open('w') as log:r=subprocess.run([str(S/'UCC.exe'),'make','-Silent','-NoBind','ini=Vigilia.ini','-unattended'],cwd=S,stdout=log,stderr=subprocess.STDOUT,timeout=180)
assert r.returncode==0,(D/'compile.log').read_text()[-1600:]
stage=D/'stage';(stage/'StaticMeshes').mkdir(parents=True,exist_ok=True);(stage/'Maps').mkdir(exist_ok=True)
p=Edit(S/'HGVigilia.u')
atlasref=next(i+1 for i,e in enumerate(p.exports) if e['name']=='VigiliaAtlas')
p.add('VigiliaSurface','Engine.FinalBlend',p.obj('Material',atlasref)+p.boolean('TwoSided',True)+p.boolean('ZWrite',True)+p.boolean('ZTest',True)+p.end(),flags=0xf0004)
p.save(stage/'StaticMeshes/HGVigilia.usx')
if '--package-only' in sys.argv:
 print('REBUILT_PACKAGE_ONLY',flush=True);sys.exit(0)
source=ROOT.parent/'l2/maps/24_19.unr';m=Edit(source);assert not any(e['name'].startswith('HGVigiliaDocked') for e in m.exports),'Already installed'
location=[146500.,52000.,11600.];scale=1.;levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0')
newrefs=[]
for part in parts:
 mesh=m.imp('HGVigilia.'+part);material=m.imp('HGVigilia.VigiliaSurface','Engine.FinalBlend')
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.obj('Skins',material,index=0)+m.vector('Location',location)+m.vector('ColLocation',location)+m.float('DrawScale',scale)
 for n,val in [('bDynamicActorFilterState',True),('bIgnoredRange',True),('bSunAffect',True),('bUpdateShadow',False),('bCollideActors',False),('bBlockActors',False),('bBlockPlayers',False),('bBlockZeroExtentTraces',False),('bBlockNonZeroExtentTraces',False)]:raw+=m.boolean(n,val)
 raw+=m.prop('AmbientGlow',1,bytes([48]))+m.nametag('Tag','StaticMeshActor')+m.end();cl=m.imp('Engine.StaticMeshActor','Core.Class');frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 newrefs.append(m.add('HGVigiliaDocked'+part,'Engine.StaticMeshActor',frame+raw,flags=0x2070001))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',count+len(newrefs),count+len(newrefs))+b''.join(ci(i) for i in refs+newrefs)+m.b[end:level['offset']+level['size']]);m.save(stage/'Maps/24_19.unr')
(D/'build-audit.json').write_text(json.dumps(dict(location=location,scale=scale,triangles=len(triangles),dropped_degenerate=dropped,vertices=len(points),source_map_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),original_level_actors=count,added_actors=len(newrefs),parts=parts),indent=2))
print('BUILT',len(triangles),'triangles',len(points),'vertices; native ship and map staged',flush=True)
