"""Prepare corrected scale, mirrored layout and UVs without touching installed files."""
import pathlib,sys,struct,json,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=ROOT/'research/dust2-integration';CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
manifest=json.loads((OLD/'installation.json').read_text(encoding='utf-8'));current={r['target']:sha(r['target']) for r in manifest['files']}
assert all(current[r['target']]==r['after_sha256'] for r in manifest['files']),'Concurrent integration changes'
(D/'source-hashes.json').write_text(json.dumps(current,indent=2))
build=json.loads((OLD/'build-audit.json').read_text());build.update(scale=.2,scale3d=[1,-1,1],goldsrc_scale=.625,mirror_axis='Y',previous_goldsrc_scale=1.5,location=[141000.,57000.,8000.],client_visual_verified=False)
(D/'build-audit.json').write_text(json.dumps(build,indent=2))
pkg=Edit(CLIENT/'StaticMeshes/HGDust2Arena.usx');assert pkg.license==28;uv_count=0
for e in pkg.exports:
 if pkg.ref(e['cl'])!='Engine.StaticMesh':continue
 pkg.props(e);r=Reader(pkg.b,pkg.last_props_end);r.read(41);n=r.compact();r.read(n*14+25);n=r.compact();r.read(n*24+4)
 for _ in range(2):n=r.compact();r.read(n*4+4)
 uvs=[]
 for _ in range(r.compact()):
  n=r.compact()
  for _ in range(n):r.read(4);uvs.append(r.p-e['offset']);r.read(4)
  r.read(8)
 ptrs,_=mesh_offsets(pkg,e);raw=bytearray(pkg.b[e['offset']:e['offset']+e['size']]);old=e['offset']
 for loc in uvs:struct.pack_into('<f',raw,loc,1-struct.unpack_from('<f',raw,loc)[0]);uv_count+=1
 def converted(off,raw=bytes(raw),old=old,ptrs=ptrs):
  out=bytearray(raw)
  for loc in ptrs:struct.pack_into('<i',out,loc,struct.unpack_from('<i',out,loc)[0]+off-old)
  return bytes(out)
 pkg.replace(e,converted)
pkg.save(D/'stage/StaticMeshes/HGDust2Arena.usx')
m=Edit(CLIENT/'Maps/24_19.unr');disabled=[];visual=0
for i,e in enumerate(m.exports):
 if e['name'].startswith('HGDust2ArenaDustPart'):
  changes={'DrawScale':m.float('DrawScale',.2),'DrawScale3D':m.vector('DrawScale3D',[1,-1,1])};m.replace(e,change_props(m,e,changes));visual+=1
 elif e['name'].startswith(('HGDust2Floor','HGDust2Wall','HGDust2NativeArrival')):
  disabled.append(i+1);changes={n:m.boolean(n,False) for n in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};changes['bHidden']=m.boolean('bHidden',True);m.replace(e,change_props(m,e,changes))
assert visual==37
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p;refs=[i for i in refs if i not in set(disabled)]
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(refs),len(refs))+b''.join(ci(i) for i in refs)+m.b[end:level['offset']+level['size']]);m.save(D/'stage/Maps/24_19.unr')
# Adapt the previously verified geometry pipeline, retaining its old source in
# place. Rebuild on the pre-Dust2 geodata only after checking the live hash.
base_geo=next(pathlib.Path(r['backup']) for r in manifest['files'] if r['target'].endswith('.l2j'));assert base_geo.exists()
s=(OLD/'build_geodata.py').read_text(encoding='utf-8')
s=s.replace('from geolib.generate import _prep_geometry,_column,_span_layers,_wall_between','from geolib.generate import _prep_geometry,_column,_span_layers,_wall_between\nimport geolib.generate as cfg\ncfg.AGENT_HEIGHT=64;cfg.LAYER_MERGE=8')
s=s.replace("actor_matrix(None,build['scale'],[1,1,1])","actor_matrix(None,build['scale'],build['scale3d'])")
s=s.replace('q=((x-ox)/1.5,(y-oy)/1.5,(z-43.35-oz)/1.5)','q=((x-ox)/.625,-(y-oy)/.625,(z-43.35-oz)/.625)')
s=s.replace("src[i]*1.5","src[i]*[.625,-.625,.625][i]").replace('z-54+43.35','z-22.5+43.35')
s=s.replace('assert len(seen)>10000','assert len(seen)>4000').replace('-96<=nz-z<=24','-96<=nz-z<=16')
s=s.replace("source=ROOT/'server/game/data/geodata/24_19.l2j'","source=pathlib.Path("+repr(str(base_geo))+')')
(D/'build_geodata.py').write_text(s,encoding='utf-8')
(D/'prepare-audit.json').write_text(json.dumps(dict(scale_ratio=.625/1.5,visual_actors=visual,old_collision_exports_disabled=len(disabled),uv_coordinates_flipped=uv_count,mirror_axis='Y',base_geo=str(base_geo),installed=False),indent=2))
print('SCALE_V2_PREPARED',visual,'visual actors, UV corrected',uv_count,'old collision disabled',len(disabled))
