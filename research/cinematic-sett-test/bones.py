import bpy,json
s=bpy.context.scene;s.frame_set(1);r=next(o for o in s.objects if o.type=='ARMATURE')
for b in r.pose.bones:
 if any(t in b.name for t in ['thigh','calf','foot','toe','head']):print(b.name,tuple(round(v,3) for v in r.matrix_world@b.head),tuple(round(v,3) for v in r.matrix_world@b.tail))
