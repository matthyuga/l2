"""Read the staged 22_22 map and retain visible StaticMesh actors."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'research/airships'))
from read_map import Package

source=HERE/'Packages/22_22.unr'
actors=Package(source).actors()
(HERE/'actors.json').write_text(json.dumps(actors,indent=2),encoding='utf-8')
print(json.dumps({'map':str(source),'actors':len(actors)}))
