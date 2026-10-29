"""Prepare references to existing visual assets; do not alter client resources."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[1];CAT=LAB/'research/model-catalog'
gallery=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
def clean(s):
 for _ in range(2):
  try:
   if any(c in s for c in ('Ã','Â','â')):s=s.encode('latin1').decode('utf-8')
  except (UnicodeError,UnicodeEncodeError):break
 return s
assets=[]
for m in gallery['models']:
 if m.get('status')!='ready' or not m.get('gltf') or not (CAT/m['gltf']).exists():continue
 assets.append({'id':m['key'],'title':clean(m['title']),'path':m['gltf'],'thumbnail':m.get('thumbnail'),'mesh':m.get('mesh'),'category':clean(m.get('category','')),'batch':m.get('batch'),'native':m.get('native') is True,'sourcePackage':m.get('sourcePackage')})

# Keep locally built visual prototypes registered when rebuilding the catalog.
custom_path=ROOT/'custom-assets.json'
if custom_path.exists():
 for custom in json.loads(custom_path.read_text(encoding='utf-8')):
  if (CAT/custom['path']).is_file():
   assets=[a for a in assets if a['id']!=custom['id']]
   assets.append(custom)

# Full native maps are editor canvases, not placeable gallery items. Register
# them separately so rebuilding the ordinary asset catalog cannot remove a
# map which has already been converted for the scene selector.
giran_gltf=CAT/'exports/scene-giran/scene.gltf'
if giran_gltf.exists():
 assets.append({'id':'scene_giran','title':'Giran · Castillo y territorio','path':'exports/scene-giran/scene.gltf','thumbnail':None,'mesh':'23_22.unr','category':'Escenarios'})
giran_city_gltf=CAT/'exports/scene-giran-city/scene.gltf'
if giran_city_gltf.exists():
 assets.append({'id':'scene_giran_city','title':'Ciudad de Giran','path':'exports/scene-giran-city/scene.gltf','thumbnail':None,'mesh':'22_22.unr','category':'Escenarios'})
audit=json.loads((LAB/'research/airships/gludio-assembly-audit.json').read_text())
placed=json.loads((LAB/'research/gludio-sky/build-audit.json').read_text())['placed']
mapping={p['source']:{'actor':p['name'],'mesh':p['mesh'].replace('Glacia_kserth_S.','HGGludioSky_S.'),'location':p['location']} for p in placed}
data_path=ROOT/'data.json'
previous=json.loads(data_path.read_text(encoding='utf-8')) if data_path.exists() else {}
live=next((p for p in (Path('E:/l2/Maps/24_19.unr'),Path('D:/l2/Maps/24_19.unr')) if p.exists()),None)
previous_reference=previous.get('reference',{})
reference={'environment':'L2 Lab','map':str(live) if live else previous_reference.get('map','24_19.unr no disponible al regenerar'),'sha256':hashlib.sha256(live.read_bytes()).hexdigest() if live else previous_reference.get('sha256',''),'coordinates':'Three.js/glTF, metros: X lateral, Y altura, Z profundidad. Las transformaciones son de edición visual; no se instalan automáticamente.'}
data={'assets':assets,'scenes':[{'id':'gludio','title':'Muelle de Gludio','asset':'airship_scene_gludio','source':'Gludio: ocho piezas arquitectónicas. Entorno y materiales aproximados.','actorMapping':mapping,'installedOrigin':[147904,46821,11933]},{'id':'gracia','title':'Aeronave de Gracia','asset':'airship_assembled_gracia','source':'Montaje de referencia de Gracia; no representa todas las aeronaves instaladas.','actorMapping':{}}],'reference':reference}
data['scenes'][1]['parts']=[{'asset':'airship_fly_boat_body002','title':'Casco','offset':[0,0,0],'yaw':0},{'asset':'airship_animated_fly_boat_body004','title':'Velamen','offset':[0,0,0],'yaw':3.141592653589793},{'asset':'airship_animated_fly_boat_body003','title':'Cola','offset':[-4.98,0,0],'yaw':3.141592653589793},{'asset':'airship_fly_boat_steering001','title':'Mando','offset':[3.63,1.02,0],'yaw':0}]
if giran_gltf.exists():
 data['scenes'].append({'id':'giran','title':'Giran · Castillo y territorio','asset':'scene_giran','source':'Giran 23_22: 1.638 actores estáticos, castillo y terreno nativo de 16 bits con nueve capas de textura; sin BSP, iluminación, partículas ni NPCs.','actorMapping':{},'installedOrigin':[114630,147072,-3754],'initialCamera':{'position':[125.55814607018041,76.3769320312698,-19.403807715511597],'target':[0.08478349472228786,5.845229911266445,1.4461724832588898],'fov':42}})
if giran_city_gltf.exists():
  data['scenes'].append({'id':'giran_city','title':'Ciudad de Giran','asset':'scene_giran_city','source':'Giran 22_22: 1.936 actores estáticos, terreno nativo de 16 bits con ocho capas y 189 pinceles BSP aditivos para plazas, calles e interiores; sin iluminación, partículas ni NPCs.','actorMapping':{},'installedOrigin':[83400,148600,-3400],'initialCamera':{'position':[95,65,95],'target':[0,5,0],'fov':42}})
# Preserve registered custom scene canvases when refreshing the model catalog.
known_scenes={s['id'] for s in data['scenes']}
known_assets={a['id'] for a in data['assets']}
for scene in previous.get('scenes',[]):
 if scene['id'] not in known_scenes and scene.get('asset') in known_assets:
  data['scenes'].append(scene)
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(assets),'assets indexed; live client read-only.')
