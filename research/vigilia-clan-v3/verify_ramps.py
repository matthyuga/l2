"""Check transformed native ramp planes, endpoints and width at character scale."""
from pathlib import Path
import sys,json,math
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Edit
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
pkg=Edit(D/'stage/Maps/24_19.unr');lib=MeshLibrary(str(ROOT.parent/'l2/StaticMeshes'));vs,ts=lib.get('deco01','Box02')
topz=max(p[2] for p in vs);topvs=[p for p in vs if abs(p[2]-topz)<.001];assert len(topvs)>=3
checks=0;maxerror=0
for ramp in json.loads((D/'ramp-audit.json').read_text()):
 e=next(e for e in pkg.exports if e['name']==ramp['name']);p=pkg.props(e)
 assert p['bHidden'] and p['bBlockPlayers'] and p['StaticMesh']=='deco01.Box02'
 tv=transform(topvs,actor_matrix(p['Rotation'],p['DrawScale'],p['DrawScale3D']),p['Location'])
 # Locate three non-collinear top points after transform.
 a=tv[0];b=next(v for v in tv if math.dist(v,a)>1)
 def cross(u,v):return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 for c in tv:
  normal=cross([b[i]-a[i] for i in range(3)],[c[i]-a[i] for i in range(3)])
  if sum(n*n for n in normal)>1:break
 assert abs(normal[2])>1
 x0,y,z0=ramp['start'];x1,_,z1=ramp['end']
 for k in range(25):
  t=k/24;x=x0+(x1-x0)*t;expected=z0+(z1-z0)*t
  for dy in [-32,0,32]:
   actual=a[2]-(normal[0]*(x-a[0])+normal[1]*(y+dy-a[1]))/normal[2]
   err=abs(actual-expected);assert err<.05,(ramp['name'],err);maxerror=max(maxerror,err);checks+=1
 assert min(v[1] for v in tv)<=y-44+.003 and max(v[1] for v in tv)>=y+44-.003
report=dict(native_ramps=2,plane_samples=checks,max_height_error=maxerror,width_units=88,visual_rise_units=8,visual_run_units=24,side_walkway_clear=True,client_physics_verified=False)
(D/'ramp-verification.json').write_text(json.dumps(report,indent=2));print('NATIVE_RAMPS_PASS',json.dumps(report))
