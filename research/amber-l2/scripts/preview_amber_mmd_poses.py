import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/mmd-variants-20261023'
sys.path.insert(0,str(ROOT/'tools/psk_addon'));sys.modules.setdefault('bpy_types',bpy.types)
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import ImportBone,_calculate_fcurve_data
reader=PsaReader(str(ROOT/'exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa'))
results=[]
for label in ['v10','v14']:
 bpy.ops.wm.open_mainfile(filepath=str(OUT/label/'amber-mmd-l2-rigged.blend'));rig=bpy.data.objects['L2_FFemale_Rig'];obj=bpy.data.objects['AmberNPC'];rig.data.pose_position='POSE'
 imports=[];byname={}
 for bone in reader.bones:
  name=bone.name.decode('windows-1252');b=rig.data.bones[name];item=ImportBone(bone);item.armature_bone=b;item.pose_bone=rig.pose.bones[name]
  assert b.get('orig_quat') is not None,'original importer coordinate metadata required'
  item.orig_quat=Quaternion(b['orig_quat']);item.orig_loc=Vector(b['orig_loc']);item.post_quat=Quaternion(b['post_quat']);imports.append(item);byname[name]=item
 for item in imports:item.parent=byname.get(item.armature_bone.parent.name) if item.armature_bone.parent else None
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=600;scene.render.resolution_y=760;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('PreviewWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.07,.08,.10,1)
 scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.image_settings.file_format='PNG'
 bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';scene.camera=camera
 for short,name,fraction in [('idle','Wait_Bow_FFighter',0),('walk','Walk_Bow_FFighter',.25),('shot','Atk01_Bow_FFighter',.5)]:
  matrix=reader.read_sequence_data_matrix(name);frame=min(len(matrix)-1,int(len(matrix)*fraction))
  for i,item in enumerate(imports):
   values=_calculate_fcurve_data(item,matrix[frame,i]);pb=item.pose_bone;pb.rotation_mode='QUATERNION';pb.rotation_quaternion=values[:4];pb.location=values[4:]
  bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();points=[evaluated.matrix_world@v.co for v in mesh.vertices]
  assert all(math.isfinite(x) for p in points for x in p),'nonfinite posed geometry'
  lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);assert 25<hi.z-lo.z<75 and max(hi-lo)<100,'pose exploded'
  evaluated.to_mesh_clear();center=(lo+hi)/2;height=hi.z-lo.z
  camera.location=center+Vector((height*.25,-height*2.8,height*.08));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=height*1.12
  scene.render.filepath=str(OUT/label/('preview-'+short+'.png'));bpy.ops.render.render(write_still=True)
  results.append(dict(variant=label,sequence=name,frame=frame,all_vertices_finite=True,bounds=[list(lo),list(hi)],source='Original exported FFighter PSA; Blender skinning preview, not an L2 screenshot'))
(OUT/'pose-verification.json').write_text(json.dumps(results,indent=2));print('PASS6 native animation pose previews; no missing bones or nonfinite/exploded geometry.')
