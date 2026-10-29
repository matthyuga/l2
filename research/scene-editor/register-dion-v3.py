from pathlib import Path
import json,struct,copy,uuid,math
import numpy as np
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';OUT=CAT/'exports/dion-hecatombe-v3';PROJECT=ROOT/'projects/dion-hecatombe-v3.json'
assert not PROJECT.exists(),'Preserve existing project'
placement=json.loads((OUT/'native-placement.json').read_text());remove=set(placement['building']+placement['walls'])
source=CAT/'exports/dion-hecatombe-v2/core.gltf';g=json.loads(source.read_text(encoding='utf-8'));g['scenes'][g.get('scene',0)]['nodes']=[i for i in g['scenes'][g.get('scene',0)]['nodes'] if g['nodes'][i].get('name') not in remove]
def matrix(n):
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return np.array(n['matrix']).reshape(4,4,order='F') if 'matrix' in n else m
def bounds(g):
 points=[]
 def walk(i,parent):
  n=g['nodes'][i];m=parent@matrix(n)
  if 'mesh' in n:
   for p in g['meshes'][n['mesh']]['primitives']:
    a=g['accessors'][p['attributes']['POSITION']];lo=a['min'];hi=a['max']
    for x in [lo[0],hi[0]]:
     for y in [lo[1],hi[1]]:
      for z in [lo[2],hi[2]]:points.append((m@np.array([x,y,z,1]))[:3])
  for child in n.get('children',[]):walk(child,m)
 for i in g['scenes'][g.get('scene',0)]['nodes']:walk(i,np.eye(4))
 points=np.array(points);return (points.min(0)+points.max(0))/2
corecenter=bounds(g);(OUT/'core.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
def glb(path):
 b=path.read_bytes();size=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+size])
assets=[{'id':'custom_dion_v3_core','title':'Dion V3 · entorno','path':'exports/dion-hecatombe-v3/core.gltf','mesh':'Dion entorno V3','category':'Escenarios','thumbnail':None,'native':False},{'id':'custom_dion_v3_walls','title':'Dion V3 · muros con daños variados','path':'exports/dion-hecatombe-v3/damaged-walls.glb','mesh':'Muros nativos destruidos','category':'Escenarios','thumbnail':None,'native':False},{'id':'custom_dion_v3_de','title':'Dion V3 · edificio DE derrumbado','path':'exports/dion-hecatombe-v3/house11.glb','mesh':'Dion_NV_DE destruido','category':'Escenarios','thumbnail':None,'native':False}]
p=json.loads((ROOT/'projects/dion-hecatombe-v2.json').read_text(encoding='utf-8'));p['name']='dion-hecatombe-v3';p['scene']='dion_hecatombe_v3';p['objects'][0].update(asset=assets[0]['id'],position=corecenter.tolist())
def entry(name,asset,position):return {'id':str(uuid.uuid4()),'name':name,'asset':asset,'node':'','kind':'model','base':True,'locked':False,'visible':True,'position':list(map(float,position)),'rotation':[0,0,0],'scale':[1,1,1],'parts':[],'surfaces':[]}
wc=bounds(glb(OUT/'damaged-walls.glb'));hc=bounds(glb(OUT/'house11.glb'));base=np.array(placement['center'])
p['objects'].insert(1,entry('Muros · daños leves, brechas y derrumbes',assets[1]['id'],wc))
p['objects'].insert(2,entry('Edificio DE · tejado y paredes derrumbados',assets[2]['id'],base+hc))
p['reference'].update(version='Hecatombe V3 · edificio DE y muros',buildings=28,types=11)
p['cameras'][3]={'position':(base+np.array([10,7,11])).tolist(),'target':(base+np.array([0,.6,0])).tolist(),'fov':48}
PROJECT.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
dp=ROOT/'data.json';data=json.loads(dp.read_text(encoding='utf-8'));backup=ROOT/'backups/dion-hecatombe-v3';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(dp.read_bytes())
ids={a['id'] for a in assets};data['assets']=[a for a in data['assets'] if a['id'] not in ids]+assets
scene={'id':'dion_hecatombe_v3','title':'Dion · Hecatombe V3 · Muros y edificio','asset':assets[0]['id'],'project':PROJECT.name,'source':'Edificio DE derrumbado y muros con daños de distinta intensidad; V2 conservado.','initialCamera':p['camera'],'actorMapping':{}}
data['scenes']=[s for s in data['scenes'] if s['id']!=scene['id']]+[scene];dp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
cp=ROOT/'custom-assets.json';custom=json.loads(cp.read_text(encoding='utf-8'));cp.write_text(json.dumps([a for a in custom if a['id'] not in ids]+assets,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'integration-audit.json').write_text(json.dumps({'removed':sorted(remove),'objects':len(p['objects']),'buildingPlacement':base.tolist(),'wallsCenter':wc.tolist(),'coreCenter':corecenter.tolist(),'previousProjectPreserved':True},indent=2))
print('V3 registered',base.tolist(),len(p['objects']))
