import bpy,sys
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(R));import nexus_animation_lab
nexus_animation_lab.register()
sys.path.insert(0,str(nexus_animation_lab.ADDON));import io_scene_psk_psa;io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=str(R/'Nexus-L2-Animation-Lab.blend'))
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.show_region_ui=True
  with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):
   bpy.ops.view3d.view_all(center=False)
