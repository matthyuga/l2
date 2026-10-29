import bpy,pathlib,json
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship'
bpy.ops.wm.open_mainfile(filepath=str(D/'airship-audit-working.blend'),load_ui=False,use_scripts=False)
scene=bpy.context.scene
for o in scene.objects:
 if o.type=='MESH' and o.name.startswith('Rope'):
  bpy.context.view_layer.objects.active=o;m=o.modifiers.new('ProbeRopeReduction','DECIMATE');m.ratio=.08;bpy.ops.object.modifier_apply(modifier=m.name)
meshes=[o for o in scene.objects if o.type=='MESH' and not o.hide_render];points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2;radius=(hi-lo).length/2
cam=scene.camera;cam.location=center+Vector((1,-1,.7)).normalized()*radius*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=24;scene.render.filepath=str(D/'optimized-perspective.png');bpy.ops.render.render(write_still=True)
print('SOURCE_TYPES',[(o.name,o.type) for o in scene.objects if o.type not in ('MESH','LIGHT','CAMERA')],flush=True)
print('WORLD_DIMENSIONS',list(hi-lo),flush=True)
