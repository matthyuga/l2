import bpy,pathlib,json
D=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship'
report={}
try:
    bpy.ops.wm.open_mainfile(filepath=str(D/'airship02/airship02.blend'),load_ui=False,use_scripts=False)
    report['blend_opened']=True
except Exception as e:
    report['blend_opened']=False;report['blend_error']=str(e)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.obj(filepath=str(D/'airship02obj/airship02obj.obj'))
    report['fallback']='OBJ'
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
report['blender_version']=bpy.app.version_string
report['objects']=[dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),triangles=sum(len(p.vertices)-2 for p in o.data.polygons),uv_layers=len(o.data.uv_layers),dimensions=list(o.dimensions)) for o in meshes]
report['images']=[dict(name=i.name,packed=bool(i.packed_file),path=i.filepath,size=list(i.size)) for i in bpy.data.images]
report['materials']=len(bpy.data.materials)
(D/'inspection.json').write_text(json.dumps(report,indent=2))
print('FANTASY_INSPECTION',json.dumps(report))
# Save a working copy only; downloaded source stays untouched.
bpy.ops.wm.save_as_mainfile(filepath=str(D/'airship-working-3.5.blend'))
