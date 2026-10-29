"""Open dragon vestibule and recessed three-person lookout; visual NPC provision."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];SOURCE=ROOT/'research/vigilia-ajustes-estructura/Vigilia-estructura.blend'
EXP=ROOT/'research/model-catalog/exports/vigilia-pasaje-dragon';EXP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
def signature(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],list(o.matrix_world))).encode()).hexdigest()
preserved={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and all(c.name!='VIG_16_Mascaron' for c in o.users_collection)}
def mat(fragment):return next(m for m in bpy.data.materials if m.name.startswith('Clan') and fragment in m.name)
wood=mat('Roble restaurado');dark=mat('Nogal oscuro');gold=mat('Bronce envejecido');iron=mat('Hierro negro');red=mat('Tapicería carmesí');light=mat('Farol ámbar')
for key in ['VIG_19_Pasaje_Dragon','VIG_20_Mirador_Dragon','VIG_21_Referencia_Mirador']:
 c=bpy.data.collections.new(key);bpy.context.scene.collection.children.link(c);p=bpy.data.objects.new(key,None);c.objects.link(p)
KEY='VIG_19_Pasaje_Dragon'
def put(o,name,material,key=None):
 key=key or KEY;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[key].objects.link(o);o.parent=bpy.data.objects[key];o.data.materials.append(material);return o
def box(name,p,s,material,be=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=put(bpy.context.object,name,material);o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if be:m=o.modifiers.new('Cantos','BEVEL');m.width=min(be,min(s)*.25);m.segments=2;o.modifiers.new('Normales','WEIGHTED_NORMAL')
 return o
def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return put(o,name,material)
def rod(name,a,b,r,material):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=(b-a).length,location=(a+b)/2);o=put(bpy.context.object,name,material);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def sphere(name,p,s,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=p);o=put(bpy.context.object,name,material);o.scale=s;return o
def fixnorm(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def difference(obj,cutter):
 bpy.context.view_layer.objects.active=obj;m=obj.modifiers.new('Hueco arquitectonico','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name)
neck=next(o for o in bpy.data.objects if o.name.startswith('Madera · cuello tallado'))
skull=next(o for o in bpy.data.objects if o.name.startswith('Madera · craneo y hocico'))
for o in list(bpy.data.collections['VIG_16_Mascaron'].objects):
 if o.name.startswith('Bronce · collar de anclaje'):bpy.data.objects.remove(o,do_unlink=True)
# True vaulted opening, .46 character-height reference, central clear width 1.16.
section=[(-.60,4.10),(.60,4.10),(.60,4.72)]+[(.60*math.cos(math.pi*j/20),4.72+.29*math.sin(math.pi*j/20)) for j in range(1,21)]
n=len(section);vs=[(x,y,z) for x in [13.8,16.4] for y,z in section];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
cut=mesh('Cortador boveda',vs,fs,dark);fixnorm(cut);difference(neck,cut);bpy.data.objects.remove(cut,do_unlink=True)
box('Suelo del pasaje',(14.9,0,4.135),(2.25,1.20,.07),wood)
box('Alfombra roja de acceso',(14.27,-.13,4.178),(2.65,.64,.014),red,.003)
for y in [-.44,.18]:box('Galon dorado alfombra',(14.27,y,4.188),(2.65,.016,.004),gold,.001)
# A continuous bronze arch frames the cut without filling it.
arch=[(-.64,4.18),(-.64,4.72)]+[(-.64*math.cos(math.pi*j/24),4.72+.33*math.sin(math.pi*j/24)) for j in range(1,25)]+[(.64,4.18)]
for (y,z),(yy,zz) in zip(arch,arch[1:]):rod('Marco de entrada abovedada',(14.095,y,z),(14.095,yy,zz),.028,gold)
for y in [-.73,.73]:
 box('Zocalo del portal',(14.17,y,4.25),(.24,.15,.20),dark)
 box('Farol de acceso',(14.06,y,4.70),(.09,.075,.13),light,.008)
 rod('Soporte farol',(14.15,y,4.56),(14.15,y,4.78),.014,gold)
# Side service counter: low enough to see the NPC behind it.
box('Barra de atencion',(14.83,.22,4.315),(.78,.19,.28),dark)
box('Encimera de bronce y nogal',(14.83,.22,4.475),(.84,.26,.055),dark)
for x in [14.5,14.83,15.16]:box('Panel barra',(x,.119,4.32),(.28,.008,.18),wood,.004)
for z in [4.22,4.42]:rod('Moldura barra',(14.44,.11,z),(15.22,.11,z),.009,gold)
rod('Reposapies barra',(14.45,.02,4.24),(15.20,.02,4.24),.012,gold)
box('Libro de registro',(14.68,.21,4.515),(.17,.12,.025),red,.004)
rod('Caliz de mostrador',(15.0,.22,4.50),(15.0,.22,4.56),.023,gold)
for i in range(10):
 x=15.55+(i+.5)*.073;z=4.18+(i+1)*.065
 box('Escalon decorativo',(x,-.12,z-.022),(.077,.62,.044),dark,.004)
 box('Contrahuella cerrada',(x-.035,-.12,z-.0325),(.012,.62,.065),dark,.002)
 box('Alfombra escalera',(x,-.12,z+.002),(.075,.48,.008),red,.001)
 rod('Nariz escalon',(x-.034,-.42,z+.006),(x-.034,.18,z+.006),.006,gold)
for y in [-.48,.25]:
 rod('Pasamano interior',(15.55,y,4.48),(16.28,y,5.13),.011,gold)
 for i in [0,4,9]:
  x=15.55+(i+.5)*.073;z=4.18+(i+1)*.065;rod('Balaustre interior',(x,y,z),(x,y,z+.29),.009,gold)
box('Fondo cerrado de escalera',(16.32,0,4.62),(.10,1.22,1.02),dark)
for y in [-.595,.595]:
 box('Revestimiento lateral escalera',(15.98,y,4.63),(.85,.04,1.04),dark)
box('Panel final decorativo',(16.255,-.12,4.94),(.02,.52,.24),wood,.006)
for y in [-.39,.15]:rod('Marco panel final',(16.235,y,4.83),(16.235,y,5.04),.012,gold)
# Subtle inlaid service medallion reserves a teleporter position, no NPC yet.
rod('Medallon NPC teleport',(13.72,-.15,4.183),(13.72,-.15,4.191),.16,gold)
# A recessed cockpit-like lookout, hollowed into the skull between the horns.
KEY='VIG_20_Mirador_Dragon'
cut=box('Cortador mirador',(19.83,0,9.13),(1.44,1.06,2.0),dark,0)
for o in [neck,skull]:difference(o,cut)
bpy.data.objects.remove(cut,do_unlink=True)
floor=box('Suelo hundido del mirador',(19.83,0,8.145),(1.44,1.06,.07),dark)
box('Alfombra mirador',(19.83,0,8.187),(1.34,.96,.014),red,.004)
# Framing remains below the silhouette of the dragon's brow.
for y in [-.55,.55]:
 box('Borde lateral del hueco',(19.83,y,8.49),(1.54,.07,.10),dark)
 rod('Perfil de bronce mirador',(19.06,y,8.55),(20.60,y,8.55),.018,gold)
for x in [19.06,20.60]:
 box('Borde transversal del hueco',(x,0,8.49),(.07,1.16,.10),dark)
 rod('Perfil transversal mirador',(x,-.55,8.55),(x,.55,8.55),.018,gold)
rod('Sello de llegada teleport',(19.83,0,8.197),(19.83,0,8.205),.16,gold)
for x in [19.12,20.54]:
 for y in [-.49,.49]:sphere('Tacha ambar del mirador',(x,y,8.57),(.028,.028,.028),light)
spots=[(19.39,-.27,8.20),(19.39,.27,8.20),(20.15,0,8.20)]
# Separate reference group for the scale variant only.
KEY='VIG_21_Referencia_Mirador'
for i,(x,y,z) in enumerate(spots):
 sphere('Referencia cabeza '+str(i),(x,y,z+.414),(.052,.052,.056),gold)
 box('Referencia torso '+str(i),(x,y,z+.28),(.14,.085,.19),iron,.018)
 for side in [-1,1]:
  rod('Referencia pierna',(x,y+side*.045,z+.02),(x,y+side*.045,z+.19),.025,iron)
  rod('Referencia brazo',(x,y+side*.085,z+.34),(x,y+side*.12,z+.21),.02,iron)
# Give newly created surfaces a consistent timber projection; keep old UVs intact.
for key in ['VIG_19_Pasaje_Dragon','VIG_20_Mirador_Dragon']:
 for o in bpy.data.collections[key].objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new()
  for p in o.data.polygons:
   axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/3.2,co[axes[1]]/3.2)
assert all(signature(bpy.data.objects[n])==h for n,h in preserved.items())
# Verify three footprints and .46 vertical clearances against the actual cut head.
deps=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
for o in bpy.data.collections['VIG_16_Mascaron'].objects:
 if o.type!='MESH':continue
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.calc_loop_triangles();offset=len(vv);vv.extend(o.matrix_world@v.co for v in me.vertices);ff.extend(tuple(offset+j for j in t.vertices) for t in me.loop_triangles)
bvh=BVHTree.FromPolygons(vv,ff,all_triangles=True)
for x,y,z in spots:
 for dx,dy in [(0,0),(.12,.12),(-.12,-.12),(.12,-.12),(-.12,.12)]:assert bvh.ray_cast(Vector((x+dx,y+dy,z+.01)),Vector((0,0,1)),.47)[0] is None,'Headroom blocked'
manifest={'passed':True,'referenceCharacterHeight':.46,'referenceCharacterWidth':.24,'lookoutCapacity':3,'lookoutClearFloor':[1.34,.96],'lookoutSpotsBlender':spots,'teleportSourceBlender':[13.72,-.15,4.20],'teleportDestinationBlender':[19.83,0,8.21],'teleportSourceThree':[13.72,4.20,.15],'teleportDestinationThree':[19.83,8.21,0],'futureServiceNPCBlender':[14.83,.48,4.18],'stairsDecorative':True,'serverTeleportImplemented':False,'preservedMeshes':len(preserved)}
(OUT/'design-audit.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-pasaje.blend'))
roots=['VIG_16_Mascaron','VIG_19_Pasaje_Dragon','VIG_20_Mirador_Dragon','VIG_21_Referencia_Mirador']
for key in roots:
 items=[o for o in bpy.data.collections[key].objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=key+'_Malla'
bpy.ops.object.select_all(action='DESELECT')
for key in roots:
 for o in bpy.data.collections[key].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'pasaje.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'pasaje.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name'] or m['name']=='Mascaron · madera del casco':m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
g['asset']['copyright']='Original naval dragon figurehead and architectural adaptation. Dragon silhouette visual guide: Red Dragon, GadgetHamster / Alexander Ostrowski, CC BY 4.0; no imported mesh.'
(EXP/'pasaje.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8');print('PASSAGE_READY',manifest,flush=True)
