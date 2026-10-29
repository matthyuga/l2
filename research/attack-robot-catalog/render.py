import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\l2-local')
OUT=ROOT/'research/model-catalog/exports/attack-robot'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'attack-robot.glb'))
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
pts=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  evaluated=o.evaluated_get(deps); mesh=evaluated.to_mesh()
  pts.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
  evaluated.to_mesh_clear()
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
(ROOT/'research/attack-robot-catalog/view-bounds.json').write_text(json.dumps([[lo.x,lo.z,-hi.y],[hi.x,hi.z,-lo.y]]))
center=(lo+hi)/2;scale=max(hi-lo)
bpy.ops.object.camera_add(location=center+Vector((1,-2.8,.65)).normalized()*scale*3)
cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO'
rot=cam.rotation_euler.to_matrix().transposed();q=[rot@(p-center) for p in pts]
cam.data.ortho_scale=max(max(p.y for p in q)-min(p.y for p in q),(max(p.x for p in q)-min(p.x for p in q))*420/384)*1.18
cam.data.clip_start=scale*.001;cam.data.clip_end=scale*20
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.22,.27,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for direction,power in [((1,-3,4),450),((-3,-1,2),260),((1,3,3),380)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(direction)*scale)
 light=bpy.context.object;light.data.energy=power*scale*scale;light.data.size=scale*3
 light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=384;scene.render.resolution_y=420;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'research/model-catalog/thumbs/custom_attack_robot.png')
bpy.ops.render.render(write_still=True)
