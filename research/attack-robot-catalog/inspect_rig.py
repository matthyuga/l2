import bpy,json,collections
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\l2-local\temp\attack-robot-review\Attack Robot.fbx")
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mesh=next(o for o in bpy.data.objects if o.type=='MESH')
counts=collections.Counter();weights=collections.defaultdict(list)
for v in mesh.data.vertices:
 for g in v.groups:
  if g.weight>.001:
   name=mesh.vertex_groups[g.group].name;counts[name]+=1;weights[name].append(g.weight)
report={'armature':arm.name,'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'deform':b.use_deform,'weighted_vertices':counts[b.name],'weight_range':[min(weights[b.name]),max(weights[b.name])] if weights[b.name] else None} for b in arm.data.bones],'actions':[a.name for a in bpy.data.actions],'modifiers':[{'name':m.name,'type':m.type} for m in mesh.modifiers]}
Path(r"E:\l2-local\research\attack-robot-catalog\rig-inspection.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report))
