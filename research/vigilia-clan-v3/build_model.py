"""V3: stock L2-relative furniture and a rebuilt rectangular bridge/stair assembly."""
from pathlib import Path
OUT=Path(__file__).resolve().parent
src=(OUT.parent/'vigilia-clan-v2/build_model.py').read_text(encoding='utf8')
exec(compile(src.split('# Scene, preview cameras')[0],str(OUT.parent/'vigilia-clan-v2/build_model.py'),'exec'))
D=OUT
# Preserve hull, balloon, dragon and gallery dimensions. Replace cabin assemblies.
prefixes=['Aposento_','Jamba_','Ventana_aposento','Marco_aposento','Parteluz_nuevo','Dintel_','Puente_superior_','Escalon_clan_','Nariz_escalon','Pasamano_clan','Pasamano_interior','Poste_escalera','Mamparo_','Parabrisas_','Pilar_puente','Baranda_superior','Dosel_plano','Cornisa_capitan','Pedestal_timon','Timon_capitan','Radios_capitan','Consola_navegacion','Carta_navegacion','Brujula','Banco_pasajeros','Pata_banco','Respaldo_banco','Banco_galeria','Pata_galeria','Mesa_estrategia_clan','Mapa_clan','Patas_estrategia']
for o in list(geo.objects):
 if any(o.name.startswith(n) for n in prefixes):bpy.data.objects.remove(o,do_unlink=True)
# Existing room furniture is scaled as a group about its own ground datum.
groups=[(['Cama_bastidor','Colchon','Manta_carmesi','Almohada','Cabecero'],(-11.6,-1.9,4.15),(-12.0,-.95,4.15)),(['Mesa_habitacion','Pata_mesa','Mapa_habitacion'],(-10,1.8,4.15),(-10.5,.9,4.15)),(['Silla_aposento','Respaldo_aposento'],(-10,.6,4.15),(-10.5,.45,4.15)),(['Cofre_clan','Tapa_cofre','Cincha_cofre','Cerradura_cofre'],(-8.2,-2,4.15),(-9.25,-.95,4.15))]
for names,old,new in groups:
 for o in geo.objects:
  if any(o.name==n or o.name.startswith(n+'.') for n in names):
   o.location=Vector(new)+(o.location-Vector(old))*.25;o.scale*=.25
   for m in o.modifiers:
    if m.type=='BEVEL':m.width*=.25
for x in [-10.56,-10.44]:
 for y in [.39,.51]:box('Pata_silla',(x,y,4.205),(.025,.025,.11),wood[2])
# Rectangular lower room, clear doorway, properly framed windows.
LOW=4.15;UP=5.43;ROOMTOP=UP-.12;MID=(LOW+ROOMTOP)/2
box('Aposento_popa_V3',(-12.9,0,MID),(.10,3.5,ROOMTOP-LOW),wood[1])
for side in [-1,1]:
 box('Aposento_lateral_V3',(-10.7,side*1.75,MID),(4.5,.10,ROOMTOP-LOW),wood[1])
 box('Aposento_frente_V3',(-8.5,side*1.15,MID),(.10,1.2,ROOMTOP-LOW),wood[1])
 rod('Jamba_V3',(-8.44,side*.55,LOW),(-8.44,side*.55,ROOMTOP),.035,gold)
 for x in [-12.25,-11.2,-10.15,-9.1]:
  box('Ventana_V3',(x,side*1.81,4.88),(.55,.02,.46),glass,.025)
  for z in [4.64,5.12]:box('Marco_V3',(x,side*1.825,z),(.61,.025,.035),gold)
  for dx in [-.29,.29]:box('Montante_V3',(x+dx,side*1.825,4.88),(.035,.025,.48),gold)
box('Dintel_V3',(-8.5,0,ROOMTOP-.10),(.10,1.1,.20),wood[1])
# One rectangle, square corners, no taper. Side landings are a distinct promenade.
box('Puente_suelo_V3',(-10.7,0,UP-.06),(4.8,6.3,.12),wood[3])
for side in [-1,1]:
 line('Borde_rectangular_V3',[(-13.1,side*3.15,UP),(-8.3,side*3.15,UP)],.04,gold)
 line('Baranda_puente_V3',[(-13.1,side*3.15,UP+.34),(-8.4,side*3.15,UP+.34)],.025,gold)
 for x in [-13,-12,-11,-10,-9]:rod('Poste_puente_V3',(x,side*3.15,UP),(x,side*3.15,UP+.34),.018,gold,8)
 # 16 treads, 8u rise, 24u run, 88u width, connected to a solid upper landing.
 for j in range(16):
  x=-4.86-j*.24;z=LOW+(j+1)*.08
  box('Escalon_V3',(x,side*2.65,z-.045),(.25,.88,.09),wood[3])
  box('Nariz_V3',(x+.11,side*2.65,z+.004),(.014,.88,.008),gold)
 for yy in [side*2.17,side*3.13]:
  line('Pasamanos_V3',[(-4.7,yy,LOW+.37),(-8.6,yy,UP+.37)],.018,gold)
  for j in [0,4,8,12,15]:
   x=-4.86-j*.24;z=LOW+(j+1)*.08;rod('Poste_escalera_V3',(x,yy,z),(x,yy,z+.37),.015,gold,8)
 # Closed exterior stair cheek below the tread; removes floating, disconnected look.
 mesh('Zanca_V3',[( -4.70,side*3.08,LOW),(-8.58,side*3.08,UP-.09),(-8.58,side*3.08,UP-.26),(-4.70,side*3.08,LOW-.12)],[(0,1,2,3)],wood[2])
# Forward-facing captain cabin: +X is the bow. Aft stays open for walking in.
for side in [-1,1]:
 box('Mamparo_lateral_V3',(-10.9,side*1.50,UP+.19),(3.6,.06,.38),wood[1])
 box('Cristal_lateral_V3',(-10.9,side*1.50,UP+.52),(3.6,.025,.28),eye)
 for x in [-12.7,-10.9,-9.1]:rod('Pilar_capitan_V3',(x,side*1.5,UP),(x,side*1.5,UP+.94),.025,gold,8)
box('Mamparo_frontal_V3',(-9.1,0,UP+.19),(.06,3.0,.38),wood[1])
box('Cristal_frontal_V3',(-9.1,0,UP+.52),(.025,3.0,.28),eye)
box('Travesano_frontal_V3',(-9.08,0,UP+.68),(.05,3.06,.035),gold)
for y in [-1.5,0,1.5]:rod('Marco_frontal_V3',(-9.08,y,UP+.36),(-9.08,y,UP+.68),.018,gold,8)
box('Techo_rectangular_V3',(-10.9,0,UP+.97),(3.8,3.2,.08),wood[2])
for y in [-1.6,1.6]:box('Cornisa_V3',(-10.9,y,UP+.99),(3.8,.035,.10),gold)
for x in [-12.8,-9.0]:box('Cornisa_extremo_V3',(x,0,UP+.99),(.035,3.2,.10),gold)
rod('Pedestal_timon_V3',(-10.15,0,UP),(-10.15,0,UP+.28),.028,gold,10)
ring('Timon_V3',(-10.15,0,UP+.34),.20,.20,wood[1],tube=.023,N=28)
for j in range(10):
 t=j*math.tau/10;rod('Radio_V3',(-10.15,0,UP+.34),(-10.15,.25*math.cos(t),UP+.34+.25*math.sin(t)),.012,gold,6)
box('Consola_V3',(-9.75,.85,UP+.20),(.48,.38,.40),wood[1],.025)
box('Carta_V3',(-9.75,.85,UP+.41),(.44,.34,.015),paper)
ring('Brujula_V3',(-9.7,.85,UP+.43),.07,.07,gold,axis='Z',tube=.008,N=16)
# More benches at character scale, all east of the stair foot; each with real legs.
def bench(x,y,z,name):
 box('Banco_'+name,(x,y,z+.125),(.85,.20,.055),wood[1],.01)
 box('Respaldo_'+name,(x,y+.105,z+.235),(.85,.035,.19),wood[1],.01)
 for dx in [-.32,.32]:
  for dy in [-.07,.07]:box('Pata_'+name,(x+dx,y+dy,z+.06),(.025,.025,.12),gold)
for side in [-1,1]:
 for x in [.5,3.5,6.5,9.0]:bench(x,side*3.8,LOW,'clan_V3')
 for x in [-1.3,1.3,3.9,5.6]:bench(x,side*3.5,11.2,'galeria_V3')
# Compact planning tables, clear of stair corridors and the central route.
for x,y in [(4,-2.7),(7,2.6)]:
 box('Mesa_clan_V3',(x,y,LOW+.21),(.85,.42,.04),wood[1],.012)
 box('Mapa_clan_V3',(x,y,LOW+.237),(.75,.35,.012),paper)
 for dx in [-.32,.32]:
  for dy in [-.14,.14]:box('Patas_mesa_V3',(x+dx,y+dy,LOW+.105),(.03,.03,.21),gold)
# 46-unit comparison mannequin, kept out of the game export and navigation.
for x,y,z in [(-10.5,-.15,LOW),(-11.1,0,UP),(-4.2,2.65,LOW)]:
 body=box('REFERENCIA_46U',(x,y,z+.24),(.105,.075,.32),navy)
 head=uv('REFERENCIA_CABEZA',(x,y,z+.42),(.06,.055,.06),ivory,12,6)
 for o in [body,head]:move(o,studio)
 for yy in [y-.035,y+.035]:
  leg=box('REFERENCIA_PIERNA',(x,yy,z+.07),(.04,.035,.14),navy);move(leg,studio)
# Navigation: ramps are continuous client support; the visual treads remain visible.
nav=[]
for o in geo.objects:
 isfloor=o.name.startswith(('Cubierta_principal','Puente_suelo_V3','Galeria_intermedia'))
 iswall=o.name.startswith(('Aposento_','Dintel_V3','Mamparo_','Cristal_','Baranda_galeria','Testero_galeria','Barandal_intermedio','Pasamanos','Cama_bastidor','Cofre_clan','Banco_clan_V3','Respaldo_clan_V3'))
 if not (isfloor or iswall):continue
 deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();wv=[tuple(o.matrix_world@v.co) for v in me.vertices]
 for t in me.loop_triangles:
  pts=[wv[i] for i in t.vertices];a,b,c=map(Vector,pts);n=(b-a).cross(c-a)
  if isfloor and (n.z<=.001 or n.z<.8*n.length):continue
  if iswall and abs(n.z)>.45*n.length:continue
  nav.append(pts)
 e.to_mesh_clear()
for side in [-1,1]:
 # Start after a level landing; rise gently with no 15/16u aliasing steps.
 x0=-4.70;x1=-8.58;y=side*2.65
 vs=[(x0,y-.44,LOW),(x0,y+.44,LOW),(x1,y+.44,UP),(x1,y-.44,UP)]
 nav.extend([[vs[0],vs[1],vs[2]],[vs[0],vs[2],vs[3]]])
(D/'navigation-source.json').write_text(json.dumps(nav))
scene.world=bpy.data.worlds.new('Estudio_V3');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.21,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((25,-35,45),24000,25),((-20,20,35),19000,20),((30,20,20),12000,15)]:
 d=bpy.data.lights.new('Luz','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new('Luz',d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,10))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camara',bpy.data.cameras.new('Camara'));studio.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=1000
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene['revision']='V3 character proportions';scene['furniture_scale_vs_v2']=.25;scene['bridge_z']=UP;scene['stairs']='16 treads per side: 8u rise,24u run; continuous support proxy'
bpy.ops.wm.save_as_mainfile(filepath=str(D/'Vigilia-clan-v3.blend'))
for name,loc,target,zoom in [('vista-general',(48,-65,38),(0,0,13),62),('cabina-frente',(0,-12,11),(-10.7,0,5.8),10),('aposento',(-8.9,0,5.12),(-11,0,4.5),4.9),('escaleras',(.5,-12,10),(-7,-2.65,4.95),12),('mobiliario',(8,-10,7),(3,-2,4.4),12)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom;scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
print('V3_MODEL_COMPLETE')
