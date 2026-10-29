from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
assets=[{'id':f'custom_dion_rubble_house{i}_v2','title':f'Dion · Escombros irregulares · casa {i}','path':f'exports/dion-rubble-v2/house{i}.glb','thumbnail':None,'mesh':f'Dion casa {i} · bordes rotos y escombros','category':'Escenarios','native':False} for i in [1,2,3]]
camera={'position':[8,9,13],'target':[0,.4,0],'fov':46}
parts=[{'asset':a['id'],'title':f'Casa {i+1} · muros, tejados y restos rotos','offset':[(i-1)*12,0,0],'yaw':0} for i,a in enumerate(assets)]
parts.append({'asset':'custom_dion_ruins_floor_v1','title':'Suelo de exposición','offset':[0,0,0],'yaw':0})
scene={'id':'dion_rubble_v2','title':'Dion · Escombros irregulares V2','asset':assets[0]['id'],'parts':parts,'initialCamera':camera,'source':'Tres ruinas estáticas con roturas geométricas, huecos, madera astillada, tejas y ladrillos. Sin física en ejecución.','actorMapping':{}}
data_path=ROOT/'data.json';data=json.loads(data_path.read_text(encoding='utf-8'));backup=ROOT/'backups/dion-rubble-v2';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(data_path.read_bytes())
ids={a['id'] for a in assets};data['assets']=[a for a in data['assets'] if a['id'] not in ids]+assets;data['scenes']=[s for s in data['scenes'] if s['id']!=scene['id']]+[scene]
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
cp=ROOT/'custom-assets.json';custom=json.loads(cp.read_text(encoding='utf-8'));cp.write_text(json.dumps([a for a in custom if a['id'] not in ids]+assets,ensure_ascii=False,indent=2),encoding='utf-8')
print('Registered separate rubble V2 scene; V1 preserved.')
