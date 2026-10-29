import bpy,sys
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon')
import io_scene_psk_psa
io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'retarget/Dust2_BombWork_FFighter.blend'))
bpy.ops.object.select_all(action='DESELECT')
mat=bpy.data.materials.new('DemoClay')
for obj in bpy.data.objects:
 if obj.type=='MESH':
  obj.data.materials.clear();obj.data.materials.append(mat)
  for p in obj.data.polygons:p.material_index=0
  obj.select_set(True)
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
opt=PskBuildOptions();opt.material_names=['DemoClay'];write_psk(build_psk(bpy.context,opt),str(R/'Dust2Demo.psk'))
