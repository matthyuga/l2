from pathlib import Path
import sys,json,struct,math,hashlib,subprocess,zlib,collections
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';V4=D.parent/'dust2-stairs-v4'
sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rects=json.loads((V4/'native-floor/rectangles.json').read_text());floorcells=collections.defaultdict(list)
for gx,gy,z,w,h,vz in rects:
 for y in range(gy,gy+h):
  for x in range(gx,gx+w):floorcells[x,y].append((z,vz))
bsp=(R/'research/dust2/source/de_dust2.bsp').read_bytes();lumps=[struct.unpack_from('<2i',bsp,4+i*8) for i in range(15)]
def lump(i):o,n=lumps[i];return bsp[o:o+n]
planes=list(struct.iter_unpack('<4fi',lump(1)));nodes=list(struct.iter_unpack('<i2h6h2H',lump(5)));leaves=list(struct.iter_unpack('<2i6h2H4B',lump(10)));head=struct.unpack_from('<i',lump(14),36)[0]
def solid(x,y,z):
 p=(x-141000,-(y-57000),z-8000);n=head
 while n>=0:
  nd=nodes[n];q=planes[nd[0]];n=nd[1 if sum(q[i]*p[i] for i in range(3))-q[3]>=0 else 2]
 return leaves[-n-1][0]==-2
walls=[]
for axis,line,start,z,h,length in json.loads((V4/'native-walls/walls.json').read_text()):
 if axis==0:lo=[131072+line*16-1,32768+start*16-.1,z-47.35];hi=[lo[0]+2,32768+(start+length)*16+.1,z-43.35+h]
 else:lo=[131072+start*16-.1,32768+line*16-1,z-47.35];hi=[131072+(start+length)*16+.1,lo[1]+2,z-43.35+h]
 walls.append((lo,hi))
flights=json.loads((D/'flights.json').read_text());accepted=[];rejected=[]
def point(f,along,u):return (u,along) if f['axis']==0 else (along,u)
def pz(f,u):return f['low']+(u-f['start'])/(f['end']-f['start'])*(f['high']-f['low'])
for idx,f in enumerate(flights):
 # Continue the same .5 slope back to an actual supported entry, if a prior
 # small riser makes the nominal approach start above the existing ground.
 for _ in range(8):
  cx,cy=point(f,(f['a']+f['b'])/2,f['start']-f['sign']*.1)
  entry=floorcells.get((int((cx-131072)//16),int((cy-32768)//16)),[])
  near=[h for _,h in entry if abs(h-f['low'])<70]
  if not near:break
  h=min(near,key=lambda h:abs(h-f['low']))
  if h>=f['low']-1:break
  extension=math.ceil(2*(f['low']-h)/16)*16
  f['start']-=f['sign']*extension;f['low']-=extension*.5
 valid=[];reasons=collections.Counter();run=abs(f['end']-f['start'])
 relevant=[]
 for lo,hi in walls:
  xx=[f['start'],f['end']] if f['axis']==0 else [f['a'],f['b']];yy=[f['a'],f['b']] if f['axis']==0 else [f['start'],f['end']]
  if hi[0]>=min(xx)-1 and lo[0]<=max(xx)+1 and hi[1]>=min(yy)-1 and lo[1]<=max(yy)+1 and hi[2]>f['low']+2 and lo[2]<f['high']+70:relevant.append((lo,hi))
 for a in range(int(f['a']),int(f['b']),16):
  reason=None
  for along in (a+2,a+8,a+14):
   for t in range(int(run)//4+1):
    u=f['start']+(f['end']-f['start'])*t/(run/4);x,y=point(f,along,u);z=pz(f,u)
    # At the upper seam select the approaching cell, not a higher side platform.
    ux=u-f['sign']*.1 if t==run/4 else u+f['sign']*.1
    fx,fy=point(f,along,ux);ls=floorcells.get((int((fx-131072)//16),int((fy-32768)//16)),[])
    near=[(gz,h) for gz,h in ls if abs(h-z)<70]
    if not near:reason='unsupported_or_higher_floor';break
    closest=min(near,key=lambda p:abs(p[1]-z))
    if closest[1]>z+1.1 or z-closest[1]>max(32,f['high']-f['low'])+1:reason='unsupported_or_higher_floor';break
    if any(solid(x,y,z+h) for h in (3,24,48,68)):reason='solid_body_or_ceiling';break
    if any(lo[0]-.01<x<hi[0]+.01 and lo[1]-.01<y<hi[1]+.01 and lo[2]<z+68 and hi[2]>z+3 for lo,hi in relevant):reason='native_wall';break
   if reason:break
  if reason:reasons[reason]+=1
  else:valid.append(a)
 # Keep contiguous valid strips; physical geometry is kept clear of the obstacles.
 while valid:
  a=valid.pop(0);b=a+16
  while valid and valid[0]==b:valid.pop(0);b+=16
  if b-a<16:reasons['narrow_strip']+=1;continue
  n=dict(f,a=a,b=b,source_flight=idx);accepted.append(n)
 if reasons:rejected.append(dict(flight=idx,reasons=dict(reasons)))
assert len(accepted)>20,(len(accepted),rejected)
(D/'ramps.json').write_text(json.dumps(accepted,indent=2));(D/'excluded.json').write_text(json.dumps(rejected,indent=2))
source=C/'Maps/24_19.unr';m=Edit(source);refs=[];disabled=[];cl=m.imp('Engine.StaticMeshActor','Core.Class');levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02')
for i,e in enumerate(m.exports):
 if e['name']=='HGDust2V5RampExample':
  disabled.append(i+1);changes={k:m.boolean(k,False) for k in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};m.replace(e,change_props(m,e,changes))
vs,ts=MeshLibrary(str(C/'StaticMeshes')).get('deco01','Box02');vlo=[min(v[i] for v in vs) for i in range(3)];vhi=[max(v[i] for v in vs) for i in range(3)];queries=0
for idx,f in enumerate(accepted):
 run=abs(f['end']-f['start']);angle=round(math.atan2(f['high']-f['low'],run)*65536/(2*math.pi));rot=[f['sign']*angle,0,0] if f['axis']==0 else [0,0,-f['sign']*angle]
 theta=angle*2*math.pi/65536;center=[(f['start']+f['end'])/2,(f['a']+f['b'])/2,(f['low']+f['high'])/2] if f['axis']==0 else [(f['a']+f['b'])/2,(f['start']+f['end'])/2,(f['low']+f['high'])/2]
 unit=actor_matrix(rot,1,[1,1,1]);loc=[center[i]-unit[i][2]*2 for i in range(3)];sx=(run/math.cos(theta)+.2)/(vhi[0]-vlo[0]) if f['axis']==0 else (f['b']-f['a']+.1)/(vhi[0]-vlo[0]);sy=(f['b']-f['a']+.1)/(vhi[1]-vlo[1]) if f['axis']==0 else (run/math.cos(theta)+.2)/(vhi[1]-vlo[1]);s3=[sx,sy,4/(vhi[2]-vlo[2])]
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.prop('Rotation',10,struct.pack('<3i',*rot),'Rotator')+m.float('DrawScale',1.)+m.vector('DrawScale3D',s3)
 for flag in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(flag,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1);refs.append(m.add('HGDust2V6Ramp'+str(idx).zfill(3),'Engine.StaticMeshActor',frame+raw,flags=0x2070001))
 wv=transform(vs,actor_matrix(rot,1,s3),loc)
 for along in (f['a']+2,(f['a']+f['b'])/2,f['b']-2):
  for k in range(int(run)//4+1):
   u=f['start']+f['sign']*k*4;x,y=point(f,along,u);hits=[]
   for face in ts:
    a,b,c=[wv[i] for i in face];v=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)];den=v[0]*w[1]-v[1]*w[0]
    if abs(den)<1e-8:continue
    s=((x-a[0])*w[1]-(y-a[1])*w[0])/den;t=(v[0]*(y-a[1])-v[1]*(x-a[0]))/den
    if s>=-1e-6 and t>=-1e-6 and s+t<=1.000001:hits.append(a[2]+s*v[2]+t*w[2])
   assert hits and abs(max(hits)-pz(f,u))<.02,(idx,x,y,hits,pz(f,u));queries+=1
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;oldrefs=[r.compact() for _ in range(n)];end=r.p;newrefs=[v for v in oldrefs if v not in disabled]+refs
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(newrefs),len(newrefs))+b''.join(ci(v) for v in newrefs)+m.b[end:level['offset']+level['size']]);out=m.save(D/'stage/Maps/24_19.unr')
geo=R/'server/game/data/geodata/24_19.l2j';data=geo.read_bytes();r=Reader(data);offsets={};decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:r.read(2);continue
  for cell in range(64):
   n=1 if ty==1 else r.num('B');x,y=bx*8+cell//8,by*8+cell%8
   for _ in range(n):
    off=r.p;v=r.num('H');z=decode(v)
    if 7500<z<8850:offsets[x,y,z]=(off,v)
patches={};rampcells=collections.defaultdict(list)
for idx,f in enumerate(accepted):
 for along in range(int(f['a'])+8,int(f['b']),16):
  for u in range(int(min(f['start'],f['end']))+8,int(max(f['start'],f['end'])),16):
   x,y=point(f,along,u);gx,gy=int((x-131072)//16),int((y-32768)//16);h=pz(f,u);keys=[k for k in offsets if k[0]==gx and k[1]==gy and abs(k[2]-(h+43.35))<=f['high']-f['low']+16]
   if not keys:continue
   key=min(keys,key=lambda k:abs(k[2]-(h+43.35)));nz=int(h+43.35)&~7
   if nz<key[2]:continue
   patches[key]=max(patches.get(key,key[2]),nz);rampcells[gx,gy].append((key,nz,idx))
patched=bytearray(data);changed=[]
for key,nz in patches.items():
 off,v=offsets[key];nv=((nz<<1)&0xfff0)|(v&15);struct.pack_into('<H',patched,off,nv)
 if nz!=key[2]:changed.append([*key,nz])
# Explicit paths within a checked ramp are traversable in both directions.
opened=0
for (gx,gy),rows in rampcells.items():
 for key,_,idx in rows:
  off,_=offsets[key];v=struct.unpack_from('<H',patched,off)[0];z=patches.get(key,key[2])
  for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
   if any(j==idx and abs(patches.get(k,k[2])-z)<=16 for k,_,j in rampcells.get((gx+dx,gy+dy),[])):
    if not v&bit:opened+=1;v|=bit
  struct.pack_into('<H',patched,off,v)
g=D/'stage/Geodata/24_19.l2j';g.parent.mkdir(parents=True,exist_ok=True);g.write_bytes(patched)
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True);subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(out)],capture_output=True,check=True)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(v^key for v in range(256)))==out.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
new=Edit(out);old=Edit(source);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel' or a['name']=='HGDust2V5RampExample':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
(D/'source-hashes.json').write_text(json.dumps({str(source):sha(source),str(geo):sha(geo)},indent=2));(D/'verification.json').write_text(json.dumps(dict(ramps=len(accepted),flights_analyzed=len(flights),native_ray_queries=queries,geo_heights_changed=len(changed),geo_bits_opened=opened,prior_payloads_preserved=preserved,changed=changed,client_test_pending=True),indent=2))
print('Prepared',len(accepted),'ramps;',queries,'native ray checks;',len(changed),'geo heights;',opened,'direction bits; excluded strips',len(rejected))
