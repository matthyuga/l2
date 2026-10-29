from pathlib import Path
import json,sys,math,struct
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import Edit,Reader
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
m=Edit(D/'client/Maps/24_19.unr');vs,ts=MeshLibrary(str(R.parent/'l2/StaticMeshes')).get('deco01','Box02');native=0;camera=0;tiles=0
for e in m.exports:
 if not e['name'].startswith('HGDust2V7'):continue
 p=m.props(e);assert p['bHidden'] and p['bCollideActors'] and p['bWorldGeometry'] and p['bBlockZeroExtentTraces']
 iscam='Camera' in e['name'];assert p['bBlockNonZeroExtentTraces']==(not iscam)
 wv=transform(vs,actor_matrix(p['Rotation'],p['DrawScale'],p['DrawScale3D']),p['Location']);lo=[min(v[i] for v in wv) for i in range(3)];hi=[max(v[i] for v in wv) for i in range(3)]
 assert p['CollisionRadius']>=math.hypot((hi[0]-lo[0])/2,(hi[1]-lo[1])/2)+7.99
 assert p['CollisionHeight']>=(hi[2]-lo[2])/2+7.99
 native+=1;camera+=iscam;tiles+=not iscam
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];assert not any(m.exports[i-1]['name'].startswith('HGDust2V6Ramp') for i in refs if i>0)
assert sum(m.exports[i-1]['name'].startswith('HGDust2V7') for i in refs if i>0)==native
assert tiles==189 and camera>1900
entry=json.loads((D/'camera-ceilings.json').read_text());at=[v for v in entry if 131072+v[0]*16<=141496<131072+(v[0]+1)*16 and 32768+v[1]*16<=55320<32768+(v[1]+1)*16 and abs(v[2]-8040)<32];assert at
plain=(D/'user.roundtrip.ini').read_bytes();assert b'HitCheckCameraMinDist=0' in plain and b'MaxZoomingDist=1800' in plain and b'bUseHitCheckCamera=true' in plain
print('VERIFIED',tiles,'native ramp pieces;',camera,'camera trace actors; profile changes only min-distance; camera ceiling at user zone',at)
(D/'reloaded-verification.json').write_text(json.dumps(dict(ramp_tiles=tiles,camera_trace_actors=camera,all_native_properties_and_bounds_checked=True,legacy_ramp_refs_removed=True,camera_player_nonzero_traces_disabled=True,current_user_zone_ceilings=at,client_test_pending=True),indent=2))
