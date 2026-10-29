from pathlib import Path
import json,struct,uuid
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';OUT=CAT/'exports/dion-collapse-demo-v1'
# Blender's exporter emitted an action per fragment. Combine their simultaneous
# channels into a single nine-second clip; do not change simulated transforms.
file=OUT/'collapse.glb';raw=file.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
g=json.loads(raw[20:20+length]);clips=g.get('animations',[])
if len(clips)>1:
    clip={'name':'Derrumbe físico de Dion','samplers':[],'channels':[]}
    for part in clips:
        offset=len(clip['samplers']);clip['samplers'].extend(part['samplers'])
        for channel in part['channels']:
            channel['sampler']+=offset;clip['channels'].append(channel)
    g['animations']=[clip];payload=json.dumps(g,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    payload+=b' '*((-len(payload))%4);tail=raw[20+length:]
    file.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
asset={'id':'custom_dion_collapse_demo_v1','title':'Dion · Prueba de derrumbe físico','path':'exports/dion-collapse-demo-v1/collapse.glb','thumbnail':None,'mesh':'Dion_NV_H01 + Dion_NV_H01_Top','category':'Escenarios','native':False}
camera={'position':[9,7,11],'target':[0,1,0],'fov':42}
scene={'id':'dion_collapse_demo','title':'Dion · Prueba de física','asset':asset['id'],'source':'Casa de Dion con derrumbe calculado en Blender. Seleccioná la casa y pulsá reproducir en el panel de animación.','initialCamera':camera,'actorMapping':{},'project':'dion-collapse-demo-v1.json'}
data_path=ROOT/'data.json';data=json.loads(data_path.read_text(encoding='utf-8'))
backup=ROOT/'backups/dion-collapse-demo-v1';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(data_path.read_bytes())
data['assets']=[a for a in data['assets'] if a['id']!=asset['id']]+[asset]
data['scenes']=[s for s in data['scenes'] if s['id']!=scene['id']]+[scene]
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
custom_path=ROOT/'custom-assets.json';custom=json.loads(custom_path.read_text(encoding='utf-8'));custom=[a for a in custom if a['id']!=asset['id']]+[asset];custom_path.write_text(json.dumps(custom,ensure_ascii=False,indent=2),encoding='utf-8')
project={'format':'l2-scene-editor-v1','name':'dion-collapse-demo-v1','scene':scene['id'],'camera':camera,'cameras':[camera,{'position':[-8,3,9],'target':[0,1,0],'fov':45}]+[None]*8,'objects':[{'id':str(uuid.uuid4()),'name':'Casa de Dion · seleccionar para reproducir derrumbe','asset':asset['id'],'node':'','kind':'model','base':True,'visible':True,'locked':True,'position':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1],'parts':[],'surfaces':[]} ]}
project_path=ROOT/'projects/dion-collapse-demo-v1.json'
if not project_path.exists():project_path.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
print('Registered demo, one combined clip with',len(g['animations'][0]['channels']),'channels')
