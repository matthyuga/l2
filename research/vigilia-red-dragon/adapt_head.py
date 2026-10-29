"""Adapt the user's original RedDragon.fbx to Vigilia without rebuilding its head."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXP=ROOT/'research/model-catalog/exports/vigilia-red-dragon';EXP.mkdir(parents=True,exist_ok=True)
SHIP=ROOT/'research/vigilia-clan-renovada2/Vigilia-renovada2.blend';SHIP_HASH=hashlib.sha256(SHIP.read_bytes()).hexdigest()
FBX=OUT/'source/source/RedDragon.fbx';FBX_HASH=hashlib.sha256(FBX.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(FBX));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rig.animation_data_clear();rig.data.pose_position='REST'
for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
allowed={rig.data.bones['head'].name,*[b.name for b in rig.data.bones['head'].children_recursive],*[f'neck{i}' for i in range(1,6)]}
# One source atlas serves skin, eyes and teeth; relink the supplied files explicitly.
material=bpy.data.materials.new('Red Dragon · original GadgetHamster');material.use_nodes=True;nodes=material.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');bsdf=nodes.new('ShaderNodeBsdfPrincipled');material.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface']);bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Roughness'].default_value=.68
for suffix,socket,space in [('Base_color','Base Color','sRGB'),('Specular_roughness','Roughness','Non-Color'),('Emission_color','Emission Color','sRGB'),('Normal_OpenGL',None,'Non-Color')]:
 image=bpy.data.images.load(str(OUT/'source/textures'/('redDragon_'+suffix+'.png')),check_existing=True);image.colorspace_settings.name=space;image.pack();node=nodes.new('ShaderNodeTexImage');node.image=image;node.label=suffix
 if suffix=='Normal_OpenGL':normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.75;material.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);material.node_tree.links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
 else:material.node_tree.links.new(node.outputs['Color'],bsdf.inputs[socket])
bsdf.inputs['Emission Strength'].default_value=.7
cap=bpy.data.materials.new('Union de cuello · corte cerrado');cap.diffuse_color=(.055,.018,.012,1);cap.use_nodes=True;cap.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.055,.018,.012,1);cap.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
cut_y=3.75;origin=Vector((0,cut_y,3.38));pitch=math.radians(29);scale=1.85
# Source forward +Y -> ship +X. Pitch is applied before the orientation change.
transform=Matrix.Translation(Vector((14.45,0,4.25)))@Matrix.Rotation(-math.pi/2,4,'Z')@Matrix.Rotation(pitch,4,'X')@Matrix.Scale(scale,4)@Matrix.Translation(-origin)
parts=[];stats=[]
for obj in list(bpy.data.objects):
 if obj.type!='MESH':continue
 source_count=len(obj.data.vertices);keep=set()
 for v in obj.data.vertices:
  weight=sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in allowed)
  if weight>=.25:keep.add(v.index)
 bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS')
 if not bm.verts:bm.free();bpy.data.objects.remove(obj,do_unlink=True);continue
 result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,cut_y,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False)
 boundary=[e for e in bm.edges if e.is_boundary and all(abs(v.co.y-cut_y)<.0001 for v in e.verts)]
 filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[]) if boundary else []
 for face in filled:face.material_index=1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
 for modifier in list(obj.modifiers):obj.modifiers.remove(modifier)
 obj.parent=None;obj.matrix_world=Matrix.Identity(4);obj.data.transform(transform);obj.data.materials.clear();obj.data.materials.append(material);obj.data.materials.append(cap)
 for polygon in obj.data.polygons:polygon.use_smooth=polygon.material_index==0
 obj.name='RedDragon · '+obj.name;parts.append(obj);stats.append({'name':obj.name,'sourceVertices':source_count,'retainedVertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'capFaces':len(filled)})
# Keep the adapted meshes alive while opening the ship via a temporary library.
bpy.data.objects.remove(rig,do_unlink=True)
head_lib=OUT/'RedDragon-head-adapted.blend';bpy.ops.wm.save_as_mainfile(filepath=str(head_lib));head_names=[o.name for o in parts]
bpy.ops.wm.open_mainfile(filepath=str(SHIP))
def signature(o):
 h=hashlib.sha256();h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
prefixes=('Cuello_acorazado','Cabeza_angular','Mandibula_dentada','Garganta_oscura','Orbita_hundida','Iris_draconico','Pupila_vertical','Ceja_acorazada','Mandibula_filigrana','Cuerno_anillado','Abanico_mejilla','Nervio_mejilla','Colmillo_superior','Diente_inferior','Narina_profunda','Narina_borde','Escama_cuello','Grabado_escama','Cresta_dorsal','Placa_frente')
old=[o for o in bpy.data.collections['VIG_00_Casco'].objects if o.name.startswith(prefixes)];removed=[o.name for o in old];preserved={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o not in old}
if len(old)<50:raise RuntimeError('Old head selection incomplete')
for o in old:bpy.data.objects.remove(o,do_unlink=True)
collection=bpy.data.collections.new('VIG_16_RedDragon');bpy.context.scene.collection.children.link(collection);parent=bpy.data.objects.new('VIG_16_RedDragon',None);collection.objects.link(parent)
with bpy.data.libraries.load(str(head_lib),link=False) as (data_from,data_to):data_to.objects=head_names
for obj in data_to.objects:
 if obj:collection.objects.link(obj);obj.parent=parent
assert all(signature(bpy.data.objects[n])==v for n,v in preserved.items())
assert hashlib.sha256(SHIP.read_bytes()).hexdigest()==SHIP_HASH
assert hashlib.sha256(FBX.read_bytes()).hexdigest()==FBX_HASH
bpy.context.scene['red_dragon_credit']='Red Dragon by GadgetHamster; character design by Alexander Ostrowski. CC BY 4.0. Head/neck isolated, posed and adapted to Vigilia.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-RedDragon.blend'))
print('MASTER_SAVED',stats,flush=True)
# Export a self-contained replacement hull and original-model head package.
col=bpy.data.collections['VIG_00_Casco'];hull_items=[o for o in col.objects if o.type in {'MESH','CURVE'}]
bpy.ops.object.select_all(action='DESELECT')
for obj in hull_items:obj.select_set(True)
bpy.context.view_layer.objects.active=hull_items[0];bpy.ops.object.convert(target='MESH')
bpy.context.view_layer.objects.active=hull_items[0];bpy.ops.object.join();bpy.context.object.name='VIG_00_Casco_Malla'
bpy.ops.object.select_all(action='DESELECT')
for col in [collection,bpy.data.collections['VIG_00_Casco']]:
 for obj in col.objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'red-dragon-head.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'red-dragon-head.gltf').read_text(encoding='utf-8'))
g['asset']['copyright']='Red Dragon by GadgetHamster; design by Alexander Ostrowski. CC BY 4.0. https://sketchfab.com/3d-models/red-dragon-77e89ab9b88a444cb51339c2ed3959a3. Modified: head and neck isolated, cut closed, static pose and scale adapted to Vigilia.'
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
(EXP/'red-dragon-head.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
report={'sourceFBXHash':FBX_HASH,'sourceShipHash':SHIP_HASH,'sourceCredit':'GadgetHamster; design Alexander Ostrowski','sourceURL':'https://sketchfab.com/3d-models/red-dragon-77e89ab9b88a444cb51339c2ed3959a3','license':'CC BY 4.0','parts':stats,'triangles':triangles,'retainedUVAndOriginalTextures':True,'cutPlaneSourceY':cut_y,'pitchDegrees':29,'scale':scale,'removedOldHeadParts':len(removed),'preservedShipMeshes':len(preserved),'otherShipGeometryUnchanged':True,'gameInstalled':False}
(OUT/'adaptation-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('ADAPTED',triangles,flush=True)
