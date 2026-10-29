from pathlib import Path
import json,uuid,ast,numpy as np
R=Path(__file__).resolve().parent;C=R.parent/'model-catalog';O=C/'exports/dion-spines-v6';P=R/'projects/dion-hecatombe-v6.json'
assert not P.exists(),'Preserve user projects'
tree=ast.parse((R/'register-dion-v3.py').read_text(encoding='utf-8'));ns={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'helpers','exec'),ns)
native=C/'exports/scene-batch1-library_fe488fdfccee/scene.gltf';g=json.loads(native.read_text(encoding='utf-8'));n=next(n for n in g['nodes'] if 'terrain' in n.get('name','').lower());a=g['accessors'][g['meshes'][n['mesh']]['primitives'][0]['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];b=(native.parent/g['buffers'][v['buffer']]['uri']).read_bytes();points=np.ndarray((a['count'],3),dtype='<f4',buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4))
def height(x,z):
 d=(points[:,0]-x)**2+(points[:,2]-z)**2;i=np.argpartition(d,3)[:3];w=1/np.maximum(d[i],.001);return float(np.sum(points[i,1]*w)/sum(w))
labels={'single':'Espina arqueada individual','giant':'Espina gigante solitaria','interlaced':'Arcos orgánicos entrelazados','branched':'Espina ramificada'}
assets=[{'id':'custom_dion_spine_v6_'+k,'title':'Plaga · '+label,'path':f'exports/dion-spines-v6/{k}.glb','mesh':label,'category':'Escenarios','thumbnail':None,'native':False} for k,label in labels.items()]
centers={k:ns['bounds'](ns['glb'](O/f'{k}.glb')) for k in labels}
p=json.loads((R/'projects/dion-hecatombe-v5.json').read_text(encoding='utf-8'));p.update(name='dion-hecatombe-v6',scene='dion_hecatombe_v6');p['reference']['version']='Hecatombe V6 · variaciones de espinas'
placements=[('single',18,-20,1),('single',18.8,-26,1.1),('single',19.6,-32,1.23),('giant',-3,4,1),('interlaced',37,5,1),('branched',48,-34,1)]
for i,(kind,x,z,scale) in enumerate(placements):
 center=centers[kind]*scale;pos=center+np.array([x,height(x,z),z]);p['objects'].append({'id':str(uuid.uuid4()),'name':('Calle · espina '+str(i+1)+' · misma dirección') if i<3 else labels[kind],'asset':'custom_dion_spine_v6_'+kind,'node':'','kind':'model','base':True,'visible':True,'locked':False,'position':pos.tolist(),'rotation':[0,0,0],'scale':[scale]*3,'parts':[],'surfaces':[]})
p['cameras'][6]={'position':[34,12,-10],'target':[19,2,-26],'fov':46};p['cameras'][7]={'position':[9,9,16],'target':[-3,2,4],'fov':46};p['cameras'][8]={'position':[49,10,17],'target':[37,2,5],'fov':46};p['cameras'][9]={'position':[58,9,-23],'target':[48,2,-34],'fov':46};p['camera']=p['cameras'][6];P.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
dp=R/'data.json';d=json.loads(dp.read_text(encoding='utf-8'));backup=R/'backups/dion-spines-v6';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(dp.read_bytes())
d['assets']+=assets;d['scenes'].append({'id':p['scene'],'title':'Dion · Hecatombe V6 · Espinas variadas','asset':'custom_dion_plague_v4_core','project':P.name,'initialCamera':p['camera'],'source':'Tres espinas arqueadas en fila y tres variantes adicionales según bocetos.','actorMapping':{}});dp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
cp=R/'custom-assets.json';d=json.loads(cp.read_text(encoding='utf-8'));d+=assets;cp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');(O/'placements.json').write_text(json.dumps(placements,indent=2));print('REGISTERED V6')
