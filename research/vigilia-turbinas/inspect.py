import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'E:\l2-local\research\vigilia-mascaron\Vigilia-mascaron.blend')
for o in bpy.data.objects:
 if any(s in o.name for s in ['motor','helice','Motor','Helice']): print(o.name,tuple(o.location),o.parent.name if o.parent else None)
