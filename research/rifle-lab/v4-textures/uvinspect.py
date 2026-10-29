import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'E:\l2-local\research\rifle-lab\build\RifleNPCV3.blend')
print('UVRANGES',[(o.name,[(min(x.uv[a] for x in o.data.uv_layers.active.data),max(x.uv[a] for x in o.data.uv_layers.active.data)) for a in (0,1)]) for o in bpy.data.objects if o.type=='MESH' and o.name!='M4A1'])
