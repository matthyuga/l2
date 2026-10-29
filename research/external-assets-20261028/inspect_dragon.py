import bpy,pathlib
p=next(pathlib.Path(r"E:\l2-local\research\external-assets-20261028\unpacked\ext3_d51ae9d0fc460c").rglob("*.fbx"))
bpy.ops.import_scene.fbx(filepath=str(p))
print([(i.name,i.filepath) for i in list(bpy.data.images)[:4]],flush=True)
