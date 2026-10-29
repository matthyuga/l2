from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;R=D.parents[1]
manifest=json.loads((D/'installation.json').read_text());row=next(v for v in manifest['files'] if v['target'].endswith('24_19.unr'))
# Rerun only the map transformation against the verified V2 backup, never against V3.
source=(D/'prepare.py').read_text(encoding='utf-8');start=source.index("m=Edit(C/'Maps/24_19.unr')");end=source.index("s=(V2/'build_geodata.py')")
sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
code=source[start:end].replace("m=Edit(C/'Maps/24_19.unr')",'m=Edit(Path('+repr(row['backup'])+'))')
exec(code)
print('Rebuilt pre-collider baseline from V2 backup')
