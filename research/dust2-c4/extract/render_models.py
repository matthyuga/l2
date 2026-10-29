import bpy, math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ['w_c4','p_c4']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.obj(filepath=str(root/name/(name+'.obj')),axis_forward='Y',axis_up='Z')
    mesh=[o for o in bpy.context.scene.objects if o.type=='MESH']
    coords=[o.matrix_world@Vector(c) for o in mesh for c in o.bound_box]
    lo=Vector([min(c[i] for c in coords) for i in range(3)])
    hi=Vector([max(c[i] for c in coords) for i in range(3)])
    center=(lo+hi)/2;span=max(hi-lo)
    world=bpy.context.scene.world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1)
    for sign in [-1,1]:
        for direction, label in [(Vector((sign,sign,1)),'top'),(Vector((sign,-sign,-1)),'bottom')]:
            bpy.ops.object.camera_add(location=center+direction.normalized()*span*2.6)
            camera=bpy.context.object
            camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            camera.data.type='ORTHO';camera.data.ortho_scale=span*1.4
            bpy.context.scene.camera=camera
            lights=[]
            for d,power in [(Vector((0,0,1)),700),(Vector((0,0,-1)),500)]:
                bpy.ops.object.light_add(type='AREA',location=center+d*span*1.7)
                light=bpy.context.object;light.data.energy=power;light.data.size=span*2
                light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler();lights.append(light)
            scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE'
            scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100
            scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
            scene.render.image_settings.file_format='PNG'
            scene.render.filepath=str(root/name/f'preview_{sign}_{label}.png')
            bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(camera,do_unlink=True)
            for light in lights:bpy.data.objects.remove(light,do_unlink=True)
