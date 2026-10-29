"""Merge corrected material exports without replacing the original catalog entries."""
from pathlib import Path
import json, collections, shutil

ROOT = Path(__file__).resolve().parents[2]
STAGE = Path(__file__).resolve().parent
GALLERY = ROOT / 'research/model-catalog'
path = GALLERY / 'gallery.json'
catalog = json.loads(path.read_text(encoding='utf-8'))
backup = STAGE / 'gallery-before-material-fix.json'
if not backup.exists():
    shutil.copy2(path, backup)
before = json.loads(backup.read_text(encoding='utf-8'))
fresh = {}
for report in (STAGE / 'packages').glob('*/gallery-models.json'):
    for model in json.loads(report.read_text(encoding='utf-8'))['models']:
        fresh[model['key']] = model
original = [m for m in catalog['models'] if m.get('batch') != 'Tanda 2']
for model in catalog['models']:
    if model.get('batch') != 'Tanda 2' or model['key'] not in fresh:
        continue
    updated = dict(fresh[model['key']])
    if updated.get('status') == 'ready':
        gltf = json.loads((GALLERY / updated['gltf']).read_text(encoding='utf-8'))
        if not any(mesh.get('primitives') for mesh in gltf.get('meshes', [])):
            updated.update(status='failed', error='El paquete declara una malla, pero UModel exporta geometria vacia.', note='Vista 3D pendiente: el paquete contiene una malla sin geometria exportable por UModel. El archivo original se conserva.')
    model.clear()
    model.update(updated)
assert original == [m for m in catalog['models'] if m.get('batch') != 'Tanda 2']
batch = [m for m in catalog['models'] if m.get('batch') == 'Tanda 2']
shared = collections.Counter(m.get('gltf') for m in batch if m.get('gltf'))
for model in batch:
    if model.get('status') == 'ready' and shared[model.get('gltf')] > 1:
        model['note'] = model.get('note', '') + ' Variantes del mismo cuerpo comparten una vista representativa; los colores y efectos exactos deben revisarse en el cliente.'
path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
ready = [m for m in batch if m.get('status') == 'ready']
for i in range(3):
    (STAGE / ('render-' + str(i) + '.json')).write_text(json.dumps({'models': ready[i::3]}), encoding='utf-8')
old_ready = [m for m in before['models'] if m.get('batch') == 'Tanda 2' and m.get('status') == 'ready']
def metrics(models):
    return dict(views=len(models), with_any_texture=sum(m.get('textured_materials',0)>0 for m in models), fully_textured=sum(m.get('material_count',0)>0 and m.get('textured_materials',0)==m.get('material_count',0) for m in models), textured_slots=sum(m.get('textured_materials',0) for m in models), total_slots=sum(m.get('material_count',0) for m in models))
summary = dict(before=metrics(old_ready), after=metrics(ready), unavailable=len(batch)-len(ready), original_preserved=len(original), reason='Package paths containing spaces were truncated while parsing UModel material references.')
(STAGE / 'material-fix-summary.json').write_text(json.dumps(summary,indent=2), encoding='utf-8')
print(json.dumps(summary))
