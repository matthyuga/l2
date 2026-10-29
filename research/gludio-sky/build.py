"""Stage a native Gludio dock above the Coliseum without touching installed files."""
from package_tools import *
from material_conversion import convert_materials
from cloud_material import add_cloud_material
import json,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;STAGE=D/'stage';SRC=ROOT/'research/airships/gracia-assets';CLIENT=ROOT.parent/'l2'
STAGE.mkdir(exist_ok=True)
DELTA=(297264.,-208492.,12184.) # Original landing -148264,255192,-184 -> 149000,46700,12000.
audit={'delta':DELTA,'destination':[149000,46700,12000],'source_hashes':{},'meshes':[]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
clone_names={'glacia_kserth_t','glacia_fieldobj_t','l2_ship_l01_t','bereth_t','spirit_island_v_t','steel_castle_t','steel_castleinside_t','hellbound_01_t','t_hellbound'}
texture_sources={q.stem.lower():q for q in (SRC/'Textures').glob('*.utx') if q.stem.lower() in clone_names}
assert set(texture_sources)==clone_names,'Missing required source textures'
mapping={k:('HGGludioSky_T' if k=='glacia_kserth_t' else 'HGGludio_'+v.stem) for k,v in texture_sources.items()}
def rename_imports(pkg):
    for imp in pkg.imports:
        if not imp['outer'] and imp['name'].lower() in mapping:
            imp['name']=mapping[imp['name'].lower()];pkg.name(imp['name'])

# Keep all original material references and native collision data. The only native
# StaticMesh layout difference from license 37 to Interlude 28 is u01 (L2unreal).
source=SRC/'StaticMeshes/Glacia_kserth_S.usx';p=Edit(source)
rename_imports(p)
for e in p.exports:
    assert p.ref(e['cl'])=='Engine.StaticMesh'
    ptrs,remove=mesh_offsets(p,e);old=e['offset'];raw=p.b[old:old+e['size']]
    # All payloads retain original references and order. Lazy-array absolute
    # endpoints are rebased when append-only save chooses their new offsets.
    def converted(new_offset,raw=raw,old=old,ptrs=ptrs,remove=remove):
        b=bytearray(raw[:remove]+raw[remove+4:]);delta=new_offset-old
        for loc in ptrs:
            val=struct.unpack_from('<i',raw,loc)[0];newloc=loc-(4 if loc>remove else 0)
            struct.pack_into('<i',b,newloc,val+delta-(4 if val>old+remove else 0))
        return bytes(b)
    p.replace(e,converted);audit['meshes'].append(e['name'])
p.data[36:52]=uuid.uuid4().bytes
p.save(STAGE/'StaticMeshes/HGGludioSky_S.usx',license=28);audit['source_hashes'][str(source)]=sha(source)

# Texture payloads stay at their source offsets; native mip offsets remain valid.
source=SRC/'Textures/Glacia_kserth_T.utx';t=Edit(source)
t.data[36:52]=uuid.uuid4().bytes
rename_imports(t)
convert_materials(t)
add_cloud_material(t)
t.save(STAGE/'Textures/HGGludioSky_T.utx',license=28);audit['source_hashes'][str(source)]=sha(source)

# Namespace dependencies as well: stock packages sometimes have the same filename
# but lack later-cronicle objects. Never replace the client's existing resources.
deps=[v.stem for k,v in texture_sources.items() if k!='glacia_kserth_t']
audit['dependencies']=[]
for name in deps:
    source=SRC/'Textures'/(name+'.utx');q=Edit(source)
    # Preserve payload offsets. These packages contain standard material/texture objects.
    allowed=['Core.Package','Engine.Texture','Engine.Shader','Engine.TexPanner','Engine.TexEnvMap','Engine.TexRotator','Engine.TexScaler','Engine.Combiner','Engine.FinalBlend','Engine.Cubemap','Engine.Palette','Engine.FadeColor','Engine.ColorModifier','Engine.TexCoordSource','Engine.VertexColor']
    assert all(q.ref(e['cl']) in allowed for e in q.exports),name
    rename_imports(q);convert_materials(q);q.data[36:52]=uuid.uuid4().bytes
    dest=q.save(STAGE/'Textures'/(mapping[name.lower()]+'.utx'),license=28)
    audit['dependencies'].append({'name':name,'new':str(dest),'source_sha256':sha(source)})

source=CLIENT/'maps/24_19.unr';m=Edit(source);audit['source_hashes'][str(source)]=sha(source)
assert not any(e['name'].startswith('HGGludio') for e in m.exports),'Dock already installed. Restore original map before rebuilding from this installer; do not append duplicates.'
actors=json.loads((ROOT/'research/airships/15_25-actors.json').read_text())
actors=[a for a in actors if a['StaticMesh'].startswith('Glacia_kserth_S.')]
assert len(actors)==8
levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0')
newrefs=[];placed=[]
for i,a in enumerate(actors):
    mesh=m.imp(a['StaticMesh'].replace('Glacia_kserth_S.','HGGludioSky_S.'))
    location=[x+y for x,y in zip(a['Location'],DELTA)]
    raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',location)+m.vector('ColLocation',location)
    if 'Rotation' in a:raw+=m.prop('Rotation',10,struct.pack('<3i',*a['Rotation']),'Rotator')
    if 'DrawScale' in a:raw+=m.float('DrawScale',a['DrawScale'])
    if 'DrawScale3D' in a:raw+=m.vector('DrawScale3D',a['DrawScale3D'])
    raw+=m.boolean('bDynamicActorFilterState',True)+m.boolean('bIgnoredRange',True)
    raw+=m.boolean('bSunAffect',True)+m.boolean('bUpdateShadow',False)+m.prop('AmbientGlow',1,bytes([64]))
    raw+=m.boolean('bCollideActors',True)+m.boolean('bBlockActors',True)+m.boolean('bBlockPlayers',True)
    raw+=m.nametag('Tag','StaticMeshActor')+m.end()
    actor_class=m.imp('Engine.StaticMeshActor','Core.Class')
    frame=ci(actor_class)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
    ref=m.add('HGGludioDock'+str(i),'Engine.StaticMeshActor',frame+raw,flags=0x2070001);newrefs.append(ref)
    placed.append(dict(name='HGGludioDock'+str(i),source=a['actor'],mesh=a['StaticMesh'],location=location,rotation=a.get('Rotation'),scale=a.get('DrawScale',1),scale3d=a.get('DrawScale3D',[1,1,1])))

# Opaque, double-sided cloud sea below the floating rock. It has no gameplay
# collision and is not included in server geodata. Stock Water01 is a 200u quad.
water=m.imp('water.Water01');cloud=m.imp('HGGludioSky_T.AcademyCloudSea','Engine.Shader')
raw=m.obj('StaticMesh',water)+m.obj('Level',levelref)+m.vector('Location',[149000,46700,7600])+m.vector('DrawScale3D',[1000,1000,1])
raw+=m.obj('Skins',cloud,index=0)+m.boolean('bUnlit',True)+m.boolean('bSunAffect',False)
raw+=m.boolean('bDynamicActorFilterState',True)+m.boolean('bIgnoredRange',True)
for name in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']:raw+=m.boolean(name,False)
raw+=m.nametag('Tag','StaticMeshActor')+m.end()
actor_class=m.imp('Engine.StaticMeshActor','Core.Class')
frame=ci(actor_class)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
newrefs.append(m.add('HGGludioCloudSea','Engine.StaticMeshActor',frame+raw,flags=0x2070001))

level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);start=m.last_props_end
r=Reader(m.b,start);ambient_count=r.num('i');assert r.num('i')==ambient_count
for _ in range(ambient_count):r.compact()
actors_start=r.p;n=r.num('i');assert r.num('i')==n
refs=[r.compact() for _ in range(n)];actors_end=r.p
assert levelref in refs
raw=m.b[level['offset']:actors_start]+struct.pack('<2i',n+len(newrefs),n+len(newrefs))+b''.join(ci(x) for x in refs+newrefs)+m.b[actors_end:level['offset']+level['size']]
m.replace(level,raw)
m.save(STAGE/'Maps/24_19.unr')
audit.update(placed=placed,new_actor_refs=newrefs,original_level_actors=n,original_ambient_actors=ambient_count,cloud_height=7600,cloud_extent=100000)
(D/'build-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({'stage':str(STAGE),'native_meshes_converted':len(audit['meshes']),'dock_actors':len(placed),'added_map_actors':len(newrefs),'spawn':audit['destination']},indent=2))
