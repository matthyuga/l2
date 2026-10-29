"""Vigilia clan renovation. Preserve V3 hull and calibrated furniture, 100 L2u/design unit."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;EXPORT=R/'research/model-catalog/exports/vigilia-renovada1';EXPORT.mkdir(parents=True,exist_ok=True)
source=R/'research/vigilia-clan-v3/Vigilia-clan-v3.blend';sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
for c in list(bpy.data.collections):
 if 'ESTUDIO' in c.name:
  for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(c)
zones={}
def zone(key,title):
 c=bpy.data.collections.new(key);scene.collection.children.link(c);zones[key]={'title':title,'collection':c};return key
H=zone('VIG_00_Casco','Casco, escamas y cabeza de dragón');B=zone('VIG_01_Globo','Globo carmesí y heráldica');D=zone('VIG_02_Cubierta','Cubierta restaurada');S=zone('VIG_03_Escaleras','Dos escaleras a escala de personaje');P=zone('VIG_04_Puente','Puente de mando y timón');T=zone('VIG_05_Techo','Techo del puente');Q=zone('VIG_06_Aposento','Aposento del capitán');F=zone('VIG_07_Muebles','Mobiliario V3 conservado');C=zone('VIG_08_Consejo','Consejo y estrategia del clan');M=zone('VIG_09_Cantina','Cantina y descanso');A=zone('VIG_10_Armeria','Armería, estandartes y trofeos');G=zone('VIG_11_Galeria','Galería de reuniones');L=zone('VIG_12_Luces','Faroles y jardines de cubierta');REF=zone('VIG_13_Escala','Referencias de personaje de 46 unidades L2')
def put(o,key,mat=None):
 for c in list(o.users_collection):c.objects.unlink(o)
 zones[key]['collection'].objects.link(o)
 if mat:o.data.materials.append(mat)
 return o
remove=('Escalon_V3','Nariz_V3','Pasamanos_V3','Poste_escalera_V3','Zanca_V3','Mamparo_','Cristal_frontal_V3','Cristal_lateral_V3','Pilar_capitan_V3','Travesano_frontal_V3','Marco_frontal_V3','Pedestal_timon_V3','Timon_V3','Radio_V3','Consola_V3','Carta_V3','Brujula_V3','Borda_ornamental','Pasamanos','Barandal_intermedio','Puntal_baranda','Brazo_farol','Vidrio_farol','Gancho_farol','Aro_farol','Jaula_farol','Capucha_farol','Asta_clan','Estandarte_clan','Sello_estandarte','Baranda_galeria','Baranda_media_galeria','Poste_galeria','Testero_galeria','Poste_testero')
furn=('Cama_','Colchon','Manta_','Almohada','Cabecero','Mesa_habitacion','Mapa_habitacion','Pata_mesa','Silla_aposento','Respaldo_aposento','Pata_silla','Cofre_','Tapa_cofre','Cincha_cofre','Cerradura_cofre')
sourceFurniture={}
for o in list(bpy.data.objects):
 if o.type not in {'MESH','CURVE','FONT'}:continue
 if o.name.startswith(remove):bpy.data.objects.remove(o,do_unlink=True);continue
 n=o.name
 if n.startswith(furn):key=F;sourceFurniture[n]={'position':list(o.location),'scale':list(o.scale),'size':list(o.dimensions)}
 elif n.startswith(('Globo','Costura_longitudinal','Sello_circular','Heraldica','Aleta','Marco_aleta')):key=B
 elif n.startswith(('Galeria','Suspension_galeria','Banco_galeria','Pata_galeria','Respaldo_galeria')):key=G
 elif n.startswith(('Techo_rectangular','Cornisa_')):key=T
 elif n.startswith(('Puente_suelo','Borde_rectangular','Baranda_puente','Poste_puente')):key=P
 elif n.startswith(('Aposento','Ventana_V3','Marco_V3','Montante_V3','Dintel_V3','Jamba_V3')):key=Q
 elif n.startswith(('Cubierta','Junta_tablas','Banco_clan','Pata_clan','Respaldo_clan','Mesa_clan','Mapa_clan','Patas_mesa')):key=D
 else:key=H
 put(o,key)
def mat(n,c,metal=0,rough=.6,texture=None,emit=0,alpha=1):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,alpha);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough;s.inputs['Alpha'].default_value=alpha
 if emit:s.inputs['Emission Color'].default_value=(*c,1);s.inputs['Emission Strength'].default_value=emit
 if alpha<1:m.surface_render_method='DITHERED'
 if texture:
  image=bpy.data.images.load(str(R/'research/model-catalog/exports/cc0-textures/ambientcg'/texture/(texture+'_2K-JPG_Color.jpg')),check_existing=True);image.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],s.inputs['Base Color'])
 return m
wood=mat('Clan · Roble restaurado',(.21,.095,.035),texture='WoodFloor051');walnut=mat('Clan · Nogal oscuro',(.052,.024,.014),rough=.65);gold=mat('Clan · Bronce envejecido',(.36,.21,.07),.65,.35);red=mat('Clan · Tapicería carmesí',(.24,.018,.027),rough=.9);fabric=mat('Clan · Lino y cartas',(.58,.46,.29),rough=.9,texture='Fabric001');ink=mat('Clan · Hierro negro',(.018,.024,.025),.6,.45);jade=mat('Clan · Cuero verde',(.025,.10,.08),rough=.85);light=mat('Clan · Farol ámbar',(.95,.48,.11),emit=1.2);glass=mat('Clan · Parabrisas transparente',(.17,.37,.35),.08,.14,alpha=.24);soil=mat('Clan · Tierra',(.045,.03,.015),rough=1);leaf=mat('Clan · Follaje',(.065,.17,.075),rough=1)
for o in bpy.data.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 for slot in o.material_slots:
  if not slot.material:continue
  name=slot.material.name
  if name.startswith('Madera_casco'):slot.material=wood if name.endswith(('1','3')) else walnut
  elif name in ['Bronce_dorado','Laton_luminoso']:slot.material=gold
  elif name=='Tapiceria_azul':slot.material=jade
  elif name=='Pergamino':slot.material=fabric
def box(n,p,size,m,key,be=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=put(bpy.context.object,key,m);o.name=n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if be:mod=o.modifiers.new('Cantos','BEVEL');mod.width=min(be,min(size)*.3);mod.segments=2;o.modifiers.new('Normales','WEIGHTED_NORMAL')
 return o
def tube(n,pts,r,m,key):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for v,p in zip(s.points,pts):v.co=(*p,1)
 o=bpy.data.objects.new(n,c);zones[key]['collection'].objects.link(o);c.materials.append(m);return o
def rod(n,a,b,r,m,key):return tube(n,[a,b],r,m,key)
def cyl(n,p,r,h,m,key,N=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=h,location=p);o=put(bpy.context.object,key,m);o.name=n;return o
def sphere(n,p,scale,m,key):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=p);o=put(bpy.context.object,key,m);o.name=n;o.scale=scale;return o
def ring(n,x,y,z,r,m,key,axis='Z',thick=.008):
 pts=[]
 for i in range(41):
  a=i*math.tau/40;pts.append((x+r*math.cos(a),y+r*math.sin(a),z) if axis=='Z' else (x,y+r*math.cos(a),z+r*math.sin(a)))
 return tube(n,pts,thick,m,key)
def text(n,value,p,size,m,key,rot=(0,0,0)):
 c=bpy.data.curves.new(n,'FONT');c.body=value;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.001;c.resolution_u=2;o=bpy.data.objects.new(n,c);zones[key]['collection'].objects.link(o);o.location=p;o.rotation_euler=rot;c.materials.append(m);return o
LOW=4.15;UP=5.43
# More gentle treads: 26 rather than 16, preserving the existing upper elevation.
steps=26;rise=(UP-LOW)/steps;going=.16;start=-4.14;width=.80
for side in [-1,1]:
 y=side*2.65
 for i in range(steps):
  x=start-(i+.5)*going;z=LOW+(i+1)*rise
  box('Escalón renovado',(x,y,z-.022),(going+.006,width,.044),wood,S,.005);box('Nariz de bronce',(x+going*.44,y,z+.002),(.009,width,.004),gold,S,.001)
 for dy in [-.44,.44]:
  yy=y+dy;rod('Pasamanos a escala',(start,yy,LOW+.31),(-8.30,yy,UP+.31),.008,gold,S)
  for i in [0,5,10,15,20,25]:
   x=start-(i+.5)*going;z=LOW+(i+1)*rise;rod('Poste escalera',(x,yy,z),(x,yy,z+.31),.007,gold,S)
  # Solid sloping cheeks behind the open risers.
  verts=[(start,yy,LOW-.06),(-8.3,yy,UP-.06),(-8.3,yy,UP-.16),(start,yy,LOW-.16)];me=bpy.data.meshes.new('Zanca');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Zanca continua',me);zones[S]['collection'].objects.link(o);me.materials.append(walnut)
 box('Descanso inferior',(start+.20,y,LOW-.025),(.40,width,.05),wood,S,.004)
 box('Descanso superior',(-8.48,y,UP-.025),(.36,width,.05),wood,S,.004)
# Rear landing, clear 0.65 design units behind the open bridge entrance.
box('Paseo trasero del puente',(-13.27,0,UP-.06),(.36,6.3,.12),wood,P)
for side in [-1,1]:
 box('Mamparo bajo',(-10.9,side*1.50,UP+.085),(3.6,.055,.17),walnut,P)
 box('Vidrio lateral',(-10.9,side*1.50,UP+.40),(3.6,.015,.45),glass,P,.004)
 for x in [-12.7,-10.9,-9.1]:rod('Pilar del puente',(x,side*1.50,UP),(x,side*1.50,UP+.91),.014,gold,P)
box('Mamparo de proa',(-9.1,0,UP+.085),(.055,3,.17),walnut,P)
box('Parabrisas de proa',(-9.1,0,UP+.40),(.015,3,.45),glass,P,.004)
for z in [.17,.63]:box('Marco delantero',(-9.08,0,UP+z),(.025,3.04,.018),gold,P,.003)
for y in [-1.5,1.5]:rod('Marco parabrisas',(-9.08,y,UP+.17),(-9.08,y,UP+.63),.009,gold,P)
rod('Pie del timón',(-10.10,0,UP),(-10.10,0,UP+.23),.018,gold,P)
ring('Timón de clan',-10.10,0,UP+.275,.12,wood,P,'X',.013)
for i in range(8):
 a=i*math.tau/8;rod('Radio del timón',(-10.10,0,UP+.275),(-10.10,.16*math.cos(a),UP+.275+.16*math.sin(a)),.006,gold,P)
box('Consola baja',(-9.73,.65,UP+.12),(.42,.28,.24),walnut,P)
box('Carta de navegación',(-9.73,.65,UP+.246),(.39,.25,.008),fabric,P,.003);ring('Brújula',-9.70,.65,UP+.255,.045,gold,P)
text('Nombre timón','VIGILIA',(-9.06,0,UP+.13),.095,gold,P,(math.pi/2,0,math.pi/2))
box('Alfombra del capitán',(-10.80,0,UP+.009),(1.5,1.2,.012),red,P,.005)
# Perimeter rails at 38u above the deck, matching the 46u reference.
stations=[(-15,.35),(-14,2.1),(-12,4.15),(-8,5.1),(-3,5.45),(3,5.35),(8,4.7),(12,3.55),(15,1.7),(16.5,.15)]
outline=[(x,-w,LOW) for x,w in stations]+[(x,w,LOW) for x,w in reversed(stations)];outline.append(outline[0])
for dz,r in [(.05,.035),(.21,.012),(.38,.018)]:tube('Baranda perimetral',[(x,y,z+dz) for x,y,z in outline],r,gold,D)
for a,b in zip(outline,outline[1:]):
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/.75))
 for j in range(n):v=a.lerp(b,j/n);rod('Puntal perimetral',(v.x,v.y,LOW+.04),(v.x,v.y,LOW+.38),.012,gold,D)
for y in [-4.05,4.05]:
 for h in [.19,.38]:rod('Baranda de galería',(-3,y,11.2+h),(7,y,11.2+h),.012,gold,G)
 for x in range(-3,8):rod('Poste galería',(x,y,11.2),(x,y,11.58),.009,gold,G)
for x in [-3,7]:
 for h in [.19,.38]:rod('Testero galería',(x,-4.05,11.2+h),(x,4.05,11.2+h),.012,gold,G)
 for y in [-4,-2,0,2,4]:rod('Poste testero',(x,y,11.2),(x,y,11.58),.009,gold,G)

def chair(x,y,z,key,yaw=0):
 parts=[]
 parts.append(box('Asiento de clan',(x,y,z+.125),(.18,.18,.035),jade,key,.007))
 parts.append(box('Respaldo de clan',(x,y+.085,z+.23),(.18,.025,.19),walnut,key,.007))
 for dx in [-.065,.065]:
  for dy in [-.065,.065]:parts.append(box('Pata de silla',(x+dx,y+dy,z+.06),(.018,.018,.12),gold,key,.003))
 for o in parts:
  v=o.location-Vector((x,y,z));o.location=(x+v.x*math.cos(yaw)-v.y*math.sin(yaw),y+v.x*math.sin(yaw)+v.y*math.cos(yaw),z+v.z);o.rotation_euler.z=yaw
def table(x,y,z,w,d,key):
 box('Mesa de clan',(x,y,z+.23),(w,d,.035),wood,key,.01)
 for dx in [-w*.35,w*.35]:
  for dy in [-d*.30,d*.30]:box('Pata de mesa',(x+dx,y+dy,z+.11),(.025,.025,.22),gold,key,.004)
def lantern(x,y,z,key):
 cyl('Base farol',(x,y,z+.025),.07,.05,gold,key);rod('Asta farol',(x,y,z+.05),(x,y,z+.62),.009,gold,key)
 box('Cristal ámbar',(x,y,z+.59),(.10,.10,.16),light,key,.012)
 cyl('Capucha farol',(x,y,z+.69),.085,.035,gold,key,8)
def plant(x,y,z,key):
 cyl('Maceta de bronce',(x,y,z+.06),.09,.12,gold,key);cyl('Tierra',(x,y,z+.125),.083,.01,soil,key)
 for i in range(7):a=i*math.tau/7;sphere('Hojas ornamentales',(x+math.cos(a)*.06,y+math.sin(a)*.06,z+.19),(.06,.045,.10),leaf,key)
def goblet(x,y,z,key):cyl('Pie de copa',(x,y,z+.025),.004,.05,gold,key,8);sphere('Copa',(x,y,z+.065),(.02,.02,.025),gold,key)
def emblem(x,y,z,r,key):
 cyl('Medallón de clan',(x,y,z),r,.014,jade,key,40);ring('Anillo heráldico',x,y,z+.01,r*.94,gold,key,thick=.012)
 pts=[(-.6,-.5),(-.1,-.32),(.42,-.4),(.54,-.02),(.23,.15),(.44,.46),(.10,.64),(-.35,.45),(-.18,.10),(-.5,-.06)]
 tube('Dragón heráldico',[(x+a*r,y+b*r,z+.022) for a,b in pts],r*.04,gold,key)
# Restored deck, a central ceremonial runner; furniture remains to the sides.
box('Alfombra de cubierta',(2.4,0,LOW+.012),(17.4,1.3,.015),red,C,.003)
for y in [-.62,.62]:box('Orla de alfombra',(2.4,y,LOW+.022),(17.3,.025,.006),gold,C,.001)
emblem(2.0,0,LOW+.03,.52,C);text('Leyenda clan','VIGILIA DEL DRAGON',(7.3,0,LOW+.035),.18,gold,C)
# Strategy corner and mess tables, sized to 46u characters rather than the hull.
for x,y,key in [(1.0,2.55,C),(5.5,-2.6,M)]:
 box('Tapiz de reunión',(x,y,LOW+.01),(2.5,1.75,.012),jade,key,.004);table(x,y,LOW,1.4,.52,key)
 for dx in [-.48,0,.48]:chair(x+dx,y-.45,LOW,key,math.pi);chair(x+dx,y+.45,LOW,key)
 if key==C:
  box('Mapa estratégico',(x,y,LOW+.252),(1.20,.44,.008),fabric,key,.002)
  for dx,dy in [(-.25,-.08),(0,.1),(.3,-.03)]:cyl('Marcador de mapa',(x+dx,y+dy,LOW+.27),.018,.025,gold,key,8)
  for i in range(4):rod('Ruta dibujada',(x-.50+i*.22,y-.13,LOW+.258),(x-.32+i*.22,y+.12,LOW+.258),.002,red,key)
 else:
  for dx in [-.45,0,.45]:
   for dy in [-.13,.13]:cyl('Plato',(x+dx,y+dy,LOW+.257),.045,.007,fabric,key);goblet(x+dx+.065,y+dy,LOW+.255,key)
# Clan refreshments along the side, with access kept away from the stair foot.
box('Mostrador de cantina',(1.2,-4.35,LOW+.16),(1.9,.32,.32),walnut,M,.015);box('Encimera cantina',(1.2,-4.35,LOW+.335),(2.0,.38,.035),wood,M,.01)
for i in range(6):
 cyl('Botella de cantina',(.5+i*.25,-4.35,LOW+.40),.025,.11,jade if i%2 else red,M,10);cyl('Cuello botella',(.5+i*.25,-4.35,LOW+.47),.009,.04,gold,M,8)
for x in [.5,1.2,1.9]:chair(x,-3.94,LOW,M,math.pi)
# Display armour and trophies, decorative stores with actual compact lids/locks.
for x in [7.4,8.1,8.8]:
 box('Cofre de provisiones',(x,3.95,LOW+.10),(.40,.25,.20),walnut,A,.02);box('Tapa de cofre',(x,3.95,LOW+.22),(.42,.27,.05),wood,A,.015)
 for dx in [-.12,.12]:box('Herraje de cofre',(x+dx,3.95,LOW+.14),(.025,.28,.25),gold,A,.003)
 box('Cerradura',(x,3.80,LOW+.14),(.055,.025,.06),gold,A,.005)
box('Expositor de armas',(4.5,4.45,LOW+.24),(1.4,.08,.48),walnut,A)
for x in [4.05,4.45,4.85]:
 rod('Espada de exposición',(x,4.38,LOW+.12),(x,4.38,LOW+.50),.012,gold,A);box('Guarda de espada',(x,4.38,LOW+.20),(.12,.025,.02),gold,A,.003)
for side in [-1,1]:
 for x in [-1.5,11.5]:
  y=side*3.5;rod('Asta de estandarte',(x,y,LOW),(x,y,LOW+.90),.012,gold,A)
  box('Estandarte carmesí',(x-.18,y,LOW+.65),(.34,.016,.42),red,A,.003);ring('Sello estandarte',x-.18,y-.015,LOW+.65,.09,gold,A,'X')
for x,y in [(-2.5,-4.5),(-2.5,4.5),(6,-4.3),(6,4.3),(11,-2.7),(11,2.7),(-13,-2.0),(-13,2.0)]:lantern(x,y,LOW,L)
for x,y in [(-3,-3.8),(-3,3.8),(3,-4.6),(3,4.6),(10,-2.5),(10,2.5)]:plant(x,y,LOW,L)
# Captain's room: retain the actual V3 bed/table/chest transforms.
box('Alfombra aposento',(-10.7,0,LOW+.012),(3.5,2.5,.014),red,Q,.005)
box('Biblioteca de mapas',(-12.68,.85,LOW+.25),(.18,.70,.5),walnut,Q)
for z in [LOW+.18,LOW+.38]:
 box('Estante de mapas',(-12.57,.85,z),(.18,.67,.025),gold,Q,.003)
 for i in range(5):cyl('Pergamino enrollado',(-12.55,.60+i*.12,z+.06),.025,.10,fabric,Q,8)
for x,y in [(-11.7,1.25),(-9.2,-1.3)]:lantern(x,y,LOW,Q)
text('Nombre aposento','CAMAROTE DEL CAPITAN',(-8.43,0,LOW+.82),.095,gold,Q,(math.pi/2,0,math.pi/2))
# Gallery is an observation/council platform, retaining the existing NPC access.
box('Tapiz del consejo',(2,0,11.212),(6.2,3.5,.012),red,G,.005);emblem(2,0,11.23,.65,G)
for x in [0,4]:
 table(x,1.85,11.2,1.1,.48,G)
 for dx in [-.35,.35]:chair(x+dx,1.42,11.2,G,math.pi);chair(x+dx,2.28,11.2,G)
for x in [-2.3,6.3]:
 for y in [-3,3]:lantern(x,y,11.2,G);plant(x+.25,y,11.2,G)
text('Nombre galería','CONSEJO DEL CLAN',(2,-1.20,11.24),.20,gold,G)

# Small humanoids only in an optional scale-review group, never in the game export.
def human(x,y,z):
 box('Referencia · torso',(x,y,z+.285),(.11,.065,.15),jade,REF,.02)
 sphere('Referencia · cabeza',(x,y,z+.415),(.045,.04,.045),fabric,REF)
 for side in [-1,1]:
  rod('Referencia · pierna',(x,y+side*.029,z+.22),(x+.01,y+side*.035,z+.04),.022,ink,REF)
  box('Referencia · bota',(x+.018,y+side*.035,z+.022),(.08,.04,.044),ink,REF,.008)
  rod('Referencia · brazo',(x,y+side*.065,z+.34),(x+.012,y+side*.09,z+.22),.016,jade,REF)
for pos in [(-3.7,-2.65,LOW),(-10.6,0,UP),(-11.45,-.90,LOW),(1.0,1.8,LOW),(2,0,11.2)]:human(*pos)

# Audit before batching: ensure the calibrated furniture was never rescaled.
furniture=[]
for name,old in sourceFurniture.items():
 o=bpy.data.objects[name];unchanged=all(abs(a-b)<1e-6 for key in ['position','scale','size'] for a,b in zip(old[key],list(o.location) if key=='position' else list(o.scale) if key=='scale' else list(o.dimensions)))
 furniture.append({'name':name,'unchanged':unchanged,**old})
 if not unchanged:raise RuntimeError('V3 furniture changed: '+name)
deps=bpy.context.evaluated_depsgraph_get();counts={};baked=[]
for key,info in zones.items():
 for o in list(info['collection'].objects):
  if o.type not in {'MESH','CURVE','FONT'}:continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.transform(o.matrix_world);name=o.name;ob=bpy.data.objects.new(name,me);info['collection'].objects.link(ob);bpy.data.objects.remove(o,do_unlink=True)
  uv=me.uv_layers.new(name='UV_Clan')
  for p in me.polygons:
   axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/.55,co[axes[1]]/.55)
  baked.append(ob)
 root=bpy.data.objects.new(key,None);info['collection'].objects.link(root)
 for o in info['collection'].objects:
  if o!=root:o.parent=root
 counts[key]=len(info['collection'].objects)-1
scene['revision']='Vigilia renovada 1 · clan';scene['character_reference_l2u']=46
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-renovada1.blend'))
for key,info in zones.items():
 bpy.ops.object.select_all(action='DESELECT');meshes=[o for o in info['collection'].objects if o.type=='MESH']
 for o in meshes:o.select_set(True)
 if len(meshes)>1:bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=info['title']
bpy.ops.object.select_all(action='DESELECT')
for info in zones.values():
 for o in info['collection'].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT/'vigilia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
file=EXPORT/'vigilia.gltf';g=json.loads(file.read_text(encoding='utf-8'))
for m in g['materials']:
 if 'Parabrisas transparente' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True
file.write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
audit={'name':'Vigilia renovada1','source':str(source),'sourceHash':sourcehash,'characterReferenceL2u':46,'designUnitsToL2u':100,'mainDeck':LOW,'bridgeDeck':UP,'stair':{'perSide':26,'riseL2u':rise*100,'goingL2u':going*100,'widthL2u':width*100,'xStart':start,'xEnd':-8.30,'centerY':2.65,'handrailL2u':31},'helm':{'rimRadiusL2u':12,'handleRadiusL2u':16,'centerAboveFloorL2u':27.5,'opaqueWallHeightL2u':17},'furniture':furniture,'zones':[{'node':key,'title':info['title'],'objects':counts[key]} for key,info in zones.items()],'gameInstalled':False}
(OUT/'design-manifest.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
if hashlib.sha256(source.read_bytes()).hexdigest()!=sourcehash:raise RuntimeError('Original changed')
print('VIGILIA_RENOVATED',len(baked),len(zones))
