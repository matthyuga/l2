import bpy,json
from pathlib import Path
p=Path('E:/l2-local/research/vigilia-clan-renovada2/Vigilia-renovada2.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
items=[]
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['dragon','cuerno','craneo','hocico','mandib','cuenca','ceja','diente','fosa','boca','espina']):items.append({'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],'location':list(o.location),'dimensions':list(o.dimensions)})
Path('E:/l2-local/research/vigilia-dragon-sculpt-20261020/original-head-inventory.json').write_text(json.dumps(items,indent=2))
print('DRAGON_INVENTORY',len(items),flush=True)
