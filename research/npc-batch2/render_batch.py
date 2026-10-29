"""Render representative, textured mesh thumbnails with the existing Blender installation."""
import bpy, math, pathlib, json, sys, traceback
from mathutils import Vector
OUT=pathlib.Path(r'E:\l2-local\research\model-catalog')
report=json.loads(pathlib.Path(next(a.split('=',1)[1] for a in sys.argv if a.startswith('--manifest='))).read_text(encoding='utf-8'))
only_sample='--sample' in sys.argv
only_key=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--only=')),None)
count=0
for m in report['models']:
    if m.get('status')!='ready':continue
    if only_key and m['key']!=only_key:continue
    target=OUT/m['thumbnail']
    if target.exists() and target.stat().st_mtime>=(OUT/m['gltf']).stat().st_mtime and '--overwrite' not in sys.argv:continue
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(OUT/m['gltf']))
        for o in bpy.context.scene.objects:
            if 'NativeTerrain' in o.name:o.hide_render=m.get('terrain_visible',True) is False
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        if not meshes:raise ValueError('No mesh objects')
        bpy.context.view_layer.update()
        points=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
        if m.get('view_bounds'):
            lo,hi=m['view_bounds'];points=[Vector((x,-z,y)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
        minimum=Vector([min(p[i] for p in points) for i in range(3)])
        maximum=Vector([max(p[i] for p in points) for i in range(3)])
        center=(minimum+maximum)/2; dimensions=maximum-minimum
        extent=max(dimensions);scale=max(extent,.01)
        direction=Vector(m.get('preview_camera_direction',(1,-2.8,.65))).normalized()
        bpy.ops.object.camera_add(location=center+direction*scale*3)
        camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'
        rotation=camera.rotation_euler.to_matrix().transposed()
        viewpoints=[rotation@(p-center) for p in points]
        width=max(p.x for p in viewpoints)-min(p.x for p in viewpoints)
        height=max(p.y for p in viewpoints)-min(p.y for p in viewpoints)
        camera.data.ortho_scale=max(height,width*420/384,.02)*1.18
        camera.data.clip_start=max(scale*.001,.0001);camera.data.clip_end=scale*20
        scene=bpy.context.scene;scene.camera=camera
        scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=16;scene.eevee.use_gtao=True
        scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
        scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.22,.27,1)
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
        for direction,energy in [((1,-3,4),450),((-3,-1,2),260),((1,3,3),380)]:
            bpy.ops.object.light_add(type='AREA',location=center+Vector(direction)*scale)
            light=bpy.context.object;light.data.energy=energy*scale*scale;light.data.size=scale*3
            light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
        scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
        scene.render.resolution_x=384;scene.render.resolution_y=420;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
        target.parent.mkdir(exist_ok=True);scene.render.filepath=str(target)
        bpy.ops.render.render(write_still=True)
        count+=1;print('THUMBNAIL '+m['key']+' '+m['mesh'],flush=True)
    except Exception as e:
        with (OUT/'render-errors.log').open('a',encoding='utf-8') as f:f.write(m['mesh']+': '+str(e)+'\n'+traceback.format_exc()+'\n')
        print('RENDER_FAILED '+m['mesh']+' '+str(e),flush=True)
print('THUMBNAILS_COMPLETE '+str(count),flush=True)
