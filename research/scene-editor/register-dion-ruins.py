"""Freeze three house ruins as editable static glTF pieces, preserving sources."""
from pathlib import Path
import json,struct,copy,uuid
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';OUT=CAT/'exports/dion-ruins-blocks-v1';OUT.mkdir(parents=True,exist_ok=True)
def read(path):
    raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0]
    g=json.loads(raw[20:20+size]);return g,raw[20+size:]
def write(path,g,tail):
    payload=json.dumps(g,ensure_ascii=False,separators=(',',':')).encode('utf-8');payload+=b' '*((-len(payload))%4)
    path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
def remove_floor(g):
    scene=g['scenes'][g.get('scene',0)];scene['nodes']=[i for i in scene['nodes'] if not g['nodes'][i].get('name','').startswith('Suelo')]
source=CAT/'exports/dion-collapse-demo-v1/collapse.glb'
g,tail=read(source)
# Sample the final key of every translation/quaternion track. All source samples
# were baked by Bullet and share their endpoint; no re-simulation is needed.
binary=tail[8:];types={5126:'f',5125:'I',5123:'H'};widths={'VEC3':3,'VEC4':4,'SCALAR':1}
for clip in g.get('animations',[]):
    for channel in clip['channels']:
        sampler=clip['samplers'][channel['sampler']];a=g['accessors'][sampler['output']];v=g['bufferViews'][a['bufferView']]
        width=widths[a['type']];stride=v.get('byteStride',4*width)
        offset=v.get('byteOffset',0)+a.get('byteOffset',0)+(a['count']-1)*stride
        values=list(struct.unpack_from('<'+types[a['componentType']]*width,binary,offset))
        g['nodes'][channel['target']['node']][channel['target']['path']]=values
g.pop('animations',None)
floor=copy.deepcopy(g);floor['scenes'][floor.get('scene',0)]['nodes']=[i for i,n in enumerate(floor['nodes']) if n.get('name','').startswith('Suelo')]
for i in floor['scenes'][floor.get('scene',0)]['nodes']:floor['nodes'][i]['scale']=[2,1,2]
write(OUT/'floor.glb',floor,tail)
remove_floor(g);write(OUT/'house1.glb',g,tail)
counts=[]
for index in [2,3]:
    path=CAT/f'exports/dion-ruins-house{index}-v1/ruins.glb'
    asset,body=read(path);assert not asset.get('animations');remove_floor(asset);write(OUT/f'house{index}.glb',asset,body)
for index in [1,2,3]:
    asset,_=read(OUT/f'house{index}.glb');counts.append(len(asset['scenes'][asset.get('scene',0)]['nodes']))
camera={'position':[25,20,29],'target':[0,.6,0],'fov':42}
assets=[{'id':f'custom_dion_ruins_house{i}_v1','title':f'Dion · Casa destruida {i} · bloques','path':f'exports/dion-ruins-blocks-v1/house{i}.glb','thumbnail':None,'mesh':f'Dion ruina tipo {i}','category':'Escenarios','native':False} for i in [1,2,3]]
assets.append({'id':'custom_dion_ruins_floor_v1','title':'Dion · suelo de exposición','path':'exports/dion-ruins-blocks-v1/floor.glb','thumbnail':None,'mesh':'Suelo','category':'Escenarios','native':False})
parts=[{'asset':a['id'],'title':f'Casa {i+1} · expandir para editar bloques','offset':[(i-1)*12,0,0],'yaw':0} for i,a in enumerate(assets[:3])]
parts.append({'asset':assets[3]['id'],'title':'Suelo de exposición','offset':[0,0,0],'yaw':0})
scene={'id':'dion_ruins_blocks','title':'Dion · Casas destruidas en bloques','asset':assets[0]['id'],'parts':parts,'initialCamera':camera,'source':'Tres casas reales de Dion, fragmentadas y fijadas al terminar sus derrumbes. Sin animación ni física en ejecución. Expandí cada casa para mover sus bloques.','actorMapping':{}}
data_path=ROOT/'data.json';data=json.loads(data_path.read_text(encoding='utf-8'));backup=ROOT/'backups/dion-ruins-blocks-v1';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(data_path.read_bytes())
ids={a['id'] for a in assets};data['assets']=[a for a in data['assets'] if a['id'] not in ids]+assets;data['scenes']=[s for s in data['scenes'] if s['id']!=scene['id']]+[scene]
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
cp=ROOT/'custom-assets.json';custom=json.loads(cp.read_text(encoding='utf-8'));cp.write_text(json.dumps([a for a in custom if a['id'] not in ids]+assets,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'static-audit.json').write_text(json.dumps({'houses':3,'fragments':counts,'totalFragments':sum(counts),'static':True,'animations':0,'textures':'original house textures; fracture interiors have a plain material','scene':scene['id']},ensure_ascii=False,indent=2),encoding='utf-8')
print('REGISTERED',counts,'static fragments; source assets preserved.')
