"""Stock-client wall colliders for closed NSWE edges and unsupported boundaries."""
import pathlib,sys,struct,json,hashlib,collections,subprocess,zlib
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2';D.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
geo=BASE/'stage/Geodata/24_19.l2j';r=Reader(geo.read_bytes());cells={};west,north=131072,32768;decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:
   z=r.num('h');vals=[[((z<<1)&0xfff0)|15]]*64
  else:
   assert ty in (1,2);vals=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');vals.append([r.num('H') for _ in range(n)])
  for i,vs in enumerate(vals):
   cx,cy=divmod(i,8);gx,gy=bx*8+cx,by*8+cy;x,y=west+gx*16+8,north+gy*16+8
   if not(137000<x<145000 and 52500<y<63000):continue
   out=[(decode(v),v&15) for v in vs if 7500<decode(v)<8850]
   if out:cells[gx,gy]=out
rects=json.loads((BASE/'native-floor/rectangles.json').read_text());seen={(x,y,z) for gx,gy,z,w,h,*rest in rects for y in range(gy,gy+h) for x in range(gx,gx+w)};assert len(seen)==30372
edges={};open_edges=0;drop_edges=0;open_heights=collections.defaultdict(set)
directions=[(1,0,1,2),(-1,0,2,1),(0,1,4,8),(0,-1,8,4)]
for x,y,z in sorted(seen):
 nswe=next(n for h,n in cells[x,y] if h==z)
 for dx,dy,bit,reverse in directions:
  ns=cells.get((x+dx,y+dy),[])
  if nswe&bit:
   assert any(-96<=nz-z<=24 and (x+dx,y+dy,nz) in seen for nz,_ in ns)
   xykey=(0,x+(dx>0),y) if dx else (1,y+(dy>0),x)
   open_heights[xykey].add(z);open_edges+=1;continue
  # A permitted drop has no full-height barrier. Its landing floor is already
  # covered, unlike a boundary with no reachable landing.
  if any(-24<=nz-z<=96 and nn&reverse and (x+dx,y+dy,nz) in seen for nz,nn in ns):drop_edges+=1;continue
  # Stop at the next storey so lower-tunnel walls cannot rise through an upper
  # walkway. Upper surface candidates include nonreachable roof layers.
  above=[h for h,_ in cells[x,y] if h-z>=64];height=min([384]+[h-z-8 for h in above]);assert height>=56
  if dx:axis=0;line=x+(dx>0);along=y
  else:axis=1;line=y+(dy>0);along=x
  key=(axis,line,along,z);edges[key]=min(edges.get(key,99999),height)
ambiguous=0
for key,height in list(edges.items()):
 axis,line,along,z=key;zs=open_heights.get((axis,line,along),set())
 # Near-height aliases at stair/ramp corners may encode the same passage with
 # different floors on either side. Do not erect an invisible wall there.
 if any(abs(h-z)<=24 for h in zs):del edges[key];ambiguous+=1;continue
 caps=[h-z-8 for h in zs if h>z+24]
 if caps:edges[key]=min([height]+caps)
segments=collections.defaultdict(set)
for (axis,line,along,z),height in edges.items():segments[axis,line,z,height].add(along)
walls=[]
for (axis,line,z,height),items in sorted(segments.items()):
 todo=set(items)
 while todo:
  start=min(todo);length=1
  while start+length in todo and length<64:length+=1
  todo.difference_update(range(start,start+length));walls.append((axis,line,start,z,height,length))
print('WALL_PLAN',len(edges),'closed edges ->',len(walls),'boxes;',open_edges,'open edges retained;',drop_edges,'directed drops retained',flush=True)
source=BASE/'stage/Maps/24_19.unr';m=Edit(source);assert not any(e['name'].startswith('HGDust2V3Wall') for e in m.exports),'Already installed/staged'
levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02');cl=m.imp('Engine.StaticMeshActor','Core.Class');newrefs=[]
# Native Box02 extents are symmetric: +-9.94559956 in XY/Z+-10.56719971.
halfxy=9.945599555969238;halfz=10.56719970703125
for idx,(axis,line,start,z,height,length) in enumerate(walls):
 if axis==0:center=[west+line*16,north+(start+length/2)*16];size=[2.,length*16+.2,height+4]
 else:center=[west+(start+length/2)*16,north+line*16];size=[length*16+.2,2.,height+4]
 loc=center+[z-43.35-4+size[2]/2];s3=[size[0]/(halfxy*2),size[1]/(halfxy*2),size[2]/(halfz*2)]
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.float('DrawScale',1.)+m.vector('DrawScale3D',s3)
 for name in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(name,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 newrefs.append(m.add('HGDust2V3Wall'+str(idx).zfill(5),'Engine.StaticMeshActor',frame+raw,flags=0x2070001))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',count+len(newrefs),count+len(newrefs))+b''.join(ci(i) for i in refs+newrefs)+m.b[end:level['offset']+level['size']]);raw=m.save(D/'stage/Maps/24_19.unr')
old=Edit(source);new=Edit(raw);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
assert len(new.exports)==len(old.exports)+len(walls)
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True);subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(raw)],capture_output=True,check=True,timeout=30)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(x^key for x in range(256)))==raw.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
(D/'walls.json').write_text(json.dumps(walls));(D/'closed-edges.json').write_text(json.dumps([[*key,h] for key,h in edges.items()]));(D/'audit.json').write_text(json.dumps(dict(source_map_sha256=sha(source),source_geodata_sha256=sha(geo),closed_edges=len(edges),native_wall_actors=len(walls),open_directed_edges_preserved=open_edges,directed_drops_preserved=drop_edges,height_alias_edges_omitted=ambiguous,prior_payloads_preserved=preserved,client_physics_verified=False),indent=2));print('NATIVE_WALLS_STAGED',len(walls),'actors',flush=True)
