import bpy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/psk_addon'))
import io_scene_psk_psa
io_scene_psk_psa.register()
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'exports/amber-source.glb'))

def summarize():
    return [{'name': o.name, 'type': o.type, 'vertices': len(o.data.vertices) if o.type == 'MESH' else None,
             'triangles': sum(len(p.vertices)-2 for p in o.data.polygons) if o.type == 'MESH' else None,
             'materials': [m.name if m else None for m in o.data.materials] if o.type == 'MESH' else None,
             'dimensions': list(o.dimensions),
             'bones': [{'name': b.name, 'head': list(b.head_local), 'parent': b.parent.name if b.parent else None} for b in o.data.bones] if o.type == 'ARMATURE' else None}
            for o in bpy.data.objects]
amber = summarize()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'exports/amber-imported.blend'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.psk(filepath=str(ROOT / 'exports/l2-reference/Fighter/SkeletalMesh/FFighter_m001_u.psk'))
reference = summarize()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'exports/fighter-reference.blend'))
(ROOT / 'reports/blender-inputs.json').write_text(json.dumps({'amber': amber, 'reference': reference}, indent=2), encoding='utf8')
print('AMBER_L2_INSPECTION_COMPLETE')
