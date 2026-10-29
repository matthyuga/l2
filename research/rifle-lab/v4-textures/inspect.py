import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'E:\l2-local\research\rifle-lab\build\RifleNPCV3.blend')
print('OBJECTS',json.dumps([{'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'uv':[u.name for u in o.data.uv_layers]} for o in bpy.data.objects if o.type=='MESH']))
