"""Replace the 27 damaged native buildings with their matching irregular ruins.

Each installed house is batched by material to keep rendering practical. Its
editable source fragments remain in the separately registered rubble collections.
"""
from pathlib import Path
import json,copy,struct,math,uuid,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog'
OUT=CAT/'exports/dion-hecatombe-v2';OUT.mkdir(parents=True,exist_ok=True)
PROJECT=ROOT/'projects/dion-hecatombe-v2.json'
assert not PROJECT.exists(),'Never overwrite an existing user project'
original=CAT/'exports/scene-batch1-library_fe488fdfccee/scene.gltf'
native=json.loads(original.read_text(encoding='utf-8'))
actors=json.loads((ROOT.parent/'scenario-batches/library_fe488fdfccee/actors.json').read_text())
actor_by={a['actor']:a for a in actors}
types={'dion_nv_h01':1,'dion_nv_h02':2,'dion_nv_h03_a':3,'dion_nv_h03_b':4,'dion_nv_h04':5,'dion_nv_agit01':6,'dion_nv_bs':7,'dion_nv_wh':8,'dion_nv_wg':9,'dion_nv_sh01':10}
canon={1:'StaticMeshActor34',2:'StaticMeshActor322',3:'StaticMeshActor89',4:'StaticMeshActor492',5:'StaticMeshActor491',6:'StaticMeshActor1352',7:'StaticMeshActor403',8:'StaticMeshActor10',9:'StaticMeshActor671',10:'StaticMeshActor527'}
native_buffers=[(original.parent/b['uri']).read_bytes() for b in native['buffers']]
def read(g,buffers,index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    return np.ndarray((a['count'],width),dtype=dt,buffer=buffers[v['buffer']],offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*width),np.dtype(dt).itemsize)).copy()
def matrix(n):
    if 'matrix' in n:return np.array(n['matrix']).reshape((4,4),order='F')
    x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
def walk(g,index,parent=None):
    node=g['nodes'][index];m=(np.eye(4) if parent is None else parent)@matrix(node)
    yield node,m
    for i in node.get('children',[]):yield from walk(g,i,m)
def bounds(g,buffers,indices):
    lo=np.full(3,np.inf);hi=-lo
    for index in indices:
        for n,m in walk(g,index):
            if 'mesh' not in n:continue
            for p in g['meshes'][n['mesh']]['primitives']:
                pos=read(g,buffers,p['attributes']['POSITION']);world=pos@m[:3,:3].T+m[:3,3];lo=np.minimum(lo,world.min(0));hi=np.maximum(hi,world.max(0))
    return lo,hi
native_nodes={n.get('name'):i for i,n in enumerate(native['nodes'])}
terrain_node=next(n for n in native['nodes'] if 'terrain' in n.get('name','').lower())
terrain=read(native,native_buffers,native['meshes'][terrain_node['mesh']]['primitives'][0]['attributes']['POSITION'])
xs=np.unique(terrain[:,0]);zs=np.unique(terrain[:,2]);grid=np.zeros((len(xs),len(zs)))
grid[np.searchsorted(xs,terrain[:,0]),np.searchsorted(zs,terrain[:,2])]=terrain[:,1]
def height(x,z):
    i=int(np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2));j=int(np.clip(np.searchsorted(zs,z)-1,0,len(zs)-2));a=float(np.clip((x-xs[i])/(xs[i+1]-xs[i]),0,1));b=float(np.clip((z-zs[j])/(zs[j+1]-zs[j]),0,1));return float((1-a)*((1-b)*grid[i,j]+b*grid[i,j+1])+a*((1-b)*grid[i+1,j]+b*grid[i+1,j+1]))
buildings=[];removed=set()
for actor in actors:
    name=actor['StaticMesh'].split('.')[-1].lower()
    if name not in types:continue
    roofs=[a for a in actors if a['StaticMesh'].split('.')[-1].lower()==name+'_top']
    roof=min(roofs,key=lambda a:sum((a.get('Location',[0,0,0])[k]-actor.get('Location',[0,0,0])[k])**2 for k in range(3)))
    indices=[native_nodes[a['actor']+'_0'] for a in [actor,roof]]
    lo,hi=bounds(native,native_buffers,indices);center=(lo+hi)/2
    buildings.append({'actor':actor['actor'],'type':types[name],'style':name,'roof':roof['actor'],'center':center,'bounds':[lo,hi],'yaw':actor.get('Rotation',[0,0,0])[1]})
    removed.update([actor['actor']+'_0',roof['actor']+'_0'])
assert len(buildings)==27,len(buildings)
# Remove the crude V1 cuts and generic cubic debris. Keep native terrain,
# surroundings, landmarks and the corruption geometry as a separate core.
core_source=CAT/'exports/dion-hecatombe-v1/scene.gltf';core=json.loads(core_source.read_text(encoding='utf-8'))
source_hash=hashlib.sha256(core_source.read_bytes()).hexdigest()
props=[]
for n in core['nodes']:
    actor=actor_by.get(n.get('name','').rsplit('_',1)[0])
    if actor and 'interior_' in actor['StaticMesh'].lower():
        loc=actor.get('Location',[0,0,0]);x=(loc[0]-17056.982191538205)*.01;z=(loc[1]-148013.21899706515)*.01
        if any(b['bounds'][0][0]-1<x<b['bounds'][1][0]+1 and b['bounds'][0][2]-1<z<b['bounds'][1][2]+1 for b in buildings):props.append(n['name'])
removed.update(props)
scene=core['scenes'][core.get('scene',0)]
scene['nodes']=[i for i in scene['nodes'] if core['nodes'][i].get('name') not in removed and not core['nodes'][i].get('name','').startswith(('Escombros','Vigas'))]
for b in core['buffers']:
    b['uri']=str((core_source.parent/b['uri']).resolve().relative_to(CAT)).replace('\\','/')
    b['uri']='../../'+b['uri']
for image in core.get('images',[]):
    if 'uri' in image:image['uri']='../../'+str((core_source.parent/image['uri']).resolve().relative_to(CAT)).replace('\\','/')
(OUT/'core.gltf').write_text(json.dumps(core,ensure_ascii=False),encoding='utf-8')
core_buffers=[(OUT/b['uri']).resolve().read_bytes() for b in core['buffers']]
lo,hi=bounds(core,core_buffers,scene['nodes']);core_center=(lo+hi)/2
assets=[{'id':'custom_dion_hecatombe_v2_core','title':'Dion devastado V2 · terreno y entorno','path':'exports/dion-hecatombe-v2/core.gltf','thumbnail':None,'mesh':'Dion entorno','category':'Escenarios','native':False}]
def entry(name,asset,position):return {'id':str(uuid.uuid4()),'name':name,'asset':asset,'node':'','kind':'model','base':True,'locked':False,'visible':True,'position':list(map(float,position)),'rotation':[0,0,0],'scale':[1,1,1],'parts':[],'surfaces':[]}
objects=[entry('Dion · terreno, calles, iglesia y entorno',assets[0]['id'],core_center)]
templates={};audit=[]
for b in buildings:
    typ=b['type']
    if typ not in templates:
        src=CAT/f'exports/{"dion-rubble-v2" if typ<=3 else "dion-city-rubble-v2"}/house{typ}.glb';raw=src.read_bytes();size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);binary=raw[28+size:]
        (OUT/f'type{typ}.bin').write_bytes(binary);g['buffers'][0]['uri']=f'type{typ}.bin'
        templates[typ]=(g,[binary])
    template,buf=templates[typ];g=copy.deepcopy(template)
    delta=-(b['yaw']-actor_by[canon[typ]].get('Rotation',[0,0,0])[1])*math.tau/65536
    c,s=math.cos(delta),math.sin(delta);rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    center=np.array([b['center'][0],height(b['center'][0],b['center'][2]),b['center'][2]])
    grouped={};blocks=0;ground_samples=[]
    for root in template['scenes'][template.get('scene',0)]['nodes']:
        fragment=template['nodes'][root]
        if fragment.get('name','').startswith('Suelo'):continue
        blocks+=1
        root_location=matrix(fragment)[:3,3]@rotation.T+center
        ground=height(root_location[0],root_location[2]);adjust=ground-center[1];ground_samples.append(ground)
        for n,m in walk(template,root):
            if 'mesh' not in n:continue
            for p in template['meshes'][n['mesh']]['primitives']:
                key=p.get('material',0);group=grouped.setdefault(key,{'pos':[],'normal':[],'uv':[],'indices':[],'count':0})
                pos=read(template,buf,p['attributes']['POSITION']);v=(pos@m[:3,:3].T+m[:3,3])@rotation.T;v[:,1]+=adjust
                normal=read(template,buf,p['attributes']['NORMAL']) if 'NORMAL' in p['attributes'] else np.tile([0,1,0],(len(v),1));normal=normal@np.linalg.inv(m[:3,:3])@rotation.T;normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
                uv=read(template,buf,p['attributes']['TEXCOORD_0']) if 'TEXCOORD_0' in p['attributes'] else np.zeros((len(v),2))
                indices=read(template,buf,p['indices']).ravel() if 'indices' in p else np.arange(len(v));group['indices'].append(indices+group['count']);group['count']+=len(v);group['pos'].append(v);group['normal'].append(normal);group['uv'].append(uv)
    # All source image bufferViews stay in buffer0. Batched geometry uses buffer1.
    binary=bytearray();primitives=[];g['accessors']=[]
    def accessor(values,kind,integer=False):
        a=np.asarray(values,dtype='<u4' if integer else '<f4');offset=len(binary);binary.extend(a.tobytes());view=len(g['bufferViews']);g['bufferViews'].append({'buffer':1,'byteOffset':offset,'byteLength':a.nbytes});item={'bufferView':view,'componentType':5125 if integer else 5126,'count':len(a),'type':kind}
        if kind=='VEC3':item.update(min=a.min(0).tolist(),max=a.max(0).tolist())
        g['accessors'].append(item);return len(g['accessors'])-1
    for mat,group in grouped.items():
        pos=np.concatenate(group['pos']);normal=np.concatenate(group['normal']);uv=np.concatenate(group['uv']);idx=np.concatenate(group['indices']).reshape(-1,1)
        primitives.append({'attributes':{'POSITION':accessor(pos,'VEC3'),'NORMAL':accessor(normal,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2')},'indices':accessor(idx,'SCALAR',True),'material':mat})
    name=b['actor'];(OUT/f'{name}.bin').write_bytes(binary)
    g['buffers'].append({'uri':f'{name}.bin','byteLength':len(binary)});g.pop('animations',None);g['meshes']=[{'name':'Ruina · '+name,'primitives':primitives}];g['nodes']=[{'name':'Ruina · '+name,'mesh':0}];g['scenes']=[{'nodes':[0]}];g['scene']=0
    (OUT/f'{name}.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
    asset={'id':'dion_v2_'+name.lower(),'title':'Dion V2 · '+b['style']+' · '+name,'path':f'exports/dion-hecatombe-v2/{name}.gltf','thumbnail':None,'mesh':b['style'],'category':'Escenarios','native':False};assets.append(asset)
    # The merged local geometry bounds are needed because the editor normalizes
    # imported models by their bounds. Compensate to preserve native placement.
    positions=np.concatenate([np.concatenate(group['pos']) for group in grouped.values()]);local_center=(positions.min(0)+positions.max(0))/2
    objects.append(entry('Ruina · '+b['style'].replace('dion_nv_','').upper()+' · '+name,asset['id'],center+local_center))
    audit.append({'actor':name,'roof':b['roof'],'type':typ,'sourceFragments':blocks,'materialBatches':len(grouped),'center':center.tolist(),'yawDelta':delta,'terrainRange':[min(ground_samples),max(ground_samples)]})
for typ in range(4,11):
    assets.append({'id':f'dion_v2_source_type{typ}','title':f'Dion · Escombros editables · tipo {typ}','path':f'exports/dion-city-rubble-v2/house{typ}.glb','thumbnail':None,'mesh':next(k for k,v in types.items() if v==typ),'category':'Escenarios','native':False})
# Preserve the existing animated effects, now in the same coordinate frame as
# the native terrain. Flame size is reduced to keep roofs and debris readable.
project=json.loads((ROOT/'projects/dion-hecatombe-v1.json').read_text(encoding='utf-8'))
for effect in project['objects']:
    if effect.get('kind')!='effect':continue
    effect=copy.deepcopy(effect);effect['id']=str(uuid.uuid4())
    if effect['effect']['type']=='fire':effect['effect'].update(radius=1.4,height=3.4,size=.65)
    elif effect['effect']['type']=='smoke':effect['effect'].update(radius=1.8,height=10,size=.75)
    objects.append(effect)
project.update(name='dion-hecatombe-v2',scene='dion_hecatombe_v2',objects=objects,camera={'position':[80,55,34],'target':[13,3,-30],'fov':46})
project['cameras']=[project['camera'],{'position':[45,16,-3],'target':[13,3,-33],'fov':48},{'position':[-9,10,-18],'target':[18,2,-33],'fov':50}]+[None]*7
project['reference']={'base':'Dion Classic IL · 20_22','version':'Hecatombe V2 · escombros irregulares','placement':'Native coordinate frame; fragments grounded against native terrain; no UNR installation','buildings':27,'types':10}
PROJECT.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
data_path=ROOT/'data.json';data=json.loads(data_path.read_text(encoding='utf-8'));backup=ROOT/'backups/dion-hecatombe-v2';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(data_path.read_bytes())
ids={a['id'] for a in assets};data['assets']=[a for a in data['assets'] if a['id'] not in ids]+assets
definition={'id':'dion_hecatombe_v2','title':'Dion · Hecatombe V2 · Escombros','asset':assets[0]['id'],'project':PROJECT.name,'source':'Dion devastado con 27 edificios sustituidos por sus ruinas irregulares, adaptadas al terreno. Fuego, humo y cenizas.','initialCamera':project['camera'],'actorMapping':{}}
data['scenes']=[s for s in data['scenes'] if s['id']!=definition['id']]+[definition];data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
custom_path=ROOT/'custom-assets.json';custom=json.loads(custom_path.read_text(encoding='utf-8'));custom_path.write_text(json.dumps([a for a in custom if a['id'] not in ids]+assets,ensure_ascii=False,indent=2),encoding='utf-8')
proof={'buildings':audit,'replaced':len(audit),'types':len(templates),'removedOldNodes':sorted(removed),'coreCenter':core_center.tolist(),'v1SourceUnchanged':hashlib.sha256(core_source.read_bytes()).hexdigest()==source_hash,'rendering':'One primitive per material per house; source fragments retained in separate catalogs','terrain':'Bilinear native heightfield sampling per fragment; approximate grounding, not a full city rigid-body simulation'}
(OUT/'placement-audit.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print('INSTALLED VISUAL PROJECT',len(audit),'buildings;',sum(a['materialBatches'] for a in audit),'house draw batches;',len(objects),'entries')
