"""Correct mixed NPC/effect archives without discarding source records or favorite keys."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVES = {"1dlggSvZwWShvtfiNCNERjnyyKzYw1dyR", "1jziyiNEGGLG2VT-nyxB_6WfsMP1p6J0h"}
# Descriptive labels from the exported previews, not official item names.
LABELS = {"01": "Gorro rojo bordado", "02": "Gorro de bufón", "03": "Casco negro y dorado", "04": "Gorro de piel", "05": "Casco con cresta", "06": "Accesorio 06", "07": "Accesorio 07", "08": "Accesorio 08"}

def main():
    path = ROOT / "gallery.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = {"items": 0, "effects": 0}
    for m in data["models"]:
        if m.get("archive_id") not in ARCHIVES:
            continue
        name = m["mesh"].split(".")[-1]
        match = re.fullmatch(r"viRUS_([MF][A-Z])_(\d{2})_m(\d+)_a", name)
        if match:
            code, design, version = match.groups()
            m.setdefault("original_catalog_title", m["title"])
            m.update(category="Accesorios / ítems", catalog_role="item", title=LABELS[design],
                     item_group="virus-accessory-" + design,
                     item_variant=f"{m.get('chronicle', '')} · {code} · m{version}",
                     classification_note="Accesorio de cabeza: familia de mallas viRUS y textura del diseño correspondiente. Las versiones de ajuste se conservan; no son NPC.")
            counts["items"] += 1
        elif "/StaticMesh/" in m.get("gltf", ""):
            m.setdefault("original_catalog_title", m["title"])
            m.update(category="Efectos", catalog_role="effect", title="Efecto · " + name)
            counts["effects"] += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(counts)

if __name__ == "__main__":
    main()
