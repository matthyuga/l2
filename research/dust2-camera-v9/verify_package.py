from pathlib import Path
import sys,json,math
D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R/'research/gludio-sky'))
from package_tools import Edit,Reader
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'))
from geolib.meshes import MeshLibrary,actor_matrix,transform
m=Edit(D/'client/Maps/24_19.unr');bounds={b['name']:b for b in json.loads((D/'bounds-audit.json').read_text())};vs,ts=MeshLibrary(str(R.parent/'l2/StaticMeshes')).get('deco01','Box02')
for e in m.exports:
 if e['name'] not in bounds:continue
 p=m.props(e);assert p['StaticMesh']=='deco01.Box02'
 wv=transform(vs,actor_matrix(None,p['DrawScale'],p['DrawScale3D']),p['Location']);lo=[min(v[i] for v in wv) for i in range(3)];hi=[max(v[i] for v in wv) for i in range(3)];b=bounds[e['name']]
 assert max(abs(lo[i]-b['min'][i]) for i in range(3))<.02
 assert max(abs(hi[i]-b['max'][i]) for i in range(3))<.02
 assert p['CollisionRadius']>=math.hypot((hi[0]-lo[0])/2,(hi[1]-lo[1])/2)+7.98
 assert p['CollisionHeight']>=(hi[2]-lo[2])/2+7.98
 assert all(p[k] for k in ['bHidden','bCollideActors','bWorldGeometry','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces'])
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];names=[m.exports[v-1]['name'] for v in refs if v>0]
assert all(names.count(name)==1 for name in bounds)
assert sum(name.startswith('HGDust2V7RampTile') for name in names)==189
(D/'reloaded-verification.json').write_text(json.dumps(dict(new_actors=len(bounds),all_refs_once=True,stock_geometry_and_bounds_verified=True,validated_ramp_refs_preserved=189),indent=2))
print('PASS:',len(bounds),'new collision actors; geometry/bounds and references verified; 189 ramp pieces retained')
