"""Preview assembly in source coordinates; does not alter game packages."""
import bpy,json,pathlib,math
from mathutils import Vector,Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
CAT=ROOT/'research/model-catalog'
report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
parts=[('airship_fly_boat_body002',(0,0,0)),('airship_animated_fly_boat_body004',(0,0,0)),('airship_animated_fly_boat_body003',(-4.98,0,0)),('airship_fly_boat_steering001',(3.63,0,1.02))]
for part,offset in parts:
 m=next(x for x in report['models'] if x['key']==part)
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(CAT/m['gltf']))
 objects=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 roots=[o for o in bpy.data.objects if o not in before and o.parent is None]
 for o in roots:
  rotation=Matrix.Rotation(math.pi,4,'Z') if part.startswith('airship_animated_') else Matrix.Identity(4)
  o.matrix_world=Matrix.Translation(Vector(offset))@rotation@o.matrix_world
 bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
 print('PART_BOUNDS',part,[round(min(p[i] for p in points),2) for i in range(3)],[round(max(p[i] for p in points),2) for i in range(3)],flush=True)
folder=CAT/'exports/assembled-gracia';folder.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
bpy.context.object.name='GraciaAirship_AssembledPreview'
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'research/airships/GraciaAirship-preview.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'airship.gltf'),export_format='GLTF_SEPARATE',export_yup=True,export_materials='EXPORT')
m={'key':'airship_assembled_gracia','mesh':'PreviewAssembly.GraciaAirship','package':'PreviewAssembly','category':'Personalizados','title':'Gracia · Nave aérea ensamblada','names':['Gracia','Barco volador','Nave aérea ensamblada'],'npcs':[],'npc_count':0,'types':['Estructura'],'external_source':True,'status':'ready','gltf':'exports/assembled-gracia/airship.gltf','thumbnail':'thumbs/airship_assembled_gracia.png','note':'Montaje corregido según VehiclePartsGrp: casco, velamen y cola animados en pose base, y mando. Offsets de cola (-498,0,0) y mando (363,0,102), escala cm→m. Materiales opacos corregidos. Sin partículas; orientación y pose final pendientes de contrastar ingame.','preview_only':True}
data=json.loads((folder/'airship.gltf').read_text())
m['material_count']=len(data.get('materials',[]));m['textured_materials']=sum('baseColorTexture' in x.get('pbrMetallicRoughness',{}) for x in data.get('materials',[]))
report['models']=[x for x in report['models'] if x['key']!=m['key']]+[m];report['model_count']=len(report['models'])
(CAT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('ASSEMBLED',len(parts),'parts',flush=True)
