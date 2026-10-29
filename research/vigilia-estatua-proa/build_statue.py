import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXP=ROOT/'research/model-catalog/exports/vigilia-estatua';EXP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/vigilia-pasaje-dragon/Vigilia-pasaje.blend'))
KEY='VIG_22_Estatua_Popa';col=bpy.data.collections.new(KEY);bpy.context.scene.collection.children.link(col);parent=bpy.data.objects.new(KEY,None);col.objects.link(parent)
gold=next(m for m in bpy.data.materials if m.name.startswith('Clan') and 'Bronce envejecido' in m.name)
dark=next(m for m in bpy.data.materials if m.name.startswith('Clan') and 'Nogal oscuro' in m.name)
light=next(m for m in bpy.data.materials if m.name.startswith('Mascaron') and 'incrustacion' in m.name)
bronze=gold.copy();bronze.name='Estatua · bronce patinado';p=bronze.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.14,.20,.145,1);p.inputs['Roughness'].default_value=.49
C=Vector((-14.20,0,4.15))
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
cyl('Pedestal · base octogonal',.025,.25,.05,gold);cyl('Pedestal · nogal',.13,.215,.17,dark);cyl('Pedestal · cornisa',.23,.24,.035,gold);cyl('Pedestal · peana',.255,.205,.025,dark)
uv('Dragon · cuerpo sentado',(-.035,0,.43),(.125,.105,.18),bronze)
tube('Dragon · cuello erguido',[(-.04,0,.48),(.015,0,.59),(.055,0,.72),(.13,0,.80)],[.105,.09,.065,.075],bronze)
uv('Dragon · cabeza',(.15,0,.81),(.11,.073,.075),bronze);uv('Dragon · hocico',(.235,0,.795),(.095,.053,.035),bronze)
tube('Dragon · cola enroscada',[(-.09,0,.37),(-.21,0,.30),(-.24,-.14,.29),(-.10,-.20,.29),(.06,-.17,.30),(.10,-.08,.34)],[.065,.05,.035,.025,.017,.002],bronze)
for s in [-1,1]:
 uv('Dragon · anca',(-.065,s*.095,.36),(.10,.068,.095),bronze);uv('Dragon · garra posterior',(.02,s*.10,.29),(.095,.05,.025),gold)
 tube('Dragon · brazo',[(.03,s*.075,.54),(.09,s*.11,.42),(.16,s*.09,.31)],[.035,.025,.023],bronze)
 uv('Dragon · garra delantera',(.18,s*.09,.29),(.052,.032,.02),gold)
 tube('Dragon · cuerno',[(.12,s*.057,.855),(.07,s*.085,.92),(.015,s*.09,.955)],[.025,.018,.001],gold)
 uv('Dragon · ojo ambar',(.20,s*.066,.828),(.018,.009,.012),light)
 wing=[(-.01,s*.075,.59),(-.16,s*.14,.80),(-.29,s*.15,.72),(-.24,s*.13,.43),(-.16,s*.12,.47),(-.11,s*.10,.35)]
 o=mesh('Dragon · ala recogida',wing,[(0,1,2,3,4,5)],bronze);o.modifiers.new('Membrana fundida','SOLIDIFY').thickness=.014
 for a,b in [(0,1),(1,2),(1,3),(1,4),(1,5)]:tube('Dragon · nervadura de ala',[wing[a],wing[b]],[.014,.007],gold)
 for i in range(3):tube('Dragon · dedos',[(.17,s*.09+(i-1)*.017,.30),(.225,s*.09+(i-1)*.02,.28)],[.009,.002],gold)
for i in range(4):
 z=.48+i*.065;x=-.13+i*.025;tube('Dragon · espina dorsal',[(x,0,z),(x-.035,0,z+.055)],[.022,.001],gold)
# The guardian looks out over the stern rather than toward the cabin wall.
turn=Matrix.Translation(C)@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-C)
bpy.context.view_layer.update()
for o in col.objects:
 if o.type=='MESH':o.matrix_world=turn@o.matrix_world
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-estatua.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in col.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=KEY+'_Malla';parent.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'estatua.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
(OUT/'design.json').write_text(json.dumps({'locationBlender':list(C),'height':.96,'pedestalDiameter':.5,'originalGeometry':True,'passageUnchanged':True},indent=2),encoding='utf-8')
