import bpy,pathlib,json
root=pathlib.Path(r"E:\l2-local\research\external-assets-20261028\unpacked")
for key in ["ext3_452ce17e9fb546","ext3_3abd40458e20ef","ext3_02ca3c6c038ee4","ext3_ced9f7d8b5da4c"]:
 src=next((root/key).rglob("*.fbx"));bpy.ops.wm.read_factory_settings(use_empty=True)
 try:bpy.ops.import_scene.fbx(filepath=str(src))
 except:bpy.ops.wm.fbx_import(filepath=str(src))
 (root.parent/(key+"-materials.json")).write_text(json.dumps({"key":key,"materials":[m.name for m in bpy.data.materials],"images":[[i.name,i.filepath] for i in bpy.data.images],"files":[p.name for p in (root/key).rglob("*") if p.suffix.lower() in [".png",".tga",".jpeg"]]},ensure_ascii=True),encoding="utf-8")
