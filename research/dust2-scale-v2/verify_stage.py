import pathlib,sys,json,struct,hashlib,subprocess,zlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
old=Edit(CLIENT/'StaticMeshes/HGDust2Arena.usx');new=Edit(D/'stage/StaticMeshes/HGDust2Arena.usx');verified=0;uvs=0
def streams(p,e):
 p.props(e);r=Reader(p.b,p.last_props_end);r.read(41);n=r.compact();r.read(n*14+25);n=r.compact();start=r.p;verts=p.b[start:start+n*24];r.read(n*24+4)
 for _ in range(2):n=r.compact();r.read(n*4+4)
 out=[]
 for _ in range(r.compact()):
  n=r.compact();out.append([struct.unpack('<2f',r.read(8)) for _ in range(n)]);r.read(8)
 return verts,out
for a,b in zip(old.exports,new.exports):
 if old.ref(a['cl'])!='Engine.StaticMesh':continue
 va,ua=streams(old,a);vb,ub=streams(new,b);assert va==vb
 for aa,bb in zip(ua,ub):
  for (u,v),(nu,nv) in zip(aa,bb):assert abs(u-nu)<.0001 and abs(1-v-nv)<.0001;uvs+=1
 ptrs,_=mesh_offsets(new,b)
 for loc in ptrs:
  target=struct.unpack_from('<i',new.b,b['offset']+loc)[0];assert b['offset']<target<=b['offset']+b['size']
 verified+=1
assert verified==37
original=Edit(CLIENT/'Maps/24_19.unr');updated=Edit(D/'stage/Maps/24_19.unr');preserved=0;visual=0;legacy=set()
for i,(a,b) in enumerate(zip(original.exports,updated.exports)):
 if a['name'].startswith(('HGDust2Floor','HGDust2Wall','HGDust2NativeArrival')):
  pr=updated.props(b);assert pr['bHidden'] and not pr['bCollideActors'];legacy.add(i+1);continue
 if a['name'].startswith('HGDust2ArenaDustPart'):
  pr=updated.props(b);assert abs(pr['DrawScale']-.2)<1e-6 and pr['DrawScale3D']==[1.,-1.,1.];visual+=1;continue
 if a['name']=='myLevel':continue
 assert original.b[a['offset']:a['offset']+a['size']]==updated.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
assert visual==37
e=next(e for e in updated.exports if e['name']=='myLevel');updated.props(e);r=Reader(updated.b,updated.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];assert not legacy.intersection(refs)
for rel in ['StaticMeshes/HGDust2Arena.usx']:
 p=D/'stage'/rel;q=D/'client'/rel;q.parent.mkdir(parents=True,exist_ok=True);subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f',p.name,'-o',str(q),str(p)],check=True,capture_output=True,timeout=30)
for rel in ['Maps/24_19.unr','StaticMeshes/HGDust2Arena.usx']:
 p=D/'stage'/rel;b=(D/'client'/rel).read_bytes();key=sum(map(ord,p.name.lower()))&255;assert b[28:-20].translate(bytes(x^key for x in range(256)))==p.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
g=json.loads((D/'geodata-audit.json').read_text());w=json.loads((D/'native-walls/verification.json').read_text());f=json.loads((D/'native-floor/verification.json').read_text());assert w['upper_storey_wall_conflicts']==0
report=dict(mesh_geometry_preserved=verified,uv_v_coordinates_corrected=uvs,visual_actor_scales_verified=visual,old_collision_references_removed=len(legacy),prior_non_dust2_payloads_preserved=preserved,reachable_layers=g['reachable_layers'],native_floor_actors=f['actors_verified'],native_wall_actors=w['native_walls_verified'],scale_ratio=.625/1.5,mirror_axis='Y',textures_vertical_flip_corrected=True,client_test_pending=True)
(D/'verification.json').write_text(json.dumps(report,indent=2));print('RESCALE_STAGE_PASS',json.dumps(report))
