"""Assemble Giran city for the local web scene editor using native actor transforms."""
from pathlib import Path
import json
import math
import os
import tempfile

import bpy
from mathutils import Matrix, Vector


LAB = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOG = LAB / "research/model-catalog"
SCENE_EDITOR = LAB / "research/scene-editor"
actors = json.loads((HERE / "actors.json").read_text())
meshes = json.loads((HERE / "visual-meshes.json").read_text(encoding="utf-8"))
mesh_by_lower = {reference.lower(): model for reference, model in meshes.items() if model.get("status") == "ready"}
origin = [83400, 148600, -3400]


def rotation(rotator):
    pitch, yaw, roll = [value * math.tau / 65536 for value in rotator]
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cy = math.sin(yaw), math.cos(yaw)
    sr, cr = math.sin(roll), math.cos(roll)
    unreal = Matrix(
        (
            (cp * cy, sr * sp * cy - cr * sy, -cr * sp * cy - sr * sy),
            (cp * sy, sr * sp * sy + cr * cy, sr * cy - cr * sp * sy),
            (sp, -sr * cp, cr * cp),
        )
    )
    conversion = Matrix.Diagonal((1, -1, 1))
    return conversion @ unreal @ conversion


bpy.ops.wm.read_factory_settings(use_empty=True)
templates = {}
used = []
missing = []
for number, actor in enumerate(actors, 1):
    reference = actor["StaticMesh"]
    model = mesh_by_lower.get(reference.lower())
    if not model:
        missing.append(actor["actor"])
        continue
    if reference.lower() not in templates:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(CATALOG / model["gltf"]))
        imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
        bpy.context.view_layer.update()
        templates[reference.lower()] = [(obj.data.copy(), obj.matrix_world.copy()) for obj in imported]
        for obj in list(bpy.data.objects):
            if obj not in before:
                bpy.data.objects.remove(obj, do_unlink=True)
    location = actor.get("Location", [0, 0, 0])
    position = Vector(
        (
            (location[0] - origin[0]) * 0.01,
            -(location[1] - origin[1]) * 0.01,
            (location[2] - origin[2]) * 0.01,
        )
    )
    scale = actor.get("DrawScale", 1)
    scale3d = actor.get("DrawScale3D", [1, 1, 1])
    scale_matrix = Matrix.Diagonal([value * scale for value in scale3d] + [1])
    transform = Matrix.Translation(position) @ rotation(actor.get("Rotation", [0, 0, 0])).to_4x4() @ scale_matrix
    for part, (mesh_data, local_transform) in enumerate(templates[reference.lower()]):
        obj = bpy.data.objects.new(actor["actor"] + f"_{part}", mesh_data)
        bpy.context.collection.objects.link(obj)
        obj.matrix_world = transform @ local_transform
    used.append(actor["actor"])
    if number % 100 == 0:
        print(f"colocados {number}/{len(actors)}", flush=True)

output = CATALOG / "exports/scene-giran-city"
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "giran-city-architecture.blend"))
bpy.ops.export_scene.gltf(
    filepath=str(output / "scene.gltf"),
    export_format="GLTF_SEPARATE",
    export_yup=True,
    export_materials="EXPORT",
)
(HERE / "visual-scene-audit.json").write_text(
    json.dumps({"map": "22_22.unr", "origin": origin, "actors": len(used), "missing": missing}, indent=2),
    encoding="utf-8",
)
if missing:
    raise RuntimeError(f"La escena quedó incompleta: {len(missing)} actores sin malla")

data_path = SCENE_EDITOR / "data.json"
data = json.loads(data_path.read_text(encoding="utf-8"))
asset = {
    "id": "scene_giran_city",
    "title": "Ciudad de Giran",
    "path": "exports/scene-giran-city/scene.gltf",
    "thumbnail": None,
    "mesh": "22_22.unr",
    "category": "Escenarios",
}
data["assets"] = [item for item in data["assets"] if item.get("id") != asset["id"]] + [asset]
scene = {
    "id": "giran_city",
    "title": "Ciudad de Giran",
    "asset": asset["id"],
    "source": "Giran 22_22: ciudad nativa reconstruida para edición visual; sin terreno, BSP, iluminación, partículas ni NPCs.",
    "actorMapping": {},
    "installedOrigin": origin,
}
data["scenes"] = [item for item in data["scenes"] if item.get("id") != scene["id"]] + [scene]
payload = json.dumps(data, ensure_ascii=False, indent=2)
handle, temporary = tempfile.mkstemp(prefix="data-giran-", suffix=".json", dir=data_path.parent)
try:
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(payload)
    os.replace(temporary, data_path)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
print(json.dumps({"actors": len(used), "scene": str(output / "scene.gltf"), "editor_data": str(data_path)}))
