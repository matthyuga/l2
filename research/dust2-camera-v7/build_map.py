from pathlib import Path
import sys,json,struct,math,collections,subprocess,zlib,hashlib,re
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';V6=D.parent/'dust2-ramps-v6';V4=D.parent/'dust2-stairs-v4'
sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'));from geolib.meshes import actor_matrix,transform,MeshLibrary
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=C/'Maps/24_19.unr';m=Edit(source);cl=m.imp('Engine.StaticMeshActor','Core.Class');levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02');refs=[];disabled=[]
vs,ts=MeshLibrary(str(C/'StaticMeshes')).get('deco01','Box02');lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];audit=[]
def actor(name,center,dimensions,rot=(0,0,0),camera=False):
 s3=[dimensions[i]/(hi[i]-lo[i]) for i in range(3)];wv=transform(vs,actor_matrix(rot,1,s3),center);mn=[min(v[i] for v in wv) for i in range(3)];mx=[max(v[i] for v in wv) for i in range(3)]
 radius=math.hypot((mx[0]-mn[0])/2,(mx[1]-mn[1])/2)+8;height=(mx[2]-mn[2])/2+8
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',center)+m.vector('ColLocation',center)+m.prop('Rotation',10,struct.pack('<3i',*rot),'Rotator')+m.float('DrawScale',1.)+m.vector('DrawScale3D',s3)+m.float('CollisionRadius',radius)+m.float('CollisionHeight',height)
 for flag in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bHidden']:raw+=m.boolean(flag,True)
 raw+=m.boolean('bBlockNonZeroExtentTraces',not camera)+m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 refs.append(m.add(name,'Engine.StaticMeshActor',frame+raw,flags=0x2070001));audit.append(dict(name=name,min=mn,max=mx,camera_only_zero_extent=camera,radius=radius,height=height));return wv
for i,e in enumerate(m.exports):
 if e['name'].startswith('HGDust2V6Ramp'):
  disabled.append(i+1);changes={k:m.boolean(k,False) for k in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};m.replace(e,change_props(m,e,changes))
# Short native pieces reproduce the validated plane and avoid long actor extents.
tiles=[];seen=set();raychecks=0
for fi,f in enumerate(json.loads((V6/'ramps.json').read_text())):
 run=abs(f['end']-f['start']);angle=round(math.atan2(f['high']-f['low'],run)*65536/(2*math.pi));theta=angle*2*math.pi/65536;rot=[f['sign']*angle,0,0] if f['axis']==0 else [0,0,-f['sign']*angle]
 def z_at(u):return f['low']+(u-f['start'])/(f['end']-f['start'])*(f['high']-f['low'])
 for a in range(int(f['a']),int(f['b']),32):
  b=min(a+32,f['b'])
  for u in range(int(min(f['start'],f['end'])),int(max(f['start'],f['end'])),32):
   v=min(u+32,max(f['start'],f['end']));key=(f['axis'],a,b,u,v,round(z_at(u),4),round(z_at(v),4))
   if key in seen:continue
   seen.add(key);center=[(u+v)/2,(a+b)/2,z_at((u+v)/2)] if f['axis']==0 else [(a+b)/2,(u+v)/2,z_at((u+v)/2)]
   mat=actor_matrix(rot,1,[1,1,1]);loc=[center[i]-mat[i][2]*2 for i in range(3)];dim=[(v-u)/math.cos(theta)+.2,b-a+.1,4] if f['axis']==0 else [b-a+.1,(v-u)/math.cos(theta)+.2,4]
   name='HGDust2V7RampTile'+str(len(tiles)).zfill(4);wv=actor(name,loc,dim,rot)
   for along in (a+1,(a+b)/2,b-1):
    for uu in (u,(u+v)/2,v):
     x,y=(uu,along) if f['axis']==0 else (along,uu);hits=[]
     for face in ts:
      aa,bb,cc=[wv[i] for i in face];vx,vy,vz=[bb[i]-aa[i] for i in range(3)];wx,wy,wz=[cc[i]-aa[i] for i in range(3)];den=vx*wy-vy*wx
      if abs(den)<1e-8:continue
      s=((x-aa[0])*wy-(y-aa[1])*wx)/den;t=(vx*(y-aa[1])-vy*(x-aa[0]))/den
      if s>=-1e-6 and t>=-1e-6 and s+t<=1.000001:hits.append(aa[2]+s*vz+t*wz)
     assert hits and abs(max(hits)-z_at(uu))<.01,(name,x,y,hits,z_at(uu));raychecks+=1
   tiles.append(dict(name=name,flight=fi,a=a,b=b,u=u,v=v,axis=f['axis']))
# Adapted invisible ceiling follows each walkable level, capped at 128u clearance.
ceilings=json.loads((D/'camera-ceilings.json').read_text());bycell=collections.defaultdict(list)
for x,y,z,h,c in ceilings:bycell[x,y].append((z,h,c))
for i,(x,y,z,w,h) in enumerate(json.loads((D/'ceiling-boxes.json').read_text())):actor('HGDust2V7CameraCeil'+str(i).zfill(4),[x+w/2,y+h/2,z+2],[w+.2,h+.2,4],camera=True)
# Close the vertical gaps where adjacent invisible ceiling heights change.
seams=collections.defaultdict(set)
for (x,y),layers in bycell.items():
 for z,h,c in layers:
  for dx,dy in [(1,0),(0,1)]:
   near=[row for row in bycell.get((x+dx,y+dy),[]) if abs(row[1]-h)<=32]
   if not near:continue
   nz,nh,nc=min(near,key=lambda row:abs(row[1]-h))
   if abs(c-nc)<1:continue
   axis=0 if dx else 1;line=x+1 if dx else y+1;along=y if dx else x;seams[axis,line,min(c,nc),max(c,nc)].add(along)
seam_count=0
for (axis,line,z0,z1),items in seams.items():
 while items:
  start=min(items);end=start+1
  while end in items:end+=1
  items.difference_update(range(start,end));length=(end-start)*16
  center=[131072+line*16,32768+(start+end)*8,(z0+z1)/2] if axis==0 else [131072+(start+end)*8,32768+line*16,(z0+z1)/2];size=[2,length+.2,z1-z0+4] if axis==0 else [length+.2,2,z1-z0+4]
  actor('HGDust2V7CameraSeam'+str(seam_count).zfill(4),center,size,camera=True);seam_count+=1
# Camera boundaries extend existing closed edges up to their local invisible roof.
wall_count=0
for axis,line,start,z,h,length in json.loads((V4/'native-walls/walls.json').read_text()):
 caps=[]
 for along in range(start,start+length):
  sides=[(line-1,along),(line,along)] if axis==0 else [(along,line-1),(along,line)]
  for cell in sides:
   caps.extend(c for gz,hh,c in bycell.get(cell,[]) if abs(gz-z)<=24)
 if not caps:continue
 bottom=z-43.35-4;top=max(caps)+4
 center=[131072+line*16,32768+(start+length/2)*16,(bottom+top)/2] if axis==0 else [131072+(start+length/2)*16,32768+line*16,(bottom+top)/2];size=[3,length*16+.2,top-bottom] if axis==0 else [length*16+.2,3,top-bottom]
 actor('HGDust2V7CameraWall'+str(wall_count).zfill(4),center,size,camera=True);wall_count+=1
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;oldrefs=[r.compact() for _ in range(n)];end=r.p;newrefs=[v for v in oldrefs if v not in disabled]+refs
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(newrefs),len(newrefs))+b''.join(ci(v) for v in newrefs)+m.b[end:level['offset']+level['size']]);out=m.save(D/'stage/Maps/24_19.unr')
new=Edit(out);old=Edit(source);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel' or a['name'].startswith('HGDust2V6Ramp'):continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True);subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(out)],capture_output=True,check=True)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(v^key for v in range(256)))==out.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
profile=D/'user.dec.ini';plain=profile.read_bytes();plain,n=re.subn(rb'HitCheckCameraMinDist=300\b',b'HitCheckCameraMinDist=0',plain);assert n==1
staged=D/'stage/user.ini';staged.write_bytes(plain);enc=D/'client/user.ini';subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','413','-o',str(enc),str(staged)],capture_output=True,check=True)
decoded=D/'user.roundtrip.ini';subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','decode','-o',str(decoded),str(enc)],capture_output=True,check=True);assert decoded.read_bytes()==plain
paths=[source,C/'system-hud/user.ini',R/'server/game/data/geodata/24_19.l2j'];(D/'source-hashes.json').write_text(json.dumps({str(p):sha(p) for p in paths},indent=2))
(D/'tiles.json').write_text(json.dumps(tiles));(D/'bounds-audit.json').write_text(json.dumps(audit));(D/'verification.json').write_text(json.dumps(dict(ramp_tiles=len(tiles),max_ramp_tile_run=32,max_ramp_tile_width=32,ramp_ray_checks=raychecks,camera_ceilings=len(json.loads((D/'ceiling-boxes.json').read_text())),camera_walls=wall_count,camera_seams=seam_count,old_ramps_disabled=len(disabled),previous_payloads_preserved=preserved,geodata_unchanged=True,zoom_max_preserved=1800,hit_check_min_dist=0,client_test_pending=True),indent=2))
print('Prepared',len(tiles),'short ramp pieces;',raychecks,'native rays;',wall_count,'camera sides;',seam_count,'roof joins;',preserved,'previous exports preserved')
