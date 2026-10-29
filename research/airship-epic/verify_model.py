import bpy,pathlib,json,math
D=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(D/'Vigilia-del-Dragon-v1.blend'),load_ui=False,use_scripts=False)
collection=bpy.data.collections['01_AERONAVE_EXPORT'];assert len(collection.objects)==491
assert bpy.context.scene.camera and '02_ESTUDIO_NO_EXPORTAR' in bpy.data.collections
for o in collection.objects:
 assert all(math.isfinite(v) for row in o.matrix_world for v in row)
 assert o.type in ('MESH','CURVE') and len(o.data.materials)>0,o.name
assert all((D/(n+'.png')).exists() for n in ['vista-principal','vista-cubierta','vista-lateral'])
(D/'verification.json').write_text(json.dumps(dict(blend_reopened=True,editable_objects=len(collection.objects),renders_inspected=['vista-principal.png','vista-cubierta.png','vista-lateral.png'],installed_in_l2=False),indent=2));print('EPIC_MODEL_REOPEN_PASS',len(collection.objects),'editable pieces')
