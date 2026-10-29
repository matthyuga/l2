"""Controlled base-color views, not a reproduction of Genshin or L2 shaders."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'reference-models/amber-web-2026-10-23'
label=sys.argv[sys.argv.index('--')+1]
def flat_material(name,image,alpha=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear()
 out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');tex=nodes.new('ShaderNodeTexImage');tex.image=image
 m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color'])
 # Preserve texture transparency for eyelashes and expression overlays.
 mix=nodes.new('ShaderNodeMixShader');transparent=nodes.new('ShaderNodeBsdfTransparent')
 m.node_tree.links.new(tex.outputs['Alpha'],mix.inputs[0]);m.node_tree.links.new(transparent.outputs[0],mix.inputs[1]);m.node_tree.links.new(em.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs['Surface'])
 return m
if label.startswith('v'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 report=json.loads((BASE/(label+'-analysis.json')).read_text(encoding='utf-8'));geo=json.loads((BASE/(label+'-geometry.json')).read_text())
 verts=[(-x,z,y) for x,y,z in geo['vertices']];indices=geo['indices'];faces=[(indices[i],indices[i+2],indices[i+1]) for i in range(0,len(indices),3)]
 mesh=bpy.data.meshes.new('PMX_reference');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Amber_'+label,mesh);bpy.context.collection.objects.link(obj)
 layer=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for loop in poly.loop_indices:
   u,v=geo['uv'][mesh.loops[loop].vertex_index];layer.data[loop].uv=(u,1-v)
 parent=Path(report['path']).parent
 for m in report['materials']:
  image=bpy.data.images.load(str(parent/report['textures'][m['texture']]['name'].replace('\\','/')),check_existing=True)
  mesh.materials.append(flat_material(m['name'],image,m['diffuse'][3]))
 start=0
 for i,m in enumerate(report['materials']):
  for poly in mesh.polygons[start:start+m['index_count']//3]:poly.material_index=i;poly.use_smooth=True
  start+=m['index_count']//3
 objects=[obj]
else:
 try:bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports'/('amber-imported.blend' if label=='source' else 'amber-l2-rigged.blend')))
 except RuntimeError as e:print('SOURCE_READ_WARNING',str(e))
 objects=[o for o in bpy.data.objects if o.type=='MESH' and (label!='source' or o.name in ['Body.baked','Outfit 00.baked'])]
 for o in bpy.data.objects:
  if o.type=='MESH' and o not in objects:o.hide_render=True
 for o in bpy.data.objects:
  if o.type=='ARMATURE':o.data.pose_position='REST'
 for o in objects:
  for i,m in enumerate(list(o.data.materials)):
   if label=='source':
    # Keep the imported UV mapping graph and replace only the final surface.
    tex=next((n for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None)
    if tex:
     em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color'])
     mix=m.node_tree.nodes.new('ShaderNodeMixShader');trans=m.node_tree.nodes.new('ShaderNodeBsdfTransparent')
     m.node_tree.links.new(tex.outputs['Alpha'],mix.inputs[0]);m.node_tree.links.new(trans.outputs[0],mix.inputs[1]);m.node_tree.links.new(em.outputs[0],mix.inputs[2]);out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL');m.node_tree.links.new(mix.outputs[0],out.inputs['Surface'])
   else:
    image=next(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
    o.data.materials[i]=flat_material(m.name+'_basecolor',image)
 for o in list(bpy.data.objects):
  if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
points=[o.matrix_world@Vector(corner) for o in objects for corner in o.bound_box]
low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
height=high.z-low.z;center=(low+high)/2
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=720;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ComparisonWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.075,.085,.10,1)
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';scene.camera=camera
for view in ['full','face']:
 target=center if view=='full' else Vector((center.x,center.y,low.z+height*.875))
 camera.location=target+Vector((0,(1 if label=='source' else -1)*height*3,0));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.data.ortho_scale=height*(1.10 if view=='full' else .285)
 scene.render.filepath=str(BASE/(label+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
# Scene is for inspecting base colors only. Original PMX/Blender files untouched.
if label=='v14':
 for image in bpy.data.images:
  if image.source=='FILE':image.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'amber-mmd-reference-basecolor.blend'))
print('COMPARISON_RENDER_COMPLETE',label)
