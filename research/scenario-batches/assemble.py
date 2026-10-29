"""Assemble original actor transforms and export one reviewable scene per map."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;CAT=ROOT/'research/model-catalog'
ident=sys.argv[sys.argv.index('--')+1];folder=D/ident;manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
actors=manifest['actors'];meshes=manifest['meshes'];origin=[sum(a.get('Location',[0,0,0])[i] for a in actors)/len(actors) for i in range(3)]
def rotation(rot):
 p,y,r=[v*math.tau/65536 for v in rot];sp,cp=math.sin(p),math.cos(p);sy,cy=math.sin(y),math.cos(y);sr,cr=math.sin(r),math.cos(r)
 ue=Matrix(((cp*cy,sr*sp*cy-cr*sy,-cr*sp*cy-sr*sy),(cp*sy,sr*sp*sy+cr*cy,sr*cy-cr*sp*sy),(sp,-sr*cp,cr*cp)));c=Matrix.Diagonal((1,-1,1));return c@ue@c
bpy.ops.wm.read_factory_settings(use_empty=True);templates={};used=[];missing=[]
for a in actors:
 ref=a['StaticMesh'];m=meshes.get(ref)
 if not m:missing.append(a['actor']);continue
 if ref not in templates:
  before=set(bpy.data.objects)
  try:
   bpy.ops.import_scene.gltf(filepath=str(CAT/m['gltf']));bpy.context.view_layer.update()
   templates[ref]=[(o.data.copy(),o.matrix_world.copy()) for o in bpy.data.objects if o not in before and o.type=='MESH']
  except Exception as e:templates[ref]=[];print('IMPORT_FAILED',ref,str(e),flush=True)
  for o in list(bpy.data.objects):
   if o not in before:bpy.data.objects.remove(o,do_unlink=True)
 if not templates[ref]:missing.append(a['actor']);continue
 loc=a.get('Location',[0,0,0]);pos=Vector(((loc[0]-origin[0])*.01,-(loc[1]-origin[1])*.01,(loc[2]-origin[2])*.01));s=a.get('DrawScale',1);s3=a.get('DrawScale3D',[1,1,1]);transform=Matrix.Translation(pos)@rotation(a.get('Rotation',[0,0,0])).to_4x4()@Matrix.Diagonal([v*s for v in s3]+[1])
 for i,(data,local) in enumerate(templates[ref]):
  o=bpy.data.objects.new(a['actor']+'_'+str(i),data);bpy.context.collection.objects.link(o);o.matrix_world=transform@local
 used.append(a['actor'])
assert used
out=CAT/'exports'/('scene-batch1-'+ident);out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'scene.gltf'),export_format='GLTF_SEPARATE',export_yup=True,export_materials='EXPORT')
data=json.loads((out/'scene.gltf').read_text(encoding='utf-8'));key='scenario_batch1_'+ident
model=dict(key=key,mesh='MapArchitecture.'+ident,package='MapArchitecture',category='Personalizados',batch='Tanda 2',title=manifest['title'],names=[manifest['title'],'Escenario','Escenarios tanda 1',manifest['tile']],npcs=[],npc_count=0,types=['Escenario'],external_source=True,preview_only=True,status='ready',gltf=str((out/'scene.gltf').relative_to(CAT)).replace('\\','/'),thumbnail='thumbs/'+key+'.png',material_count=len(data.get('materials',[])),textured_materials=sum('baseColorTexture' in m.get('pbrMetallicRoughness',{}) for m in data.get('materials',[])),preview_camera_direction=[1,-2.8,1.8],note='Escenarios, primera tanda. Arquitectura del mapa '+manifest['tile']+' ensamblada con posiciones, rotaciones y escalas originales: '+str(len(used))+' actores; '+str(len(missing))+' actores no representados. Sin terreno, BSP, agua, partículas, iluminación original, sonidos ni NPCs. Materiales representativos. Preparado para el visor; no instalado en el juego.')
(folder/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'audit.json').write_text(json.dumps(dict(origin=origin,used=used,missing=missing,source=manifest['source'],sha256=manifest['sha256']),indent=2),encoding='utf-8')
print('ASSEMBLED',ident,len(used),'MISSING',len(missing),flush=True)
