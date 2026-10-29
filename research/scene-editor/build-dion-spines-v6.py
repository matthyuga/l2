"""Four original blade-shaped organic variations following Kevin's sketches."""
from pathlib import Path
import bpy,math,json,random
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R.parent/'model-catalog/exports/dion-spines-v6';O.mkdir(parents=True,exist_ok=True)
assert not (O/'single.glb').exists(),'Preserve existing version'
rng=random.Random(271030)
def mat(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough
 v=m.node_tree.nodes.new('ShaderNodeVertexColor');v.layer_name='TissueTint';m.node_tree.links.new(v.outputs['Color'],s.inputs['Base Color']);return m
def blade(name,base,h,lean,angle,width,depth,material):
 verts=[];faces=[];rings=38;sides=18;direction=Vector((math.cos(angle),math.sin(angle),0));cross=Vector((-math.sin(angle),math.cos(angle),0))
 for i in range(rings):
  t=i/(rings-1);curve=lean*(.25*t+.75*t*t);center=Vector(base)+direction*curve+Vector((0,0,h*t))
  # Broad, asymmetric crescent cross-section, flatter than a conical thorn.
  w=max(.005,width*(1-t)**.85*(1+.30*math.sin(t*math.pi)))
  d=max(.004,depth*(1-t)**1.05)
  for j in range(sides):
   a=j*math.tau/sides;groove=1+.045*math.cos(a*5+t*18)
   p=center+direction*(math.cos(a)*w*groove)+cross*(math.sin(a)*d*groove)
   verts.append(tuple(p))
  if i:
   for j in range(sides):faces.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
 faces.append(tuple(reversed(range(sides))));faces.append(tuple(range((rings-1)*sides,rings*sides)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);mesh.materials.append(material)
 tint=mesh.color_attributes.new(name='TissueTint',type='FLOAT_COLOR',domain='POINT')
 for i,v in enumerate(tint.data):
  t=(i//sides)/(rings-1);v.color=(.13+t*.035,.035+t*.025,.052+t*.02,1)
 for p in mesh.polygons:p.use_smooth=True
 return obj
def foot(name,x,y,r,material):
 # Small asymmetrical rooting collars; deliberately no broad star-shaped membrane.
 verts=[];faces=[];sides=20
 for ring,(z,size) in enumerate([(-.1,1.05),(.05,1),(.32,.55)]):
  for j in range(sides):
   a=j*math.tau/sides;rad=r*size*(1+.15*math.sin(a*5));verts.append((x+math.cos(a)*rad,y+math.sin(a)*rad,z))
  if ring:
   for j in range(sides):faces.append(((ring-1)*sides+j,(ring-1)*sides+(j+1)%sides,ring*sides+(j+1)%sides,ring*sides+j))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);mesh.materials.append(material);color=mesh.color_attributes.new(name='TissueTint',type='FLOAT_COLOR',domain='POINT')
 for v in color.data:v.color=(.16,.035,.052,1)
 for p in mesh.polygons:p.use_smooth=True
for variant in ['single','giant','interlaced','branched']:
 bpy.ops.wm.read_factory_settings(use_empty=True);horn=mat('Quitina acanalada',(.14,.045,.06),.48);flesh=mat('Base orgánica',(.16,.035,.05),.64)
 if variant in ['single','giant']:
  scale=1 if variant=='single' else 1.75
  blade('Espina arqueada' if variant=='single' else 'Hoja orgánica gigante',(0,0,0),3.7*scale,1.45*scale,0,.48*scale,.24*scale,horn);foot('Raíz compacta',0,0,.60*scale,flesh)
 elif variant=='interlaced':
  for i,(x,y,h,lean,a) in enumerate([(-.65,-.2,4.8,2.1,0),(.55,.5,3.7,1.4,math.pi),(-.2,.85,2.8,1.6,.45)]):
   blade(f'Arco entrelazado {i+1}',(x,y,0),h,lean,a,.46,.23,horn);foot(f'Apoyo {i+1}',x,y,.55,flesh)
 else:
  blade('Tronco espinoso',(0,0,0),3.9,1.25,0,.52,.29,horn);foot('Raíz compacta',0,0,.65,flesh)
  blade('Rama lateral',(0.20,0,1.1),1.8,2.1,math.pi,.26,.17,horn)
  blade('Rama superior',(.45,.05,2.05),1.4,1.3,math.pi*.85,.23,.14,horn)
 bpy.ops.export_scene.gltf(filepath=str(O/f'{variant}.glb'),export_format='GLB',export_animations=False,export_yup=True)
 print('VARIANT',variant,flush=True)
(O/'variation-audit.json').write_text(json.dumps({'variants':['single','giant','interlaced','branched'],'sketchInterpretation':'Three aligned independent curved blades; giant single blade; interlaced arcs; branching thorn','static':True,'seed':271030},indent=2))
