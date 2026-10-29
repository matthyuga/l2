import pathlib,sys,json,subprocess,hashlib,struct
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
build=json.loads((D/'build-audit.json').read_text());logs=D/'native-load';logs.mkdir(exist_ok=True);rows=[]
for name in build['parts']+['AirshipAtlas','AirshipSurface']:
 r=subprocess.run([str(ROOT/'research/amber-l2/tools/umodel.exe'),'-dump','-game=l2','-path='+str(D/'stage/StaticMeshes'),'HGSkyAirship.usx',name],capture_output=True,text=True,errors='replace',timeout=30);text=r.stdout+r.stderr;(logs/(name+'.log')).write_text(text)
 assert r.returncode==0 and '*** ERROR' not in text and 'Unable to load' not in text and 'WARNING: missing' not in text,(name,text[-1600:]);rows.append(name)
old=Edit(ROOT.parent/'l2/maps/24_19.unr');new=Edit(D/'stage/Maps/24_19.unr');assert len(new.exports)==len(old.exports)+build['added_actors']
preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert a['name']==b['name'] and old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
added=[e for e in new.exports if e['name'].startswith('HGSkyAirshipDocked')];assert len(added)==len(build['parts'])
for e in added:
 p=new.props(e);assert all(abs(a-b)<.01 for a,b in zip(p['Location'],build['location'])) and p['DrawScale']==build['scale'];assert p['bIgnoredRange'] and p['bDynamicActorFilterState'];assert e['flags']&0x02000000
geo=json.loads((D/'geodata-audit.json').read_text());assert abs(geo['spawn_floor']-12040)<40 and geo['reachable_layers']>100
report=dict(native_load=True,objects_loaded=rows,map_preserved=True,original_payloads_preserved=preserved,new_actor_count=len(added),geo_spawn_valid=True,spawn=geo['spawn'],reachable_layers=geo['reachable_layers'],client_visual_verified=False,stationary=True)
(D/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
