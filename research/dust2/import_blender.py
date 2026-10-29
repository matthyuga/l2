"""Import the user's original GoldSrc BSP; do not touch either game install."""
import bpy,pathlib,importlib.util,json,math
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
spec=importlib.util.spec_from_file_location('goldimporter_reference',D/'reference/goldimporter/bsp_importer.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.skipped_textures=['sky','aaatrigger','clip','origin','hint','skip','null','bevel','noclip','playerclip']
options=dict(scale=.03125,brightness_adjust=0.,create_materials=True,import_lights=False,import_brush_entities=True,import_point_entities=True,stitch_changelevel=False)
mod.import_bsp(bpy.context,str(D/'source/de_dust2.bsp'),dict(wadpath=str(D/'textures')+'/'),options)
hidden=[]
for o in bpy.context.scene.objects:
 if o.get('classname','') in ('func_bomb_target','func_buyzone'):
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and len(o.data.polygons)]
bpy.context.view_layer.update()
triangles=0;images=[]
for o in meshes:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
for i in bpy.data.images:
 if i.source=='FILE':images.append(dict(name=i.name,size=list(i.size),loaded=i.has_data))
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box];lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);center=(lo+hi)/2;radius=(hi-lo).length/2
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Dust2Inspection');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.64,.75,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
sun=bpy.data.objects.new('InspectionSun',bpy.data.lights.new('InspectionSun','SUN'));scene.collection.objects.link(sun);sun.data.energy=2.;sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-30));sun.data.angle=.12
cam=bpy.data.objects.new('InspectionCamera',bpy.data.cameras.new('InspectionCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=radius*2.05;cam.data.clip_end=radius*20
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
for name,direction in [('dust2-aerial',(1,-1,1.6)),('dust2-top',(0,0,3))]:
 cam.location=center+Vector(direction).normalized()*radius*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(D/'Dust2-CS16-original.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.wm.obj_export(filepath=str(D/'Dust2-CS16.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
report=dict(source='D:/juegos/cs1.6/cstrike/maps/de_dust2.bsp',blender=bpy.app.version_string,visible_meshes=len(meshes),triangles=triangles,images=images,hidden_trigger_meshes=hidden,scale_goldsrc_to_blender=.03125,bounds=[list(lo),list(hi)],dimensions=list(hi-lo),lightmaps_imported=False,l2_installed=False,objects=[dict(name=o.name,triangles=len(o.data.loop_triangles),materials=[m.name for m in o.data.materials],classname=o.get('classname','worldspawn')) for o in meshes])
(D/'blender-audit.json').write_text(json.dumps(report,indent=2));print('DUST2_IMPORTED',triangles,'triangles;',len(meshes),'meshes;',len(images),'textures',flush=True)
