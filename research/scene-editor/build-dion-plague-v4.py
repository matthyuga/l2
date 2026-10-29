from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent;C=R.parent/'model-catalog';O=C/'exports/dion-plague-v4';O.mkdir(parents=True,exist_ok=True)
project=R/'projects/dion-hecatombe-v4.json'
assert not project.exists(),'Preserve existing user project'
src=C/'exports/dion-hecatombe-v3/core.gltf';g=json.loads(src.read_text(encoding='utf-8'))
scene=g['scenes'][g.get('scene',0)];scene['nodes']=[i for i in scene['nodes'] if not g['nodes'][i].get('name','').startswith('Fisuras')]
for b in g['buffers']:b['uri']='../../'+str((src.parent/b['uri']).resolve().relative_to(C)).replace('\\','/')
for image in g.get('images',[]):
 if 'uri' in image:image['uri']='../../'+str((src.parent/image['uri']).resolve().relative_to(C)).replace('\\','/')
terrain=next(n for n in g['nodes'] if n.get('name')=='R4NativeTerrain')
for p in g['meshes'][terrain['mesh']]['primitives']:
 p['attributes'].pop('COLOR_0',None)
 mat=g['materials'][p['material']];mat['pbrMetallicRoughness']['baseColorFactor']=[.84,.80,.72,1];mat['name']='Dion_Plague_Terrain_V4'
g.setdefault('extras',{})['plague']='Procedural local terrain material in terrain-plague.js. No purple strip geometry.'
(O/'core.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
a={'id':'custom_dion_plague_v4_core','title':'Dion V4 · suelo enfermo','path':'exports/dion-plague-v4/core.gltf','mesh':'Dion terreno plagado V4','category':'Escenarios','thumbnail':None,'native':False}
p=json.loads((R/'projects/dion-hecatombe-v3.json').read_text(encoding='utf-8'));p.update(name='dion-hecatombe-v4',scene='dion_hecatombe_v4');p['objects'][0]['asset']=a['id'];p['objects'][0]['name']='Dion · terreno marchito y plaga';p['reference']['version']='Hecatombe V4 · suelo marchito';p['cameras'][4]={'position':[4,9,-2],'target':[14,1,-20],'fov':48};project.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
dp=R/'data.json';d=json.loads(dp.read_text(encoding='utf-8'));backup=R/'backups/dion-plague-v4';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(dp.read_bytes())
d['assets'].append(a);d['scenes'].append({'id':p['scene'],'title':'Dion · Hecatombe V4 · Suelo marchito','asset':a['id'],'project':project.name,'source':'Plaga integrada al terreno, tierra enferma, bordes orgánicos y raíces oscuras.','initialCamera':p['camera'],'actorMapping':{}});dp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
cp=R/'custom-assets.json';d=json.loads(cp.read_text(encoding='utf-8'));d.append(a);cp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('V4 registered; removed flat fissure geometry; existing V3 preserved.')
