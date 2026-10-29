import bpy,json,sys,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent/(sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'r4_arena');CAT=ROOT/'research/model-catalog';audit=json.loads((D/'audit.json').read_text());origin=audit['origin'];props=json.loads((D/'terrain-props.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(D/'scene.blend'))
height=np.load(D/'height.npy');visible=np.load(D/'QuadVisibilityBitmap.npy');edge=np.load(D/'EdgeTurnBitmap.npy');h,w=height.shape;vertices=[];faces=[]
for y in range(h):
 for x in range(w):
  wx=(props['MapX']-20)*32768+x*props['TerrainScale'][0];wy=(props['MapY']-18)*32768+y*props['TerrainScale'][1];z=props.get('Location',[0,0,0])[2]+(int(height[y,x])-32768)*props['TerrainScale'][2]/256
  vertices.append(((wx-origin[0])*.01,-(wy-origin[1])*.01,(z-origin[2])*.01))
for y in range(h-1):
 for x in range(w-1):
  if not visible[y,x]:continue
  a=y*w+x;b=a+1;c=a+w;d=c+1;faces.extend([(a,c,b),(b,c,d)] if edge[y,x] else [(a,c,d),(a,d,b)])
mesh=bpy.data.meshes.new('R4NativeHeight16');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('R4NativeTerrain',mesh);bpy.context.collection.objects.link(obj);uv=mesh.uv_layers.new(name='TerrainUV')
for poly in mesh.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  idx=mesh.loops[li].vertex_index;uv.data[li].uv=((idx%w)/(w-1),1-(idx//w)/(h-1))
mat=bpy.data.materials.new('R4OriginalTerrainLayers');mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.95;img=nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(D/'terrain-color.png'));mat.node_tree.links.new(img.outputs['Color'],bs.inputs['Base Color']);mesh.materials.append(mat)
out=CAT/'exports'/('scene-batch1-'+D.name);bpy.ops.wm.save_as_mainfile(filepath=str(D/'scene-with-terrain.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'scene.gltf'),export_format='GLTF_SEPARATE',export_yup=True,export_materials='EXPORT')
data=json.loads((out/'scene.gltf').read_text());p=D/'model.json';model=json.loads(p.read_text(encoding='utf-8'));model['material_count']=len(data.get('materials',[]));model['textured_materials']=sum('baseColorTexture' in m.get('pbrMetallicRoughness',{}) for m in data.get('materials',[]));model['terrain_included']=True
manifest=json.loads((D/'manifest.json').read_text(encoding='utf-8'));zs=[a.get('Location',[0,0,0])[2] for a in manifest['actors']];terrain_min=props.get('Location',[0,0,0])[2]+(int(height.min())-32768)*props['TerrainScale'][2]/256;model['terrain_visible']=sum(z<terrain_min-500 for z in zs)<len(zs)*.7
layers=json.loads((D/'terrain-audit.json').read_text())['layers'];model['note']=manifest['title']+', mapa '+manifest['tile']+': '+str(len(audit['used']))+' actores estaticos; '+str(len(audit['missing']))+' actores pendientes. Terreno original de 16 bits con '+str(len(layers))+' capas activas. Sin BSP, agua, particulas, iluminacion original ni NPCs. Materiales representativos. No instalado en el juego.'
if not model['terrain_visible']:model['note']+=' Terreno oculto inicialmente para no tapar salas subterraneas; usar Mostrar terreno.'
p.write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8');audit['terrain']=dict(vertices=len(vertices),triangles=len(faces),layers=len(layers));(D/'audit-with-terrain.json').write_text(json.dumps(audit,indent=2));print('TERRAIN_ADDED',len(vertices),len(faces),flush=True)
