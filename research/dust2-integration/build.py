"""Stage Dust2 arena; append to current client map, never overwrite installed files."""
import pathlib,sys,json,struct,hashlib,subprocess
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];SRC=ROOT/'research/dust2';stage=D/'stage'
sys.path.insert(0,str(ROOT/'research/gludio-sky'))
from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
proof=json.loads((SRC/'l2-probe/proof.json').read_text());parts=proof['parts'];location=[141000.,57000.,8000.];scale=.48
p=Edit(SRC/'l2-probe/compiler/HGDust2Probe.u')
for i in range(34):
 name='DustTex'+str(i).zfill(2);ref=next(i+1 for i,e in enumerate(p.exports) if e['name']==name)
 p.add('DustSurface'+str(i).zfill(2),'Engine.FinalBlend',p.obj('Material',ref)+p.boolean('TwoSided',True)+p.boolean('ZWrite',True)+p.boolean('ZTest',True)+p.end(),flags=0xf0004)
p.save(stage/'StaticMeshes/HGDust2Arena.usx')
source=ROOT.parent/'l2/maps/24_19.unr';m=Edit(source);assert not any(e['name'].startswith('HGDust2Arena') for e in m.exports),'Already added'
levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');newrefs=[]
for part in parts:
 mesh=m.imp('HGDust2Arena.'+part['name']);material=m.imp('HGDust2Arena.DustSurface'+part['texture'][-2:],'Engine.FinalBlend')
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.obj('Skins',material,index=0)+m.vector('Location',location)+m.vector('ColLocation',location)+m.float('DrawScale',scale)
 for n,val in [('bDynamicActorFilterState',True),('bIgnoredRange',True),('bSunAffect',True),('bUpdateShadow',False),('bCollideActors',True),('bBlockActors',True),('bBlockPlayers',True),('bBlockZeroExtentTraces',True),('bBlockNonZeroExtentTraces',True)]:raw+=m.boolean(n,val)
 raw+=m.prop('AmbientGlow',1,bytes([96]))+m.nametag('Tag','StaticMeshActor')+m.end();cl=m.imp('Engine.StaticMeshActor','Core.Class');frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 newrefs.append(m.add('HGDust2Arena'+part['name'],'Engine.StaticMeshActor',frame+raw,flags=0x2070001))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',count+len(newrefs),count+len(newrefs))+b''.join(ci(i) for i in refs+newrefs)+m.b[end:level['offset']+level['size']]);m.save(stage/'Maps/24_19.unr')
new=Edit(stage/'Maps/24_19.unr');old=Edit(source);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert a['name']==b['name'] and old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
logs=D/'native-load';logs.mkdir(exist_ok=True)
for name in [x['name'] for x in parts]+['DustTex'+str(i).zfill(2) for i in range(34)]+['DustSurface'+str(i).zfill(2) for i in range(34)]:
 r=subprocess.run([str(ROOT/'research/amber-l2/tools/umodel.exe'),'-dump','-game=l2','-path='+str(stage/'StaticMeshes'),'HGDust2Arena.usx',name],capture_output=True,text=True,errors='replace',timeout=25);t=r.stdout+r.stderr;(logs/(name+'.log')).write_text(t)
 assert r.returncode==0 and '*** ERROR' not in t and 'Unable to load' not in t and 'WARNING: missing' not in t,(name,t[-1000:])
audit=dict(location=location,scale=scale,goldsrc_scale=1.5,parts=[p['name'] for p in parts],source_map_sha256=sha(source),added_actors=len(newrefs),preserved_payloads=preserved,native_objects_loaded=105,client_visual_verified=False)
(D/'build-audit.json').write_text(json.dumps(audit,indent=2));print('DUST2_MAP_STAGED',json.dumps(audit),flush=True)
