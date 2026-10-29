import bpy
import pathlib
import re

SOURCE = pathlib.Path(r"D:\l2-local\research\web-assets\sources\3td_fantasy-ruins")
TARGET = pathlib.Path(r"D:\l2-local\research\model-catalog\exports\web-3td-fantasy-ruins")
TARGET.mkdir(parents=True, exist_ok=True)
bpy.ops.preferences.addon_enable(module="bl_ext.user_default.collada_support")

for source in sorted(SOURCE.rglob("*.dae")):
    if source.name.endswith(".l2lab.dae"):
        continue
    patched = source.with_suffix(".l2lab.dae")
    xml = source.read_text(encoding="utf-8-sig")
    xml = re.sub(r"file:///[^<\\]+[/\\]([^/<\\]+)</init_from>", r"\1</init_from>", xml)
    patched.write_text(xml, encoding="utf-8")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module="bl_ext.user_default.collada_support")
    bpy.ops.import_scene.collada(filepath=str(patched))
    for obj in list(bpy.context.scene.objects):
        if "collision" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.export_scene.gltf(
        filepath=str(TARGET / (source.stem + ".glb")),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
    )
    patched.unlink(missing_ok=True)
    print("CONVERTED", source.name)
