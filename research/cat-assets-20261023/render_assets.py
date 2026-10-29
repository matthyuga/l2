import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
GALLERY=OUT.parent/'model-catalog'
assets=json.loads((OUT/'inventory.json').read_text())
for a in assets:
    if '--only-first' in sys.argv and a['key']!='web_cat_review_01':continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    file=Path(a['source'])
    if file.suffix=='.glb':bpy.ops.import_scene.gltf(filepath=str(file))
    elif file.suffix=='.fbx':bpy.ops.import_scene.fbx(filepath=str(file))
    elif file.suffix=='.stl':bpy.ops.import_mesh.stl(filepath=str(file))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    a['mesh_count']=len(meshes);a['armatures']=sum(o.type=='ARMATURE' for o in bpy.context.scene.objects)
    a['triangles_actual']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    # Normalize only the preview copy. Source downloads stay untouched.
    bpy.context.view_layer.update();points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
    center=(lo+hi)/2;scale=1/max(hi-lo)
    for o in list(bpy.context.scene.objects):
        if o.parent is None:o.location=(o.location-center)*scale;o.scale*=scale
    if a['key']=='web_cat_review_01':
        from mathutils import Matrix
        rotate=Matrix.Rotation(-math.pi/2,4,'Z')
        for o in list(bpy.context.scene.objects):
            if o.parent is None:o.matrix_world=rotate@o.matrix_world
    bpy.context.view_layer.update()
    # Package a web-preview copy with all imported textures embedded.
    dest=GALLERY/'exports/web-cat-review'/a['key'];dest.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type in ['MESH','ARMATURE']:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(dest/'model.glb'),export_format='GLB',use_selection=True,export_animations=False)
    a['gltf']=(dest/'model.glb').relative_to(GALLERY).as_posix()
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.eevee.use_gtao=True
    scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.18,.23,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    for pos,power in [((2,-3,4),350),((-3,-1,2),180),((1,3,3),300)]:
        bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=3;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(1,-3,.8));camera=bpy.context.object;camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1.35;scene.camera=camera
    scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
    scene.render.resolution_x=540;scene.render.resolution_y=600;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(dest/'preview.png');bpy.ops.render.render(write_still=True)
    a['thumbnail']=(dest/'preview.png').relative_to(GALLERY).as_posix()
    print('CAT_RENDERED',a['archive'],flush=True)
(OUT/'inventory.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
