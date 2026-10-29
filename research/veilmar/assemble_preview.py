"""Reconstruct native actor placements and 16-bit terrain in a portable viewer scene."""
import bpy,pathlib,json,math,sys
from mathutils import Vector,Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar';CAT=ROOT/'research/model-catalog'
actors=json.loads((D/'actors.json').read_text());meshes=json.loads((D/'scene-meshes.json').read_text());origin=[-81920,212992,0]
def rotation(rot):
 p,y,r=[x*math.tau/65536 for x in rot];sp,cp=math.sin(p),math.cos(p);sy,cy=math.sin(y),math.cos(y);sr,cr=math.sin(r),math.cos(r)
 ue=Matrix(((cp*cy,sr*sp*cy-cr*sy,-cr*sp*cy-sr*sy),(cp*sy,sr*sp*sy+cr*cy,sr*cy-cr*sp*sy),(sp,-sr*cp,cr*cp)));c=Matrix.Diagonal((1,-1,1));return c@ue@c
def terrain():
 import numpy as np
 height=np.load(D/'height.npy');visible=np.load(D/'QuadVisibilityBitmap.npy');edge=np.load(D/'EdgeTurnBitmap.npy');props=json.loads((D/'terrain-props.json').read_text())
 vertices=[];faces=[]
 for y in range(256):
  for x in range(256):
   wx=-98304+x*128;wy=196608+y*128;z=props['Location'][2]+(int(height[y,x])-32768)*props['TerrainScale'][2]/256
   vertices.append(((wx-origin[0])*.01,-(wy-origin[1])*.01,z*.01))
 for y in range(255):
  for x in range(255):
   if not visible[y,x]:continue
   a=y*256+x;b=a+1;c=a+256;d=c+1
   faces.extend([(a,c,b),(b,c,d)] if edge[y,x] else [(a,c,d),(a,d,b)])
 mesh=bpy.data.meshes.new('VeilmarNativeTerrain');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('Terrain_17_24_Height16',mesh);bpy.context.collection.objects.link(obj)
 uv=mesh.uv_layers.new(name='TerrainUV')
 for poly in mesh.polygons:
  poly.use_smooth=True
  for li in poly.loop_indices:
   idx=mesh.loops[li].vertex_index;x=idx%256;y=idx//256;uv.data[li].uv=(x/255,1-y/255)
 mat=bpy.data.materials.new('VeilmarTerrain_OriginalLayers');mat.use_nodes=True;mat.diffuse_color=(.4,.4,.3,1)
 nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.95;img=nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(CAT/'exports/scene-veilmar/terrain-color.png'));mat.node_tree.links.new(img.outputs['Color'],bs.inputs['Base Color']);mesh.materials.append(mat)
 print('TERRAIN_CREATED',len(vertices),len(faces),flush=True)
for ident,title,underground in [('veilmar_surface','Veilmar · Fortaleza y santuario · Superficie',False),('veilmar_underground','Veilmar · Salas subterráneas',True)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);templates={};used=[];missing=[]
 selection=[a for a in actors if (a.get('Location',[0,0,0])[2]<=-5000)==underground]
 for a in selection:
  ref=a['StaticMesh'];m=meshes.get(ref)
  if not m:missing.append(a['actor']);continue
  if ref not in templates:
   before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(CAT/m['gltf']));bpy.context.view_layer.update()
   templates[ref]=[(o.data.copy(),o.matrix_world.copy()) for o in bpy.data.objects if o not in before and o.type=='MESH']
   for o in list(bpy.data.objects):
    if o not in before:bpy.data.objects.remove(o,do_unlink=True)
  loc=a.get('Location',[0,0,0]);pos=Vector(((loc[0]-origin[0])*.01,-(loc[1]-origin[1])*.01,(loc[2]-origin[2])*.01));s=a.get('DrawScale',1);s3=a.get('DrawScale3D',[1,1,1]);transform=Matrix.Translation(pos)@rotation(a.get('Rotation',[0,0,0])).to_4x4()@Matrix.Diagonal([v*s for v in s3]+[1])
  for i,(data,local) in enumerate(templates[ref]):
   obj=bpy.data.objects.new(a['actor']+f'_{i}',data);bpy.context.collection.objects.link(obj);obj.matrix_world=transform@local
  used.append(a['actor'])
 bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(c) for o in bpy.data.objects if o.type=='MESH' for c in o.bound_box]
 lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 view_bounds=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
 if not underground:terrain()
 folder=CAT/'exports'/('scene-'+ident);folder.mkdir(exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/(ident+'.blend')))
 bpy.ops.export_scene.gltf(filepath=str(folder/'scene.gltf'),export_format='GLTF_SEPARATE',export_yup=True,export_materials='EXPORT')
 data=json.loads((folder/'scene.gltf').read_text());key=ident
 note=f'Mapa original 17_24 de deMEV, {len(used)} actores estáticos con posiciones/rotaciones/escalas de origen. '+('Relieve original de 16 bits y capas de terreno horneadas para el visor. ' if not underground else 'Selección de actores a Z≤-5000 para inspeccionar las salas sin que la superficie las oculte. ')+ 'Materiales representativos; sin agua, partículas, iluminación del juego, puertas animadas, sonidos ni NPCs. Esta vista representa arquitectura; la validacion ingame se documenta en VEILMAR-PVP.md. El paquete del autor no incluye geodata.'
 m=dict(key=key,mesh='MapArchitecture.'+ident,package='MapArchitecture',category='Personalizados',title=title,names=['Veilmar','Monarca del Amanecer','Sanctuary of the Dawn Monarch','Escenario',title],npcs=[],npc_count=0,types=['Escenario'],external_source=True,status='ready',gltf=f'exports/scene-{ident}/scene.gltf',thumbnail=f'thumbs/{key}.png',note=note,preview_only=True,material_count=len(data.get('materials',[])),textured_materials=sum('baseColorTexture' in x.get('pbrMetallicRoughness',{}) for x in data.get('materials',[])))
 m['view_bounds']=view_bounds;m['preview_camera_direction']=[1,-2.8,1.6]
 report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'));report['models']=[x for x in report['models'] if x['key']!=key]+[m];report['model_count']=len(report['models']);(CAT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (D/(ident+'-assembly-audit.json')).write_text(json.dumps(dict(tile='17_24',origin=origin,actors=used,missing=missing,terrain=not underground),indent=2))
 print('SCENE_COMPLETE',ident,len(used),'missing',missing,flush=True)
