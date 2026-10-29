import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/model-catalog/exports/attack-robot'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'temp/attack-robot-review/Attack Robot.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
before=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
for o in meshes:
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Catalog optimization','DECIMATE');mod.ratio=.35
 bpy.ops.object.modifier_apply(modifier=mod.name)
for im in bpy.data.images:
 if im.size[0]>2048: im.scale(2048,2048)
for mat in bpy.data.materials:
 if mat.use_nodes:
  bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs: bs.inputs['Roughness'].default_value=.65
bpy.ops.export_scene.gltf(filepath=str(OUT/'attack-robot.glb'),export_format='GLB',export_animations=False,export_image_format='JPEG',export_jpeg_quality=90)
after=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
report={'source_triangles':before,'catalog_triangles':after,'bones':sum(len(o.data.bones) for o in bpy.data.objects if o.type=='ARMATURE'),'animations':len(bpy.data.actions),'glb_bytes':(OUT/'attack-robot.glb').stat().st_size,'textures':[{'name':im.name,'size':list(im.size)} for im in bpy.data.images]}
(Path(__file__).parent/'conversion.json').write_text(json.dumps(report,indent=2))
# Render the exported GLB to verify the actual catalog artifact.
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
print('COMPLETE',json.dumps(report),flush=True)
