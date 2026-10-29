"""Convert imported UE2 meshes to the Interlude collision-array layout; stage only."""
import pathlib,sys,struct,json,hashlib,subprocess,zlib
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
p=Edit(CLIENT/'StaticMeshes/HGDust2Arena.usx');assert p.license==0
audit=[]
for e in p.exports:
 cl=p.ref(e['cl']);p.props(e);prop_end=p.last_props_end;old=e['offset'];end=old+e['size'];props=p.b[old:prop_end]
 if cl=='Engine.StaticMesh':
  r=Reader(p.b,prop_end);r.read(41);n=r.compact();r.read(n*14+25);n=r.compact();r.read(n*24+4)
  for _ in range(2):n=r.compact();r.read(n*4+4)
  for _ in range(r.compact()):n=r.compact();r.read(n*8+8)
  for _ in range(2):n=r.compact();r.read(n*2+4)
  r.compact();a=r.p
  faces=r.compact();assert faces>0
  for _ in range(faces):
   r.read(64)
   for __ in range(4):r.compact()
  b=r.p;nodes=r.compact();assert nodes>0
  for _ in range(nodes):
   for __ in range(4):r.compact()
   r.read(25)
  c=r.p;after=r.num('i');assert c<after<=end
  original=p.b[old:end];ra,rb,rc=a-old,b-old,c-old
  # Interlude adds two lazy-array endpoints and its collision transform metadata.
  extra=struct.pack('<i',0)+ci(0)+ci(0)+struct.pack('<5f',0,0,0,1,1)+bytes(12)+struct.pack('<i',0)
  assert len(extra)==42
  def converted(off,raw=original,ra=ra,rb=rb,rc=rc,after=after,old=old,extra=extra):
   out=bytearray(raw[:ra])+struct.pack('<i',off+rb+4)+raw[ra:rb]+struct.pack('<i',off+rc+8)+raw[rb:rc]+extra
   out+=struct.pack('<i',off+(after-old)+50)+raw[rc+4:]
   assert len(out)==len(raw)+50
   return bytes(out)
  p.replace(e,converted);audit.append(dict(name=e['name'],collision_faces=faces,collision_nodes=nodes,added_native_bytes=50))
 elif cl in ('Engine.Texture','Engine.FinalBlend'):
  native=p.b[prop_end:end];ptrs=[]
  if cl=='Engine.Texture':
   r=Reader(native);n=r.compact();assert 0<n<20
   for _ in range(n):
    loc=r.p;ptr=r.num('i');sz=r.compact();r.read(sz);assert ptr==prop_end+r.p,(e['name'],ptr,prop_end+r.p)
    ptrs.append(loc);r.read(10)
   assert r.p==len(native)
  else:assert not native
  def converted(off,props=props,native=native,ptrs=ptrs,old_start=prop_end):
   data=bytearray(native);delta=off+len(props)+4-old_start
   for loc in ptrs:struct.pack_into('<i',data,loc,struct.unpack_from('<i',data,loc)[0]+delta)
   return props+bytes(4)+data
  p.replace(e,converted)
assert len(audit)==37
out=p.save(D/'stage/StaticMeshes/HGDust2Arena.usx',license=28)
# Verify all native collision endpoints and counts with the Interlude-aware parser.
q=Edit(out)
for row in audit:
 e=next(e for e in q.exports if e['name']==row['name']);ptrs,_=mesh_offsets(q,e)
 for i,loc in enumerate(ptrs):
  r=Reader(q.b,e['offset']+loc);target=r.num('i');assert r.p<=target<=e['offset']+e['size']
  count=r.compact();assert count>0
  if i==0:assert count==row['collision_faces']
  if i==1:assert count==row['collision_nodes']
m=Edit(CLIENT/'Maps/24_19.unr');count=0
for e in m.exports:
 if not e['name'].startswith('HGDust2Arena'):continue
 changes={n:m.boolean(n,v) for n,v in [('bWorldGeometry',True),('bCollideWorld',True),('bUseCylinderCollision',False),('bStatic',True),('bCollideActors',True),('bBlockActors',True),('bBlockPlayers',True),('bBlockZeroExtentTraces',True),('bBlockNonZeroExtentTraces',True)]}
 m.replace(e,change_props(m,e,changes));count+=1
assert count==37;m.save(D/'stage/Maps/24_19.unr')
for rel in ['StaticMeshes/HGDust2Arena.usx','Maps/24_19.unr']:
 source=D/'stage'/rel;target=D/'client'/rel;target.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f',source.name,'-o',str(target),str(source)],check=True,capture_output=True,timeout=60)
 enc=target.read_bytes();key=sum(map(ord,source.name.lower()))&255;assert enc[28:-20].translate(bytes(x^key for x in range(256)))==source.read_bytes();assert struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20])
(D/'audit.json').write_text(json.dumps(dict(source_mesh_sha256=sha(CLIENT/'StaticMeshes/HGDust2Arena.usx'),source_map_sha256=sha(CLIENT/'Maps/24_19.unr'),actors=count,meshes=audit,client_physics_verified=False),indent=2))
print('STAGED_INTERLUDE_COLLISION',len(audit),'meshes',sum(x['collision_faces'] for x in audit),'collision faces',count,'actors')
