"""Prepare an isolated, editable Giran city (22_22) workspace.

The live client is read-only. Decrypted packages and the working map are written
under research/giran-editor only.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parent.parent
CLIENT = Path("D:/l2")
EDITOR_BASE = LAB_ROOT / "research/amber-l2/tools/l2editor/L2Editor"
PACKAGE_READER = LAB_ROOT / "research/airships"
SYSTEM = ROOT / "System"
PACKAGES = ROOT / "Packages"
ORIGINAL = ROOT / "Original"
WORKING = ROOT / "Working"
MAP_NAME = "22_22"

sys.path.insert(0, str(PACKAGE_READER))
from read_map import Package  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for directory in (SYSTEM, PACKAGES, ORIGINAL, WORKING):
    directory.mkdir(parents=True, exist_ok=True)

working_map = WORKING / f"{MAP_NAME}.unr"
if working_map.exists():
    raise SystemExit(f"La copia editable ya existe; no se sobrescribe: {working_map}")

index = {}
for folder in (
    "maps",
    "staticmeshes",
    "textures",
    "sounds",
    "systextures",
    "system",
    "system-hud",
    "animations",
):
    source_dir = CLIENT / folder
    if not source_dir.exists():
        continue
    for path in source_dir.iterdir():
        if path.suffix.lower() in (".unr", ".u", ".utx", ".usx", ".uax", ".ukx"):
            index.setdefault(path.stem.lower(), path)

native = {"core", "engine", "editor", "fire", "unrealed", "ipdrv", "alaudio", "uweb"}
manifest = {
    "client": str(CLIENT),
    "map": MAP_NAME,
    "files": [],
    "native_editor_packages": sorted(native),
    "missing": [],
    "live_client_modified": False,
}
seen = set()


def stage(name: str) -> None:
    key = name.lower()
    if key in seen or key in native:
        return
    seen.add(key)
    source = index.get(key)
    if source is None:
        manifest["missing"].append(name)
        return

    backup = ORIGINAL / source.name
    if backup.exists() and sha256(backup) != sha256(source):
        raise RuntimeError(f"El respaldo existente no coincide con el cliente: {source}")
    if not backup.exists():
        shutil.copy2(source, backup)

    raw = source.read_bytes()
    if raw[:4] != b"\xc1\x83\x2a\x9e":
        marker = raw[:28].decode("utf-16le", errors="ignore")
        if marker not in ("Lineage2Ver111", "Lineage2Ver121"):
            raise RuntimeError(f"Formato no soportado: {source}")
        key_byte = 172 if marker.endswith("111") else sum(map(ord, source.name.lower())) & 255
        table = bytes.maketrans(bytes(range(256)), bytes(value ^ key_byte for value in range(256)))
        raw = raw[28:-20].translate(table)

    staged = PACKAGES / source.name
    staged.write_bytes(raw)
    package = Package(staged)
    manifest["files"].append(
        {
            "source": str(source),
            "backup": str(backup),
            "sha256": sha256(source),
            "bytes": source.stat().st_size,
            "version": package.version,
            "license": package.license,
        }
    )
    print(f"Preparado {source.name}", flush=True)
    for imported in package.imports:
        if imported["outer"] == 0 and imported["cl"] == "Package":
            stage(imported["name"])


stage(MAP_NAME)

for path in EDITOR_BASE.iterdir():
    if not path.is_file() or path.suffix.lower() not in (".dll", ".int", ".exe", ".u", ".ini", ".bmp"):
        continue
    if path.suffix.lower() == ".u" and path.stem.lower() not in native:
        continue
    shutil.copy2(path, SYSTEM / path.name)
for folder in ("EditorRes", "UDE"):
    source = EDITOR_BASE / folder
    if source.exists():
        shutil.copytree(source, SYSTEM / folder, dirs_exist_ok=True)

ini = (EDITOR_BASE / "UT2003.ini").read_text()
ini = re.sub(r"^Paths=.*\n?", "", ini, flags=re.M)
private_paths = "\n".join(f"Paths=../Packages/*.{ext}" for ext in ("u", "utx", "usx", "unr", "uax", "ukx"))
ini = ini.replace("[Core.System]", f"[Core.System]\nPaths=./*.u\n{private_paths}")
(SYSTEM / "GiranEditor.ini").write_text(ini)

shutil.copy2(PACKAGES / f"{MAP_NAME}.unr", working_map)

unchanged = all(
    sha256(Path(item["source"])) == item["sha256"] == sha256(Path(item["backup"]))
    for item in manifest["files"]
)
if not unchanged:
    raise RuntimeError("Algún archivo vivo cambió durante la preparación.")

manifest["live_and_backups_match"] = True
manifest["working_map"] = str(working_map)
manifest["ready_for_direct_client_install"] = False
(ROOT / "snapshot.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"packages": len(manifest["files"]), "missing": manifest["missing"], "working": str(working_map)}))
