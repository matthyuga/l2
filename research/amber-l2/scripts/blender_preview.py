import bpy
import math
import pathlib
import sys
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parents[1]
rigged = '--rigged' in sys.argv
animated = '--animated' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(ROOT / ('exports/amber-l2-animated.blend' if animated else ('exports/amber-l2-rigged.blend' if rigged else 'exports/amber-imported.blend'))))
walk = '--walk' in sys.argv
if walk:
    bpy.data.objects['L2_FFemale_Rig'].animation_data.action=bpy.data.actions['Walk_Hand_FFighter']
    bpy.context.scene.frame_set(10)
if rigged:
    for name in ('AmberBody','AmberOutfit'):
        material = bpy.data.materials[name]
        nodes=material.node_tree.nodes
        texture=next(n for n in nodes if n.type=='TEX_IMAGE')
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        emission=nodes.new('ShaderNodeEmission')
        transparent=nodes.new('ShaderNodeBsdfTransparent')
        mix=nodes.new('ShaderNodeMixShader')
        material.node_tree.links.new(texture.outputs['Color'],emission.inputs['Color'])
        material.node_tree.links.new(texture.outputs['Alpha'],mix.inputs[0])
        material.node_tree.links.new(transparent.outputs[0],mix.inputs[1])
        material.node_tree.links.new(emission.outputs[0],mix.inputs[2])
        material.node_tree.links.new(mix.outputs[0],output.inputs[0])
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.name not in {'Body.baked', 'Outfit 00.baked', 'AmberBody', 'AmberOutfit'}:
        bpy.data.objects.remove(obj, do_unlink=True)
for obj in bpy.data.objects:
    obj.hide_render = False
    obj.hide_viewport = False
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
minimum = Vector(tuple(min(p[i] for p in points) for i in range(3)))
maximum = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (minimum + maximum)/2
height = maximum.z-minimum.z
bpy.ops.object.camera_add(location=center + Vector((0, (-2 if rigged else 2)*height, 0.1*height)))
camera = bpy.context.object
camera.rotation_euler = (center-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = (maximum.z-minimum.z)*1.15
bpy.context.scene.camera = camera
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.use_gtao = True
scene.eevee.taa_render_samples = 32
scene.world.color = (0.45,0.45,0.45)
for location, energy, size in [((1,-2,3),300,4),((-2,-1,2),180,3),((0,2,3),220,3)]:
    bpy.ops.object.light_add(type='AREA', location=center+Vector(location)*(height/1.7))
    light = bpy.context.object
    light.data.energy = energy*(height/1.7)**2
    light.data.size = size*height/1.7
    light.rotation_euler = (center-light.location).to_track_quat('-Z', 'Y').to_euler()
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.render.resolution_x = 900
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(ROOT / ('reports/amber-l2-walk-preview.png' if walk else ('reports/amber-l2-idle-preview.png' if animated else ('reports/amber-l2-preview.png' if rigged else 'reports/amber-source-preview.png'))))
bpy.ops.render.render(write_still=True)
