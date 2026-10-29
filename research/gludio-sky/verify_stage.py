from package_tools import *
import json,hashlib
D=pathlib.Path(__file__).resolve().parent;original=ROOT.parent/'l2/maps/24_19.unr'
if (D/'installation.json').exists():
    installation=json.loads((D/'installation.json').read_text())
    original=pathlib.Path(next(e['backup'] for e in installation['files'] if pathlib.Path(e['target']).as_posix().lower().endswith('/maps/24_19.unr')))
old=Package(original);new=Package(D/'stage/Maps/24_19.unr')
assert len(new.exports)==len(old.exports)+9
unchanged=0
for a,b in zip(old.exports,new.exports):
    assert a['name']==b['name'] and a['cl']==b['cl'] and a['flags']==b['flags']
    if a['name']=='myLevel':continue
    assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];unchanged+=1
for i in range(8):
    e=next(e for e in new.exports if e['name']=='HGGludioDock'+str(i));p=new.props(e)
    assert p['StaticMesh'].startswith('HGGludioSky_S.') and p['Location'][2]>9500
    assert p['bCollideActors'] and p['bBlockPlayers']
e=next(e for e in new.exports if e['name']=='HGGludioCloudSea');p=new.props(e)
assert p['Location'][2]==7600 and p['DrawScale3D']==[1000.,1000.,1.] and not p['bCollideActors']
def refs(pkg):
    e=next(e for e in pkg.exports if e['name']=='myLevel');pkg.props(e);r=Reader(pkg.b,pkg.last_props_end)
    n=r.num('i');assert r.num('i')==n
    amb=[r.compact() for _ in range(n)];n=r.num('i');assert r.num('i')==n
    return amb,[r.compact() for _ in range(n)]
oa,ob=refs(old);na,nb=refs(new);assert oa==na and ob==nb[:-9]
assert all(new.ref(x).startswith('HGGludio') for x in nb[-9:])
t=Package(D/'stage/Textures/HGGludioSky_T.utx');p=t.props(next(e for e in t.exports if e['name']=='AcademyCloudSea'))
assert p['TwoSided'] and p['ZWrite'] and p['SelfIllumination']=='AcademyCloudBlend'
assert not json.loads((D/'dependency-audit.json').read_text())['missing']
geo=json.loads((D/'geodata-audit.json').read_text());assert geo['reachable_layers']>1200 and geo['spawn_nswe']==15
proof=dict(original_map_payloads_preserved=unchanged,ambient_actors_preserved=len(oa),original_actors_preserved=len(ob),added_dock_actors=8,cloud_actors=1,existing_sky_preserved=True,dependencies_resolved=True,reachable_layers=geo['reachable_layers'],visual_client_test=False)
(D/'stage-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
