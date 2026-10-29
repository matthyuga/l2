import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'research/vigilia-clan-v3/Vigilia-clan-v3.blend'))
report=[]
for o in bpy.data.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 if any('studio' in c.name.lower() or 'estudio' in c.name.lower() for c in o.users_collection):continue
 report.append({'name':o.name,'collection':[c.name for c in o.users_collection],'loc':list(o.location),'size':list(o.dimensions),'material':[m.name for m in o.data.materials]})
(Path(__file__).resolve().parent/'source-objects.json').write_text(json.dumps(report,indent=2))
print('INSPECTED',len(report))
