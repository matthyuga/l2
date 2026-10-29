"""Build a separate editable Dion disaster project; source maps stay read-only."""
from pathlib import Path
import copy, hashlib, json, math, random, uuid, sys
import numpy as np

ROOT = Path(__file__).resolve().parent
CAT = ROOT.parent / 'model-catalog'
SOURCE = CAT / 'exports/scene-batch1-library_fe488fdfccee/scene.gltf'
OUT = CAT / 'exports/dion-hecatombe-v1'
PROJECT = ROOT / 'projects/dion-hecatombe-v1.json'
if PROJECT.exists() and '--rebuild' not in sys.argv:
    raise SystemExit('Project already exists; preserve user edits.')
OUT.mkdir(parents=True, exist_ok=True)
original_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
g = json.loads(SOURCE.read_text(encoding='utf-8'))
actors = {a['actor']: a for a in json.loads((ROOT.parent/'scenario-batches/library_fe488fdfccee/actors.json').read_text())}
source_buffers = [(SOURCE.parent/b['uri']).read_bytes() for b in g['buffers']]
for b in g['buffers']:
    b['uri'] = '../scene-batch1-library_fe488fdfccee/' + b['uri']
for image in g.get('images', []):
    if 'uri' in image:
        image['uri'] = '../scene-batch1-library_fe488fdfccee/' + image['uri']
extra = bytearray()
buffer_index = len(g['buffers'])
def read(index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
    width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    raw=source_buffers[v['buffer']]
    offset=v.get('byteOffset',0)+a.get('byteOffset',0)
    stride=v.get('byteStride',np.dtype(dtype).itemsize*width)
    return np.ndarray((a['count'],width),dtype=dtype,buffer=raw,offset=offset,strides=(stride,np.dtype(dtype).itemsize)).copy()
def accessor(values,kind='VEC3',integer=False):
    array=np.asarray(values,dtype='<u4' if integer else '<f4')
    while len(extra)%4:extra.append(0)
    offset=len(extra);extra.extend(array.tobytes())
    view=len(g['bufferViews']);g['bufferViews'].append({'buffer':buffer_index,'byteOffset':offset,'byteLength':array.nbytes})
    item={'bufferView':view,'componentType':5125 if integer else 5126,'count':len(array),'type':kind}
    if kind=='VEC3':item.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
    g['accessors'].append(item);return len(g['accessors'])-1

rng=random.Random(261026)
# Preserve the town's layout. Char textures through material factors, not source images.
for m in g['materials']:
    p=m.setdefault('pbrMetallicRoughness',{})
    base=p.get('baseColorFactor',[1,1,1,1]);p['baseColorFactor']=[base[0]*.47,base[1]*.40,base[2]*.39,base[3]]
    p['roughnessFactor']=1
def material(name,color,emission=None):
    m={'name':name,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':1}}
    if emission:m['emissiveFactor']=emission
    g['materials'].append(m);return len(g['materials'])-1
stone=material('Mampostería calcinada',[.24,.21,.19,1])
wood=material('Vigas carbonizadas',[.065,.042,.035,1])
violet=material('Corrupción bajo la corteza',[.16,.025,.20,1],[.55,.035,.8])
black=material('Borde de tierra carbonizada',[.025,.018,.03,1])
terrain_node=next(n for n in g['nodes'] if 'terrain' in n.get('name','').lower())
terrain=read(g['meshes'][terrain_node['mesh']]['primitives'][0]['attributes']['POSITION'])
def height(x,z):
    d=(terrain[:,0]-x)**2+(terrain[:,2]-z)**2
    ids=np.argpartition(d,3)[:3]; w=1/np.maximum(d[ids],.001)
    return float(np.sum(terrain[ids,1]*w)/sum(w))
def geometry(name,positions,indices,mat):
    # Flat material, explicit normals supplied by the glTF loader when omitted.
    mesh=len(g['meshes']);g['meshes'].append({'name':name,'primitives':[{'attributes':{'POSITION':accessor(positions)},'indices':accessor(np.asarray(indices).reshape(-1,1),'SCALAR',True),'material':mat}]})
    node=len(g['nodes']);g['nodes'].append({'name':name,'mesh':mesh});g['scenes'][g.get('scene',0)]['nodes'].append(node)
    return name
damage=[];fires=[];roofs=0;ruins=0
for node in list(g['nodes']):
    actor=actors.get(node.get('name','').rsplit('_',1)[0])
    if not actor or 'mesh' not in node:continue
    ref=actor['StaticMesh'].lower();p=node.get('translation',[0,0,0]);x,y,z=p
    if 'dion_nv_' in ref and '_top' in ref:
        # Roofs become genuinely collapsed geometry, not merely a color overlay.
        mesh=copy.deepcopy(g['meshes'][node['mesh']]);node['mesh']=len(g['meshes']);g['meshes'].append(mesh)
        for prim in mesh['primitives']:
            points=read(prim['attributes']['POSITION']);points[:,1]*=.22
            points[:,0]+=np.sin(points[:,2]*1.8)*.45
            prim['attributes']['POSITION']=accessor(points)
            if 'indices' in prim:
                faces=read(prim['indices']).reshape(-1,3)
                keep=np.array([rng.random()>.24 for _ in faces]);prim['indices']=accessor(faces[keep].reshape(-1,1),'SCALAR',True)
        roofs+=1;damage.append({'node':node['name'],'source':actor['StaticMesh'],'damage':'collapsed roof'})
    elif 'dion_nv_' in ref and any(w in ref for w in ['_h0','_agit01','_wh','_wg','_bs','_sh01']):
        mesh=copy.deepcopy(g['meshes'][node['mesh']]);node['mesh']=len(g['meshes']);g['meshes'].append(mesh)
        for prim in mesh['primitives']:
            points=read(prim['attributes']['POSITION']);lo,hi=points[:,1].min(),points[:,1].max()
            if hi-lo<.1:continue
            faces=read(prim['indices']).reshape(-1,3) if 'indices' in prim else np.arange(len(points)).reshape(-1,3)
            center=points[faces].mean(axis=1)
            cut=lo+(hi-lo)*(.53+.14*np.sin(center[:,0]*1.7+center[:,2]*.9))
            keep=center[:,1]<cut
            if keep.any():prim['indices']=accessor(faces[keep].reshape(-1,1),'SCALAR',True)
        ruins+=1;damage.append({'node':node['name'],'source':actor['StaticMesh'],'damage':'upper masonry removed along jagged break'})
        fires.append([x,height(x,z)+.25,z])
    elif any(w in ref for w in ['tree','girantree']) and -40<x<65 and -70<z<35:
        # Suppress leafy crowns in the affected area and leave fallen trunks below.
        node['scale']=[.55,.23,.55]

# Rubble and snapped timber grouped in a few editable meshes, to keep draw calls low.
verts={stone:[],wood:[]};faces={stone:[],wood:[]}
def box(cx,cy,cz,sx,sy,sz,yaw,mat):
    start=len(verts[mat]);c,s=math.cos(yaw),math.sin(yaw)
    for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
        xx,zz=a*sx/2,d*sz/2;verts[mat].append([cx+c*xx-s*zz,cy+b*sy/2,cz+s*xx+c*zz])
    for tri in [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(3,7,6),(3,6,2),(1,2,6),(1,6,5),(0,4,7),(0,7,3)]:faces[mat].extend(start+i for i in tri)
for i,p in enumerate(fires):
    for j in range(22):
        x=p[0]+rng.uniform(-5,5);z=p[2]+rng.uniform(-5,5);h=height(x,z)
        box(x,h+.18,z,rng.uniform(.3,1.1),rng.uniform(.25,.65),rng.uniform(.35,.9),rng.random()*math.tau,stone)
    for j in range(4):
        x=p[0]+rng.uniform(-3.8,3.8);z=p[2]+rng.uniform(-3.8,3.8)
        box(x,height(x,z)+.28,z,.22,.25,rng.uniform(2,4.5),rng.random()*math.tau,wood)
for mat in verts:
    geometry('Escombros · piedra' if mat==stone else 'Vigas partidas',verts[mat],faces[mat],mat)

# Branching fissures follow the native heightfield through streets and outskirts.
cracks=[];borders=[];ci=[];bi=[]
for branch in range(11):
    x,z=12+rng.uniform(-9,9),-29+rng.uniform(-8,8);angle=branch*math.tau/11
    for segment in range(rng.randint(8,16)):
        angle+=rng.uniform(-.55,.55);nx=x+math.cos(angle)*rng.uniform(2,4);nz=z+math.sin(angle)*rng.uniform(2,4)
        width=rng.uniform(.12,.35);dx,dz=-math.sin(angle),math.cos(angle)
        for target,indices,mult,raise_y in [(cracks,ci,1,.075),(borders,bi,3,.05)]:
            start=len(target)
            for xx,zz,sign in [(x,z,-1),(nx,nz,-1),(nx,nz,1),(x,z,1)]:
                xx+=sign*dx*width*mult;zz+=sign*dz*width*mult;target.append([xx,height(xx,zz)+raise_y,zz])
            indices.extend([start,start+2,start+1,start,start+3,start+2])
        x,z=nx,nz
geometry('Fisuras · corrupción violeta',cracks,ci,violet)
geometry('Fisuras · bordes quemados',borders,bi,black)
# Native terrain vertex colors burn the town footprint and poison its outskirts.
for prim in g['meshes'][terrain_node['mesh']]['primitives']:
    points=read(prim['attributes']['POSITION'])
    distance=((points[:,0]-13)/52)**2+((points[:,2]+29)/59)**2
    amount=np.exp(-distance*1.7)
    colors=np.ones((len(points),4),dtype=np.float32)
    colors[:,:3]=1-amount[:,None]*np.array([.69,.82,.72])
    prim['attributes']['COLOR_0']=accessor(colors,'VEC4')
g['buffers'].append({'uri':'damage.bin','byteLength':len(extra)})
(OUT/'damage.bin').write_bytes(extra)
g['asset']['generator']='L2 Lab · Dion Hecatombe V1, derived from imported Dion Classic IL'
(OUT/'scene.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')

asset={'id':'custom_dion_hecatombe_v1','title':'Dion · Hecatombe V1','path':'exports/dion-hecatombe-v1/scene.gltf','thumbnail':None,'mesh':'Dion Classic IL · devastated','category':'Escenarios','native':False}
data_path=ROOT/'data.json';data=json.loads(data_path.read_text(encoding='utf-8'))
backup=ROOT/'backups/dion-hecatombe-v1';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():
    (backup/'data.json').write_bytes(data_path.read_bytes())
scene={'id':'dion_hecatombe','title':'Dion · Hecatombe','asset':asset['id'],'source':'Dion Classic IL: variante visual devastada con terreno nativo, edificios dañados, escombros y corrupción. Proyecto del Taller; no instalado en el cliente.','actorMapping':{},'initialCamera':{'position':[78,56,38],'target':[14,4,-29],'fov':48}}
scene['project']='dion-hecatombe-v1.json'
data['assets']=[a for a in data['assets'] if a['id']!=asset['id']]+[asset]
data['scenes']=[s for s in data['scenes'] if s['id']!=scene['id']]+[scene]
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
custom_path=ROOT/'custom-assets.json';custom=json.loads(custom_path.read_text(encoding='utf-8'));custom=[a for a in custom if a['id']!=asset['id']]+[asset];custom_path.write_text(json.dumps(custom,ensure_ascii=False,indent=2),encoding='utf-8')
def entry(name,node='',kind='model',position=None,effect=None):
    obj={'id':str(uuid.uuid4()),'name':name,'asset':asset['id'],'node':node,'kind':kind,'base':kind=='model','visible':True,'locked':False,'position':position or [0,0,0],'rotation':[0,0,0],'scale':[1,1,1],'surfaces':[],'parts':[]}
    if effect:obj['effect']=effect
    return obj
# One model root keeps startup light; every source actor remains available as an internal piece.
objects=[entry('Dion · arquitectura devastada, terreno y escombros')]
for i,p in enumerate(fires):
    if i%2:continue
    for typ,color,count,radius,h,speed in [('fire','#ff8a24',30,2.5,5.5,1),('smoke','#343039',18,3.1,15,.6)]:
        objects.append(entry(('Incendio' if typ=='fire' else 'Humo')+' · edificio '+str(i+1),kind='effect',position=p,effect={'type':typ,'seed':i+100,'count':count,'color':color,'radius':radius,'height':h,'speed':speed,'size':1}))
project={'format':'l2-scene-editor-v1','name':'dion-hecatombe-v1','scene':scene['id'],'reference':{'base':'Dion Classic · maps IL · 20_22','sourceSha256':original_hash,'limitations':'Vista visual del Taller; sin exportación UNR, BSP original, geodata o NPCs.'},'objects':objects,'camera':scene['initialCamera'],'cameras':[scene['initialCamera'],{'position':[41,13,-3],'target':[9,3,-35],'fov':55},{'position':[-26,25,-64],'target':[18,4,-26],'fov':50}]+[None]*7,'atmosphere':{'sky':None,'rotation':0,'brightness':.85,'weather':'ash','density':.6,'wind':.7,'fog':.08,'particle':None}}
PROJECT.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
audit={'source':str(SOURCE),'sourceSha256':original_hash,'sourceUnchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==original_hash,'collapsedRoofs':roofs,'brokenBuildings':ruins,'fireLocations':len(fires),'emitters':len(objects)-1,'damage':damage,'project':str(PROJECT)}
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k!='damage'},indent=2))
