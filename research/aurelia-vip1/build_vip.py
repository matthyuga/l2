"""Aurelia VIP: independent, editable design; Blender Z up, metres."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
EXPORT=ROOT/'research/model-catalog/exports/aurelia-vip1'
OUT.mkdir(exist_ok=True);EXPORT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'research/airship-resort-v1/Aurelia-v1.blend'))
scene=bpy.context.scene
for col in list(bpy.data.collections):
    if col.name.startswith(('08_','09_')):
        for obj in list(col.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(col)
for o in list(bpy.data.objects):
    if o.name.startswith(('Tabique_','Tabique_fondo_','Frente_camarote_','Dintel_','Cama_','Armario_','Pasillo_','Escala_humana','Salon_popa','Bar','Taburete','Nombre_cubierta','Copa_arbol','Tronco','Jardinera')):
        bpy.data.objects.remove(o,do_unlink=True)

ZONES={};ROOMS=[];SOLIDS=[];ROUTES=[]
def zone(key,title,deck):
    c=bpy.data.collections.new(key);scene.collection.children.link(c)
    ZONES[key]={'collection':c,'title':title,'deck':deck};return key
HULL=zone('VIP_00_Casco','Casco con abertura del mirador','exterior')
ARCH=zone('VIP_01_ArcoMotores','Arco, aletas y motores','exterior')
TOP=zone('VIP_02_Terraza','Terraza y escaleras superiores','superior')
POOL=zone('VIP_03_Piscina','Piscina y cascadas','superior')
CAB=zone('VIP_04_Cabanas','Diez cabañas VIP y solárium','superior')
CLUB=zone('VIP_05_Club','Pista y escenario de eventos','superior')
SKY=zone('VIP_06_Skybar','Sky Bar y salón de popa','superior')
GARDEN=zone('VIP_07_Jardines','Jardines y lounge de bienvenida','superior')
ACCESS=zone('VIP_08_Conexion','Escalera entre A y B','conexion')
BRIDGE=zone('VIP_09_Puente','Puente de navegación','superior')
AFLOOR=zone('VIP_A0_Cubierta','Cubierta A y recepción','A')
ABAR=zone('VIP_A1_Bar','Bar de la cubierta A','A')
CASINO=zone('VIP_A2_Casino','Casino privado','A')
BAZAR=zone('VIP_A3_Bazar','Bazar y exposición','A')
LOUNGE=zone('VIP_A4_Descanso','Salón de descanso','A')
GAMES=zone('VIP_A5_Recreativa','Sala recreativa','A')
OWNER=zone('VIP_A6_Suite','Suite del anfitrión','A')
BFLOOR=zone('VIP_B0_Cubierta','Cubierta B y galería','B')
SUITES=zone('VIP_B1_Camarotes','Seis suites para invitados','B')
GYM=zone('VIP_B2_Gimnasio','Gimnasio y bienestar','B')
LOCKER=zone('VIP_B3_Vestuarios','Vestuarios y descanso deportivo','B')
ARENA=zone('VIP_B4_Arena','Miniarena de exhibición','B')
GLASS=zone('VIP_B5_Mirador','Mirador de cristal hacia tierra','B')

def put(o,g,m=None):
    for c in list(o.users_collection):c.objects.unlink(o)
    ZONES[g]['collection'].objects.link(o)
    if m:o.data.materials.append(m)
    return o
for o in list(bpy.data.objects):
    if o.type not in {'MESH','CURVE','FONT'}:continue
    old=o.users_collection[0].name if o.users_collection else ''
    if old=='01_Casco':g=HULL
    elif old in {'05_Arco','06_Propulsion'}:g=ARCH
    elif old=='03_Piscina':g=POOL
    elif o.name.startswith('Suelo_interior_A'):g=AFLOOR
    elif o.name.startswith('Suelo_interior_B'):g=BFLOOR
    elif o.name.startswith('Escalon_B_A'):g=ACCESS
    elif o.name.startswith(('Suelo_puente','Consola_puente','Sillon_piloto')):g=BRIDGE
    elif old=='07_Interiores':g=TOP
    elif old=='04_Mobiliario':g=CAB
    else:g=TOP
    put(o,g)

def material(name,color,metal=0,rough=.5,texture=None,emission=0,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,alpha);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;bs.inputs['Alpha'].default_value=alpha
    if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    if alpha<1:m.surface_render_method='DITHERED'
    if texture:
        file=ROOT/'research/model-catalog/exports/cc0-textures/ambientcg'/texture/(texture+'_2K-JPG_Color.jpg')
        im=bpy.data.images.load(str(file),check_existing=True)
        if im.size[0]>1024:im.scale(1024,1024)
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    return m
pearl=material('VIP · Cerámica perla',(.72,.77,.76),.24,.28)
ivory=material('VIP · Lino marfil',(.78,.72,.57),rough=.9,texture='Fabric001')
navy=material('VIP · Terciopelo noche',(.018,.055,.065),rough=.88)
teal=material('VIP · Verde petróleo',(.025,.16,.16),rough=.7)
gold=material('VIP · Bronce champagne',(.56,.36,.13),.68,.28)
wood=material('VIP · Roble cálido',(.39,.24,.12),rough=.65,texture='WoodFloor051')
marble=material('VIP · Mármol claro',(.68,.69,.64),rough=.38,texture='Marble001')
dark=material('VIP · Cristal oscuro',(.012,.032,.043),.35,.23)
carpet=material('VIP · Alfombra noche',(.03,.10,.13),rough=.96)
red=material('VIP · Granate de juego',(.26,.018,.035),rough=.9)
felt=material('VIP · Paño de juego',(.025,.20,.12),rough=.95)
soil=material('VIP · Tierra de macetas',(.055,.037,.021),rough=1)
green=material('VIP · Vegetación',(.06,.19,.085),rough=.95)
black=material('VIP · Equipamiento grafito',(.018,.025,.03),.25,.55)
light=material('VIP · Luz cálida',(.95,.66,.29),rough=.4,emission=2)
cyan=material('VIP · Luz acuática',(.12,.55,.60),rough=.4,emission=1.3)
glass=material('VIP · Vidrio mirador',(.20,.52,.62),.05,.09,alpha=.20)
water=material('VIP · Agua estática de respaldo',(.025,.29,.37),.15,.2,alpha=.85)

# Replace the source palette throughout the preserved architecture.
replace={'Ceramica_perla':pearl,'Cristal_azul_opaco':dark,'Tarima_calida':wood,'Piedra_clara':marble,'Agua_visual':water,'Titanio':gold,'Lino_marfil':ivory,'Vegetacion':green,'Acento_laton':gold,'Senaletica_cian':cyan}
for o in list(bpy.data.objects):
    if o.type in {'MESH','CURVE','FONT'}:
        for slot in o.material_slots:
            if slot.material and slot.material.name in replace:slot.material=replace[slot.material.name]

def box(n,loc,size,m,g,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object,g,m);o.name=n;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Acabado de cantos','BEVEL');mod.width=min(bevel,min(size)*.4);mod.segments=2
        o.modifiers.new('Normales','WEIGHTED_NORMAL')
    return o
def cyl(n,loc,r,depth,m,g,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=put(bpy.context.object,g,m);o.name=n
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o
def sphere(n,loc,size,m,g):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=loc);o=put(bpy.context.object,g,m);o.name=n;o.scale=size;return o
def tube(n,points,r,m,g):
    c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(n,c);ZONES[g]['collection'].objects.link(o);c.materials.append(m);return o
def ring(n,x,y,z,r,m,g,t=.035):return tube(n,[(x+r*math.cos(i*math.tau/48),y+r*math.sin(i*math.tau/48),z) for i in range(49)],t,m,g)
def text(n,value,loc,size,m,g,rot=(0,0,0)):
    c=bpy.data.curves.new(n,'FONT');c.body=value;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.003;c.resolution_u=3
    o=bpy.data.objects.new(n,c);ZONES[g]['collection'].objects.link(o);o.location=loc;o.rotation_euler=rot;c.materials.append(m);return o
def boolean_cut(obj,loc,size):
    bpy.context.view_layer.objects.active=obj
    for mod in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if obj.name.startswith('Suelo_'):
        mod=obj.modifiers.new('Espesor de cubierta','SOLIDIFY');mod.thickness=.20;bpy.ops.object.modifier_apply(modifier=mod.name)
    cut=box('Cortador temporal',loc,size,pearl,GLASS,0);bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Hueco real del mirador','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)

# The viewing well passes through the floor AND the lower hull.
boolean_cut(bpy.data.objects['Suelo_interior_B'],(0,0,5.5),(12,8,1))
boolean_cut(bpy.data.objects['Casco_abierto_con_borda'],(0,0,2.5),(12,8,7))
for x in [-4,0,4]:
    for y in [-2,2]:box('Panel laminado del mirador',(x,y,5.50),(3.94,3.94,.16),glass,GLASS,.015)
for x in [-6,-2,2,6]:box('Montante del mirador',(x,0,5.52),(.08,8.1,.18),gold,GLASS,.015)
for y in [-4,0,4]:box('Travesaño del mirador',(0,y,5.52),(12.1,.08,.18),gold,GLASS,.015)
for y in [-4.4,4.4]:
    # Leave a 2.4 m passage aligned with suites 03 and 06.
    for a,b in [(-6.4,-4.2),(-1.8,6.4)]:tube('Baranda lateral del mirador',[(a,y,6.60),(b,y,6.60)],.05,gold,GLASS)
    for x in [-6.4,-4.2,-1.8,2.4,6.4]:cyl('Poste de mirador',(x,y,6.03),.04,1.05,gold,GLASS,12)
    for x in [-7.3,7.3]:box('Baliza de vidrio',(x,y,5.72),(.25,.25,.4),cyan,GLASS)
text('Rótulo mirador','SKY WALK',(0,0,5.60),.75,gold,GLASS)

# Shared furniture designed for this palette.
def sofa(x,y,z,g,yaw=0,length=3.4):
    parts=[]
    def b(n,p,s,m,be=.10):parts.append(box(n,(x+p[0],y+p[1],z+p[2]),s,m,g,be))
    b('Sofá · base',(0,0,.24),(length,1.15,.34),gold,.06);b('Sofá · asiento',(0,-.05,.52),(length-.2,1.15,.30),navy,.14);b('Sofá · respaldo',(0,.49,.92),(length,.22,1),navy,.12)
    for sx in [-1,1]:b('Sofá · brazo',(sx*(length/2-.08),0,.72),(.26,1.18,.65),navy,.12)
    for dx in [-.85,.85]:b('Cojín marfil',(dx,.26,.95),(.60,.21,.60),ivory,.12)
    if yaw:
        for o in parts:
            d=o.location-Vector((x,y,z));o.location=Vector((x+math.cos(yaw)*d.x-math.sin(yaw)*d.y,y+math.sin(yaw)*d.x+math.cos(yaw)*d.y,z+d.z));o.rotation_euler.z+=yaw
def table(x,y,z,g,r=.65):
    cyl('Mesa · pie',(x,y,z+.30),.09,.60,gold,g);cyl('Mesa · base',(x,y,z+.05),.36,.08,gold,g);cyl('Mesa · mármol',(x,y,z+.64),r,.10,marble,g)
def stool(x,y,z,g):
    cyl('Taburete · pie',(x,y,z+.45),.07,.85,gold,g);cyl('Taburete · base',(x,y,z+.06),.30,.08,gold,g);cyl('Taburete · asiento',(x,y,z+.94),.34,.18,navy,g)
def lamp(x,y,z,g,h=2.4):
    cyl('Lámpara · base',(x,y,z+.05),.25,.1,gold,g);cyl('Lámpara · asta',(x,y,z+h/2),.035,h,gold,g,12);cyl('Lámpara · pantalla',(x,y,z+h-.2),.32,.40,ivory,g);cyl('Lámpara · difusor',(x,y,z+h-.42),.25,.025,light,g)
def bottle(x,y,z,g,m=teal):
    cyl('Botella',(x,y,z+.16),.075,.30,m,g,10);cyl('Cuello botella',(x,y,z+.35),.028,.14,gold,g,8)
def glassware(x,y,z,g):
    cyl('Copa · tallo',(x,y,z+.11),.012,.18,gold,g,8);sphere('Copa',(x,y,z+.24),(.07,.07,.09),glass,g)

PROTOTYPES={}
def prototype(name,file):
    old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'research/model-catalog/exports/web-kenney-nature'/file));new=[o for o in bpy.data.objects if o not in old];meshes=[]
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    for obj in new:
        if obj.type!='MESH':continue
        data=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps);data.transform(obj.matrix_world);copy=bpy.data.objects.new('PROTOTYPE_'+name,data);scene.collection.objects.link(copy);meshes.append(copy)
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();proto=bpy.context.object
    coords=[v.co for v in proto.data.vertices];lo=min(v.z for v in coords);hi=max(v.z for v in coords);cx=(min(v.x for v in coords)+max(v.x for v in coords))/2;cy=(min(v.y for v in coords)+max(v.y for v in coords))/2
    for v in proto.data.vertices:v.co-=Vector((cx,cy,lo))
    PROTOTYPES[name]=(proto.data,hi-lo);bpy.data.objects.remove(proto,do_unlink=True)
prototype('Palmera','tree_palmDetailedTall.glb');prototype('Arbusto','plant_bushDetailed.glb');prototype('Flor','flower_purpleC.glb')
def plant(x,y,z,g,h=2.0,palm=False,pot=.65):
    cyl('Maceta cerámica',(x,y,z+.32),pot,.64,pearl,g);ring('Labio de bronce',x,y,z+.65,pot,gold,g);cyl('Sustrato',(x,y,z+.65),pot*.88,.025,soil,g)
    data,ph=PROTOTYPES['Palmera' if palm else 'Arbusto'];o=bpy.data.objects.new('Palmera de cubierta' if palm else 'Planta ornamental',data);ZONES[g]['collection'].objects.link(o);o.location=(x,y,z+.66);o.scale=(h/ph,)*3
    if not palm:
        data,fh=PROTOTYPES['Flor']
        for i in range(3):a=i*math.tau/3;f=bpy.data.objects.new('Flor ornamental',data);ZONES[g]['collection'].objects.link(f);f.location=(x+.28*math.cos(a),y+.28*math.sin(a),z+.70);f.scale=(.45/fh,)*3

# Upper deck: refresh cushions and give the ten cabanas a complete fit-out.
for o in list(ZONES[CAB]['collection'].objects):
    if o.name.startswith(('Tumbona_cojin','Tumbona_solarium')):
        x,y,z=o.location;box('Toalla enrollada',(x,y+.65,z+.16),(.95,.26,.18),teal,CAB,.08)
for side in [-1,1]:
    for x in [-24,-12,0,12,24]:
        y=side*12.5
        for dx in [-2.8,2.8]:
            # Soft outer curtains, open on the pool-facing edge.
            vertices=[];faces=[]
            for j in range(9):
                for k in range(2):vertices.append((x+dx+(k-.5)*.65,y+side*(1.70+.07*math.sin(j*1.8+k)),18.35+j*.36))
            for j in range(8):faces.append((j*2,j*2+1,j*2+3,j*2+2))
            me=bpy.data.meshes.new('Cortina');me.from_pydata(vertices,[],faces);me.update();o=bpy.data.objects.new('Cortina recogida',me);ZONES[CAB]['collection'].objects.link(o);me.materials.append(ivory)
        cyl('Luz de cabaña',(x,y,21.08),.30,.16,light,CAB)
        bottle(x,y,19.03,CAB);glassware(x+.22,y,19.03,CAB)
    for x in [-18,18]:plant(x,side*16.0,18.02,GARDEN,4.4,True,.60)
    for x in [-6,6]:plant(x,side*16.4,18.02,GARDEN,.78,False,.54)
    for x in [-30,30]:lamp(x,side*11,18.03,GARDEN,2.35)
for y in [-3.7,3.7]:sofa(-25,y,18.04,GARDEN,0 if y>0 else math.pi,4.3)
for y in [-2.05,2.05]:table(-25,y,18.04,GARDEN,.65)
for x in [-30,-21]:
    for y in [-3.8,3.8]:plant(x,y,18.03,GARDEN,.70,False,.50)
cyl('Emblème accueil',(-28.7,0,18.035),1.65,.035,navy,GARDEN);ring('Médaillon accueil',-28.7,0,18.06,1.58,gold,GARDEN,.035)
text('Signature de pont','AURELIA',(-28.7,0,18.10),.52,gold,GARDEN)

# Main pool: a proper overflow feature at the bow end; runtime water is separate.
for y in [-3,0,3]:
    tube('Col de cygne de piscine',[(-18.2,y,18.0),(-18.2,y,19.25),(-17.7,y,19.3),(-17.5,y,19.10)],.09,gold,POOL)
for y in [-5.82,5.82]:box('Ligne lumineuse piscine',(0,y,17.1),(36,.035,.06),cyan,POOL,.005)
for x in [-15,-5,5,15]:
    for y in [-6.64,6.64]:cyl('Balise de piscine',(x,y,18.17),.10,.07,light,POOL,12)

# Aft event club: no solid placeholder cube enclosing the bar.
box('Fond du skybar',(45.95,0,20.0),(.22,14,4.0),navy,SKY,.04)
for y in [-7,7]:box('Baie latérale du skybar',(40,y,20.0),(11.9,.10,3.8),glass,SKY,.02)
for x in [34.0,40,46.0]:
    for y in [-7,7]:cyl('Colonne skybar',(x,y,20),.08,4,gold,SKY,12)
box('Bar · socle',(41.3,0,18.65),(1.55,10,1.3),navy,SKY,.15);box('Bar · plateau',(41.3,0,19.38),(1.9,10.5,.18),marble,SKY,.06)
box('Rétro-bar',(45,0,19.05),(.65,9.6,2.1),wood,SKY,.05)
for z in [19.3,20.2]:
    box('Etagère de bouteilles',(44.6,0,z),(.8,9.4,.10),gold,SKY)
    for i in range(13):bottle(44.5,-4.1+i*.68,z+.06,SKY,teal if i%2 else red)
for y in [-3.8,-1.9,0,1.9,3.8]:stool(39.25,y,18.02,SKY)
for y in [-5,5]:sofa(36.2,y,18.02,SKY,0 if y>0 else math.pi,3.0);table(36.2,y-math.copysign(1.35,y),18.02,SKY,.54)
text('Enseigne sky club','AURELIA / PRIVATE CLUB',(33.82,0,21.25),.54,gold,SKY,(math.pi/2,0,-math.pi/2))
box('Piste de réception',(24.6,0,18.06),(7.8,9.2,.10),navy,CLUB,.08)
for x in [21.0,23.4,25.8,28.2]:box('Ligne de piste',(x,0,18.12),(.035,9,.025),gold,CLUB,.005)
for y in [-4.4,-2.2,0,2.2,4.4]:box('Ligne de piste',(24.6,y,18.12),(7.6,.035,.025),gold,CLUB,.005)
box('Estrade DJ',(30.5,0,18.20),(3.1,10.4,.4),wood,CLUB,.10)
box('Façade de scène',(28.9,0,18.24),(.08,10.2,.18),light,CLUB,.02)
box('Régie DJ',(30.1,0,18.99),(1.10,4.4,1.15),navy,CLUB,.10)
for y in [-1.1,1.1]:cyl('Platine DJ',(30.1,y,19.61),.40,.05,black,CLUB);ring('Anneau platine',30.1,y,19.65,.32,gold,CLUB,.02)
box('Mixage DJ',(30.1,0,19.65),(.65,.7,.12),black,CLUB)
for side in [-1,1]:
    box('Enceinte de scène',(30.4,side*4.5,19.50),(.85,.70,2.2),black,CLUB,.10)
    for z in [19.1,19.9]:
        o=cyl('Haut-parleur',(29.94,side*4.5,z),.23,.03,dark,CLUB);o.rotation_euler.y=math.pi/2
    tube('Portique lumière',[(29.6,side*5.0,18.4),(29.6,side*5.0,22.0),(30.8,side*5.0,22.0)],.07,gold,CLUB)
    for y in [side*4.5,side*3.5]:cyl('Projecteur événement',(30,y,21.9),.20,.35,cyan,CLUB)
text('Inscription piste','PRIVATE EVENTS',(24.6,0,18.155),.58,gold,CLUB)

# Rooms open onto a central corridor. Furnishings stay inside their room bounds.
def room(name,x,y,z,w,d,g,door=2.4):
    side=1 if y>0 else -1;front=y-side*d/2;back=y+side*d/2;h=3.3
    box(name+' · parquet',(x,y,z+.025),(w-.2,d-.2,.045),wood,g,.01)
    for sx in [-1,1]:box(name+' · cloison latérale',(x+sx*w/2,y,z+h/2),(.13,d,h),pearl,g)
    box(name+' · mur du fond',(x,back,z+h/2),(w,.13,h),pearl,g)
    for sx in [-1,1]:
        piece=(w-door)/2;cx=x+sx*(door/2+piece/2);box(name+' · entrée',(cx,front,z+h/2),(piece,.13,h),pearl,g)
    box(name+' · linteau',(x,front,z+3.05),(door,.13,.50),navy,g)
    for sx in [-1,1]:box(name+' · chambranle',(x+sx*(door/2+.04),front,z+1.4),(.07,.20,2.8),gold,g,.01)
    # A low decorative cornice, not a roof, keeps the rooms inspectable.
    for sx in [-1,1]:box(name+' · frise',(x+sx*(w/2-.12),y,z+3.10),(.05,d-.2,.05),light,g,.005)
    text(name+' · enseigne',name,(x,front-side*.10,z+3.06),.38,gold,g,(math.pi/2 if side>0 else -math.pi/2,0,0 if side>0 else math.pi))
    ROOMS.append({'name':name,'deck':ZONES[g]['deck'],'center':[x,y,z],'size':[w,d],'door':[x,front,z],'doorWidth':door,'group':g})
    ROUTES.append({'room':name,'from':[x,front-side*1.1,z+.1],'to':[x,front+side*1.8,z+.1],'clearance':door})
def rug(x,y,z,w,d,g):box('Tapis',(x,y,z+.075),(w,d,.025),carpet,g,.01)
def plaque(name,x,y,z,g):
    box('Plaque',(x,y,z),(.09,1.5,.7),navy,g);text('Signalétique',name,(x-.055,y,z),.20,gold,g,(math.pi/2,0,-math.pi/2))

# Deck A: entertainment, shopping and the host's private suite.
for name,x,y,w,d,g in [('THE OBSIDIAN BAR',-26,-11,18,12,ABAR),('CASINO',0,-11,23,12,CASINO),('BAZAR',25,-11,18,12,BAZAR),('QUIET LOUNGE',-26,11,18,12,LOUNGE),('GAME ROOM',0,11,23,12,GAMES),('OWNER SUITE',25,11,18,12,OWNER)]:room(name,x,y,10.5,w,d,g)
for y in [-2.8,2.8]:box('Liseré de circulation A',(-4,y,10.53),(78,.07,.035),gold,AFLOOR,.01)
box('Comptoir concierge',(-46,0,11.12),(1.25,4.5,1.24),navy,AFLOOR,.15)
text('Hall A','AURELIA / MEMBERS CLUB',(-39,0,10.55),.60,gold,AFLOOR)
for y in [-3.1,3.1]:plant(-44,y,10.52,AFLOOR,.85,False,.5)
for y in [-1.76,1.76]:
    tube('Garde-corps trémie A',[(28.1,y,11.6),(35.6,y,11.6)],.045,gold,ACCESS)
    for x in [28.1,31.8,35.6]:cyl('Poste trémie',(x,y,11.03),.035,1.05,gold,ACCESS,12)

# Interior bar with seating, bottles and a long counter at the rear.
box('Bar A · comptoir',(-26,-14.2,11.15),(13,1.25,1.3),navy,ABAR,.12);box('Bar A · dessus',(-26,-14.2,11.86),(13.4,1.55,.14),marble,ABAR,.06)
for x in [-31,-28.5,-26,-23.5,-21]:stool(x,-12.5,10.54,ABAR)
for x in [-32,-20]:table(x,-8.6,10.54,ABAR,.72);sofa(x,-6.9,10.54,ABAR,0,2.3)
for i in range(14):bottle(-31.6+i*.85,-14.2,11.94,ABAR,teal if i%2 else red)
for x in [-33,-19]:lamp(x,-15.6,10.53,ABAR,2.8)

# Casino: modelled poker, roulette, slots and chips; visual furnishings only.
def poker(x,y,z,g):
    cyl('Table de poker · pied',(x,y,z+.40),.32,.8,gold,g);cyl('Table de poker · plateau',(x,y,z+.88),1.75,.18,wood,g);cyl('Tapis de poker',(x,y,z+.98),1.60,.025,felt,g);ring('Repose-bras poker',x,y,z+1.03,1.66,navy,g,.09)
    for i in range(5):a=i*math.tau/5;stool(x+2.25*math.cos(a),y+2.25*math.sin(a),z,g);cyl('Pile de jetons',(x+math.cos(a),y+math.sin(a),z+1.025),.09,.08,red if i%2 else gold,g,12);box('Carte',(x+.60*math.cos(a),y+.60*math.sin(a),z+1.01),(.18,.27,.015),ivory,g,.005)
poker(-5.7,-10.6,10.55,CASINO);poker(4.7,-10.6,10.55,CASINO)
box('Table roulette',(0,-15.0,11.10),(4.3,1.5,1.1),wood,CASINO,.1);cyl('Roulette',(1.1,-15.0,11.72),.62,.15,gold,CASINO);cyl('Cuvette roulette',(1.1,-15.0,11.81),.52,.035,black,CASINO)
for i in range(16):a=i*math.tau/16;box('Case roulette',(1.1+.43*math.cos(a),-15+.43*math.sin(a),11.84),(.10,.10,.025),red if i%2 else ivory,CASINO,.005)
for x in [-9,9]:
    for y in [-8,-11,-14]:
        box('Machine de jeu',(x,y,11.25),(.95,1,1.4),navy,CASINO,.10);o=box('Écran de jeu',(x,y+.52,11.68),(.72,.035,.66),cyan,CASINO,.02)
        for dx in [-.22,0,.22]:box('Symbole écran',(x+dx,y+.545,11.68),(.12,.02,.18),gold,CASINO,.02)

# Bazar: glazed counters and display shelves.
for x in [20,30]:
    box('Vitrine · socle',(x,-11,10.98),(2.2,4,.85),navy,BAZAR,.08);box('Vitrine de bijoux',(x,-11,11.65),(2.1,3.9,.55),glass,BAZAR,.02)
    for i in range(3):ring('Objet exposé',x,-12+i,11.65,.22,gold,BAZAR,.055)
for x in [19,25,31]:
    box('Rayonnage bazar',(x,-16.25,11.90),(4.5,.5,2.8),wood,BAZAR,.04)
    for z in [11.0,11.8,12.6]:
        box('Étagère bazar',(x,-15.9,z),(4.35,.7,.08),gold,BAZAR)
        for dx in [-1.3,0,1.3]:sphere('Artefact bazar',(x+dx,-15.9,z+.23),(.22,.18,.22),teal if dx else gold,BAZAR)
plant(25,-7.3,10.54,BAZAR,.7,False,.5)

# Quiet lounge with facing sofas, books and a tea table.
rug(-26,11,10.53,12,7,LOUNGE)
for x in [-31,-21]:sofa(x,11,10.57,LOUNGE,-math.pi/2 if x< -26 else math.pi/2,4.6)
table(-26,11,10.57,LOUNGE,1.15)
for x in [-33,-19]:lamp(x,15,10.53,LOUNGE,2.7);plant(x,7.2,10.53,LOUNGE,.90,False,.5)
for i in range(12):box('Livre de salon',(-30+i*.7,16.3,11.5),(.22,.45,.68),teal if i%2 else ivory,LOUNGE,.02)
box('Bibliothèque basse',(-26,16.3,10.98),(13,.65,.85),wood,LOUNGE,.05)

# Recreation: billiards, table football and arcade terminals.
box('Billard',(-5,11.2,11.03),(4.3,2.4,1),wood,GAMES,.12);box('Tapis de billard',(-5,11.2,11.56),(4.0,2.12,.04),felt,GAMES,.03)
for dx in [-1.95,0,1.95]:
    for dy in [-1.02,1.02]:cyl('Poche de billard',(-5+dx,11.2+dy,11.59),.13,.025,black,GAMES,12)
for i in range(7):sphere('Bille',(-5.5+(i%3)*.22,11+(i//3)*.22,11.67),(.075,)*3,ivory if i%2 else gold,GAMES)
for y in [9.7,12.7]:tube('Queue de billard',[(-7,y,11.67),(-3,y,11.67)],.025,wood,GAMES)
box('Baby-foot',(4.8,11.2,11.10),(2.8,1.7,1.1),wood,GAMES,.08);box('Terrain baby-foot',(4.8,11.2,11.68),(2.5,1.4,.06),felt,GAMES,.02)
for x in [3.9,4.5,5.1,5.7]:
    tube('Barre baby-foot',[(x,10,11.8),(x,12.4,11.8)],.025,gold,GAMES)
    for y in [10.8,11.3,11.8]:box('Joueur baby-foot',(x,y,11.78),(.10,.14,.32),teal if x<5 else red,GAMES,.025)
for x in [-7,-3,1,5,9]:
    box('Borne arcade',(x,16,11.55),(1.45,.85,2),navy,GAMES,.10);box('Écran arcade',(x,15.55,11.95),(1.15,.035,.9),cyan,GAMES,.03);stool(x,14.7,10.54,GAMES)

# Owner suite and six cabins use the same detailed bedding modules.
def bed(x,y,z,g):
    box('Lit · socle',(x,y,z+.28),(2.9,3.6,.50),wood,g,.12);box('Lit · matelas',(x,y,z+.63),(2.8,3.5,.28),ivory,g,.16)
    box('Lit · tête',(x,y+1.80,z+.95),(3.1,.18,1.55),navy,g,.12);box('Lit · jeté',(x,y-.7,z+.82),(2.85,1.45,.10),teal,g,.06)
    for dx in [-.65,.65]:box('Oreiller',(x+dx,y+1.08,z+.86),(1.05,.65,.20),ivory,g,.14)
    for dx in [-1.9,1.9]:box('Chevet',(x+dx,y+1.0,z+.36),(.65,.65,.72),wood,g,.06);cyl('Lampe de chevet',(x+dx,y+1.0,z+.90),.18,.35,light,g)
bed(28,12.6,10.55,OWNER);sofa(20,12,10.55,OWNER,-math.pi/2,3.8);table(22,12,10.55,OWNER,.7);rug(25,10.5,10.54,11,7,OWNER)
box('Bureau propriétaire',(25,6.5,11.05),(4.8,1.1,1),wood,OWNER,.08);stool(25,8,10.55,OWNER);plant(32,7.1,10.55,OWNER,1.1,False,.6)

# Deck B: guest suites forward, sport aft, and the transparent central promenade.
for side in [-1,1]:
    for i,x in enumerate([-23,-13,-3]):
        y=side*8.8;name='SUITE '+str((0 if side<0 else 3)+i+1).zfill(2);room(name,x,y,5.5,8,8,SUITES,1.8)
        bed(x+.5,y+side*.6,5.55,SUITES)
        box('Penderie suite',(x-3,y+side*2.7,6.55),(1.2,1.7,2),wood,SUITES,.06)
        box('Console suite',(x,y-side*2.7,5.98),(2.3,.6,.85),wood,SUITES,.06)
        # A compact private wash corner, with screened shower and basin.
        box('Séparation salle d’eau',(x+2.7,y+side*2.4,6.6),(.09,2,2.1),glass,SUITES,.01)
        cyl('Vasque suite',(x+2.1,y+side*2.6,6.37),.30,.12,pearl,SUITES)
        tube('Robinet suite',[(x+2.1,y+side*2.6,6.4),(x+2.1,y+side*2.6,6.7),(x+1.96,y+side*2.6,6.7)],.025,gold,SUITES)
        lamp(x-2.8,y-side*2.5,5.54,SUITES,2.1)
room('FITNESS',12.5,11.0,5.5,11,6.8,GYM,2.2)
room('SPORT LOUNGE',12.5,-11.0,5.5,11,6.8,LOCKER,2.2)
for x in [9.3,12.5,15.7]:
    box('Tapis de course',(x,11.4,5.72),(1.35,2.6,.35),black,GYM,.10);box('Bande de course',(x,11.4,5.92),(1.08,2.20,.035),navy,GYM,.01)
    for dx in [-.55,.55]:tube('Poignée tapis de course',[(x+dx,12.2,5.9),(x+dx,12.2,6.9),(x+dx,11.7,6.9)],.045,gold,GYM)
    box('Console fitness',(x,12.2,7),(1.0,.2,.35),cyan,GYM,.06)
for x in [10,15]:
    box('Banc musculation',(x,8.8,6.02),(2.2,.55,.45),navy,GYM,.12)
    tube('Haltère',[(x-.55,8.8,6.5),(x+.55,8.8,6.5)],.06,gold,GYM)
    for dx in [-.5,.5]:o=cyl('Disque haltère',(x+dx,8.8,6.5),.22,.16,black,GYM);o.rotation_euler.y=math.pi/2
for x in [9,10.4,11.8,13.2,14.6,16]:box('Casier sportif',(x,-13.6,6.7),(1.20,.65,2.3),wood,LOCKER,.04);box('Poignée casier',(x+.38,-13.22,6.7),(.035,.05,.3),gold,LOCKER,.01)
sofa(12.5,-9,5.54,LOCKER,0,5.6);table(12.5,-10.6,5.54,LOCKER,.7)

# Octagonal mini-arena with four open entries and spectator seats outside.
cyl('Socle de mini-arène',(16.5,0,5.67),6,.30,wood,ARENA,8);cyl('Tapis de mini-arène',(16.5,0,5.84),5.72,.035,carpet,ARENA,8)
ring('Cercle de duel',16.5,0,5.87,4.4,gold,ARENA,.035);text('Marque arène','AURELIA / DUEL',(16.5,0,5.90),.56,gold,ARENA)
for i in range(8):
    a=(i+.5)*math.tau/8;x=16.5+5.8*math.cos(a);y=5.8*math.sin(a);cyl('Poteau arène',(x,y,6.36),.07,1.0,gold,ARENA,12)
    a2=(i+1.5)*math.tau/8
    if i%2==0:
        for h in [.45,.90]:tube('Corde arène',[(x,y,5.85+h),(16.5+5.8*math.cos(a2),5.8*math.sin(a2),5.85+h)],.025,gold,ARENA)
for y in [-3.2,3.2]:sofa(25,y,5.55,ARENA,math.pi/2,2.8)
for x in [9.8,23.2]:box('Marche arène',(x,0,5.60),(1.25,2.1,.20),marble,ARENA,.04)
for y in [-3.0,3.0]:plant(-33,y,5.54,BFLOOR,.9,False,.6)
text('Accueil cabines','GUEST DECK',(-32,0,5.55),.55,gold,BFLOOR)

# Retain route dimensions for geometric validation, including the two stair cores.
ROUTES.extend([{'room':'Escalier terrasse A '+str(side),'from':[-32,side*6,18.1],'to':[-43.3,side*6,10.6],'clearance':2.8} for side in [-1,1]])
ROUTES.append({'room':'Escalier A B','from':[35.5,0,10.6],'to':[28.1,0,5.6],'clearance':2.8})

# Give every mesh a consistent world-space UV projection for the existing CC0 maps.
deps=bpy.context.evaluated_depsgraph_get();all_objects=[]
for key,info in ZONES.items():
    for o in list(info['collection'].objects):
        if o.type not in {'MESH','CURVE','FONT'}:continue
        evaluated=o.evaluated_get(deps);me=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);me.transform(o.matrix_world)
        ob=bpy.data.objects.new(o.name,me);info['collection'].objects.link(ob);bpy.data.objects.remove(o,do_unlink=True)
        uv=me.uv_layers.new(name='UV_VIP')
        for poly in me.polygons:
            axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
            for li in poly.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2.4,v[axes[1]]/2.4)
        # The exported groups contain individually named furniture for piece selection.
        all_objects.append(ob)

# A single root per zone keeps whole decks easy to show/hide in the scene editor.
manifest=[]
for key,info in ZONES.items():
    root=bpy.data.objects.new(key,None);info['collection'].objects.link(root)
    objects=list(info['collection'].objects)
    for ob in objects:
        if ob!=root:ob.parent=root
    manifest.append({'node':key,'title':info['title'],'deck':info['deck'],'objects':len(objects)-1})

bpy.ops.object.select_all(action='DESELECT')
for info in ZONES.values():
    for o in info['collection'].objects:o.select_set(True)
bpy.context.view_layer.objects.active=all_objects[0]
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
# Export a render-efficient copy while the saved Blender retains every part.
for info in ZONES.values():
    bpy.ops.object.select_all(action='DESELECT');meshes=[o for o in info['collection'].objects if o.type=='MESH']
    for o in meshes:o.select_set(True)
    if len(meshes)>1:
        bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=info['title']
bpy.ops.object.select_all(action='DESELECT')
for info in ZONES.values():
    for o in info['collection'].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT/'aurelia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)

# Explicit alpha blending makes the viewing floor work in a plain glTF renderer.
gltf_path=EXPORT/'aurelia.gltf';gltf=json.loads(gltf_path.read_text(encoding='utf-8'))
for m in gltf.get('materials',[]):
    if 'Vidrio mirador' in m.get('name',''):
        m['alphaMode']='BLEND';m['doubleSided']=True;m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=[.20,.52,.62,.20]
    if 'Agua estática' in m.get('name',''):m['alphaMode']='BLEND';m['doubleSided']=True
gltf_path.write_text(json.dumps(gltf,ensure_ascii=False),encoding='utf-8')
audit={'name':'Aurelia VIP1','zones':manifest,'rooms':ROOMS,'routes':ROUTES,'objects':len(all_objects),'glassWell':{'opening':[12,8],'floorZ':5.5,'hullCut':True,'panels':6,'alpha':.20},'pool':{'size':[38,12],'waterZ':17.65,'spouts':3},'source':'../airship-resort-v1/Aurelia-v1.blend','gameInstallation':False}
(OUT/'design-manifest.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
print('AURELIA_VIP_COMPLETE',json.dumps({'objects':len(all_objects),'zones':len(manifest),'rooms':len(ROOMS)}))
