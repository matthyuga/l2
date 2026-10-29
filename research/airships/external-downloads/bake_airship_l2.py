"""Bake the authored materials into an Interlude-friendly atlas, preserving source."""
import bpy,pathlib,json,math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[3];D=ROOT/'research/airship-integration';D.mkdir(exist_ok=True)
SRC=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'airship-probe-optimized.blend'),load_ui=False,use_scripts=False)
scene=bpy.context.scene;objects=[o for o in scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in objects:
 o.hide_set(False);o.select_set(True)
 if not o.data.uv_layers:o.data.uv_layers.new(name='SourceUV')
 o.data.uv_layers.active.name='SourceUV'
 o.data.uv_layers.new(name='L2Atlas');o.data.uv_layers.active_index=len(o.data.uv_layers)-1;o.data.uv_layers.active.active_render=True
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
atlas=bpy.data.images.new('HGAirshipAtlas',width=2048,height=2048,alpha=False);atlas.generated_color=(.12,.08,.05,1)
materials={m for o in objects for m in o.data.materials if m}
visited=set()
def preserve_uv(tree):
 if tree in visited:return
 visited.add(tree);source=tree.nodes.new('ShaderNodeUVMap');source.uv_map='SourceUV'
 for n in list(tree.nodes):
  if n.type=='GROUP' and n.node_tree:preserve_uv(n.node_tree)
  elif n.type=='TEX_COORD':
   for link in list(n.outputs['UV'].links):tree.links.new(source.outputs['UV'],link.to_socket)
  elif n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:tree.links.new(source.outputs['UV'],n.inputs['Vector'])
for m in materials:
 if not m.use_nodes:m.use_nodes=True
 tree=m.node_tree;preserve_uv(tree)
 for n in tree.nodes:n.select=False
 # Bake authored base colour, including metals, rather than diffuse response.
 principled=next((n for n in tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if principled:
  emission=tree.nodes.new('ShaderNodeBsdfDiffuse');socket=principled.inputs['Base Color']
  if socket.is_linked:tree.links.new(socket.links[0].from_socket,emission.inputs['Color'])
  else:emission.inputs['Color'].default_value=socket.default_value
  output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);tree.links.new(emission.outputs[0],output.inputs['Surface'])
 target=tree.nodes.new('ShaderNodeTexImage');target.name='L2_BakeTarget';target.image=atlas;target.select=True;tree.nodes.active=target
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;scene.render.bake.use_clear=False;scene.render.bake.margin=8
bpy.ops.object.select_all(action='DESELECT')
for i,o in enumerate(objects):
 o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.bake(type='DIFFUSE',uv_layer='L2Atlas');o.select_set(False)
 print('BAKED',i+1,len(objects),o.name,flush=True)
atlas.filepath_raw=str(D/'AirshipAtlas.png');atlas.file_format='PNG';atlas.save()
atlas.filepath_raw=str(D/'AirshipAtlas.tga');atlas.file_format='TARGA';atlas.save()
mat=bpy.data.materials.new('AirshipAtlas');mat.use_nodes=True;nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;mat.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
for o in objects:
 for name in [layer.name for layer in o.data.uv_layers]:
  if name!='L2Atlas':o.data.uv_layers.remove(o.data.uv_layers[name])
 o.data.uv_layers.active_index=0;o.data.materials.clear();o.data.materials.append(mat)
 for p in o.data.polygons:p.material_index=0
 o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ship=bpy.context.object;ship.name='HGSkyAirship'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# Coordinates in this scene are metres. Center XY while retaining vertical shape.
coords=[v.co.copy() for v in ship.data.vertices];center=Vector([(min(v[i] for v in coords)+max(v[i] for v in coords))/2 for i in range(3)])
for v in ship.data.vertices:v.co.x-=center.x;v.co.y-=center.y
bpy.ops.wm.obj_export(filepath=str(D/'HGSkyAirship.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'HGSkyAirship-baked.blend'))
ship.data.calc_loop_triangles();verts=[list(v.co) for v in ship.data.vertices];triangles=[list(t.vertices) for t in ship.data.loop_triangles]
(D/'source-geometry.json').write_text(json.dumps(dict(vertices=verts,triangles=triangles)))
(D/'bake-audit.json').write_text(json.dumps(dict(atlas=[2048,2048],source_materials=[m.name for m in materials],triangles=len(triangles),bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],objects_baked=len(objects)),indent=2));print('BAKE_COMPLETE',flush=True)
