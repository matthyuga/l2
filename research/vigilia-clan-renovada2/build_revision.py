"""Vigilia revision 2: lateral bridge exits, roof stairs and anchored suspension."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;R=OUT.parents[1];EXPORT=R/'research/model-catalog/exports/vigilia-renovada2';EXPORT.mkdir(parents=True,exist_ok=True)
SOURCE=R/'research/vigilia-clan-renovada1/Vigilia-renovada1.blend';original_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
gold=bpy.data.materials['Clan · Bronce envejecido'];wood=bpy.data.materials['Clan · Roble restaurado'];dark=bpy.data.materials['Clan · Nogal oscuro'];iron=bpy.data.materials['Clan · Hierro negro'];glass=bpy.data.materials['Clan · Parabrisas transparente']
manifest=json.loads((R/'research/vigilia-clan-renovada1/design-manifest.json').read_text(encoding='utf-8'))
for key,title in [('VIG_14_Suspension','Bastidor, tirantes y anclajes del globo'),('VIG_15_Azotea','Escalera trasera y mirador del techo')]:
 c=bpy.data.collections.new(key);scene.collection.children.link(c);o=bpy.data.objects.new(key,None);c.objects.link(o);manifest['zones'].append({'node':key,'title':title,'objects':0})
def put(o,key,material):
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[key].objects.link(o);o.parent=bpy.data.objects[key];o.data.materials.append(material);return o
def box(name,p,size,material,key,be=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=put(bpy.context.object,key,material);o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if be:mod=o.modifiers.new('Cantos','BEVEL');mod.width=min(be,min(size)*.3);mod.segments=2;o.modifiers.new('Normales','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,material,key,N=12):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=(b-a).length,location=(a+b)/2);o=put(bpy.context.object,key,material);o.name=name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def ball(name,p,r,material,key):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=r,location=p);o=put(bpy.context.object,key,material);o.name=name;return o

# Delete the two full-length side units, including their low opaque walls.
for o in list(bpy.data.objects):
 if o.name.startswith(('Mamparo bajo','Vidrio lateral','Jarcia_suspension','Anclaje_bronce')):bpy.data.objects.remove(o,do_unlink=True)
for side in [-1,1]:
 # Only the forward half remains: the aft half is a flush, unobstructed opening.
 box('Mamparo lateral delantero',(-10,side*1.5,5.515),(1.8,.055,.17),dark,'VIG_04_Puente')
 box('Cristal lateral delantero',(-10,side*1.5,5.83),(1.8,.015,.45),glass,'VIG_04_Puente',.004)
 rod('Marco lateral delantero',(-10.9,side*1.5,6.06),(-9.1,side*1.5,6.06),.009,gold,'VIG_04_Puente')

# The old rear eave is at -12.8. Trim it to -12.35; the stair fits behind it.
roof_old_min=-12.8;roof_min=-12.35;roof_max=-9.0
for o in bpy.data.collections['VIG_05_Techo'].objects:
 if o.type!='MESH':continue
 for v in o.data.vertices:
  if o.name.startswith('Techo_rectangular_V3'):
   # Source slab includes a bevel: map its actual -12.8..-9.0 footprint.
   v.co.x=roof_min+(v.co.x-roof_old_min)*(roof_max-roof_min)/(roof_max-roof_old_min)
  elif o.name.startswith('Cornisa_V3'):
   v.co.x=roof_min+(v.co.x-roof_old_min)*(roof_max-roof_min)/(roof_max-roof_old_min)
  elif o.name.startswith('Cornisa_extremo_V3') and sum(q.co.x for q in o.data.vertices)/len(o.data.vertices)<-12:
   v.co.x+=.45

# Rear stair runs across the stern rather than obstructing either lateral exit.
LOW=5.43;TOP=6.44;N=21;RISE=(TOP-LOW)/N;GOING=.13;X=-13.0;Y0=-1.37;WIDTH=.50;KEY='VIG_15_Azotea'
for i in range(N):
 y=Y0+(i+.5)*GOING;z=LOW+(i+1)*RISE
 box('Peldaño al techo',(X,y,z-.018),(WIDTH,GOING+.006,.036),wood,KEY,.004)
 box('Nariz peldaño techo',(X,y-GOING*.45,z+.002),(WIDTH,.008,.004),gold,KEY,.001)
for dx in [-.29,.29]:
 x=X+dx;rod('Pasamano escalera techo',(x,Y0,LOW+.31),(x,Y0+N*GOING,TOP+.31),.008,gold,KEY)
 for i in [0,4,8,12,16,20]:
  y=Y0+(i+.5)*GOING;z=LOW+(i+1)*RISE;rod('Poste escalera techo',(x,y,z),(x,y,z+.31),.007,gold,KEY)
 # Sloping, solid cheeks with a small rectangular section.
 rod('Zanca de escalera techo',(x,Y0,LOW-.045),(x,Y0+N*GOING,TOP-.045),.022,dark,KEY)
box('Descanso inferior techo',(X,Y0-.14,LOW-.025),(.50,.28,.05),wood,KEY,.004)
box('Pasarela a azotea',(-12.60,1.57,TOP-.025),(1.30,.54,.05),wood,KEY,.004)
# Rail the three exposed roof edges, retaining a .54 opening into the landing.
for y in [-1.57,1.63]:
 start_x=roof_min if y<0 else -11.90
 rod('Baranda longitudinal azotea',(start_x,y,TOP+.34),(-9.02,y,TOP+.34),.009,gold,KEY)
 for x in [start_x,-11.25,-10.15,-9.02]:rod('Poste azotea',(x,y,TOP),(x,y,TOP+.34),.007,gold,KEY)
rod('Baranda proa azotea',(-9.02,-1.57,TOP+.34),(-9.02,1.63,TOP+.34),.009,gold,KEY)
for y in [-1.55,-.65,.3,1.0]:rod('Poste popa azotea',(roof_min,y,TOP),(roof_min,y,TOP+.34),.007,gold,KEY)
rod('Baranda popa azotea',(roof_min,-1.57,TOP+.34),(roof_min,1.07,TOP+.34),.009,gold,KEY)
rod('Baranda pasarela exterior',(-13.25,1.84,TOP+.34),(-11.90,1.84,TOP+.34),.009,gold,KEY)
rod('Retorno baranda pasarela',(-11.90,1.84,TOP+.34),(-11.90,1.63,TOP+.34),.009,gold,KEY)
for x in [-13.25,-12.8,-11.90]:rod('Poste pasarela',(x,1.84,TOP),(x,1.84,TOP+.34),.007,gold,KEY)

# Large visible suspension members touch the hull and the envelope at both ends.
stations=[(-15,.35),(-14,2.1),(-12,4.15),(-8,5.1),(-3,5.45),(3,5.35),(8,4.7),(12,3.55),(15,1.7),(16.5,.15)]
def width(x):
 for (a,w),(b,v) in zip(stations,stations[1:]):
  if a<=x<=b:return w+(v-w)*(x-a)/(b-a)
 return .1
def anchor(x,side):
 t=math.asin((x+1)/19.5);rad=math.cos(t)**.72;phi=-.90 if side>0 else -math.pi+.90
 return Vector((x,6.65*rad*math.cos(phi),21+6.15*rad*math.sin(phi)))
anchors=[]
for side in [-1,1]:
 for x in [-12,-6,1,8,12]:
  bottom=Vector((x,side*(width(x)-.055),4.14));top=anchor(x,side);joint=Vector((x,side*(max(width(x),abs(top.y))+.10),9.0))
  rod('Puntal principal inferior',bottom,joint,.045,iron,'VIG_14_Suspension')
  rod('Puntal principal superior',joint,top,.045,iron,'VIG_14_Suspension')
  for p in [bottom,joint,top]:ball('Rótula de bronce',p,.095,gold,'VIG_14_Suspension')
  box('Placa anclada a cubierta',(bottom.x,bottom.y,4.15),(.34,.24,.075),gold,'VIG_14_Suspension')
  for dx in [-.12,.12]:ball('Remache de anclaje',(bottom.x+dx,bottom.y,4.195),.018,iron,'VIG_14_Suspension')
  # An upper clevis overlaps the canvas, with a bronze collar on the spar.
  rod('Collar superior',top.lerp(joint,.015),top.lerp(joint,.04),.07,gold,'VIG_14_Suspension')
  anchors.append({'base':list(bottom),'knee':list(joint),'top':list(top)})
 # Crossed ropes connect successive bays to make the suspension read as a frame.
 for xa,xb in [(-12,-6),(-6,1),(1,8),(8,12)]:
  a=Vector((xa,side*(width(xa)-.055),4.24));b=anchor(xb,side)
  rod('Tensor diagonal de suspensión',a,b,.018,gold,'VIG_14_Suspension')

# Preserve individual objects in the master; batch only the interchange copy.
deps=bpy.context.evaluated_depsgraph_get()
for key in ['VIG_04_Puente','VIG_14_Suspension','VIG_15_Azotea']:
 for o in list(bpy.data.collections[key].objects):
  if o.type!='MESH':continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.transform(o.matrix_world);name=o.name;ob=bpy.data.objects.new(name,me);bpy.data.collections[key].objects.link(ob);ob.parent=bpy.data.objects[key];bpy.data.objects.remove(o,do_unlink=True)
  uv=me.uv_layers.new(name='UV_revision2')
  for p in me.polygons:
   axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/.55,co[axes[1]]/.55)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-renovada2.blend'))
for col in bpy.data.collections:
 if not col.name.startswith('VIG_'):continue
 meshes=[o for o in col.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 if len(meshes)>1:bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=col.name+'_Mobiliario'
bpy.ops.object.select_all(action='DESELECT')
for col in bpy.data.collections:
 if col.name.startswith('VIG_'):
  for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT/'vigilia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
file=EXPORT/'vigilia.gltf';g=json.loads(file.read_text(encoding='utf-8'))
for m in g['materials']:
 if 'Parabrisas transparente' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
file.write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
manifest.update({'name':'Vigilia renovada2','sourceRevision1Hash':original_hash,'sideExits':{'xMin':-12.7,'xMax':-10.9,'sideY':[-1.5,1.5],'flushFloor':True},'roofStair':{'steps':N,'riseL2u':RISE*100,'goingL2u':GOING*100,'widthL2u':WIDTH*100,'x':X,'yStart':Y0,'yEnd':Y0+N*GOING,'zStart':LOW,'zEnd':TOP,'roofRearX':roof_min},'suspensionAnchors':anchors,'gameInstalled':False})
(OUT/'design-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==original_hash
print('VIGILIA_REV2_COMPLETE',len(g['meshes']),sum(len(m['primitives']) for m in g['meshes']))
