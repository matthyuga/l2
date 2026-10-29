import pathlib,json,bpy
ROOT=pathlib.Path(__file__).resolve().parent;MASTER=ROOT.parent/'external-assets-20261028'
for key in ['ext3_2493ca25e8066e','ext3_f645befc212d2d']:
 job=json.loads((MASTER/'jobs'/(key+'.json')).read_text('utf-8'));bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=job['input'],use_anim=True)
 fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base;actions=[{'name':a.name,'frames':list(a.frame_range),'duration_seconds':(a.frame_range[1]-a.frame_range[0])/fps} for a in bpy.data.actions]
 (ROOT/'source-structure'/(key+'-import-ranges.json')).write_text(json.dumps({'fps':fps,'actions':actions},ensure_ascii=False,indent=2),encoding='utf-8');print('ACTION_RANGE',key,len(actions),'seconds',sum(a['duration_seconds'] for a in actions),actions[:3],flush=True)
