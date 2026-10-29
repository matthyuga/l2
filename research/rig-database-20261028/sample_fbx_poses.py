import bpy,pathlib,json
OUT=pathlib.Path(__file__).resolve().parent
source=json.loads((OUT/'sett-fbx-observation.json').read_text('utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=source['source_path'],use_anim=True)
fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
samples=[]
for seconds in [0.,1/60,1.,5.,15.,30.,45.,60.,75.,90.,90.9]:
    frame=seconds*fps;bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
    positions={}
    for obj in bpy.context.scene.objects:
        if obj.type!='ARMATURE':continue
        for bone in obj.pose.bones:
            v=obj.matrix_world@bone.head
            positions[bone.name]=[v.x,v.z,-v.y]
    samples.append({'seconds':seconds,'blender_frame':frame,'joint_world_glTF_basis':positions})
(OUT/'sett-fbx-pose-samples.json').write_text(json.dumps({'source_sha256':source['source_sha256'],'fps':fps,'coordinate_conversion':'Blender world (x,y,z) -> glTF world (x,z,-y)','samples':samples},ensure_ascii=False,indent=2),encoding='utf-8')
print('FBX_POSES_SAMPLED',len(samples),flush=True)
