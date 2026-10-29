"""Export only the static meshes referenced by Giran's private map copy."""
from pathlib import Path
import hashlib
import json
import sys


LAB = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOG = LAB / "research/model-catalog"
sys.path.insert(0, str(CATALOG))
import build_gallery as gallery  # noqa: E402


gallery.OPTIONS = ["-game=l2", "-path=" + str(HERE / "Packages")]
original_run = gallery.run
gallery.run = lambda args: original_run([item.replace(".ukx", ".usx") for item in args])

actors = json.loads((HERE / "actors.json").read_text())
mesh_file = HERE / "visual-meshes.json"
meshes = json.loads(mesh_file.read_text(encoding="utf-8")) if mesh_file.exists() else {}
references = sorted({actor["StaticMesh"] for actor in actors}, key=str.lower)

for position, reference in enumerate(references, 1):
    old = meshes.get(reference)
    if old and old.get("status") == "ready" and (CATALOG / old["gltf"]).exists():
        print(f"[{position}/{len(references)}] reutilizada {reference}", flush=True)
        continue
    # Actor references preserve UE2 groups (Package.Group.Object), while
    # umodel selects the export by its leaf object name.
    export_reference = reference.split(".", 1)[0] + "." + reference.rsplit(".", 1)[-1]
    model = {
        "key": "giran_" + hashlib.sha1(reference.encode()).hexdigest()[:12],
        "mesh": export_reference,
        "source_reference": reference,
        "npcs": [],
    }
    try:
        gallery.prepare(model)
        meshes[reference] = model
        print(
            f"[{position}/{len(references)}] preparada {reference} "
            f"({model['textured_materials']}/{model['material_count']} materiales)",
            flush=True,
        )
    except Exception as error:
        model.update(status="failed", error=str(error))
        meshes[reference] = model
        print(f"[{position}/{len(references)}] FALLO {reference}: {error}", flush=True)
    mesh_file.write_text(json.dumps(meshes, ensure_ascii=False, indent=2), encoding="utf-8")
    gallery.cache_file.write_text(json.dumps(gallery.texture_cache, indent=2), encoding="utf-8")

failed = [reference for reference in references if meshes.get(reference, {}).get("status") != "ready"]
print(json.dumps({"references": len(references), "ready": len(references) - len(failed), "failed": failed}))
if failed:
    raise SystemExit(1)
