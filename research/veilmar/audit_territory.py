import pathlib,sys,json,hashlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[2];D=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
path=ROOT.parent/'l2/MAPS/17_24.unr';p=Package(path)
report=dict(path=str(path),size=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),version=p.version,license=p.license,exports=len(p.exports),classes=dict(collections.Counter(p.ref(e['cl']) for e in p.exports)),static_mesh_actors=len(p.actors()),tile=dict(x=17,y=24,size=32768,origin_x=20,origin_y=18,bounds_x=[-98304,-65536],bounds_y=[196608,229376]),source_world='source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/World.java',source_instance='source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/managers/InstanceManager.java')
(D/'local-territory-audit.json').write_text(json.dumps(report,indent=2));print('TERRITORY',report['static_mesh_actors'],'static actors; tile already inside server bounds')
