"""Non-destructive optimization copy for native import validation."""
import bpy,pathlib,json
D=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship'
bpy.ops.wm.open_mainfile(filepath=str(D/'airship02/airship02.blend'),load_ui=False,use_scripts=False)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ('MESH','CURVE'):o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.selected_objects if o.type=='MESH')
bpy.ops.object.convert(target='MESH')
report=[]
for o in bpy.context.selected_objects:
 if o.type!='MESH':continue
 before=sum(len(p.vertices)-2 for p in o.data.polygons)
 if o.name.startswith('Rope'):
  bpy.context.view_layer.objects.active=o;m=o.modifiers.new('ProbeRopeReduction','DECIMATE');m.ratio=.08;bpy.ops.object.modifier_apply(modifier=m.name)
 report.append(dict(name=o.name,before=before,after=sum(len(p.vertices)-2 for p in o.data.polygons)))
bpy.ops.wm.obj_export(filepath=str(D/'airship-probe-optimized.obj'),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'airship-probe-optimized.blend'))
(D/'optimization-probe.json').write_text(json.dumps(report,indent=2));print('OPTIMIZED',sum(r['before'] for r in report),sum(r['after'] for r in report),flush=True)
