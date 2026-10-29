import bpy,json
from pathlib import Path
root=Path(r'E:\l2-local\research\dust2-animation-study\retarget')
result={}
for label,fn in [('l2','fighter-reference.blend'),('koi','amber-imported.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(Path(r'E:\l2-local\research\amber-l2\exports')/fn))
 rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
 result[label]=[{'name':r.name,'matrix_world':[list(row) for row in r.matrix_world],'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'matrix_local':[list(row) for row in b.matrix_local]} for b in r.data.bones]} for r in rigs]
(root/'rig-inventory.json').write_text(json.dumps(result,indent=2))
print('RIGS',[(k,[(r['name'],len(r['bones'])) for r in v]) for k,v in result.items()])
