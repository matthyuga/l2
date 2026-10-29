from pathlib import Path
import sys,json,subprocess,collections,hashlib,struct,zlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((D/'build-audit.json').read_text());col=json.loads((D/'collision-audit.json').read_text())
logs=D/'native-load';logs.mkdir(exist_ok=True)
for name in build['parts']+['AureliaAtlas','AureliaSurface']:
 r=subprocess.run([str(ROOT/'research/amber-l2/tools/umodel.exe'),'-dump','-game=l2','-path='+str(D/'stage/StaticMeshes'),'HGAurelia.usx',name],capture_output=True,text=True,errors='replace',timeout=30)
 s=r.stdout+r.stderr;(logs/(name+'.log')).write_text(s)
 assert r.returncode==0 and not any(x in s for x in ['*** ERROR','Unable to load','WARNING: missing']),(name,s[-1000:])
old=Edit(CLIENT/'Maps/24_19.unr');new=Edit(D/'stage/Maps/24_19.unr');preserved=0
for a,b in zip(old.exports,new.exports):
 assert a['name']==b['name']
 if a['name']=='myLevel':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
boxes=json.loads((D/'collision-boxes.json').read_text());actors={e['name']:e for e in new.exports}
for row in boxes:
 p=new.props(actors[row['name']]);assert p['bHidden'] and p['bBlockPlayers'] and p['bWorldGeometry'] and p['StaticMesh']=='deco01.Box02'
 assert not p['bUseCylinderCollision']
assert len(new.exports)==len(old.exports)+len(boxes)+len(build['parts'])
seen={tuple(x) for x in json.loads((D/'reachable.json').read_text())};rects=json.loads((D/'rectangles.json').read_text())
covered={(yy*2048+xx,z) for x,y,z,w,h in rects for yy in range(y,y+h) for xx in range(x,x+w)};assert seen==covered
barriers=collections.defaultdict(list)
for axis,ln,a,z,h,l in json.loads((D/'walls.json').read_text()):
 for along in range(a,a+l):barriers[axis,ln,along].append((z-4,z+h))
decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
layers={int(c):[(decode(v),v&15) for v in vs] for c,vs in json.loads((D/'encoded-layers.json').read_text()).items()}
checked=0;conflicts=[]
for c,z in seen:
 x,y=c%2048,c//2048;ns=next(n for h,n in layers[c] if h==z)
 for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
  if not ns&bit:continue
  key=(0,x+(dx>0),y) if dx else (1,y+(dy>0),x)
  if any(a<z+24<b for a,b in barriers.get(key,[])):conflicts.append([c,z,key])
  checked+=1
assert not conflicts,conflicts[:10]
def block(r):
 ty=r.num('B')
 if ty==0:
  z=r.num('h');return [[((z<<1)&0xfff0)|15]]*64
 assert ty in (1,2)
 return [[r.num('H') for _ in range(1 if ty==1 else r.num('B'))] for _ in range(64)]
r=Reader((ROOT/'server/game/data/geodata/24_19.l2j').read_bytes());q=Reader((D/'stage/Geodata/24_19.l2j').read_bytes());oldlayers=0
for _ in range(65536):
 a,b=block(r),block(q)
 for vs,ns in zip(a,b):
  assert not (collections.Counter(vs)-collections.Counter(ns)),'Original geo layer changed';oldlayers+=len(vs)
encoded=D/'client';codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
for rel in ['StaticMeshes/HGAurelia.usx','Maps/24_19.unr']:
 p=D/'stage'/rel;out=encoded/rel;out.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([str(codec),'-c','encode','-p','121','-f',p.name,'-o',str(out),str(p)],check=True,capture_output=True,timeout=60)
 b=out.read_bytes();key=sum(map(ord,p.name.lower()))&255
 assert b[:28].decode('utf-16le')=='Lineage2Ver121'
 assert b[28:-20].translate(bytes(x^key for x in range(256)))==p.read_bytes()
 assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
audit=dict(native_load=True,native_objects=len(build['parts'])+2,previous_map_payloads_preserved=preserved,original_geodata_layers_preserved=oldlayers,collision_actors_verified=len(boxes),floor_coverage_layers=len(covered),open_edges_checked=checked,wall_conflicts=0,encrypted_roundtrip_crc=True,stationary=True,client_visual_verified=False)
(D/'verification.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
