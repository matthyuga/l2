import bpy,json
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r'E:\l2-local\research\model-catalog\exports\external-assets-3\ext3_02b86c82826120\model.glb')
s=bpy.context.scene
info={'objects':[(o.name,o.type,list(o.dimensions)) for o in s.objects], 'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions], 'rigs':{o.name:[b.name for b in o.data.bones] for o in s.objects if o.type=='ARMATURE'}}
open(r'E:\l2-local\research\cinematic-sett-test\inspection.json','w').write(json.dumps(info,indent=2))
print('INSPECT_DONE')
