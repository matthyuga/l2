"""Original sculpt-like figurehead inspired by winner_77's public reference image.
No Sketchfab mesh is downloaded or reconstructed from viewer data.
Blender coordinates: +X bow, Y port/starboard, Z up. Preserve all other ship parts.
"""
import bpy,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXP=ROOT/'research/model-catalog/exports/vigilia-dragon-sculpt';EXP.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'research/vigilia-clan-renovada2/Vigilia-renovada2.blend';sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
prefixes=('Cuello_acorazado','Cabeza_angular','Mandibula_dentada','Garganta_oscura','Orbita_hundida','Iris_draconico','Pupila_vertical','Ceja_acorazada','Mandibula_filigrana','Cuerno_anillado','Abanico_mejilla','Nervio_mejilla','Colmillo_superior','Diente_inferior','Narina_profunda','Narina_borde','Escama_cuello','Grabado_escama','Cresta_dorsal','Placa_frente')
old=[o for o in bpy.data.collections['VIG_00_Casco'].objects if o.name.startswith(prefixes)]
if len(old)<50:raise RuntimeError('Incomplete old head identification: '+str(len(old)))
removed=[o.name for o in old]
def signature(o):
 h=hashlib.sha256();h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode());h.update(str([m.name if m else '' for m in o.data.materials]).encode())
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
preserved={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o not in old}
for o in old:bpy.data.objects.remove(o,do_unlink=True)
collection=bpy.data.collections.new('VIG_16_Dragon');scene.collection.children.link(collection)
parent=bpy.data.objects.new('VIG_16_Dragon',None);collection.objects.link(parent)
def mat(name,color,metal=.65,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
 if emission:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emission
 return m
bronze=mat('Dragon · bronce patinado',(.19,.155,.085),.72,.57)
gold=mat('Dragon · bordes de bronce antiguo',(.36,.235,.085),.74,.46)
plate=mat('Dragon · escamas de bronce verde',(.115,.16,.105),.70,.54)
lightplate=mat('Dragon · relieves gastados',(.255,.235,.14),.70,.48)
shadow=mat('Dragon · hendiduras oscuras',(.014,.024,.022),.35,.72)
ivory=mat('Dragon · colmillos de laton',(.48,.39,.22),.48,.38)
eye=mat('Dragon · ojos de turquesa',(.018,.29,.25),.28,.22,.12)
created=[]
def put(o,name,material):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.parent=parent
 o.data.materials.clear();o.data.materials.append(material)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 created.append(o);return o
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);collection.objects.link(o);o.parent=parent;o.data.materials.append(material)
 for p in me.polygons:p.use_smooth=True
 created.append(o);return o
def ellipsoid(name,pos,scale,material,rotation=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=16,radius=1,location=pos);o=put(bpy.context.object,name,material);o.scale=scale
 if rotation:o.rotation_euler=rotation
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def catmull(points,steps=10):
 p=[Vector(v) for v in points];result=[]
 for i in range(len(p)-1):
  a,b,c,d=p[max(i-1,0)],p[i],p[i+1],p[min(i+2,len(p)-1)]
  for j in range(steps):
   t=j/steps;result.append((b*2+(c-a)*t+(a*2-b*5+c*4-d)*t*t+(-a+b*3-c*3+d)*t*t*t)*.5)
 result.append(p[-1]);return result
def sweep(name,points,radii,material,sides=16,steps=10,rib=0):
 path=catmull(points,steps);vs=[];fs=[]
 for i,p in enumerate(path):
  tangent=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized();axis=Vector((0,1,0))
  if abs(axis.dot(tangent))>.9:axis=Vector((0,0,1))
  u=tangent.cross(axis).normalized();v=tangent.cross(u).normalized();t=i/(len(path)-1)*(len(radii)-1);k=min(int(t),len(radii)-2);r=max(.002,radii[k]*(1-(t-k))+radii[k+1]*(t-k));r*=1+rib*math.sin(i*1.35)
  for j in range(sides):vs.append(tuple(p+r*(u*math.cos(math.tau*j/sides)+v*math.sin(math.tau*j/sides))))
  if i:
   for j in range(sides):a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
 fs.extend([tuple(reversed(range(sides))),tuple((len(path)-1)*sides+j for j in range(sides))]);return mesh(name,vs,fs,material)
def armor(name,center,normal,direction,length,width,depth,material):
 n=Vector(normal).normalized();u=Vector(direction);u=(u-n*u.dot(n)).normalized();v=n.cross(u);c=Vector(center)
 outline=[(-.52,0),(-.31,-.44),(.10,-.50),(.52,0),(.10,.50),(-.31,.44)];verts=[]
 for f,z in [(1,0),(.74,depth*.70),(.24,depth)]:
  for x,y in outline:verts.append(tuple(c+u*x*length*f+v*y*width*f+n*z))
 faces=[]
 for ring in range(2):
  for j in range(6):faces.append((ring*6+j,ring*6+(j+1)%6,(ring+1)*6+(j+1)%6,(ring+1)*6+j))
 faces.extend([tuple(reversed(range(6))),tuple(range(12,18))]);o=mesh(name,verts,faces,material);be=o.modifiers.new('Cantos pulidos','BEVEL');be.width=.017;be.segments=2;return o

# Continuous anatomy: remesh overlapping volumes into a single sculpted bronze surface.
anatomy=[]
anatomy.append(sweep('Cuello continuo',[(14.45,0,4.25),(16.0,0,4.95),(17.55,0,6.6),(18.8,0,7.9),(20.0,0,8.15)],[.96,1.02,.88,.85,.75],bronze,24,12))
for name,pos,size,rot in [
 ('Craneo continuo',(20.0,0,8.15),(1.55,1.03,.93),None),
 ('Puente nasal',(21.15,0,7.98),(1.22,.65,.50),(0,.04,0)),
 ('Menton',(21.65,0,6.97),(1.8,.58,.23),(0,-.06,0)),
 ('Articulacion mandibular',(20.05,0,7.38),(.76,.76,.54),None)]:anatomy.append(ellipsoid(name,pos,size,bronze,rot))
vs=[];fs=[]
outline=[(0,1),(.72,.82),(1,.30),(.96,-.48),(.61,-.80),(0,-.88),(-.61,-.80),(-.96,-.48),(-1,.30),(-.72,.82)]
for i,(x,z,ry,rz) in enumerate([(21.1,7.92,.67,.49),(21.8,7.90,.62,.42),(22.65,7.91,.57,.34),(23.32,7.92,.43,.31),(23.65,7.90,.16,.18)]):
 for y,zz in outline:vs.append((x,y*ry,z+zz*rz))
 if i:
  for j in range(10):a=(i-1)*10+j;b=(i-1)*10+(j+1)%10;fs.append((a,b,b+10,a+10))
fs.extend([tuple(reversed(range(10))),tuple(range(40,50))]);anatomy.append(mesh('Hocico de perfiles tallados',vs,fs,bronze))
bpy.ops.object.select_all(action='DESELECT')
for o in anatomy:o.select_set(True)
bpy.context.view_layer.objects.active=anatomy[0];bpy.ops.object.join();body=bpy.context.object;body.name='Dragon · anatomia continua'
rem=body.modifiers.new('Fusion organica voxel','REMESH');rem.mode='VOXEL';rem.voxel_size=.050;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
smooth=body.modifiers.new('Suavizado de anatomia','SMOOTH');smooth.factor=.8;smooth.iterations=4;bpy.ops.object.modifier_apply(modifier=smooth.name)
for f in body.data.polygons:f.use_smooth=True
print('ANATOMY_READY',len(body.data.polygons),flush=True)

# Mouth cavity, raised lips, tapered curved fangs and inset nostrils.
ellipsoid('Boca · cavidad profunda',(22.0,0,7.27),(1.42,.57,.18),shadow)
for side in [-1,1]:
 sweep('Labio superior tallado',[(20.6,side*.70,7.56),(21.1,side*.68,7.62),(21.8,side*.61,7.43),(22.7,side*.54,7.48),(23.5,side*.28,7.64)],[.075,.08,.055,.045,.025],bronze)
 sweep('Borde de mandibula',[(20.2,side*.63,7.14),(21.2,side*.59,6.94),(22.4,side*.53,7.00),(23.25,side*.32,7.19)],[.07,.055,.05,.025],bronze)
 for j in range(7):
  x=20.9+j*.34;drop=.54 if j in (1,4) else .28
  sweep('Colmillo superior curvo',[(x,side*.49,7.50),(x+.04,side*.48,7.50-drop*.7),(x+.15,side*.46,7.50-drop)],[.115 if j in (1,4) else .057,.045,0],ivory,12,5)
 for j in range(5):
  x=21.2+j*.39;sweep('Diente inferior',[(x,side*.47,7.04),(x+.02,side*.46,7.20),(x-.04,side*.44,7.28)],[.044,.025,0],ivory,10,5)
 ellipsoid('Narina ahuecada',(23.10,side*.51,8.04),(.25,.055,.115),shadow,(0,-.20,0))
 sweep('Narina · borde esculpido',[(22.8,side*.55,8.08),(23.05,side*.57,8.22),(23.34,side*.43,8.12)],[.035,.05,.018],gold,12)
 # Separate brow sockets, turquoise eyes and severe lids.
 ellipsoid('Cuenca del ojo',(20.7,side*.96,8.42),(.43,.12,.18),shadow,(0,.23,0))
 ellipsoid('Ojo de turquesa',(20.82,side*1.065,8.43),(.21,.055,.082),eye,(0,.23,0))
 ellipsoid('Pupila vertical',(20.85,side*1.12,8.44),(.025,.014,.066),shadow)
 sweep('Ceja · arco severo',[(20.0,side*.93,8.71),(20.48,side*1.07,8.64),(20.96,side*.97,8.51),(21.40,side*.76,8.27)],[.13,.17,.13,.045],lightplate,16)
 sweep('Parpado inferior',[(20.28,side*1.02,8.34),(20.72,side*1.12,8.31),(21.14,side*.89,8.34)],[.035,.045,.025],bronze,12)
 # Long swept horns echo the reference, with their own tapered growth rings.
 horn=[(19.25,side*.72,8.65),(18.85,side*1.13,9.52),(17.5,side*1.75,10.24),(15.95,side*1.95,10.05),(15.10,side*1.65,8.65)]
 sweep('Gran cuerno barrido',horn,[.31,.23,.155,.085,0],gold,20,14,.018)
 # Sculpted cheek frill: a curved bronze membrane supported by horns and ribs.
 anchor=Vector((18.65,side*.72,7.50));edge=catmull(horn,8);vs=[];faces=[]
 for j,p in enumerate(edge):
  for k in range(5):
   t=k/4;v=anchor.lerp(p,t);v.y+=side*.15*math.sin(t*math.pi)*math.sin(j/len(edge)*math.pi);vs.append(tuple(v))
  if j:
   for k in range(4):a=(j-1)*5+k;faces.append((a,a+1,a+6,a+5))
 frill=mesh('Abanico posterior nervado',vs,faces,plate);sol=frill.modifiers.new('Espesor de bronce','SOLIDIFY');sol.thickness=.045
 for j in [7,13,20,26,31]:sweep('Nervadura de abanico',[tuple(anchor),tuple(anchor.lerp(edge[j],.5)+Vector((0,side*.10,0))),tuple(edge[j])],[.065,.05,.02],lightplate,10,8)
 for j in range(4):
  x=19.25-j*.26;z=8.18-j*.37;sweep('Espina de mejilla',[(x,side*.80,z),(x-.55,side*1.18,z+.16),(x-1.05,side*1.35,z+.32)],[.18,.10,0],gold,12,8)

# Overlapping shield scales wrap around the neck. Small irregularity avoids a grid.
rng=random.Random(1729)
for row in range(12):
 t=row/11;cx=15.0+4.55*t;cz=4.6+3.65*t;radius=.98-.12*t
 direction=Vector((1,0,.8)).normalized()
 for band in range(9):
  a=math.tau*band/9+(row%2)*.13;n=Vector((-.5*math.sin(a),math.cos(a),.62*math.sin(a))).normalized();c=(cx,radius*math.cos(a),cz+radius*.90*math.sin(a))
  armor('Escama de cuello',c,n,direction,.70+rng.random()*.08,.59,.10,[plate,lightplate,bronze][(row+band)%3])
# Throat armor: broad articulated ventral plates, tapering towards the jaw.
for j in range(9):
 t=j/8;armor('Placa de garganta',(15.0+t*5.0,0,3.75+t*3.05),(.5,0,-.85),(1,0,.55),.69,1.58-.55*t,.12,gold if j%3==0 else lightplate)
for row in range(7):
 x=19.0+row*.44;f=max(.15,math.sqrt(max(.02,1-((x-20.05)/1.8)**2)))
 for band in range(11):
  a=-.20+band*math.pi*1.4/10
  # Eye recess stays free of overlaid scale geometry.
  if 20.25<x<21.40 and (abs(math.cos(a))>.8 and math.sin(a)>.03):continue
  n=Vector(((x-20.05)/2,math.cos(a),math.sin(a))).normalized();c=(x,1.03*f*math.cos(a),8.15+.92*f*math.sin(a))
  armor('Escama craneal',c,n,(1,0,.12),.54,.40,.075,lightplate if (row+band)%4==0 else plate)
# Smaller overlapping cheek and muzzle scutes carry detail beyond the forehead.
for side in [-1,1]:
 for row in range(8):
  x=21.05+row*.28;yy=side*(.67-row*.035);zz=8.05-row*.012
  for band in range(3):
   armor('Escama del hocico',(x,yy,zz+(band-1)*.17),(0,side*.95,.20),(1,0,-.05),.39,.24,.045,plate if (row+band)%3 else lightplate)
 for j in range(4):sweep('Arruga de expresion',[(21.15+j*.21,side*(.72-j*.025),8.29),(21.24+j*.21,side*(.77-j*.03),8.10),(21.38+j*.21,side*(.70-j*.03),7.91)],[.013,.021,.012],shadow,8,6)
# Nasal ridge, central horn, chin points and a stepped dorsal crown.
for j in range(5):armor('Placa nasal',(21.15+j*.45,0,8.57-j*.10),(0,0,1),(1,0,-.16),.70,.62-j*.045,.12,lightplate)
sweep('Cuerno nasal',[(23.05,0,8.18),(23.30,0,8.62),(23.18,0,9.07)],[.23,.15,0],gold,16,12)
for j in range(8):
 t=j/7;x=15.2+4.7*t;z=5.55+3.50*t
 sweep('Corona dorsal',[(x,0,z),(x-.22,0,z+.51),(x-.70,0,z+.88)],[.18,.12,0],gold,12,8)
for side in [-1,1]:sweep('Espolon de mandibula',[(20.35,side*.48,7.02),(20.02,side*.68,6.72),(19.72,side*.74,6.65)],[.14,.09,0],gold,12,8)

assert all(signature(bpy.data.objects[n])==h for n,h in preserved.items()),'Other ship geometry changed'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sourcehash
scene['dragon_recreation']='Original sculpt-inspired geometry from visual reference; not the Sketchfab mesh.'
scene['dragon_reference']='winner_77 / 9557cfecc9fc489295e23bc91a57d603'
scene['game_installed']=False
head_parts=sum(o.type=='MESH' for o in collection.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-dragon-recreado.blend'))
print('MASTER_SAVED',flush=True)

# Export only replacement hull and the new head. Other zones reuse the original glTF.
for key in ['VIG_00_Casco','VIG_16_Dragon']:
 col=bpy.data.collections[key];items=[o for o in col.objects if o.type in {'MESH','CURVE'}];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH')
 # Apply evaluated detail modifiers before material batching.
 for o in list(bpy.context.selected_objects):
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except RuntimeError:pass
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();bpy.context.object.name=key+'_Malla'
bpy.ops.object.select_all(action='DESELECT')
for key in ['VIG_00_Casco','VIG_16_Dragon']:
 for o in bpy.data.collections[key].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'dragon.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
g=json.loads((EXP/'dragon.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
(EXP/'dragon.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
report={'sourceHash':sourcehash,'removedOldHeadParts':removed,'preservedShipObjects':len(preserved),'otherShipGeometryUnchanged':True,'newHeadParts':head_parts,'exportTriangles':triangles,'export':str(EXP/'dragon.gltf'),'gameInstalled':False,'originalGeometry':True,'reference':'https://sketchfab.com/3d-models/dragon-head-3d-print-model-57x50x57-9557cfecc9fc489295e23bc91a57d603'}
(OUT/'recreation-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print('DRAGON_RECREATED',triangles,flush=True)
