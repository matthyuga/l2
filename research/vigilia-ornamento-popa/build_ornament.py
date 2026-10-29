import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXP=ROOT/'research/model-catalog/exports/vigilia-ornamento-popa';EXP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/vigilia-pasaje-dragon/Vigilia-pasaje.blend'))
KEY='VIG_22_Ornamento_Popa';col=bpy.data.collections.new(KEY);bpy.context.scene.collection.children.link(col);parent=bpy.data.objects.new(KEY,None);col.objects.link(parent)
gold=next(m for m in bpy.data.materials if m.name.startswith('Clan') and 'Bronce envejecido' in m.name)
dark=next(m for m in bpy.data.materials if m.name.startswith('Clan') and 'Nogal oscuro' in m.name)
light=next(m for m in bpy.data.materials if m.name.startswith('Mascaron') and 'incrustacion' in m.name)
bronze=gold.copy();bronze.name='Estatua · bronce patinado';p=bronze.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.14,.20,.145,1);p.inputs['Roughness'].default_value=.49
C=Vector((-15.15,0,3.0))
def put(o,name,mat):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.name=name;o.parent=parent;o.data.materials.append(mat);return o
def uv(name,p,s,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=C+Vector(p));o=put(bpy.context.object,name,mat);o.scale=s
 for f in o.data.polygons:f.use_smooth=True
 return o
def cyl(name,z,r,d,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=d,location=C+Vector((0,0,z)));o=put(bpy.context.object,name,mat);m=o.modifiers.new('Cantos de fundicion','BEVEL');m.width=.008;m.segments=2;return o
def tube(name,pts,rs,mat):
 vs=[];fs=[];ps=[C+Vector(p) for p in pts]
 for i,c in enumerate(ps):
  t=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized();u=t.cross(Vector((0,1,0))).normalized();v=t.cross(u)
  for j in range(12):vs.append(c+rs[i]*(u*math.cos(math.tau*j/12)+v*math.sin(math.tau*j/12)))
  if i:
   for j in range(12):a=(i-1)*12+j;b=(i-1)*12+(j+1)%12;fs.append((a,b,b+12,a+12))
 fs.extend([tuple(reversed(range(12))),tuple((len(ps)-1)*12+j for j in range(12))]);return mesh(name,vs,fs,mat,world=True)
def mesh(name,vs,fs,mat,world=False):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v if world else C+Vector(v)) for v in vs],[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;me.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 return o
# Exterior stern carving: a vertical dragon guardian, no deck pedestal.
# The solid end closure remains behind the carving as structural backing.
tube('Soporte tallado de popa',[(.06,0,-1.27),(-.04,0,-1.0),(-.12,0,-.60),(-.17,0,-.15),(-.17,0,.40),(-.08,0,.93)],[.025,.08,.13,.19,.22,.24],dark)
tube('Dragon - cuello del remate',[(-.08,0,-.94),(-.24,0,-.58),(-.30,0,-.14),(-.32,0,.26),(-.44,0,.52)],[.07,.12,.18,.20,.21],bronze)
uv('Dragon - craneo del remate',(-.49,0,.55),(.27,.235,.22),bronze)
uv('Dragon - hocico tallado',(-.74,0,.48),(.30,.16,.13),bronze)
tube('Dragon - mandibula',[(-.43,0,.28),(-.68,0,.26),(-.91,0,.34)],[.13,.105,.055],dark)
for s in [-1,1]:
 tube('Dragon - cuerno de popa',[(-.36,s*.16,.67),(-.20,s*.30,.89),(-.07,s*.37,1.12),(-.13,s*.36,1.30)],[.085,.068,.038,.002],gold)
 uv('Dragon - ojo de popa',(-.64,s*.205,.58),(.07,.028,.038),light)
 tube('Dragon - ceja',[(-.43,s*.20,.73),(-.60,s*.24,.69),(-.74,s*.18,.60)],[.045,.045,.014],gold)
 # Fan-shaped cast cheek plates follow the taper of the stern instead of occupying the deck.
 wing=[(-.22,s*.17,.48),(-.02,s*.56,.86),(.03,s*.50,.31),(-.04,s*.36,-.10),(-.16,s*.17,-.52)]
 o=mesh('Dragon - aleta de popa',wing,[(0,1,2,3,4)],bronze);o.modifiers.new('Relieve de fundicion','SOLIDIFY').thickness=.04
 for a,b in [(0,1),(0,2),(0,3),(0,4)]:tube('Dragon - nervadura del remate',[wing[a],wing[b]],[.027,.012],gold)
 tube('Voluta lateral de popa',[(.04,s*.32,.93),(-.06,s*.40,.58),(-.10,s*.31,.12),(-.07,s*.19,-.50),(.02,s*.07,-1.10)],[.024,.028,.024,.020,.003],gold)
 for j in range(3):
  x=-.54-j*.13;z=.38+j*.012;tube('Colmillo del remate',[(x,s*.12,z),(x-.025,s*.11,z-.08)],[.023,.001],gold)
for j in range(5):
 z=-.78+j*.18;uv('Escama de garganta',(-.26-j*.015,0,z),(.055,.09+j*.012,.10),gold)
# Replace the projecting stern wedge with a near-flat closed backing for the carving.
bpy.context.view_layer.update()
for o in bpy.data.collections['VIG_00_Casco'].objects:
 if o.type!='MESH' or not o.name.startswith(('Casco_curvo_listones','Remate de cubierta','Remate de borda')):continue
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  w=o.matrix_world@v.co
  if w.x<-15.025:w.x=-15.025;v.co=inv@w
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-ornamento.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in col.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=KEY+'_Malla';parent.select_set(True)
bpy.ops.object.select_all(action='DESELECT')
items=[o for o in bpy.data.collections['VIG_00_Casco'].objects if o.type=='MESH']
for o in items:o.select_set(True)
bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='VIG_00_Casco_Malla'
for c in [col,bpy.data.collections['VIG_00_Casco']]:
 for o in c.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'ornamento.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'ornamento.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
(EXP/'ornamento.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
(OUT/'design.json').write_text(json.dumps({'locationBlender':list(C),'exteriorSternOrnament':True,'deckStatueRemoved':True,'originalGeometry':True,'passageUnchanged':True},indent=2),encoding='utf-8')
