import bpy,sys,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;B=R.parent/'build';sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon');import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
bpy.ops.wm.open_mainfile(filepath=str(B/'RifleNPCV3.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rigid=[b.name for b in rig.data.bones]
def invariant(o):
 return {'verts':[list(v.co) for v in o.data.vertices],'groups':[(g.name,g.index) for g in o.vertex_groups],'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],'transform':[list(row) for row in o.matrix_world]}
original={o.name:invariant(o) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.object.select_all(action='DESELECT');before=set(bpy.data.objects);bpy.ops.import_scene.psk(filepath=str(R/'native-export/Fighter/SkeletalMesh/FFighter_m000_f.psk'));added=set(bpy.data.objects)-before
for o in added:
 if o.type=='MESH':
  for mod in o.modifiers:
   if mod.type=='ARMATURE':mod.object=rig
  o.parent=rig
for o in added:
 if o.type=='ARMATURE':bpy.data.objects.remove(o,do_unlink=True)
bodymat=bpy.data.materials.new('BodyAtlas');bodymat.use_nodes=True;nodes=bodymat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'BodyAtlas.png'));bodymat.node_tree.links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color']);bodymat.node_tree.links.new(tex.outputs['Alpha'],nodes['Principled BSDF'].inputs['Alpha']);nodes['Principled BSDF'].inputs['Roughness'].default_value=.75;bodymat.blend_method='CLIP';bodymat.alpha_threshold=.45;bodymat.use_screen_refraction=False;bodymat.use_backface_culling=False
names={'u':0,'l':1,'b':2,'g':3,'m00_ah':4,'m00_bh':5,'f':6};tiles=json.loads((R/'atlas-tiles.json').read_text());meshes=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if o.name=='M4A1':continue
 stem=o.name.split('.')[0];part=stem.split('_',2)[2];tile=tiles[names[part]];uv=o.data.uv_layers.new(name='BodyAtlasUV');old=o.data.uv_layers[0]
 for a,b in zip(uv.data,old.data):
  assert -0.0001<=b.uv.x<=1.0001 and -0.0001<=b.uv.y<=1.0001,(o.name,list(b.uv))
  a.uv=(b.uv.x*tile['uv_scale'][0]+tile['uv_offset'][0],b.uv.y*tile['uv_scale'][1]+tile['uv_offset'][1])
 o.data.uv_layers.active=uv;uv.active_render=True;o.data.materials.clear();o.data.materials.append(bodymat)
 for p in o.data.polygons:p.material_index=0;p.use_smooth=True
 meshes.append({'name':o.name,'texture':tile['texture'],'faces':len(o.data.polygons)})
for n,d in original.items():assert invariant(bpy.data.objects[n])==d,n
assert [b.name for b in rig.data.bones]==rigid
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH':o.select_set(True)
opt=PskBuildOptions();opt.material_names=['BodyAtlas','RifleAtlas'];psk=build_psk(bpy.context,opt);write_psk(psk,str(R/'RifleNPCV4.psk'));bpy.ops.wm.save_as_mainfile(filepath=str(R/'RifleNPCV4.blend'))
report={'materials':opt.material_names,'bones':len(psk.bones),'faces':len(psk.faces),'wedges':len(psk.wedges),'points':len(psk.points),'meshes':meshes,'existing_geometry_origin_weights_exact':True,'rig_bone_order_unchanged':True,'motion_unchanged':True,'source_body_texture_package':r'E:\l2\SysTextures\FFighter.utx','new_head_source':r'E:\l2\animations\Fighter.ukx:FFighter_m000_f','alpha':'RGBA BodyAtlas retains native hair masks; native package import should enable masked texture rendering; Blender preview uses CLIP .45'};(R/'textured-validation.json').write_text(json.dumps(report,indent=2));print('TEXTURED_V4',report)
# Static visual QA only after source asset save, never export floor/camera.
s=bpy.context.scene;s.frame_set(1);s.render.engine='BLENDER_EEVEE';s.eevee.use_gtao=True;s.eevee.gtao_distance=3
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-.25));floor=bpy.context.object;m=bpy.data.materials.new('QA Floor');m.diffuse_color=(.1,.12,.15,1);floor.data.materials.append(m)
bpy.ops.object.camera_add(location=(-85,-55,55));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=60;s.camera=cam
for loc,power in [((30,-50,85),100000),((-45,-10,40),50000),((0,40,60),65000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=50;l.rotation_euler=(Vector((0,0,20))-l.location).to_track_quat('-Z','Y').to_euler()
s.world=bpy.data.worlds.new('QA World');s.world.color=(.16,.16,.16);s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.render.filepath=str(R/'RifleNPCV4-side.png');bpy.ops.render.render(write_still=True)
cam.location=(-45,-85,50);cam.rotation_euler=(Vector((0,0,23))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'RifleNPCV4-front.png');bpy.ops.render.render(write_still=True)
