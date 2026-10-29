"""Place architecture using map actor transforms; no guessed joins or positions."""
import bpy,json,pathlib,math,sys
from mathutils import Vector,Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/airships';CAT=ROOT/'research/model-catalog'
meshes=json.loads((D/'scene-meshes.json').read_text(encoding='utf-8'))
specs=[('gludio','15_25','Gludio · Muelle aéreo',[-149360,255313,-251]),('keucereus','14_25','Keucereus · Base y muelles aéreos',[-185398,242717,1535])]
specs.append(('aerial','13_25','Gracia · Zona aérea 13_25',[-213016,244888,2040]))
superion_only='--superion' in sys.argv
if superion_only:
 report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
 meshes={m['mesh']:m for m in report['models'] if m['key'].startswith('superion_')}
 specs=[('superion','helios-22_22','Superion · Fortaleza aérea ensamblada',[90000,140000,15000])]
def rotation(rot):
 p,y,r=[x*math.tau/65536 for x in rot];sp,cp=math.sin(p),math.cos(p);sy,cy=math.sin(y),math.cos(y);sr,cr=math.sin(r),math.cos(r)
 ue=Matrix(((cp*cy,sr*sp*cy-cr*sy,-cr*sp*cy-sr*sy),(cp*sy,sr*sp*sy+cr*cy,sr*cy-cr*sp*sy),(sp,-sr*cp,cr*cp)))
 c=Matrix.Diagonal((1,-1,1));return c@ue@c
for ident,tile,title,origin in specs:
 bpy.ops.wm.read_factory_settings(use_empty=True);templates={};used=[];omitted=[]
 actors=json.loads((D/(tile+'-actors.json')).read_text())
 # Architecture only: surrounding terrain, water, caves, skies and particles are separate systems.
 prefix='Superion_' if superion_only else 'Glacia_kserth_S.'
 actors=[a for a in actors if a['StaticMesh'].startswith(prefix)]
 for a in actors:
  ref=a['StaticMesh'];m=meshes.get(ref)
  if not m:omitted.append(a['actor']);continue
  if ref not in templates:
   before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(CAT/m['gltf']))
   objs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];bpy.context.view_layer.update()
   templates[ref]=[(o.data.copy(),o.matrix_world.copy()) for o in objs]
   for o in list(bpy.data.objects):
    if o not in before:bpy.data.objects.remove(o,do_unlink=True)
  loc=a.get('Location',[0,0,0]);pos=Vector(((loc[0]-origin[0])*.01,-(loc[1]-origin[1])*.01,(loc[2]-origin[2])*.01))
  s=a.get('DrawScale',1);s3=a.get('DrawScale3D',[1,1,1]);scale=Matrix.Diagonal([v*s for v in s3]+[1]);rot=rotation(a.get('Rotation',[0,0,0])).to_4x4()
  transform=Matrix.Translation(pos)@rot@scale
  for i,(data,local) in enumerate(templates[ref]):
   obj=bpy.data.objects.new(a['actor']+f'_{i}',data);bpy.context.collection.objects.link(obj);obj.matrix_world=transform@local
  used.append(a['actor'])
 folder=CAT/'exports'/('scene-'+ident);folder.mkdir(exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/(ident+'-architecture.blend')))
 bpy.ops.export_scene.gltf(filepath=str(folder/'scene.gltf'),export_format='GLTF_SEPARATE',export_yup=True,export_materials='EXPORT')
 data=json.loads((folder/'scene.gltf').read_text());key='airship_scene_'+ident
 source_map='22_22.unr (Helios)' if superion_only else tile+'.unr'
 note=f'Arquitectura reconstruida del mapa {source_map}: {len(used)} actores con sus posiciones, rotaciones y escalas de origen. Sin terreno, cielo, partículas, NPCs ni iluminación original; algunos materiales especiales son aproximados.'
 if superion_only:note+=' Las piezas giratorias permanecen en la orientación guardada del mapa.'
 m=dict(key=key,mesh='MapArchitecture.'+ident,package='MapArchitecture',category='Personalizados',title=title,names=['Superion' if superion_only else 'Gracia','Estructuras aéreas','Escenario aéreo',title],npcs=[],npc_count=0,types=['Escenario'],external_source=True,status='ready',gltf=f'exports/scene-{ident}/scene.gltf',thumbnail=f'thumbs/{key}.png',note=note,preview_only=True,material_count=len(data.get('materials',[])),textured_materials=sum('baseColorTexture' in x.get('pbrMetallicRoughness',{}) for x in data.get('materials',[])))
 report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'));report['models']=[x for x in report['models'] if x['key']!=key]+[m];report['model_count']=len(report['models']);(CAT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (D/(ident+'-assembly-audit.json')).write_text(json.dumps(dict(tile=tile,origin=origin,actors=used,missing=omitted),indent=2))
 print('SCENE_COMPLETE',ident,len(used),'actors','missing',omitted,flush=True)
