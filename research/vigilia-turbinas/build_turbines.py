"""Original naval turbine pair, visually inspired by Astro G-Toilet Cannon."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=ROOT/'research/vigilia-mascaron/Vigilia-mascaron.blend'
EXP=ROOT/'research/model-catalog/exports/vigilia-turbinas'
EXP.mkdir(parents=True,exist_ok=True)
sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
def signature(o):
 if o.type!='MESH':return None
 return hashlib.sha256(repr((list(o.matrix_world),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[m.name for m in o.data.materials])).encode()).hexdigest()
prefixes=('Brazo_motor','Gondola_motor','Costilla_motor','Nucleo_motor_ambar','Eje_helice','Aspa_helice','Buje_helice')
removed=[o.name for o in bpy.data.objects if o.name.startswith(prefixes)]
for n in removed:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
preserved={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
def material(fragment,name,color=None,metal=None,rough=None):
 m=next(m for m in bpy.data.materials if fragment in m.name).copy();m.name=name
 p=m.node_tree.nodes.get('Principled BSDF')
 if color:p.inputs['Base Color'].default_value=(*color,1)
 if metal is not None:p.inputs['Metallic'].default_value=metal
 if rough is not None:p.inputs['Roughness'].default_value=rough
 return m
iron=material('Hierro negro','Turbina · hierro pavonado',(.065,.077,.085),.65,.40)
brass=material('Bronce envejecido','Turbina · bronce envejecido',None,.72,.38)
red=material('Tapicería carmesí','Turbina · esmalte carmesi',(.19,.025,.023),.42,.43)
dark=material('Hierro negro','Turbina · interior sombreado',(.012,.017,.021),.3,.7)
glow=material('Farol ámbar','Turbina · energia ambar',(.65,.24,.035),.3,.32)
p=glow.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.34,.045,1);p.inputs['Emission Strength'].default_value=2.2
for mat in [iron,brass,red]:
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;shader=nodes.get('Principled BSDF')
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=115;noise.inputs['Detail'].default_value=2
 bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.025
 links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal'])
 # Exported glTF uses the material's deliberately subdued roughness.
 shader.inputs['Roughness'].default_value=.52 if mat==iron else .46
created=[]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update()
 o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;created.append(o)
 for p in me.polygons:p.use_smooth=True
 return o
def tube(name,rings,mat,n=48,start=0,end=math.tau):
 # x, radius cross sections around engine axis. Open wall; profile supplies thickness.
 vs=[(x,Y+r*math.cos(start+(end-start)*j/n),Z+r*math.sin(start+(end-start)*j/n)) for x,r in rings for j in range(n+1)]
 fs=[]
 for k in range(len(rings)-1):
  for j in range(n):a=k*(n+1)+j;fs.append((a,a+1,a+n+2,a+n+1))
 return mesh(name,vs,fs,mat)
def ring(name,x,r,t,mat):
 return tube(name,[(x+t*math.sin(math.tau*k/12),r+t*math.cos(math.tau*k/12)) for k in range(13)],mat)
def rod(name,a,b,r,mat,n=12):
 a,b=Vector(a),Vector(b);w=(b-a).normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.01:u=w.cross(Vector((0,1,0)))
 u.normalize();v=w.cross(u)
 vs=[tuple(c+r*(u*math.cos(math.tau*j/n)+v*math.sin(math.tau*j/n))) for c in [a,b] for j in range(n)]
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 return mesh(name,vs,fs,mat)
def box(name,center,size,mat):
 c=Vector(center);vs=[tuple(c+Vector((a*size[0]/2,b*size[1]/2,d*size[2]/2))) for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 o=mesh(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
 be=o.modifiers.new('Bordes de fundicion','BEVEL');be.width=.06;be.segments=2
 return o
for side,label in [(-1,'Babor'),(1,'Estribor')]:
 key='VIG_'+('17' if side==-1 else '18')+'_Turbina_'+label
 col=bpy.data.collections.new(key);bpy.context.scene.collection.children.link(col)
 parent=bpy.data.objects.new(key,None);col.objects.link(parent)
 Y=side*6.35;Z=1.35
 # Hollow, flared aft nozzle and a smaller forward intake.
 tube('Turbina · garganta de escape',[(-10.8,.72),(-11.55,.80),(-12.3,.96),(-13.05,1.18),(-13.62,1.43),(-13.78,1.43),(-13.78,1.27),(-13.05,1.04),(-12.3,.81),(-11.55,.65),(-10.8,.60)],iron)
 ring('Turbina · labio de escape',-13.70,1.36,.13,brass)
 ring('Turbina · aro de energia',-12.77,1.13,.09,glow)
 for x,r in [(-12.9,1.18),(-12.62,1.09)]:ring('Turbina · proteccion del aro',x,r,.065,brass)
 tube('Turbina · carcasa central',[(-12.18,1.03),(-11.9,1.18),(-9.2,1.18),(-8.5,1.02),(-7.65,.99),(-7.42,1.10),(-7.2,1.10),(-7.2,.88),(-7.6,.79),(-8.5,.73)],iron)
 ring('Turbina · borde de admision',-7.29,1.01,.115,brass)
 for x,r in [(-11.85,1.20),(-10.8,1.20),(-9.25,1.20),(-8.45,1.06)]:ring('Turbina · nervadura de carcasa',x,r,.06,brass)
 for j in range(7):
  x=-9.15+j*.085;r=1.19-j*.023
  tube('Turbina · aleta de refrigeracion',[(x-.018,r),(x-.018,r+.13),(x+.018,r+.13),(x+.018,r),(x-.018,r)],iron)
 # Radial ribs and stators create a deep mechanical mouth.
 for j in range(16):
  a=math.tau*j/16
  rod('Turbina · nervio de tobera',(-13.55,Y+1.31*math.cos(a),Z+1.31*math.sin(a)),(-12.0,Y+.94*math.cos(a),Z+.94*math.sin(a)),.035,brass,8)
 for x in [-11.8,-7.9]:
  rod('Turbina · buje',(x-.15,Y,Z),(x+.30,Y,Z),.23,brass,24)
  for j in range(12):
   a=math.tau*j/12
   vs=[]
   for xx,rr,aa in [(x,.22,a),(x+.16,.84,a+.25),(x+.25,.84,a+.43),(x+.03,.22,a+.45)]:vs.append((xx,Y+rr*math.cos(aa),Z+rr*math.sin(aa)))
   o=mesh('Turbina · alabe de rotor',vs,[(0,1,2,3)],brass);o.modifiers.new('Espesor de alabe','SOLIDIFY').thickness=.045
 # Segmented enamel panels and vent slots on the cylindrical casing.
 for j in range(8):
  a=math.tau*j/8+.10
  tube('Turbina · panel de servicio',[(-11.65,1.21),(-9.45,1.21),(-9.45,1.24),(-11.65,1.24),(-11.65,1.21)],red if j in [1,3,5,7] else iron,12,a,a+.54)
  if j in [0,2,4,6]:
   for k in range(6):
    x=-11.35+k*.26
    tube('Turbina · ranura de ventilacion',[(x,1.247),(x+.095,1.247)],dark,8,a+.10,a+.45)
  for x in [-11.45,-9.65]:
   for aa in [a+.06,a+.48]:
    rod('Turbina · remache',(x,Y+1.23*math.cos(aa),Z+1.23*math.sin(aa)),(x,Y+1.29*math.cos(aa),Z+1.29*math.sin(aa)),.043,brass,8)
 # External auxiliary compressors, echoing the reference's side cylinders.
 for a in [0,math.pi,math.pi/2]:
  yy=Y+1.35*math.cos(a);zz=Z+1.35*math.sin(a)
  rod('Turbina · compresor auxiliar',(-11.65,yy,zz),(-9.45,yy,zz),.25,iron,20)
  for x in [-11.65,-11.40,-9.65,-9.45]:rod('Turbina · collar del compresor',(x-.045,yy,zz),(x+.045,yy,zz),.29,brass,20)
  rod('Turbina · tuberia de presion',(-11.9,yy,zz+.32),(-8.75,yy,zz+.32),.055,brass)
 for x in [-11.6,-9.4]:
  box('Turbina · soporte del casco',(x,side*4.45,1.50),(.65,.55,.80),brass)
  rod('Turbina · brazo de bancada',(x,side*3.85,1.9),(x,Y,1.25),.18,iron)
  rod('Turbina · tirante diagonal',(x+.7,side*3.70,.25),(x,Y,.8),.115,brass)
  box('Turbina · silla de montaje',(x,Y,1.22),(.33,2.5,.30),iron)
assert all(signature(bpy.data.objects[n])==h for n,h in preserved.items())
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-turbinas.blend'))
roots=['VIG_00_Casco','VIG_17_Turbina_Babor','VIG_18_Turbina_Estribor']
for key in roots:
 items=[o for o in bpy.data.collections[key].objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=key+'_Malla'
bpy.ops.object.select_all(action='DESELECT')
for key in roots:
 for o in bpy.data.collections[key].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'turbinas.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'turbinas.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
g['asset']['copyright']='Original naval turbines. Visual reference: Astro G-Toilet Cannon (Sketchfab a5f05f0430ce451f880e79dd45272ae5), Eveston / EvesStudio2008, CC BY 4.0. No source mesh used.'
(EXP/'turbinas.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sourcehash
report={'sourceHash':sourcehash,'removedOriginalEngineParts':removed,'preservedMeshes':len(preserved),'preservedGeometryUnchanged':True,'newParts':len(created),'sourceMeshUsed':False,'roots':roots}
(OUT/'design-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('TURBINES_READY',len(created),len(preserved),flush=True)
