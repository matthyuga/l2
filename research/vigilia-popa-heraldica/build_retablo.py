import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXP=ROOT/'research/model-catalog/exports/vigilia-popa-heraldica';EXP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/vigilia-ornamento-popa/Vigilia-ornamento.blend'))

for o in list(bpy.data.collections['VIG_22_Ornamento_Popa'].objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(bpy.data.collections['VIG_22_Ornamento_Popa'])
KEY='VIG_22_Retablo_Popa';col=bpy.data.collections.new(KEY);bpy.context.scene.collection.children.link(col);parent=bpy.data.objects.new(KEY,None);col.objects.link(parent)
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
  t=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized();u=t.cross(Vector((0,1,0)) if abs(t.y)<.95 else Vector((0,0,1))).normalized();v=t.cross(u)
  for j in range(12):vs.append(c+rs[i]*(u*math.cos(math.tau*j/12)+v*math.sin(math.tau*j/12)))
  if i:
   for j in range(12):a=(i-1)*12+j;b=(i-1)*12+(j+1)%12;fs.append((a,b,b+12,a+12))
 fs.extend([tuple(reversed(range(12))),tuple((len(ps)-1)*12+j for j in range(12))]);return mesh(name,vs,fs,mat,world=True)
def mesh(name,vs,fs,mat,world=False):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v if world else C+Vector(v)) for v in vs],[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;me.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 return o
# Symmetrical stern cartouche inspired by baroque naval scrollwork.
# All ornament is outside the hull; its upper edge stays below the deck rail.
def smooth(pts,steps=10):
 ps=[Vector(p) for p in pts];out=[]
 for i in range(len(ps)-1):
  a,b,c,d=ps[max(0,i-1)],ps[i],ps[i+1],ps[min(len(ps)-1,i+2)]
  for j in range(steps):
   t=j/steps;out.append(tuple(.5*(2*b+(c-a)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
 return out+[tuple(ps[-1])]
def scroll(name,pts,r,mat):
 ps=smooth(pts);tube(name,ps,[r*(.55+.45*math.sin(math.pi*i/(len(ps)-1))**.5) for i in range(len(ps))],mat)
def relief(name,outline,x,depth,mat):
 # Raised bevel with a ridge rather than a flat decal.
 cy=sum(y for y,z in outline)/len(outline);cz=sum(z for y,z in outline)/len(outline);vs=[];n=len(outline)
 for inset,xx in [(1,x),(.84,x-depth*.65),(.30,x-depth)]:
  vs.extend((xx,cy+(y-cy)*inset,cz+(z-cz)*inset) for y,z in outline)
 fs=[]
 for k in range(2):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple(range(2*n,3*n))]);return mesh(name,vs,fs,mat)
outline=[(0,1.08),(.27,.99),(.40,.72),(.35,.30),(.24,-.17),(.13,-.77),(0,-1.29),(-.13,-.77),(-.24,-.17),(-.35,.30),(-.40,.72),(-.27,.99)]
relief('Nogal - retablo del remate',outline,-.06,.13,dark)
scroll('Bronce - contorno del retablo',[(-.13,y,z) for y,z in outline+[outline[0]]],.025,gold)
shield=[(0,.76),(.24,.68),(.25,.42),(.16,.12),(0,-.08),(-.16,.12),(-.25,.42),(-.24,.68)]
relief('Bronce - escudo central',shield,-.22,.055,gold)
relief('Nogal - campo del escudo',[(y*.80,.35+(z-.35)*.82) for y,z in shield],-.282,.025,dark)
# Compass-sun medallion recalls Soleil Royal without importing its sculpture.
for j in range(12):
 a=math.tau*j/12;r=.145 if j%3==0 else .12
 relief('Bronce - rayo heraldico',[(.055*math.cos(a-.25),.40+.055*math.sin(a-.25)),(r*math.cos(a),.40+r*math.sin(a)),(.055*math.cos(a+.25),.40+.055*math.sin(a+.25))],-.32,.014,gold)
uv('Ambar - sello central',(-.345,0,.40),(.025,.052,.052),light)
# Twin S scrolls lie against the two stern quarters, widening only near the top.
for s in [-1,1]:
 ps=[(.02,s*.08,-1.16),(-.12,s*.19,-.63),(-.19,s*.36,-.12),(-.17,s*.57,.39),(-.10,s*.63,.77),(-.09,s*.46,.92),(-.17,s*.34,.78),(-.20,s*.40,.63),(-.19,s*.49,.68)]
 scroll('Bronce - gran voluta lateral',ps,.041,gold)
 scroll('Nogal - tallo de acanto',[(x+.025,y*1.04,z-.018) for x,y,z in ps],.066,dark)
 # Separate fleshy acanthus leaves and engraved midribs.
 for k in range(5):
  z=-.72+k*.28;y=s*(.17+k*.062)
  leaf=[(y,z-.12),(y+s*.12,z-.045),(y+s*.18,z+.15),(y+s*.08,z+.12),(y,z+.035),(y-s*.03,z-.025)]
  relief('Bronce - hoja de acanto',leaf,-.19,.045,gold)
  scroll('Nogal - nervio de hoja',[(-.24,y,z-.09),(-.25,y+s*.07,z+.04),(-.21,y+s*.17,z+.14)],.008,dark)
 # Small lower curls tie into the keel rather than ending as a spike.
 scroll('Bronce - voluta inferior',[(-.15,0,-1.22),(-.19,s*.13,-.97),(-.20,s*.23,-.78),(-.20,s*.19,-.66),(-.21,s*.12,-.72)],.018,gold)
# Shell-shaped crown at the top, below the railing.
fan=[(0,.75),(.35,.94),(.32,1.09),(.18,1.14),(0,1.16),(-.18,1.14),(-.32,1.09),(-.35,.94)]
relief('Nogal - couronnement en concha',fan,-.16,.04,dark)
for j in range(9):
 a=-1+j/4;y=.31*a;z=1.13-.15*abs(a)
 scroll('Bronce - nervadura de concha',[(-.22,0,.79),(-.23,y*.62,.99),(-.20,y,z)],.013,gold)
scroll('Bronce - borde de concha',[(-.205,y,z) for y,z in fan[1:]+[fan[1]]],.021,gold)
# Three narrow hanging reliefs taper into the lower stem.
for z,r in [(-.25,.085),(-.43,.068),(-.59,.05)]:
 relief('Bronce - gota del remate',[(0,z+.08),(r,z),(0,z-.12),(-r,z)],-.22,.03,gold)
# Replace the projecting stern wedge with a near-flat closed backing for the carving.
bpy.context.view_layer.update()
for o in bpy.data.collections['VIG_00_Casco'].objects:
 if o.type!='MESH' or not o.name.startswith(('Casco_curvo_listones','Remate de cubierta','Remate de borda')):continue
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  w=o.matrix_world@v.co
  if w.x<-15.025:w.x=-15.025;v.co=inv@w
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-retablo.blend'))
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
bpy.ops.export_scene.gltf(filepath=str(EXP/'retablo.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'retablo.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
(EXP/'retablo.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
(OUT/'design.json').write_text(json.dumps({'locationBlender':list(C),'exteriorSternOrnament':True,'deckStatueRemoved':True,'originalGeometry':True,'passageUnchanged':True},indent=2),encoding='utf-8')
