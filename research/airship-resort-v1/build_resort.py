"""Aurelia / reference-inspired visual asset. Blender 5, metres, +X aft, +Z up."""
import bpy, math, json, os
from mathutils import Vector
from pathlib import Path
from xml.sax.saxutils import escape

OUT=Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
COL={}
def group(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); COL[name]=c; return c
for n in ['01_Casco','02_Cubierta','03_Piscina','04_Mobiliario','05_Arco','06_Propulsion','07_Interiores','08_Estudio']:
    group(n)
def put(o,g,mat=None):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[g].objects.link(o)
    if mat: o.data.materials.append(mat)
    return o
def material(n,c,metal=0,rough=.4):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
    s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough
    return m
white=material('Ceramica_perla',(.74,.82,.85),.35,.26)
dark=material('Cristal_azul_opaco',(.018,.055,.085),.65,.19)
teak=material('Tarima_calida',(.38,.25,.13),0,.65)
deckmat=material('Piedra_clara',(.64,.66,.61),0,.7)
water=material('Agua_visual',(.015,.42,.55),.4,.15)
metal=material('Titanio',(.23,.30,.34),.8,.25)
fabric=material('Lino_marfil',(.86,.80,.65),0,.9)
green=material('Vegetacion',(.08,.22,.12),0,.9)
gold=material('Acento_laton',(.62,.39,.14),.7,.3)
blue=material('Senaletica_cian',(.04,.62,.74),.3,.3)
def mesh(n,v,f,g,m):
    d=bpy.data.meshes.new(n); d.from_pydata(v,[],f); d.update()
    o=bpy.data.objects.new(n,d); COL[g].objects.link(o); d.materials.append(m); return o
def smooth(o):
    for p in o.data.polygons:p.use_smooth=True
    return o
def box(n,loc,size,m,g='04_Mobiliario',bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=put(bpy.context.object,g,m); o.name=n; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Bordes','BEVEL'); mod.width=bevel;mod.segments=2
        o.modifiers.new('Normales','WEIGHTED_NORMAL')
    return o
def tube(n,pts,r,m,g='05_Arco'):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=3
    s=c.splines.new('POLY');s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new(n,c);COL[g].objects.link(o);c.materials.append(m);return o
def ellipse(n,rx,ry,z,m,g='02_Cubierta',cx=0):
    pts=[(cx+rx*math.cos(i*2*math.pi/160),ry*math.sin(i*2*math.pi/160),z) for i in range(160)]
    return mesh(n,pts,[tuple(range(160))],g,m)
def ringpts(rx,ry,z):return [(rx*math.cos(t*math.tau/160),ry*math.sin(t*math.tau/160),z) for t in range(161)]
RINGS=[(1,.5,0),(25,11,1.5),(43,19,5),(55,24,10),(60,26,16),(59,25.5,20),(56,24,23),(51,19,23),(51,19,18)]
v=[]
for rx,ry,z in RINGS:v += ringpts(rx,ry,z)[:-1]
f=[]
for j in range(len(RINGS)-1):
    for i in range(160):a=j*160+i;b=j*160+(i+1)%160;f.append((a,b,b+160,a+160))
f.append(tuple(reversed(range(160))))
hull=smooth(mesh('Casco_abierto_con_borda',v,f,'01_Casco',white))
sol=hull.modifiers.new('Espesor_visual_35cm','SOLIDIFY');sol.thickness=.35
# Window panels lie on the existing hull surface, separated by mullions.
def radius(z):
    for a,b in zip(RINGS[:6],RINGS[1:7]):
        if a[2]<=z<=b[2]:
            t=(z-a[2])/(b[2]-a[2]);return a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t
    return 59,25.5
for i in range(48):
    t0=math.tau*i/48+.012;t1=math.tau*(i+1)/48-.012
    vv=[]
    window_z=[13.3,14,15,16,16.7]
    for z in window_z:
        rx,ry=radius(z)
        for k in range(5):
            t=t0+(t1-t0)*k/4; vv.append(((rx+.16)*math.cos(t),(ry+.16)*math.sin(t),z))
    mesh(f'Ventanal_{i+1:02}',vv,[(j*5+k,j*5+k+1,j*5+k+6,j*5+k+5) for j in range(len(window_z)-1) for k in range(4)],'01_Casco',dark)
# Nose glazing, a continuous dark visor spanning the foremost quarter.
vv=[]
for z in [18.0,19,20,21.5,22.9]:
    rx,ry=radius(z)
    for j in range(33):
        t=math.pi-.63+1.26*j/32;vv.append(((rx+.09)*math.cos(t),(ry+.09)*math.sin(t),z))
mesh('Visera_panoramica_proa',vv,[(a*33+j,a*33+j+1,(a+1)*33+j+1,(a+1)*33+j) for a in range(4) for j in range(32)],'01_Casco',dark)
for z,rx,ry in [(10,55.2,24.2),(20,59.2,25.7),(23.06,56,24)]:tube('Junta_perimetral',ringpts(rx,ry,z),.09,metal,'01_Casco')
ellipse('Terraza_oval_102x38',51,19,18,deckmat)
tube('Borde_terraza',ringpts(50.8,18.8,18.09),.15,gold,'02_Cubierta')
# Real recessed pool: the upper terrace is cut by a boolean, then a basin sits below.
cutter=box('Cortador_piscina',(0,0,18),(38,12,4),white,'03_Piscina',.7)
bpy.context.view_layer.objects.active=cutter
for mod in list(cutter.modifiers):
    bpy.ops.object.modifier_apply(modifier=mod.name)
terrace=bpy.data.objects['Terraza_oval_102x38']
# A planar mesh can be boolean-cut with EXACT; surface hole is generated explicitly instead.
bpy.data.objects.remove(terrace,do_unlink=True)
bpy.data.objects.remove(cutter,do_unlink=True)
# Four strips from rectangle pool edge to ellipse perimeter: simple exact ring topology.
vv=[]
for i in range(160):
    t=math.tau*i/160;c=math.cos(t);s=math.sin(t);r=min(19/max(abs(c),1e-8),6/max(abs(s),1e-8))
    vv.append((r*c,r*s,18))
vv+=ringpts(51,19,18)[:-1]
mesh('Terraza_con_hueco_piscina',vv,[(i,i+160,(i+1)%160+160,(i+1)%160) for i in range(160)],'02_Cubierta',deckmat)
box('Fondo_piscina',(0,0,16.5),(38,12,.25),white,'03_Piscina')
box('Espejo_agua',(0,0,17.65),(37.6,11.6,.04),water,'03_Piscina',.12)
for y in [-6,6]:box('Muro_vaso',(0,y,17.2),(38,.25,1.5),white,'03_Piscina')
for x in [-19,19]:box('Muro_vaso',(x,0,17.2),(.25,12,1.5),white,'03_Piscina')
for y in [-6.3,6.3]:box('Coronacion_piscina',(0,y,18.08),(39,.55,.18),white,'03_Piscina',.12)
for x in [-19.3,19.3]:box('Coronacion_piscina',(x,0,18.08),(.55,12.6,.18),white,'03_Piscina',.12)
for x in [-17,17]:
    for y in [-6.5,-5.7]:tube('Escala_piscina',[(x,y,17),(x,y,18.7),(x+.6,y,18.7),(x+.6,y,18)],.045,metal,'03_Piscina')
    for z in [17,17.4,17.8]:tube('Peldano_piscina',[(x,-6.5,z),(x,-5.7,z)],.04,metal,'03_Piscina')
# Longitudinal deck seams.
for y in [-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,8,9,10,11,12,13,14,15,16,17]:
    reach=50*math.sqrt(1-(y/19)**2)
    tube('Junta_tarima',[(-reach,y,18.015),(reach,y,18.015)],.018,teak,'02_Cubierta')
# Open cabanas flank the pool; these are reusable modules with shared dimensions.
cab=[]
for side in [-1,1]:
    for x in [-24,-12,0,12,24]:
        y=side*12.5; cab.append([x,y])
        box('Cabana_base',(x,y,18.12),(6,4,.24),teak,bevel=.08)
        for dx in [-2.8,2.8]:
            for dy in [-1.8,1.8]:box('Cabana_pilar',(x+dx,y+dy,19.7),(.15,.15,3.2),metal)
        for dy in [-1.8,1.8]:box('Cabana_viga',(x,y+dy,21.3),(5.9,.18,.18),metal)
        box('Cabana_lona',(x,y,21.42),(5.8,3.8,.10),fabric,bevel=.08)
        for dx in [-1.4,1.4]:
            box('Tumbona_base',(x+dx,y,18.45),(1.1,2.5,.25),teak,bevel=.08)
            box('Tumbona_cojin',(x+dx,y,18.65),(1.05,2.4,.18),fabric,bevel=.1)
        box('Mesa_cabana',(x,y,18.6),(.8,.8,.8),white,bevel=.12)
for side in [-1,1]:
    for x in [-34,-29,29,34]:
        y=side*8
        box('Tumbona_solarium',(x,y,18.45),(1.1,2.5,.65),fabric,bevel=.15)
for x in [-39,39]:
    for y in [-7,7]:
        box('Jardinera',(x,y,18.5),(2.2,2.2,1),white,bevel=.2)
        tube('Tronco',[(x,y,19),(x+.2,y,22)],.15,teak,'04_Mobiliario')
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1.5,location=(x+.2,y,22.1));put(bpy.context.object,'04_Mobiliario',green).name='Copa_arbol'
# Curved aft lounge and panoramic doors.
box('Salon_popa',(40,0,20.0),(12,14,4),dark,'02_Cubierta',1)
box('Techo_salon',(40,0,22.15),(12.6,14.6,.3),white,'02_Cubierta',.5)
for y in [-3,0,3]:box('Montante_salon',(33.95,y,20),(.12,.12,4),white,'02_Cubierta')
box('Bar',(38,0,18.7),(3,6,1.4),white,bevel=.2)
for y in [-4,-2,0,2,4]:box('Taburete',(35,y,18.6),(.65,.65,1.2),teak,bevel=.1)
# Bow stair cores descend to internal decks, deliberately positioned clear of the pool.
def opening(obj,loc,size):
    bpy.context.view_layer.objects.active=obj
    if obj.name.startswith(('Terraza_','Suelo_')) and not any(m.type=='SOLIDIFY' for m in obj.modifiers):
        sol=obj.modifiers.new('Espesor_suelo','SOLIDIFY');sol.thickness=.22
        bpy.ops.object.modifier_apply(modifier=sol.name)
    cut=box('Corte_temporal',loc,size,white,'07_Interiores')
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Hueco_escalera','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
for side in [-1,1]:
    y=side*6
    opening(bpy.data.objects['Terraza_con_hueco_piscina'],(-37.7,y,18),(11.4,3.2,1))
    for dy in [-1.7,1.7]:
        tube('Pasamanos_escalera',[(-43.3,y+dy,19.1),(-32,y+dy,19.1)],.06,metal,'02_Cubierta')
        for x in [-43.3,-40,-36,-32]:tube('Poste_escalera',[(x,y+dy,18),(x,y+dy,19.1)],.045,metal,'02_Cubierta')
    box('Marquesina_escalera',(-33.5,y,20.8),(4,3.8,.2),white,'02_Cubierta',.15)
    for dy in [-1.7,1.7]:box('Pilar_acceso',(-32,y+dy,19.4),(.16,.16,2.8),metal,'02_Cubierta')
    for k in range(38):
        box('Escalon_A_terraza',(-43.25+k*.3,y,10.5+(k+1)*7.5/38-.1),(.3,2.8,.2),deckmat,'07_Interiores')
# Signature arch, high enough above all terrace furniture.
for side in [-1,1]:
    pts=[(-54+108*i/80,side*.5,23+11*math.sin(math.pi*i/80)) for i in range(81)]
    tube('Arco_longitudinal',pts,.48,white)
    tube('Luz_arco',[(x,y,z-.42) for x,y,z in pts],.06,blue)
for i in range(0,81,4):
    x=-54+108*i/80;z=23+11*math.sin(math.pi*i/80)
    tube('Travesano_arco',[(x,-.5,z),(x,.5,z)],.12,metal)
# Tail planes, each with a measurable polygon outline.
def prism(n,outline,z,thick,m,g='06_Propulsion'):
    vv=[(x,y,z+dz) for dz in [-thick/2,thick/2] for x,y in outline];N=len(outline)
    ff=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh(n,vv,ff,g,m)
WINGS=[]
for side in [-1,1]:
    poly=[(34,side*18),(48,side*38),(67,side*38),(58,side*17)]
    WINGS.append(poly);prism('Estabilizador_horizontal',poly,13.5,.65,white)
    tube('Borde_estabilizador',[(x,y,13.9) for x,y in poly+[poly[0]]],.08,metal,'06_Propulsion')
outline=[(44,22),(64,40),(69,40),(61,21)]
vv=[(x,y,z) for y in [-.4,.4] for x,z in outline];N=4
mesh('Aleta_dorsal',vv,[(0,3,2,1),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],'06_Propulsion',white)
def engine(n,x,y,z,r=2.7,length=6):
    # Axis X; open annular duct with a dark inner wall.
    vv=[]
    for xx,rr in [(x-length/2,r),(x+length/2,r),(x+length/2,r*.78),(x-length/2,r*.78)]:
        vv += [(xx,y+rr*math.cos(i*math.tau/64),z+rr*math.sin(i*math.tau/64)) for i in range(64)]
    ff=[]
    for a in range(4):
        for i in range(64):ff.append((a*64+i,a*64+(i+1)%64,((a+1)%4)*64+(i+1)%64,((a+1)%4)*64+i))
    smooth(mesh(n,vv,ff,'06_Propulsion',white))
    for j in range(7):
        a=j*math.tau/7
        pts=[(x,y,z),(x+.15,y+r*.76*math.cos(a),z+r*.76*math.sin(a)),(x+.35,y+r*.64*math.cos(a+.3),z+r*.64*math.sin(a+.3))]
        mesh('Alabe_ventilador',pts,[(0,1,2)],'06_Propulsion',metal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r*.22,location=(x,y,z));smooth(put(bpy.context.object,'06_Propulsion',metal))
for side in [-1,1]:
    engine('Turbina_lateral',32,side*24,7.4)
    tube('Soporte_turbina',[(30,side*21,12),(32,side*24,9.8)],.5,metal,'06_Propulsion')
engine('Turbina_popa',62,0,22,3.7,8)
# Lower internal decks. Independent meshes, no hidden implication of real engineering.
ROOMS=[]
for level,z,rx,ry in [('B',5.5,42,18),('A',10.5,54,23)]:
    ellipse('Suelo_interior_'+level,rx,ry,z,deckmat,'07_Interiores')
    for side in [-1,1]:
        for x in [-30,-20,-10,0,10,20,30]:
            y=side*10
            # Rooms stop well inside the curved shell.
            if (abs(x)+5)**2/rx**2+(abs(y)+5)**2/ry**2>.95: continue
            ROOMS.append(dict(level=level,x=x,y=y,z=z,w=10,d=10))
            box('Tabique_'+level,(x+5,y,z+1.65),(.14,10,3.3),white,'07_Interiores')
            box('Tabique_fondo_'+level,(x,y+side*5,z+1.65),(10,.14,3.3),white,'07_Interiores')
            # Corridor wall split around a 1.2m doorway.
            for dx in [-2.8,2.8]:box('Frente_camarote_'+level,(x+dx,side*5,z+1.65),(4.4,.14,3.3),white,'07_Interiores')
            box('Dintel_'+level,(x,side*5,z+3),(1.2,.14,.6),white,'07_Interiores')
            box('Cama_'+level,(x+1,y,z+.45),(2,3,.9),fabric,'07_Interiores',.12)
            box('Armario_'+level,(x-3,y+side*2,z+1),(1.2,2,2),teak,'07_Interiores')
    box('Pasillo_'+level,(0,0,z+.015),(rx*1.65,9,.03),teak,'07_Interiores')
# Central aft stair connects the two accommodation decks; floor and corridor both have a shaft.
for name in ['Suelo_interior_A','Pasillo_A']:
    opening(bpy.data.objects[name],(31.75,0,10.5),(7.5,3.2,1))
for k in range(25):box('Escalon_B_A',(28.15+k*.3,0,5.5+(k+1)*.2-.1),(.3,2.8,.2),deckmat,'07_Interiores')
# Navigation bridge in bow, at intermediate elevation.
box('Suelo_puente',(-43,0,14.2),(16,12,.25),metal,'07_Interiores')
for side in [-1,1]:opening(bpy.data.objects['Suelo_puente'],(-37.7,side*6,14.2),(11.4,3.2,1))
for y in [-3,0,3]:
    box('Consola_puente',(-48,y,15),(2.2,2,1.3),dark,'07_Interiores',.2)
    box('Sillon_piloto',(-45,y,14.8),(1,1,1.2),fabric,'07_Interiores',.2)
# Design labels and a human scale reference on the terrace.
def label(n,text,loc,size,m,rot=(0,0,0),g='02_Cubierta'):
    c=bpy.data.curves.new(n,'FONT');c.body=text;c.size=size;c.extrude=.006
    o=bpy.data.objects.new(n,c);COL[g].objects.link(o);o.location=loc;o.rotation_euler=rot;c.materials.append(m);return o
label('Nombre_cubierta','A U R E L I A',(-30,-2,18.035),1.3,gold)
for x,y in [(-25,8),(26,-8)]:
    box('Escala_humana_cuerpo',(x,y,18.9),(.42,.24,1.25),blue,bevel=.1)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.15,location=(x,y,19.65));put(bpy.context.object,'04_Mobiliario',blue).name='Escala_humana_180cm'
# Render studio and review cameras.
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.17,.17,.17)
scene.view_settings.view_transform='AgX'
for name,loc,power,size in [('Key',(-50,-70,100),140000,80),('Fill',(20,60,75),110000,70),('Rim',(70,-10,80),150000,60)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);COL['08_Estudio'].objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,15))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(n,loc,target,scale=160):
    d=bpy.data.cameras.new(n);d.type='ORTHO';d.ortho_scale=scale;d.lens=45;d.clip_end=1000
    o=bpy.data.objects.new(n,d);COL['08_Estudio'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
CAMS={
 'perspectiva':camera('CAM_Perspectiva',(-130,-145,122),(4,0,15),166),
 'superior':camera('CAM_Superior',(0,0,180),(0,0,0),170),
 'lateral':camera('CAM_Lateral',(0,-180,19),(0,0,19),170),
 'frontal':camera('CAM_Frontal',(-180,0,18),(0,0,18),112),
 'popa':camera('CAM_Popa',(180,0,20),(0,0,20),112),
 'terraza':camera('CAM_Terraza',(-72,-73,105),(0,0,18),115),
}
# Ensure orthographic top uses +X to the right and +Y up.
CAMS['superior'].rotation_euler=(0,0,0)
scene.camera=CAMS['perspectiva']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_distance=155
        area.spaces.active.region_3d.view_location=Vector((0,0,16))
# Inspect data before export; rendering rigs excluded.
objects=[o for c in COL.values() if c.name!='08_Estudio' for o in c.objects]
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=hull
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Aurelia-v1.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Aurelia-v1.glb'),export_format='GLB',use_selection=True,export_apply=True)
deps=bpy.context.evaluated_depsgraph_get();tris=0
for o in objects:
    if o.type in {'MESH','CURVE','FONT'}:
        e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);e.to_mesh_clear()
audit={'version':1,'units':'metres','axes':{'aft':'+X','port':'+Y','up':'+Z'},'body_length':120,'body_width':52,'overall_width':76,'overall_height':40,'overall_length':129,'deck_height':18,'pool':[38,12,1.5],'cabanas':len(cab),'rooms':len(ROOMS),'objects':len(objects),'triangles_evaluated':tris,'integration':'NOT imported into L2','reference':'Single user-provided perspective; unseen parts are original proposals','rooms_data':ROOMS}
(OUT/'design-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
for n,cam in CAMS.items():
    if os.environ.get('AURELIA_VIEWS') and n not in os.environ['AURELIA_VIEWS'].split(','):continue
    scene.camera=cam;scene.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True)
# Real geometric half-section: duplicate evaluated geometry and bisect along centreline.
import bmesh
section=group('09_Corte_solo_revision')
for o in objects:
    if o.type not in {'MESH','CURVE','FONT'}:continue
    e=o.evaluated_get(deps);me=bpy.data.meshes.new_from_object(e,depsgraph=deps)
    me.transform(o.matrix_world)
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,0,0),plane_no=(0,-1,0),clear_outer=True,clear_inner=False)
    bm.to_mesh(me);bm.free()
    du=bpy.data.objects.new('CORTE_'+o.name,me);section.objects.link(du)
for c in COL.values():
    if c.name not in ['08_Estudio','09_Corte_solo_revision']:c.hide_render=True
scene.camera=camera('CAM_Corte',(-105,-145,84),(0,0,15),160)
scene.render.filepath=str(OUT/'corte-3d.png');bpy.ops.render.render(write_still=True)
section.hide_render=True;section.hide_viewport=True
for c in COL.values():
    if c.name!='09_Corte_solo_revision':c.hide_render=False
scene.camera=CAMS['perspectiva']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Aurelia-v1.blend'))
print('AURELIA_COMPLETE',json.dumps({k:v for k,v in audit.items() if k!='rooms_data'}))
