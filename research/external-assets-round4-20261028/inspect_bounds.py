import bpy,pathlib,json
from mathutils import Vector
p=pathlib.Path(r"E:\l2-local\research\model-catalog\exports\external-assets-3\ext3_8098fc274498bb\model.glb")
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.visible_get():continue
 raw=[o.matrix_world@Vector(v) for v in o.bound_box];e=o.evaluated_get(dg);ev=[e.matrix_world@Vector(v) for v in e.bound_box]
 print(o.name,'raw',[[round(f(v[i] for v in raw),3) for i in range(3)] for f in [min,max]],'evaluated',[[round(f(v[i] for v in ev),3) for i in range(3)] for f in [min,max]],flush=True)
