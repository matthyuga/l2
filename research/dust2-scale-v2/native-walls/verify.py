import pathlib,sys,json,struct,collections
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Edit,Reader
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
walls=json.loads((D/'walls.json').read_text());edges=json.loads((D/'closed-edges.json').read_text());edge_map=collections.defaultdict(list)
for axis,line,along,z,height in edges:edge_map[axis,line,along].append((z,z+height))
covered=set();p=Edit(D/'stage/Maps/24_19.unr');actors=[e for e in p.exports if e['name'].startswith('HGDust2V2Wall')];assert len(actors)==len(walls)
vs,ts=MeshLibrary(str(ROOT.parent/'l2/StaticMeshes')).get('deco01','Box02');assert len(ts)==12
for e,(axis,line,start,z,height,length) in zip(actors,walls):
 props=p.props(e);assert props['bHidden'] and props['bBlockPlayers'] and props['bBlockNonZeroExtentTraces']
 wv=transform(vs,actor_matrix(None,props['DrawScale'],props['DrawScale3D']),props['Location']);lo=[min(v[i] for v in wv) for i in range(3)];hi=[max(v[i] for v in wv) for i in range(3)]
 assert abs(lo[2]-(z-43.35-4))<.003 and abs(hi[2]-(z-43.35+height))<.003
 if axis==0:
  assert lo[0]<131072+line*16<hi[0];assert lo[1]<32768+start*16 and hi[1]>32768+(start+length)*16
 else:
  assert lo[1]<32768+line*16<hi[1];assert lo[0]<131072+start*16 and hi[0]>131072+(start+length)*16
 for along in range(start,start+length):covered.add((axis,line,along,z,height))
assert covered=={tuple(e) for e in edges}
# Every walkable edge at character-body height must remain unobstructed by a
# different-storey barrier sharing that XY edge.
geo=D.parent/'stage/Geodata/24_19.l2j';r=Reader(geo.read_bytes());cells={};decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:
   z=r.num('h');vals=[[((z<<1)&0xfff0)|15]]*64
  else:
   vals=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');vals.append([r.num('H') for _ in range(n)])
  for i,vs0 in enumerate(vals):
   cx,cy=divmod(i,8);gx,gy=bx*8+cx,by*8+cy
   if not(137000<131072+gx*16+8<144100 and 54500<32768+gy*16+8<62800):continue
   out=[(decode(v),v&15) for v in vs0 if 7500<decode(v)<8850]
   if out:cells[gx,gy]=out
rects=json.loads((D.parent/'native-floor/rectangles.json').read_text());seen={(x,y,z) for gx,gy,z,w,h in rects for y in range(gy,gy+h) for x in range(gx,gx+w)};open_checked=0;conflicts=[]
for x,y,z in seen:
 n=next(n for h,n in cells[x,y] if h==z)
 for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
  if not n&bit:continue
  key=(0,x+(dx>0),y) if dx else (1,y+(dy>0),x)
  if any(bottom-4<z+24<top for bottom,top in edge_map.get(key,[])):conflicts.append((x,y,z,key))
  open_checked+=1
assert not conflicts,conflicts[:20]
report=dict(native_walls_verified=len(walls),closed_edges_covered=len(covered),open_directed_edges_checked=open_checked,upper_storey_wall_conflicts=len(conflicts),floor_support_actors_preserved=sum(e['name'].startswith('HGDust2V2Floor') for e in p.exports),client_physics_verified=False)
assert report['floor_support_actors_preserved']==json.loads((D.parent/'native-floor/audit.json').read_text())['floor_actors']
(D/'verification.json').write_text(json.dumps(report,indent=2));print('NATIVE_WALLS_GEOMETRY_PASS',json.dumps(report))
