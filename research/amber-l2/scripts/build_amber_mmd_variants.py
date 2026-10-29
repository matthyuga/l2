"""Retarget both downloaded PMX references to the established L2 female rig.
Preserve original UVs, base texture resolution, material slots and triangle count.
"""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'reference-models/amber-web-2026-10-23'
OUT=ROOT/'exports/mmd-variants-20261023';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/psk_addon'))
sys.modules.setdefault('bpy_types',bpy.types) # legacy exporter import, Blender5 compatibility
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
# PMX left/right are anatomical. X remains X; Y-up is converted to Z-up,
# and PMX front (-Z) becomes Blender front (-Y). Reflection flips winding.
def convert(v):return Vector((v[0],v[2],v[1]))
mapping={13:'Bip01_Pelvis',4:'Bip01_Pelvis',11:'bip01_spine',12:'bip01_spine2',14:'Bip01_Neck',15:'Bip01_head',
 17:'Bip01_R_Clavicle',19:'Bip01_R_UpperArm',24:'Bip01_R_Forearm',31:'Bip01_R_Hand',
 35:'Bip01_L_Clavicle',37:'Bip01_L_UpperArm',42:'Bip01_L_Forearm',49:'Bip01_L_Hand',
 58:'Bip01_R_Thigh',59:'Bip01_R_Calf',60:'bip01_r_foot',66:'Bip01_R_Toe0',
 62:'Bip01_L_Thigh',63:'Bip01_L_Calf',64:'bip01_l_foot',67:'Bip01_L_Toe0',
 68:'Bip01_R_Thigh',69:'Bip01_R_Calf',70:'bip01_r_foot',71:'Bip01_R_Toe0',
 72:'Bip01_L_Thigh',73:'Bip01_L_Calf',74:'bip01_l_foot',75:'Bip01_L_Toe0',
 85:'Bip01_L_Finger0',90:'Bip01_L_Finger01',86:'Bip01_L_Finger1',93:'Bip01_L_Finger11',
 105:'Bip01_R_Finger0',110:'Bip01_R_Finger01',106:'Bip01_R_Finger1',113:'Bip01_R_Finger11'}
next_joint={13:11,4:11,11:12,12:14,14:15,17:19,19:24,24:31,35:37,37:42,42:49,
 58:59,59:60,60:66,62:63,63:64,64:67,68:69,69:70,70:71,72:73,73:74,74:75,
 85:90,86:93,105:110,106:113}
# Additional helper finger bones inherit their mapped nearest ancestor.
slot_names=['EyeWhite','Face','Eyes','Skin','Hair','Outfit','Accessory','Expression']
all_reports=[]
for label in ['v10','v14']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 report=json.loads((BASE/(label+'-analysis.json')).read_text(encoding='utf-8'))
 geo=json.loads((BASE/(label+'-geometry.json')).read_text())
 with bpy.data.libraries.load(str(ROOT/'exports/fighter-reference.blend'),link=False) as (src,dst):dst.objects=list(src.objects)
 rig=next(o for o in dst.objects if o.type=='ARMATURE');bpy.context.collection.objects.link(rig);rig.name='L2_FFemale_Rig'
 expected=(ROOT/'reports/expected-bones.txt').read_text().splitlines();assert [b.name for b in rig.data.bones]==expected
 bones=report['bones'];source=[convert(b['position']) for b in bones]
 assert source[49].x>0 and rig.data.bones['Bip01_L_Hand'].head_local.x>0,'anatomical left/right preserved'
 scale=rig.data.bones['Bip01_head'].head_local.z/source[15].z
 transforms={}
 for index,name in mapping.items():
  turn=Matrix.Identity(3)
  if index in next_joint:
   other=next_joint[index];a=source[other]-source[index];b=rig.data.bones[mapping[other]].head_local-rig.data.bones[name].head_local
   if a.length>1e-6 and b.length>1e-6:turn=a.rotation_difference(b).to_matrix()
  transforms[index]=(rig.data.bones[name].head_local.copy(),source[index],turn)
 resolved={}
 for i in range(len(bones)):
  visited=set();at=i
  while at not in mapping:
   assert at not in visited;visited.add(at);at=bones[at]['parent']
   if at<0:at=13;break
  resolved[i]=at
 vertices=[];vertex_weights=[]
 for co,weights in zip(geo['vertices'],geo['weights']):
  merged={}
  for bone,weight in weights:
   if weight>1e-6 and bone>=0:
    key=resolved[bone];merged[key]=merged.get(key,0)+weight
  assert merged,'every source vertex is weighted'
  merged=dict(sorted(merged.items(),key=lambda x:x[1],reverse=True)[:4]);total=sum(merged.values());merged={k:v/total for k,v in merged.items()}
  point=convert(co);new=Vector((0,0,0));dest_weights={}
  for index,weight in merged.items():
   target,origin,turn=transforms[index];new+=(target+turn@((point-origin)*scale))*weight
   name=mapping[index];dest_weights[name]=dest_weights.get(name,0)+weight
  vertices.append(new);vertex_weights.append(dest_weights)
 indices=geo['indices'];faces=[(indices[i],indices[i+2],indices[i+1]) for i in range(0,len(indices),3)]
 mesh=bpy.data.meshes.new('AmberNPC');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('AmberNPC',mesh);bpy.context.collection.objects.link(obj)
 uv=mesh.uv_layers.new(name='UVMap')
 for p in mesh.polygons:
  p.use_smooth=True
  for loop in p.loop_indices:
   u,v=geo['uv'][mesh.loops[loop].vertex_index];uv.data[loop].uv=(u,1-v)
 parent=Path(report['path']).parent;texture_names=['FaceTex','HairTex','OutfitTex','SphereTex','ToonTex','ExpressionTex']
 textures=[]
 for t,n in zip(report['textures'],texture_names):
  image=bpy.data.images.load(str(parent/t['name'].replace('\\','/')),check_existing=True);textures.append(image)
 start=0;material_manifest=[]
 for i,m in enumerate(report['materials']):
  # Version1.0 has Outfit before Hair; choose by semantic source name.
  semantic={'\u773c\u767d':'EyeWhite','\u8138':'Face','\u773c\u775b':'Eyes','\u76ae\u80a4':'Skin','\u5934\u53d1':'Hair','\u8863\u670d':'Outfit','\u5934\u9970':'Accessory','\u8868\u60c5':'Expression'}[m['name']]
  mat=bpy.data.materials.new(semantic);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');emit=nodes.new('ShaderNodeEmission');tex=nodes.new('ShaderNodeTexImage');tex.image=textures[m['texture']]
  alpha=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader')
  for a,b in [(tex.outputs['Color'],emit.inputs['Color']),(tex.outputs['Alpha'],mix.inputs[0]),(alpha.outputs[0],mix.inputs[1]),(emit.outputs[0],mix.inputs[2]),(mix.outputs[0],out.inputs['Surface'])]:mat.node_tree.links.new(a,b)
  mesh.materials.append(mat)
  for p in mesh.polygons[start:start+m['index_count']//3]:p.material_index=i
  start+=m['index_count']//3
  material_manifest.append(dict(slot=i,name=semantic,texture=texture_names[m['texture']],triangles=m['index_count']//3))
 groups={n:obj.vertex_groups.new(name=n) for n in set(mapping.values())}
 for index,weights in enumerate(vertex_weights):
  assert abs(sum(weights.values())-1)<1e-5 and len(weights)<=4
  for name,weight in weights.items():groups[name].add([index],weight,'REPLACE')
 obj.parent=rig;modifier=obj.modifiers.new('L2 Armature','ARMATURE');modifier.object=rig
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 options=PskBuildOptions();options.material_names=[m['name'] for m in material_manifest]
 psk=build_psk(bpy.context,options);assert len(psk.bones)==76;assert len(psk.points)==report['vertices'];assert len(psk.faces)==report['triangles']
 target=OUT/label;target.mkdir(exist_ok=True);write_psk(psk,str(target/'AmberNPC.psk'))
 for image in textures:image.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(target/'amber-mmd-l2-rigged.blend'))
 entry=dict(variant=label,package='AmberMMD10' if label=='v10' else 'AmberMMD14',vertices=len(psk.points),triangles=len(psk.faces),bones=76,materials=material_manifest,scale=scale,all_weights_normalized=True,max_influences=max(map(len,vertex_weights)),uv_preserved=True,anatomical_sides_preserved=True,source_pmx_sha256=report['sha256'],source_mapping={str(k):v for k,v in mapping.items()},bounds=[[min(v[i] for v in vertices),max(v[i] for v in vertices)] for i in range(3)])
 (target/'build.json').write_text(json.dumps(entry,indent=2));all_reports.append(entry)
 print('MMD_VARIANT_BUILT',label,len(psk.points),len(psk.faces),'76 bones; original UV and material slots preserved')
(OUT/'build.json').write_text(json.dumps(all_reports,indent=2))
