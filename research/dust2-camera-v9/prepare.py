from pathlib import Path
import sys,json,math,struct,hashlib,subprocess,zlib,collections
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';V7=D.parent/'dust2-camera-v7';V8=D.parent/'dust2-camera-v8'
sys.path.insert(0,str(R/'research/gludio-sky'))
from package_tools import Edit,Reader,ci
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=C/'Maps/24_19.unr';m=Edit(source);prior=json.loads((V8/'installation.json').read_text())
assert sha(source)==prior['files'][0]['after_sha256']
rows=json.loads((V7/'camera-ceilings.json').read_text());grid=collections.defaultdict(list)
for x,y,z,h,c in rows:grid[x,y].append(h)
proposal=json.loads((V8/'split-proposal.json').read_text());adjust={(x,y,c):n for x,y,c,n in proposal}
# The proposal uses every neighboring walkable cell within 2 cells, covering
# the whole 16u cell plus 9u pawn radius, not just its center point.
def bodies(x0,y0,x1,y1):
 return [h for x in range(math.floor((x0-25-131072)/16),math.floor((x1+25-131072)/16)+1) for y in range(math.floor((y0-25-32768)/16),math.floor((y1+25-32768)/16)+1) if x0-25<131072+x*16+8<x1+25 and y0-25<32768+y*16+8<y1+25 for h in grid.get((x,y),[])]
refs=[];audit=[];levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02');cl=m.imp('Engine.StaticMeshActor','Core.Class')
def actor(kind,lo,hi):
 assert all(hi[i]>lo[i] for i in range(3));near=bodies(lo[0],lo[1],hi[0],hi[1]);assert not any(lo[2]<h+88 and hi[2]>h+2 for h in near),(kind,lo,hi)
 center=[(lo[i]+hi[i])/2 for i in range(3)];dims=[hi[i]-lo[i] for i in range(3)];s3=[dims[0]/19.891199112,dims[1]/19.891199112,dims[2]/21.134399414]
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',center)+m.vector('ColLocation',center)+m.float('DrawScale',1)+m.vector('DrawScale3D',s3)+m.float('CollisionRadius',math.hypot(dims[0]/2,dims[1]/2)+8)+m.float('CollisionHeight',dims[2]/2+8)
 for flag in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(flag,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end()
 name='HGDust2V9Camera'+kind+str(len(refs)).zfill(4);frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1);refs.append(m.add(name,'Engine.StaticMeshActor',frame+raw,flags=0x2070001));audit.append(dict(name=name,min=lo,max=hi))
# Regroup only the previously excluded roof into small, locally safe rectangles.
planes=collections.defaultdict(set)
for x,y,c,n in proposal:planes[n].add((x,y))
roof_rects=[]
for z,items in sorted(planes.items()):
 while items:
  x,y=min(items,key=lambda p:(p[1],p[0]));w=1
  while w<8 and (x+w,y) in items:w+=1
  h=1
  while h<8 and all((xx,y+h) in items for xx in range(x,x+w)):h+=1
  for xx in range(x,x+w):
   for yy in range(y,y+h):items.remove((xx,yy))
  lo=[131072+x*16-.1,32768+y*16-.1,z];hi=[131072+(x+w)*16+.1,32768+(y+h)*16+.1,z+4]
  actor('Roof',lo,hi);roof_rects.append([x,y,w,h,z])
# Build missing short joins at the adjusted roof's edges. Subtract standing body
# envelopes and already enabled V8 joins; never create a new wall through a path.
v8=json.loads((V8/'verification.json').read_text());enabled=set(v8['enabled']);existing=collections.defaultdict(list)
for b in json.loads((V7/'bounds-audit.json').read_text()):
 if b['name'] not in enabled or 'Seam' not in b['name']:continue
 lo,hi=b['min'],b['max'];axis=0 if hi[0]-lo[0]<3 else 1;line=round(((lo[axis]+hi[axis])/2-[131072,32768][axis])/16);other=1-axis
 for along in range(round((lo[other]+.1-[131072,32768][other])/16),round((hi[other]-.1-[131072,32768][other])/16)):existing[axis,line,along].append((lo[2],hi[2]))
bycell=collections.defaultdict(list)
for x,y,z,h,c in rows:bycell[x,y].append((h,adjust.get((x,y,c),c)))
def subtract(intervals,a,b):
 return [(lo,hi) for l,h in intervals for lo,hi in [(l,min(h,a)),(max(l,b),h)] if hi-lo>.1]
seen=set();trimmed=0;seams=0
for (x,y),layers in bycell.items():
 for floor,c in layers:
  for dx,dy in [(1,0),(0,1)]:
   candidates=[v for v in bycell.get((x+dx,y+dy),[]) if abs(v[0]-floor)<=32]
   if not candidates:continue
   nf,nc=min(candidates,key=lambda p:abs(p[0]-floor))
   if c==nc:continue
   axis=0 if dx else 1;line=x+1 if dx else y+1;along=y if dx else x;key=axis,line,along,min(c,nc),max(c,nc)
   if key in seen:continue
   seen.add(key);low,high=min(c,nc)-2,max(c,nc)+2
   if axis==0:xylo=[131072+line*16-1,32768+along*16-.1];xyhi=[xylo[0]+2,32768+(along+1)*16+.1]
   else:xylo=[131072+along*16-.1,32768+line*16-1];xyhi=[131072+(along+1)*16+.1,xylo[1]+2]
   ranges=[(low,high)]
   for a,b in existing.get((axis,line,along),[]):ranges=subtract(ranges,a,b)
   before=sum(b-a for a,b in ranges)
   for h in bodies(*xylo,*xyhi):ranges=subtract(ranges,h+1.9,h+88.1)
   if sum(b-a for a,b in ranges)<before-.01:trimmed+=1
   for a,b in ranges:actor('Join',xylo+[a],xyhi+[b]);seams+=1
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;oldrefs=[r.compact() for _ in range(n)];end=r.p
allrefs=oldrefs+refs;m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(allrefs),len(allrefs))+b''.join(ci(v) for v in allrefs)+m.b[end:level['offset']+level['size']])
out=m.save(D/'stage/Maps/24_19.unr');old=Edit(source);new=Edit(out)
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name']
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(out)],capture_output=True,check=True)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(v^key for v in range(256)))==out.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
loaded=Edit(encoded)
for e in loaded.exports:
 if e['name'].startswith('HGDust2V9'):
  p=loaded.props(e);assert p['bBlockNonZeroExtentTraces'] and p['bBlockZeroExtentTraces'] and p['bHidden']
report=dict(version='camera-v9',roof_rectangles=len(roof_rects),recovered_roof_cells=len(proposal),raised_roof_cells=sum(c!=n for x,y,c,n in proposal),max_roof_raise=max(n-c for x,y,c,n in proposal),added_joins=seams,joins_trimmed_for_body_clearance=trimmed,new_actors=len(refs),old_payloads_preserved_except_actor_list=True,source_sha256=sha(source),staged_sha256=sha(encoded),client_camera_test_pending=True)
(D/'verification.json').write_text(json.dumps(report,indent=2));(D/'bounds-audit.json').write_text(json.dumps(audit));(D/'roof-rectangles.json').write_text(json.dumps(roof_rects));print(json.dumps(report,indent=2))
