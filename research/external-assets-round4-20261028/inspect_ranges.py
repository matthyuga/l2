import bpy,pathlib,json
root=pathlib.Path(r"E:\l2-local\research\external-assets-20261028")
inv=json.loads((root/'inventory.json').read_text('utf-8'))['records']
results=[]
for r in inv:
 if r['file'] not in ['arachnida.zip','deep-monstrosity.zip']:continue
 source=pathlib.Path(r['root'])/r['models'][0];bpy.ops.wm.read_factory_settings(use_empty=True)
 try:bpy.ops.import_scene.fbx(filepath=str(source),use_anim=True)
 except:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.fbx_import(filepath=str(source))
 a={'file':r['file'],'fps':bpy.context.scene.render.fps,'fps_base':bpy.context.scene.render.fps_base,'scene_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end],'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions]}
 results.append(a);print('ACTION_RANGE',json.dumps(a,ensure_ascii=True),flush=True)
(pathlib.Path(__file__).parent/'source-ranges.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
