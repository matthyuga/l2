"""Author the weighted mount and real L2 reference riders in an isolated Blender file."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parent;LAB=R.parents[2];CAT=LAB/'research/model-catalog'
sys.path.insert(0,str(LAB/'research/amber-l2/tools/psk_addon'))
import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import import_psa,PsaImportOptions
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
bpy.ops.wm.read_factory_settings(use_empty=True)
PSK=R/'native-source/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.psk'
PSA=R/'native-source/LineageMonsters3/MeshAnimation/antaras_ex_a_anim.psa'
bpy.ops.import_scene.psk(filepath=str(PSK))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.name='Behemoth_Rig'
body=[o for o in bpy.data.objects if o.type=='MESH'];native=set(bpy.data.objects)
texture_dir=R/'native-source/LineageMonstersTex3/Texture'
for o in body:
 for i,m in enumerate(o.data.materials):
  m.name='BeastHide'+str(i);m.use_nodes=True
  img=bpy.data.images.load(str(texture_dir/('antaras_ex_a_t0'+str(i)+'_sp.tga')),check_existing=True)
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
  bsdf=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.87

bpy.ops.import_scene.gltf(filepath=str(CAT/'exports/l2lab-behemoth-two-riders/behemoth-two-riders.gltf'))
kit=set(bpy.data.objects)-native
gear=[o for o in kit if o.type=='MESH' and not o.name.startswith('antaras')]
for o in gear:
 world=Matrix.Scale(25,4)@o.matrix_world;o.parent=None;o.matrix_world=world
for o in list(kit):
 if o not in gear:bpy.data.objects.remove(o,do_unlink=True)
for o in gear:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

trunk=['Bip01 Pelvis','Bip01 Spine','Bip01 Spine1','bip01 spine2','Bip01 Neck']
tree=KDTree(sum(len(o.data.vertices) for o in body));samples=[]
for o in body:
 for v in o.data.vertices:
  weights={o.vertex_groups[w.group].name:w.weight for w in v.groups if o.vertex_groups[w.group].name in trunk}
  index=len(samples);samples.append(weights);tree.insert(o.matrix_world@v.co,index)
tree.balance();spine='Bip01 Spine1'
rigid=[];flex=[]
for o in gear:
 o.vertex_groups.clear()
 flexible=any(s in o.name.lower() for s in ['cincha','correa','pechera','rienda','tirante'])
 for v in o.data.vertices:
  if flexible:
   _,i,_=tree.find(v.co);weights=dict(samples[i])
   if not weights:weights={('Bip01 Pelvis' if v.co.y>30 else spine):1.}
  else:weights={spine:1.}
  total=sum(weights.values())
  for n,w in weights.items():
   vg=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);vg.add([v.index],w/total,'REPLACE')
 o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted()
 mod=o.modifiers.new('Behemoth skin binding','ARMATURE');mod.object=rig
 (flex if flexible else rigid).append(o.name)

reader=PsaReader(str(PSA));clips=list(reader.sequences)
opt=PsaImportOptions();opt.sequence_names=clips;opt.should_use_fake_user=True
result=import_psa(bpy.context,reader,rig,opt)
rig.animation_data_create();rig.animation_data.action=None;bpy.context.view_layer.update()

# Export native mesh with exactly the original 98 bones and ordered materials.
bpy.ops.object.select_all(action='DESELECT')
for o in body+gear:o.select_set(True)
bpy.context.view_layer.objects.active=body[0]
materials=[]
for o in body+gear:
 for m in o.data.materials:
  if m.name not in materials:materials.append(m.name)
options=PskBuildOptions();options.material_names=materials
write_psk(build_psk(bpy.context,options),str(R/'BehemothTwoRiders.psk'))

anchors={}
for role,position in [('driver',(0,-6.75,101.75)),('gunner',(0,38,90.75))]:
 matrix=rig.data.bones[spine].matrix_local
 anchors[role]={'bone':spine,'nativeWorld':position,'boneLocal':list(matrix.inverted()@Vector(position))}
(R/'rider-anchors.json').write_text(json.dumps(anchors,indent=2),encoding='utf8')

# Native units -> the same visual size used by the first editor prototype.
root=bpy.data.objects.new('BehemothTwoRiders',None);bpy.context.collection.objects.link(root)
rig.parent=root;root.scale=(.04,.04,.04)
rig.animation_data.action=bpy.data.actions['Walk'];bpy.context.scene.render.fps=30
dest=CAT/'exports/l2lab-behemoth-two-riders-animated';dest.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for o in [root,rig]+body+gear:o.select_set(True)
clipdir=R/'clip-exports';clipdir.mkdir(exist_ok=True);clipfiles=[]
for clip in clips:
 rig.animation_data.action=bpy.data.actions[clip];bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=int(bpy.data.actions[clip].frame_range[1]);bpy.context.scene.frame_set(1)
 file=clipdir/(clip+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_animations=True,export_anim_single_armature=False,export_nla_strips=False,export_nla_strips_merged_animation_name=clip,export_frame_range=True,export_skins=True,export_yup=True)
 clipfiles.append((clip,file))
sys.path.insert(0,str(R));from merge_animations import merge
merge(clipfiles,dest/'behemoth-animated.glb')

# Append real human-female L2 reference meshes, not substitute mannequins.
human_psa=LAB/'research/amber-l2/exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa'
human_source=LAB/'research/dust2-animation-study/retarget/Dust2_BombWork_FFighter.blend'
riders=[]
for role in ['driver','gunner']:
 with bpy.data.libraries.load(str(human_source),link=False) as (src,target):target.objects=list(src.objects)
 imported=[o for o in target.objects if o and o.type in ['MESH','ARMATURE']]
 for o in imported:bpy.context.collection.objects.link(o)
 character=next(o for o in imported if o.type=='ARMATURE');character.name='Rider_'+role
 character.animation_data_clear();character.animation_data_create()
 for o in imported:
  if o.type=='MESH':o.name=role+'_'+o.name
 hreader=PsaReader(str(human_psa));selected='Strider_FFighter' if role=='driver' else 'Wait_Bow_FFighter'
 hop=PsaImportOptions();hop.sequence_names=[selected];hop.should_use_fake_user=True;hop.action_name_prefix=role+'_'
 import_psa(bpy.context,hreader,character,hop);character.animation_data.action=bpy.data.actions[role+'_'+selected]
 character.parent=root;character.location=(0,0,0);character.rotation_euler=(0,0,0);character.scale=(1,1,1)
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 bone_delta=rig.pose.bones[spine].matrix@rig.data.bones[spine].matrix_local.inverted()
 anchor_native=rig.pose.bones[spine].matrix@Vector(anchors[role]['boneLocal'])
 turn=bone_delta.to_quaternion()
 character.rotation_mode='QUATERNION';character.rotation_quaternion=turn
 if role=='driver':
  pelvis=character.pose.bones.get('Bip01_Pelvis') or character.pose.bones.get('Bip01 Pelvis')
  if not pelvis:raise ValueError('Human pelvis bone not found')
  local=pelvis.matrix.translation;character.location=anchor_native-turn@local
 else:
  points=[]
  deps=bpy.context.evaluated_depsgraph_get()
  for o in imported:
   if o.type=='MESH':
    evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh()
    points.extend(root.matrix_world.inverted()@evaluated.matrix_world@v.co for v in mesh.vertices)
    evaluated.to_mesh_clear()
  # Evaluate feet in character local space so the mount's tilt is not counted twice.
  feet=min(p.z for p in points);character.location=anchor_native-turn@Vector((0,0,feet))
 bpy.context.view_layer.update()
 world=character.matrix_world.copy()
 parent_world=rig.matrix_world@rig.pose.bones[spine].matrix@Matrix.Translation((0,rig.data.bones[spine].length,0))
 character.parent=rig;character.parent_type='BONE';character.parent_bone=spine
 character.matrix_parent_inverse=parent_world.inverted();character.matrix_basis=world
 riders.append({'role':role,'rig':character.name,'pose':selected,'nativeLocation':list(character.location)})

rig.animation_data.action=bpy.data.actions['Walk'];bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=51
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
for img in bpy.data.images:
 if img.source=='FILE':
  try:img.pack()
  except Exception:pass
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Behemoth-Two-Riders.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type in ['MESH','ARMATURE','EMPTY']:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(dest/'behemoth-riders-preview.glb'),export_format='GLB',use_selection=True,export_animations=True,export_anim_single_armature=False,export_nla_strips=False,export_frame_range=True,export_skins=True)

report={'nativeBones':len(rig.data.bones),'clips':clips,'importWarnings':result.warnings,'rigidParts':rigid,'flexibleParts':flex,'riders':riders,'nativeMaterials':materials,'anchors':anchors,'nativeClientVerified':False,'twoClientCombatVerified':False}
(R/'animation-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('BEHEMOTH_ANIMATED_BUILD_READY',len(gear),len(clips))
