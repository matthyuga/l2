"""One captured staircase: native sloped Box02 support and matching geodata."""
from pathlib import Path
import sys,json,struct,math,hashlib,subprocess,zlib,re
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=C/'Maps/24_19.unr';m=Edit(source);name='HGDust2V5RampExample';assert not any(e['name']==name for e in m.exports)
x0,x1,top_y,bottom_y,low,high=139232,139440,56464,56528,8000,8032
theta=math.atan2(high-low,bottom_y-top_y);roll=round(theta*65536/(2*math.pi));theta=roll*2*math.pi/65536
vs,ts=MeshLibrary(str(C/'StaticMeshes')).get('deco01','Box02');lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
length=(bottom_y-top_y)/math.cos(theta);s3=[(x1-x0+.1)/(hi[0]-lo[0]),(length+.2)/(hi[1]-lo[1]),4/(hi[2]-lo[2])]
loc=[(x0+x1)/2,(top_y+bottom_y)/2-2*math.sin(theta),(low+high)/2-2*math.cos(theta)]
cl=m.imp('Engine.StaticMeshActor','Core.Class');levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0')
raw=m.obj('StaticMesh',m.imp('deco01.Box02'))+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.prop('Rotation',10,struct.pack('<3i',0,0,roll),'Rotator')+m.float('DrawScale',1.)+m.vector('DrawScale3D',s3)
for flag in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(flag,True)
raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
ref=m.add(name,'Engine.StaticMeshActor',frame+raw,flags=0x2070001)
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];end=r.p;refs.append(ref)
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(refs),len(refs))+b''.join(ci(v) for v in refs)+m.b[end:level['offset']+level['size']]);out=m.save(D/'stage/Maps/24_19.unr')
new=Edit(out);p=new.props(next(e for e in new.exports if e['name']==name));assert p['Rotation']==[0,0,roll]
wv=transform(vs,actor_matrix(p['Rotation'],p['DrawScale'],p['DrawScale3D']),p['Location'])
def ramp_z(y):return (low+high)/2-math.tan(theta)*(y-(top_y+bottom_y)/2)
queries=[]
for x in (x0+2,(x0+x1)/2,x1-2):
 for y in range(top_y,bottom_y+1,4):
  hits=[]
  for face in ts:
   a,b,c=[wv[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];nz=u[0]*v[1]-u[1]*v[0]
   if abs(nz)<1e-8:continue
   s=((x-a[0])*v[1]-(y-a[1])*v[0])/nz;t=(u[0]*(y-a[1])-u[1]*(x-a[0]))/nz
   if s>=-1e-6 and t>=-1e-6 and s+t<=1.000001:hits.append(a[2]+s*u[2]+t*v[2])
  assert hits and abs(max(hits)-ramp_z(y))<.004,(x,y,hits,ramp_z(y));queries.append([x,y,max(hits)])
# Only the existing floor layer in the ramp footprint is raised, never an unrelated storey.
geo=R/'server/game/data/geodata/24_19.l2j';data=geo.read_bytes();r=Reader(data);patched=bytearray(data);changes=[];decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:r.read(2);continue
  for cell in range(64):
   count=1 if ty==1 else r.num('B');x=131072+(bx*8+cell//8)*16+8;y=32768+(by*8+cell%8)*16+8
   for _ in range(count):
    off=r.p;v=r.num('H');z=decode(v)
    if x0<x<x1 and top_y<y<bottom_y and 8032<=z<=8072:
     nz=int(ramp_z(y)+43.35)&~7;assert z<=nz<=z+16
     if nz!=z:struct.pack_into('<H',patched,off,((nz<<1)&0xfff0)|(v&15));changes.append([x,y,z,nz])
assert len(changes)==26,len(changes)
g=D/'stage/Geodata/24_19.l2j';g.parent.mkdir(parents=True,exist_ok=True);g.write_bytes(patched)
rel='data/scripts/custom/Dust2Arena/Dust2Arena.java';s=(R/'server/game'/rel).read_text(encoding='utf-8')
s=s.replace('a.equals("entrar")','a.equals("escalera")||a.equals("entrar")').replace('int[] s=a.equals("t")?T:CT;','int[] s=a.equals("escalera")?new int[]{139336,56560,8064}:a.equals("t")?T:CT;').replace('floor+24,0,0,false','floor+24,a.equals("escalera")?49152:0,0,false')
s=s.replace('.dust2 | ct | t | salir | estado.','.dust2 | ct | t | escalera | salir | estado.')
path=D/'stage/server'/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding='utf-8')
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True);subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(out)],capture_output=True,check=True)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(v^key for v in range(256)))==out.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
old=Edit(source);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']];preserved+=1
(D/'source-hashes.json').write_text(json.dumps({str(source):sha(source),str(geo):sha(geo),str(R/'server/game'/rel):sha(R/'server/game'/rel)},indent=2))
(D/'verification.json').write_text(json.dumps(dict(actor=name,rotation=p['Rotation'],location=p['Location'],drawscale3d=p['DrawScale3D'],slope_degrees=theta*180/math.pi,native_ray_queries=len(queries),geo_layers_changed=changes,prior_payloads_preserved=preserved,client_test_pending=True,scope='one captured staircase'),indent=2))
print('PREPARED local ramp:',len(queries),'native ray checks;',len(changes),'geo heights adjusted;',preserved,'existing payloads unchanged')
