import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'E:\l2-local\research\vigilia-turbinas\Vigilia-turbinas.blend')
for key in ['VIG_00_Casco','VIG_05_Techo','VIG_15_Azotea']:
 for o in bpy.data.collections[key].objects:
  if o.type=='MESH' and (key!='VIG_00_Casco' or o.name.startswith(('Casco_curvo','Junta_liston','Borda_'))):
   vs=[o.matrix_world@Vector(c) for c in o.bound_box];mi=[min(v[i] for v in vs) for i in range(3)];ma=[max(v[i] for v in vs) for i in range(3)];print(o.name,mi,ma)
