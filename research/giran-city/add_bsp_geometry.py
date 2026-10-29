"""Add Giran's rendered additive BSP brushes to the converted city scene."""
from pathlib import Path
import json
import math
import re
import sys

import bpy
from mathutils import Matrix, Vector


LAB = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOG = LAB / "research/model-catalog"
sys.path.insert(0, str(CATALOG))
import build_gallery as gallery  # noqa: E402


SOURCE = HERE / "Exports/myLevel.t3d"
INPUT_BLEND = HERE / "giran-city-with-terrain.blend"
OUTPUT_BLEND = HERE / "giran-city-complete.blend"
SCENE = CATALOG / "exports/scene-giran-city/scene.gltf"
ORIGIN = Vector((83400.0, 148600.0, -3400.0))
SPECIAL_TEXTURES = (
    "antiportal",
    "zoneportal",
    "hazering",
    "cloud_final",
    "waterantiportal",
)


def tuple_property(text, name, default):
    match = re.search(rf"^\s*{re.escape(name)}=\(([^\r\n]+)\)", text, re.M)
    if not match:
        return list(default)
    values = dict(re.findall(r"([XYZ]|Pitch|Yaw|Roll)=([-+0-9.]+)", match.group(1)))
    keys = ("Pitch", "Yaw", "Roll") if len(default) == 3 and name == "Rotation" else ("X", "Y", "Z")
    return [float(values.get(key, default[i])) for i, key in enumerate(keys)]


def scalar_property(text, name, default):
    match = re.search(rf"^\s*{re.escape(name)}=([-+0-9.]+)", text, re.M)
    return float(match.group(1)) if match else default


def unreal_rotation(rotator):
    pitch, yaw, roll = [value * math.tau / 65536.0 for value in rotator]
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cy = math.sin(yaw), math.cos(yaw)
    sr, cr = math.sin(roll), math.cos(roll)
    return Matrix(
        (
            (cp * cy, sr * sp * cy - cr * sy, -cr * sp * cy - sr * sy),
            (cp * sy, sr * sp * sy + cr * cy, sr * cy - cr * sp * sy),
            (sp, -sr * cp, cr * cp),
        )
    )


def vector_line(text, label):
    match = re.search(rf"^\s*{label}\s+([-+0-9.]+),([-+0-9.]+),([-+0-9.]+)", text, re.M)
    return Vector(tuple(map(float, match.groups()))) if match else Vector((0, 0, 0))


text = SOURCE.read_text(encoding="latin1")
actor_blocks = re.findall(r"^Begin Actor Class=Brush\b.*?^End Actor\s*$", text, re.M | re.S)
vertices = []
faces = []
face_uvs = []
face_textures = []
brushes = 0
skipped_special = 0
skipped_flagged = 0

for actor in actor_blocks:
    if not re.search(r"^\s*CsgOper=CSG_Add\s*$", actor, re.M):
        continue
    brushes += 1
    location = Vector(tuple_property(actor, "Location", (0, 0, 0)))
    prepivot = Vector(tuple_property(actor, "PrePivot", (0, 0, 0)))
    rotation = unreal_rotation(tuple_property(actor, "Rotation", (0, 0, 0)))
    draw_scale = scalar_property(actor, "DrawScale", 1.0)
    draw_scale3d = Vector(tuple_property(actor, "DrawScale3D", (1, 1, 1))) * draw_scale
    polygons = re.findall(r"^\s*Begin Polygon([^\r\n]*)\r?\n(.*?)^\s*End Polygon", actor, re.M | re.S)
    for header, body in polygons:
        texture_match = re.search(r"\bTexture=([^\s]+)", header)
        texture = texture_match.group(1) if texture_match else "None"
        lower = texture.lower()
        if any(token in lower for token in SPECIAL_TEXTURES):
            skipped_special += 1
            continue
        flags_match = re.search(r"\bFlags=(\d+)", header)
        flags = int(flags_match.group(1)) if flags_match else 0
        # UE2 marks helper/back faces in these city brushes with this editor-only bit.
        if flags & 0x400000:
            skipped_flagged += 1
            continue
        raw_vertices = [Vector(tuple(map(float, match))) for match in re.findall(
            r"^\s*Vertex\s+([-+0-9.]+),([-+0-9.]+),([-+0-9.]+)", body, re.M
        )]
        if len(raw_vertices) < 3:
            continue
        tex_origin = vector_line(body, "Origin")
        tex_u = vector_line(body, "TextureU")
        tex_v = vector_line(body, "TextureV")
        start = len(vertices)
        uvs = []
        for raw in raw_vertices:
            transformed = location + rotation @ ((raw - prepivot) * draw_scale3d)
            relative = transformed - ORIGIN
            vertices.append((relative.x * 0.01, -relative.y * 0.01, relative.z * 0.01))
            uvs.append(((raw - tex_origin).dot(tex_u) / 128.0, (raw - tex_origin).dot(tex_v) / 128.0))
        faces.append(tuple(range(start, start + len(raw_vertices))))
        face_uvs.append(uvs)
        face_textures.append(texture)

bpy.ops.wm.open_mainfile(filepath=str(INPUT_BLEND))
old = bpy.data.objects.get("Giran_BSP")
if old:
    bpy.data.objects.remove(old, do_unlink=True)

mesh = bpy.data.meshes.new("Giran_BSP_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new("Giran_BSP", mesh)
bpy.context.scene.collection.objects.link(obj)

gallery.OPTIONS = ["-game=l2", "-path=" + str(HERE / "Packages")]
materials = {}
texture_results = {}
for texture in sorted(set(face_textures), key=str.lower):
    material = bpy.data.materials.new("BSP_" + texture.replace(".", "_"))
    material.diffuse_color = (0.46, 0.39, 0.28, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.9
    result = gallery.texture(texture) if texture != "None" else None
    if result:
        image_path = CATALOG / result["file"]
        image = bpy.data.images.load(str(image_path), check_existing=True)
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Linear"
        material.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        if result.get("alpha"):
            material.node_tree.links.new(node.outputs["Alpha"], bsdf.inputs["Alpha"])
            material.surface_render_method = "DITHERED"
    texture_results[texture] = bool(result)
    materials[texture] = len(mesh.materials)
    mesh.materials.append(material)

uv_layer = mesh.uv_layers.new(name="UVMap")
for polygon, uvs, texture in zip(mesh.polygons, face_uvs, face_textures):
    polygon.material_index = materials[texture]
    for loop_index, uv in zip(polygon.loop_indices, uvs):
        uv_layer.data[loop_index].uv = uv

bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
bpy.ops.export_scene.gltf(
    filepath=str(SCENE),
    export_format="GLTF_SEPARATE",
    export_apply=True,
    export_yup=True,
)

audit = {
    "source": str(SOURCE),
    "brushActors": len(actor_blocks),
    "additiveBrushes": brushes,
    "renderedPolygons": len(faces),
    "vertices": len(vertices),
    "specialPolygonsSkipped": skipped_special,
    "editorFlaggedPolygonsSkipped": skipped_flagged,
    "materials": len(materials),
    "texturedMaterials": sum(texture_results.values()),
    "missingTextures": [name for name, ready in texture_results.items() if not ready and name != "None"],
}
(HERE / "bsp-audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
gallery.cache_file.write_text(json.dumps(gallery.texture_cache, indent=2), encoding="utf-8")
print(json.dumps(audit, indent=2), flush=True)
