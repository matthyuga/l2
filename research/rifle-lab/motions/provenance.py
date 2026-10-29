import json,hashlib,csv,io,zipfile
from pathlib import Path
root=Path(r'E:\l2-local\research\rifle-lab\motions');p=next(Path(r'K:\JUEGOS\KOIKATSU 22\mods\Sideloader Modpack - Animations\AgiShark').glob('*'));z=zipfile.ZipFile(p);data=z.read('abdata/studio/info/Kohai/Anime_00_1011_06.csv');(root/'Anime_00_1011_06.csv').write_bytes(data)
manifest=dict(source_zipmod=str(p),source_zipmod_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_csv='abdata/studio/info/Kohai/Anime_00_1011_06.csv',source_csv_sha256=hashlib.sha256(data).hexdigest(),bundles=[])
for path in root.glob('mixamo_gun_part*.unity3d'):manifest['bundles'].append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size=path.stat().st_size))
(root/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print('saved',manifest['source_zipmod_sha256'])
