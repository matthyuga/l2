"""Add Giran's native 16-bit terrain and nine baked layers to the visual scene."""
from pathlib import Path
import json

import bpy
import numpy as np


LAB = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOG = LAB / "research/model-catalog"
origin = [114630, 147072, -3754]
props = json.loads((HERE / "terrain-props.json").read_text())
height = np.load(HERE / "height.npy")
visible = np.load(HERE / "QuadVisibilityBitmap.npy")
edge = np.load(HERE / "EdgeTurnBitmap.npy")

bpy.ops.wm.open_mainfile(filepath=str(HERE / "giran-architecture.blend"))
h, w = height.shape
vertices = []
faces = []
for y in range(h):
    for x in range(w):
        world_x = (props["MapX"] - 20) * 32768 + x * props["TerrainScale"][0]
        world_y = (props["MapY"] - 18) * 32768 + y * props["TerrainScale"][1]
        world_z = props.get("Location", [0, 0, 0])[2] + (int(height[y, x]) - 32768) * props["TerrainScale"][2] / 256
        vertices.append(
            (
                (world_x - origin[0]) * 0.01,
                -(world_y - origin[1]) * 0.01,
                (world_z - origin[2]) * 0.01,
            )
        )
for y in range(h - 1):
    for x in range(w - 1):
        if not visible[y, x]:
            continue
        a = y * w + x
        b, c, d = a + 1, a + w, a + w + 1
        faces.extend([(a, c, b), (b, c, d)] if edge[y, x] else [(a, c, d), (a, d, b)])

mesh = bpy.data.meshes.new("GiranNativeHeight16")
mesh.from_pydata(vertices, [], faces)
mesh.update()
terrain = bpy.data.objects.new("GiranNativeTerrain", mesh)
bpy.context.collection.objects.link(terrain)
uv = mesh.uv_layers.new(name="TerrainUV")
for polygon in mesh.polygons:
    polygon.use_smooth = True
    for loop_index in polygon.loop_indices:
        vertex = mesh.loops[loop_index].vertex_index
        uv.data[loop_index].uv = ((vertex % w) / (w - 1), 1 - (vertex // w) / (h - 1))

material = bpy.data.materials.new("GiranOriginalTerrainLayers")
material.use_nodes = True
nodes = material.node_tree.nodes
shader = nodes.get("Principled BSDF")
shader.inputs["Roughness"].default_value = 0.95
image_node = nodes.new("ShaderNodeTexImage")
image_node.image = bpy.data.images.load(str(HERE / "terrain-color.png"))
material.node_tree.links.new(image_node.outputs["Color"], shader.inputs["Base Color"])
mesh.materials.append(material)

output = CATALOG / "exports/scene-giran"
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "giran-with-terrain.blend"))
bpy.ops.export_scene.gltf(
    filepath=str(output / "scene.gltf"),
    export_format="GLTF_SEPARATE",
    export_yup=True,
    export_materials="EXPORT",
)

audit = json.loads((HERE / "visual-scene-audit.json").read_text())
audit["terrain"] = {
    "vertices": len(vertices),
    "triangles": len(faces),
    "layers": len(json.loads((HERE / "terrain-audit.json").read_text())["layers"]),
    "height_min": int(height.min()),
    "height_max": int(height.max()),
}
(HERE / "visual-scene-audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

data_path = LAB / "research/scene-editor/data.json"
data = json.loads(data_path.read_text(encoding="utf-8"))
asset = next(item for item in data["assets"] if item.get("id") == "scene_giran")
asset.update(terrain_included=True, terrain_visible=True)
scene = next(item for item in data["scenes"] if item.get("id") == "giran")
scene["source"] = "Giran 23_22: 1.638 actores estáticos y terreno nativo de 16 bits con nueve capas de textura; sin BSP, iluminación, partículas ni NPCs."
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"vertices": len(vertices), "triangles": len(faces), "layers": audit["terrain"]["layers"]}))
