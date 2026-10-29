import bpy
import json
import math
import pathlib
import sys
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
import bmesh

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/psk_addon'))
import io_scene_psk_psa
io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'exports/amber-imported.blend'))
source_rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name in {'Body.baked', 'Outfit 00.baked'}]
for obj in list(bpy.data.objects):
    if obj not in meshes and obj != source_rig:
        bpy.data.objects.remove(obj, do_unlink=True)
with bpy.data.libraries.load(str(ROOT / 'exports/fighter-reference.blend'), link=False) as (source, target):
    target.objects = list(source.objects)
reference = next(o for o in target.objects if o.type == 'ARMATURE')
bpy.context.collection.objects.link(reference)
reference.name = 'L2_FFemale_Rig'

human = json.loads((ROOT / 'reports/amber-vrm-input.json').read_text())['human_bones']
destinations = {
    'hips': 'Bip01_Pelvis', 'spine': 'bip01_spine', 'chest': 'Bip01_Spine1',
    'upperChest': 'bip01_spine2', 'neck': 'Bip01_Neck', 'head': 'Bip01_head',
    'leftShoulder': 'Bip01_L_Clavicle', 'leftUpperArm': 'Bip01_L_UpperArm',
    'leftLowerArm': 'Bip01_L_Forearm', 'leftHand': 'Bip01_L_Hand',
    'rightShoulder': 'Bip01_R_Clavicle', 'rightUpperArm': 'Bip01_R_UpperArm',
    'rightLowerArm': 'Bip01_R_Forearm', 'rightHand': 'Bip01_R_Hand',
    'leftUpperLeg': 'Bip01_L_Thigh', 'leftLowerLeg': 'Bip01_L_Calf',
    'leftFoot': 'bip01_l_foot', 'leftToes': 'Bip01_L_Toe0',
    'rightUpperLeg': 'Bip01_R_Thigh', 'rightLowerLeg': 'Bip01_R_Calf',
    'rightFoot': 'bip01_r_foot', 'rightToes': 'Bip01_R_Toe0',
}
source_names = {h['bone']: h['name'] for h in human}
mapping = {source_names[k]: v for k, v in destinations.items()}
rotation = Matrix.Rotation(math.pi, 4, 'Z')
source_points = {k: rotation @ source_rig.matrix_world @ source_rig.data.bones[v].head_local for k, v in source_names.items()}
target_points = {k: reference.matrix_world @ reference.data.bones[v].head_local for k, v in destinations.items()}
scale = target_points['head'].z / source_points['head'].z
next_joint = {'hips': 'spine', 'spine': 'chest', 'chest': 'upperChest', 'upperChest': 'neck',
              'neck': 'head', 'leftShoulder': 'leftUpperArm', 'leftUpperArm': 'leftLowerArm',
              'leftLowerArm': 'leftHand', 'rightShoulder': 'rightUpperArm',
              'rightUpperArm': 'rightLowerArm', 'rightLowerArm': 'rightHand',
              'leftUpperLeg': 'leftLowerLeg', 'leftLowerLeg': 'leftFoot', 'leftFoot': 'leftToes',
              'rightUpperLeg': 'rightLowerLeg', 'rightLowerLeg': 'rightFoot', 'rightFoot': 'rightToes'}
transforms = {}
for key, source_name in source_names.items():
    turn = Matrix.Identity(3)
    if key in next_joint:
        a = source_points[next_joint[key]] - source_points[key]
        b = target_points[next_joint[key]] - target_points[key]
        if a.length > 1e-6 and b.length > 1e-6:
            turn = a.rotation_difference(b).to_matrix()
    transforms[source_name] = (target_points[key], source_points[key], turn)

resolved = {}
for bone in source_rig.data.bones:
    ancestor = bone
    while ancestor and ancestor.name not in mapping:
        ancestor = ancestor.parent
    resolved[bone.name] = ancestor.name if ancestor else source_names['hips']

def merged_weights(obj, vertex):
    merged = {}
    for group in vertex.groups:
        name = resolved.get(obj.vertex_groups[group.group].name, source_names['hips'])
        merged[name] = merged.get(name, 0) + group.weight
    if not merged:
        merged = {source_names['hips']: 1.0}
    # The old client expects a small number of influences per vertex.
    merged = dict(sorted(merged.items(), key=lambda x:x[1], reverse=True)[:4])
    total = sum(merged.values())
    return {name:weight/total for name,weight in merged.items()}

body = next(obj for obj in meshes if obj.name=='Body.baked')
body_weights = [merged_weights(body, v) for v in body.data.vertices]
body_tree = KDTree(len(body.data.vertices))
for v in body.data.vertices:
    body_tree.insert(rotation @ body.matrix_world @ v.co, v.index)
body_tree.balance()
# Use the same deformation field for the body and the close-fitting clothes.
# Preserve the head/hair/accessory bindings, which should follow the head rigidly.
outfit = next(obj for obj in meshes if obj.name=='Outfit 00.baked')
head_vertices = {i for p in outfit.data.polygons if p.material_index in (0,1) for i in p.vertices}
outfit_weights=[]
for v in outfit.data.vertices:
    if v.index in head_vertices:
        outfit_weights.append(merged_weights(outfit,v))
        continue
    point=rotation @ outfit.matrix_world @ v.co
    merged={}
    neighbors=body_tree.find_n(point,4)
    for _,index,distance in neighbors:
        factor=1/max(distance,0.00005)**2
        for name,weight in body_weights[index].items():
            merged[name]=merged.get(name,0)+weight*factor
    merged=dict(sorted(merged.items(),key=lambda x:x[1],reverse=True)[:4])
    total=sum(merged.values())
    outfit_weights.append({name:weight/total for name,weight in merged.items()})

report = {'source_bones': len(source_rig.data.bones), 'target_bones': len(reference.data.bones),
          'scale': scale, 'mapping': mapping, 'meshes': []}
report['visual_revision']=3
report['clothing_weights']='nearest body surface, four neighbors; head accessories preserve original weights'
texture_dir = ROOT / 'exports/textures'
texture_dir.mkdir(exist_ok=True)
for obj in meshes:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.data.shape_keys:
        bpy.ops.object.shape_key_remove(all=True)
    prepared_weights=body_weights if obj==body else outfit_weights
    weights = []
    for vertex in obj.data.vertices:
        merged = prepared_weights[vertex.index]
        world = rotation @ obj.matrix_world @ vertex.co
        position = Vector((0,0,0))
        for name, weight in merged.items():
            target_pos, source_pos, turn = transforms[name]
            position += (target_pos + turn @ ((world-source_pos)*scale))*weight
        vertex.co = position
        weights.append(merged)
    obj.parent = None
    obj.matrix_world = Matrix.Identity(4)
    obj.vertex_groups.clear()
    groups = {name: obj.vertex_groups.new(name=mapping[name]) for name in mapping}
    for index, merged in enumerate(weights):
        for name, weight in merged.items():
            groups[name].add([index], weight, 'REPLACE')
    hidden_faces=0
    if obj==body:
        # Remove only internal torso and lower-leg skin covered by the fixed outfit.
        covered={source_names[k] for k in ('hips','spine','chest','upperChest','leftLowerLeg','rightLowerLeg','leftFoot','rightFoot','leftToes','rightToes')}
        neck_limit=target_points['neck'].z-0.8
        hidden_vertices={i for i,w in enumerate(weights) if max(w,key=w.get) in covered and obj.data.vertices[i].co.z<neck_limit}
        bm=bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table()
        faces=[f for f in bm.faces if all(v.index in hidden_vertices for v in f.verts)]
        hidden_faces=len(faces)
        bmesh.ops.delete(bm,geom=faces,context='FACES')
        bm.to_mesh(obj.data); bm.free(); obj.data.update()
    obj.modifiers.clear()
    armature = obj.modifiers.new('L2 Armature', 'ARMATURE')
    armature.object = reference
    obj.parent = reference
    before = len(obj.data.polygons)
    decimate = obj.modifiers.new('NPC polygon reduction', 'DECIMATE')
    decimate.ratio = 0.85
    bpy.ops.object.modifier_move_up(modifier=decimate.name)
    bpy.ops.object.modifier_apply(modifier=decimate.name)

    old_materials = list(obj.data.materials)
    cols = 4 if len(old_materials) <= 16 else 5
    rows = math.ceil(len(old_materials)/cols)
    size = 2048
    cell_width, cell_height = size//cols, size//rows
    padding = 8
    atlas_pixels = np.zeros((size,size,4),dtype=np.float32)
    base_name = 'AmberBody' if obj.name.startswith('Body') else 'AmberOutfit'
    for index, material in enumerate(old_materials):
        shader = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        color = np.array(shader.inputs['Base Color'].default_value[:], dtype=np.float32) if shader else np.ones(4,dtype=np.float32)
        alpha = shader.inputs['Alpha'].default_value if shader else 1.0
        color[3] *= alpha
        links = list(shader.inputs['Base Color'].links) if shader else []
        texture = next((n.image for n in material.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
        if links and links[0].from_node.type == 'TEX_IMAGE':
            texture = links[0].from_node.image
        if texture:
            width,height = texture.size
            pixels = np.empty(width*height*4,dtype=np.float32)
            texture.pixels.foreach_get(pixels)
            pixels = pixels.reshape(height,width,4)
            # Extend the border pixels through the gutter. UV and pixel transforms match.
            xs = np.clip(((np.arange(cell_width)-padding)*width/(cell_width-2*padding)).astype(int),0,width-1)
            ys = np.clip(((np.arange(cell_height)-padding)*height/(cell_height-2*padding)).astype(int),0,height-1)
            sampled = pixels[ys[:,None],xs[None,:],:].copy()
            # glTF's material factor is already folded into the imported nodes only when linked.
            if not links:
                sampled[:,:,:3] *= color[:3]
            sampled[:,:,3] *= color[3]
        else:
            sampled = np.broadcast_to(color,(cell_height,cell_width,4)).copy()
        x0,y0 = (index%cols)*cell_width,(index//cols)*cell_height
        atlas_pixels[y0:y0+cell_height,x0:x0+cell_width,:] = sampled
    uv_layer = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        column,row = polygon.material_index%cols,polygon.material_index//cols
        for loop_index in polygon.loop_indices:
            uv = uv_layer.data[loop_index].uv.copy()
            u,v = min(max(uv.x,0),1), min(max(uv.y,0),1)
            uv_layer.data[loop_index].uv = ((column*cell_width+padding+u*(cell_width-2*padding))/size,
                                           (row*cell_height+padding+v*(cell_height-2*padding))/size)
        polygon.material_index = 0
    atlas = bpy.data.images.new(base_name,width=size,height=size,alpha=True)
    atlas.pixels.foreach_set(atlas_pixels.ravel())
    atlas.filepath_raw = str(texture_dir / (base_name+'.png'))
    atlas.file_format = 'PNG'
    atlas.save()
    atlas.filepath_raw = str(texture_dir / (base_name+'.tga'))
    atlas.file_format = 'TARGA'
    atlas.save()
    material = bpy.data.materials.new(base_name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    node = material.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = atlas
    material.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    material.node_tree.links.new(node.outputs['Alpha'],shader.inputs['Alpha'])
    shader.inputs['Roughness'].default_value = 0.8
    material.blend_method = 'CLIP'
    material.use_backface_culling = False
    obj.data.materials.clear()
    obj.data.materials.append(material)
    obj.name = base_name
    report['meshes'].append({'name':base_name,'source_faces':before,'faces':len(obj.data.polygons),
                             'vertices':len(obj.data.vertices),'source_materials':len(old_materials),'hidden_body_faces_removed':hidden_faces})
bpy.data.objects.remove(source_rig,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
from io_scene_psk_psa.psk.builder import build_psk, PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
options = PskBuildOptions()
options.material_names = ['AmberBody','AmberOutfit']
write_psk(build_psk(bpy.context, options), str(ROOT / 'exports/AmberNPC.psk'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'exports/amber-l2-rigged.blend'))
(ROOT / 'reports/amber-build.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('AMBER_L2_BUILD_COMPLETE',json.dumps(report['meshes']))
