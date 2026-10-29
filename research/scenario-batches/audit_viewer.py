from pathlib import Path
from urllib.parse import unquote
import json,collections
ROOT=Path(__file__).resolve().parents[2];G=ROOT/'research/model-catalog';OUT=Path(__file__).resolve().parent/'audit';OUT.mkdir(exist_ok=True)
j=json.loads((G/'gallery.json').read_text(encoding='utf-8'));reports=[]
for m in j['models']:
 if 'Escenario' not in m.get('types',[]):continue
 p=G/m['gltf'];g=json.loads(p.read_text(encoding='utf-8'));missing=[]
 for resource in g.get('buffers',[])+g.get('images',[]):
  uri=resource.get('uri','')
  if uri and not uri.startswith('data:') and not (p.parent/unquote(uri)).is_file():missing.append(uri)
 terrain=[n.get('name','') for n in g.get('nodes',[]) if 'terrain' in n.get('name','').lower()]
 mats=g.get('materials',[]);untextured=[a.get('name','') for a in mats if 'baseColorTexture' not in a.get('pbrMetallicRoughness',{})]
 actors=None;omitted=None
 paths={
  'scenario_batch1_r4_arena':ROOT/'research/scenario-batches/r4_arena/audit-with-terrain.json',
  'scenario_batch1_canon_cathedral':ROOT/'research/scenario-batches/canon_cathedral/audit-with-terrain.json',
  'veilmar_surface':ROOT/'research/veilmar/veilmar_surface-assembly-audit.json',
  'veilmar_underground':ROOT/'research/veilmar/veilmar_underground-assembly-audit.json',
 }
 audit=paths.get(m['key'])
 if m['key'].startswith('airship_scene_'):audit=ROOT/'research/airships'/(m['key'].replace('airship_scene_','')+'-assembly-audit.json')
 if audit and audit.exists():
  a=json.loads(audit.read_text(encoding='utf-8'));actors=len(a.get('used',a.get('actors',[])));omitted=len(a.get('missing',[]))
 reports.append(dict(key=m['key'],title=m['title'],gltf=m['gltf'],thumbnail_exists=(G/m['thumbnail']).is_file(),missing_links=missing,materials=len(mats),materials_without_basecolor_texture=untextured,terrain_nodes=terrain,terrain_visible=m.get('terrain_visible',True),actors_in_assembly=actors,omitted_actors=omitted,note=m.get('note'),status='broken_links' if missing else 'resources_present_partial_preview'))
(OUT/'viewer-audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
for a in reports:print(a['key'],'missing_links',len(a['missing_links']),'terrain',bool(a['terrain_nodes']),'materials_without_texture',len(a['materials_without_basecolor_texture']),'omitted',a['omitted_actors'])
