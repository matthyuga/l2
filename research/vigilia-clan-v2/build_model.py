"""Vigilia clan revision, derived non-destructively from the V1 source."""
from pathlib import Path
OUT=Path(__file__).resolve().parent
src=(OUT.parent/'airship-epic/build_epic.py').read_text(encoding='utf8')
exec(compile(src.split('# Export-oriented metadata')[0],str(OUT.parent/'airship-epic/build_epic.py'),'exec'))
D=OUT
remove=['Cabina_capitan','Puerta_capitan','Jamba_puerta','Techo_doble_aguas','Cumbrera_capitan','Alero_capitan','Plataforma_timon','Escalon_puente','Pasamano_escalera','Soporte_timon','Rueda_timon','Radio_timon','Toldo_central_carmesi','Borde_toldo','Tirante_toldo','Marco_ventana','Vidrio_ambar','Parteluz','Esquina_reforzada','Cuello_dragon','Craneo_dragon','Hocico_dragon','Boca_sombra','Mandibula_dragon','Cuenca_ojo','Ojo_dragon','Ceja_dragon','Cuerno_dragon','Diente_dragon','Fosa_nasal','Espina_cuello']
for o in list(geo.objects):
 if any(o.name==n or o.name.startswith(n+'.') for n in remove):bpy.data.objects.remove(o,do_unlink=True)
scale=mat('Escamas_obsidiana',(.055,.105,.105),.65,.35)
scale2=mat('Escamas_jade',(.14,.28,.23),.7,.3)
redcloth=reds[1]
navy=mat('Tapiceria_azul',(.025,.08,.12),0,.7)
paper=mat('Pergamino',(.62,.48,.27),0,.9)
# Open lower cabin: actual walls with a clear 2.4m entrance.
box('Aposento_pared_popa',(-13.1,0,5.75),(.22,6.6,3.2),wood[1])
for side in [-1,1]:
 box('Aposento_lateral',(-10,side*3.3,5.75),(6.4,.20,3.2),wood[1])
 box('Aposento_frente_abierto',(-6.8,side*2.25,5.75),(.22,2.1,3.2),wood[1])
 rod('Jamba_entrada',(-6.65,side*1.2,4.15),(-6.65,side*1.2,7.35),.10,gold)
 for x in [-11.8,-9.8,-7.8]:
  box('Ventana_aposento',(x,side*3.415,5.9),(1.25,.035,1.35),glass,.06)
  for zz in [5.2,6.6]:box('Marco_aposento',(x,side*3.45,zz),(1.45,.08,.10),gold)
  rod('Parteluz_nuevo',(x,side*3.46,5.2),(x,side*3.46,6.6),.035,gold,6)
box('Dintel_entrada',(-6.8,0,7.15),(.22,2.4,.4),wood[1])
# Sleeping and planning quarters, furniture sized around a 1.8m human.
box('Cama_bastidor',(-11.6,-1.9,4.4),(2.4,1.55,.5),wood[2],.08)
box('Colchon',(-11.6,-1.9,4.73),(2.25,1.4,.22),ivory,.1)
box('Manta_carmesi',(-11.35,-1.9,4.87),(1.55,1.4,.08),redcloth,.06)
box('Almohada',(-12.35,-1.9,4.94),(.45,1.1,.14),paper,.08)
box('Cabecero',(-12.85,-1.9,4.95),(.18,1.65,1.25),gold,.06)
box('Mesa_habitacion',(-10,1.8,4.95),(2,1.2,.14),wood[3],.06)
for x in [-10.75,-9.25]:
 for y in [1.35,2.25]:box('Pata_mesa',(x,y,4.55),(.12,.12,.8),gold)
box('Mapa_habitacion',(-10,1.8,5.04),(1.5,.9,.025),paper)
box('Silla_aposento',(-10,.6,4.58),(.65,.65,.12),navy,.04)
box('Respaldo_aposento',(-10,.3,4.95),(.65,.12,.8),wood[2],.04)
box('Cofre_clan',(-8.2,-2,4.6),(1.5,.85,.9),wood[0],.12)
box('Tapa_cofre',(-8.2,-2,5.1),(1.55,.9,.22),wood[1],.1)
for x in [-8.7,-7.7]:box('Cincha_cofre',(x,-2,4.7),(.10,.92,1.05),gold,.02)
box('Cerradura_cofre',(-8.2,-1.52,4.8),(.22,.08,.3),edge,.03)
# Flat upper captain deck replaces the tiled roof; side stair landings meet it.
upper=[(-13.4,-2.7,7.45),(-7.3,-4.65,7.45),(-6.65,-4.65,7.45),(-6.65,4.65,7.45),(-7.3,4.65,7.45),(-13.4,2.7,7.45)]
o=mesh('Puente_superior_plano',upper,[tuple(range(len(upper)))],wood[3]);s=o.modifiers.new('Losa','SOLIDIFY');s.thickness=.18
for side in [-1,1]:
 # 22 steps instead of 8, each rising 15u in game; two grid columns per tread.
 for j in range(22):
  top=4.15+(j+1)*.15;x=-.20-j*.32
  box('Escalon_clan_15cm',(x,side*4.05,top-.10),(.34,1.35,.20),wood[3])
  box('Nariz_escalon',(x+.15,side*4.05,top+.012),(.035,1.35,.024),gold)
 line('Pasamano_clan',[(-.04,side*4.78,5.2),(-7.1,side*4.78,8.5)],.065,gold)
 line('Pasamano_interior',[(-.04,side*3.32,5.2),(-6.7,side*3.32,8.35)],.055,gold)
 for j in range(0,22,4):
  x=-.2-j*.32;z=4.15+(j+1)*.15
  rod('Poste_escalera',(x,side*4.78,z),(x,side*4.78,z+1.05),.045,gold,8)
 # Partial windshield and posts; bridge has an open front and no tiled roof.
 box('Mamparo_puente',(-10,side*2.65,8.05),(5.6,.12,1.2),wood[1])
 box('Parabrisas_lateral',(-10,side*2.67,9),(5.6,.04,.7),eye)
 for x in [-12.7,-9.7,-7.2]:rod('Pilar_puente',(x,side*2.7,7.45),(x,side*2.7,10.2),.075,gold)
 line('Baranda_superior',[(-13.25,side*2.65,8.55),(-7.5,side*4.4,8.55)],.06,gold)
box('Mamparo_trasero_puente',(-13,0,8),( .14,5.3,1.1),wood[1])
box('Dosel_plano_capitan',(-10,0,10.25),(6.6,5.7,.15),wood[2],.05)
for side in [-1,1]:box('Cornisa_capitan',(-10,side*2.85,10.3),(6.8,.10,.2),gold,.03)
rod('Pedestal_timon',(-8.5,0,7.45),(-8.5,0,8.45),.11,gold)
ring('Timon_capitan',(-8.45,0,8.65),.65,.65,wood[1],tube=.065,N=32)
for j in range(10):
 t=j*math.tau/10;rod('Radios_capitan',(-8.45,0,8.65),(-8.45,.85*math.cos(t),8.65+.85*math.sin(t)),.035,gold,8)
box('Consola_navegacion',(-9.6,1.6,8.25),(1.3,1,.9),wood[1],.1)
box('Carta_navegacion',(-9.6,1.6,8.73),(1.15,.85,.035),paper)
ring('Brujula',(-9.5,1.6,8.78),.23,.23,gold,axis='Z',tube=.025,N=20)
# The former fabric canopy becomes a rigid, walkable observation gallery.
box('Galeria_intermedia',(2,0,11.10),(10,8.2,.20),wood[3])
for y in [-4.05,4.05]:
 line('Baranda_galeria',[(-3,y,12.25),(7,y,12.25)],.075,gold)
 line('Baranda_media_galeria',[(-3,y,11.75),(7,y,11.75)],.045,gold)
 for x in range(-3,8):rod('Poste_galeria',(x,y,11.2),(x,y,12.25),.05,gold,8)
for x in [-3,7]:
 line('Testero_galeria',[(x,-4.05,12.25),(x,4.05,12.25)],.075,gold)
 for y in [-4,-2,0,2,4]:rod('Poste_testero',(x,y,11.2),(x,y,12.25),.05,gold,8)
for x in [-2.8,6.8]:
 for side in [-1,1]:line('Suspension_galeria',[(x,side*4,11.1),(x,side*4.7,16.7)],.065,iron)
for side in [-1,1]:
 box('Banco_galeria',(2,side*3,11.65),(3,.65,.16),wood[1],.05)
 for x in [.8,3.2]:box('Pata_galeria',(x,side*3,11.4),(.1,.4,.4),gold)
# Clan identity: banner posts and meeting chart, retaining a broad central aisle.
for side in [-1,1]:
 rod('Asta_clan',(10,side*3.5,4.15),(10,side*3.5,7.7),.055,gold)
 mesh('Estandarte_clan',[(10,side*3.5,7.5),(8.9,side*3.5,7.5),(8.9,side*3.5,5.8),(9.45,side*3.5,5.45),(10,side*3.5,5.8)],[(0,1,2,3,4)],redcloth)
 ring('Sello_estandarte',(0,0,0),.28,.28,edge) .location=(9.45,side*3.51,6.65)
box('Mesa_estrategia_clan',(5,-2.2,5),(2.8,1.3,.16),wood[1],.07)
box('Mapa_clan',(5,-2.2,5.1),(2.5,1.1,.025),paper)
for x in [4,6]:
 for y in [-2.65,-1.75]:box('Patas_estrategia',(x,y,4.55),(.14,.14,.8),gold)
# Sculpted segmented figurehead: angular muzzle, recessed slit eyes, scale plates,
# swept horns, cheek fans and a layered armored neck instead of smooth cylinders.
def loft(name,rings,material,N=12):
 vs=[]
 for x,z,ry,rz in rings:
  for j in range(N):
   t=math.tau*j/N;vs.append((x,ry*math.cos(t),z+rz*math.sin(t)))
 fs=[tuple(reversed(range(N)))]
 for k in range(len(rings)-1):
  for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 fs.append(tuple((len(rings)-1)*N+j for j in range(N)))
 return mesh(name,vs,fs,material)
loft('Cuello_acorazado',[(14.5,4.2,1.1,1),(16,4.8,1.05,1.15),(17.3,6.2,.9,1.2),(18.3,7.7,1.0,1.05),(19.5,8.3,1.05,.95)],scale)
loft('Cabeza_angular',[(18.5,8.5,.65,.7),(19.4,8.65,1.2,1.0),(20.4,8.4,1.15,1.05),(21.1,8.1,.78,.65),(22.3,7.9,.65,.48),(23.3,8.0,.60,.4),(23.6,8.05,.4,.3)],patina)
loft('Mandibula_dentada',[(19.6,7.2,.65,.25),(20.6,6.9,.7,.22),(22.1,6.95,.6,.18),(23.3,7.18,.45,.15)],gold)
loft('Garganta_oscura',[(20,7.45,.65,.3),(21.5,7.3,.58,.3),(23.3,7.52,.44,.17)],black)
for side in [-1,1]:
 # Eye sockets become long and slanted; ridges create a deliberate severe brow.
 uv('Orbita_hundida',(20.3,side*1.08,8.65),(.55,.12,.25),black,16,8)
 uv('Iris_draconico',(20.42,side*1.20,8.64),(.29,.055,.11),eye,16,8)
 box('Pupila_vertical',(20.45,side*1.255,8.65),(.045,.02,.17),black)
 line('Ceja_acorazada',[(19.5,side*.95,9.12),(20.1,side*1.24,9.04),(20.9,side*.91,8.63)],.16,scale2)
 line('Mandibula_filigrana',[(19.4,side*.8,7.6),(20.7,side*.73,7.0),(23.25,side*.5,7.21)],.06,edge)
 horn=[(19.1,side*.8,9.2),(18.7,side*1.2,10.1),(17.7,side*1.65,11),(16.4,side*1.9,11.45),(15.8,side*1.75,11.7)]
 for j,(a,b) in enumerate(zip(horn,horn[1:])):rod('Cuerno_anillado',a,b,.36*(1-j/4),gold,10,r2=max(0,.36*(1-(j+1)/4)))
 for j in range(3):
  a=(19-j*.25,side*(.85+j*.05),8.5-j*.43);b=(17.2-j*.35,side*(1.7-j*.1),9.0-j*.65)
  mesh('Abanico_mejilla',[a,b,(b[0]+.6,b[1],b[2]-.5),(a[0]+.5,a[1],a[2]-.2)],[(0,1,2,3)],scale2)
  line('Nervio_mejilla',[a,b],.055,gold)
 for j in range(8):
  x=20.2+j*.40;z=7.65 if j<4 else 7.64+(j-4)*.045
  rod('Colmillo_superior',(x,side*.53,z),(x+.1,side*.50,z-(.65 if j in [1,5] else .30)),.10 if j in [1,5] else .065,ivory,7,r2=0)
 for j in range(5):rod('Diente_inferior',(20.6+j*.48,side*.50,7.12),(20.65+j*.48,side*.48,7.42),.055,ivory,6,r2=0)
 uv('Narina_profunda',(23.1,side*.48,8.2),(.22,.075,.12),black,12,6)
 line('Narina_borde',[(22.75,side*.55,8.35),(23.15,side*.57,8.37),(23.4,side*.43,8.24)],.045,edge)
 # Shingled neck armor, each scale a raised diamond with an engraved rim.
 for row in range(8):
  t=row/7;x=15.2+t*3.8;z=4.7+t*3.7
  for band in range(3):
   yy=side*(.78+.10*math.sin(t*math.pi));zz=z+(band-1)*.50
   pts=[(x-.45,yy,zz),(x-.12,yy+side*.12,zz+.28),(x+.50,yy,zz+.13),(x+.1,yy+side*.10,zz-.25)]
   mesh('Escama_cuello',pts,[(0,1,2,3)],scale2 if (row+band)%3 else patina)
   line('Grabado_escama',pts[:3],.022,edge,res=0)
for j in range(8):
 x=15+j*.62;z=5.2+j*.56
 mesh('Cresta_dorsal',[(x-.3,0,z),(x-.7,0,z+1.25),(x+.35,0,z+.45)],[(0,1,2)],gold)
for j in range(4):
 x=20.5+j*.55
 mesh('Placa_frente',[(x-.4,-.5,8.85-j*.15),(x+.2,0,9.08-j*.2),(x-.4,.5,8.85-j*.15),(x-.8,0,9.13-j*.15)],[(0,1,2,3)],scale2)
# Scene, preview cameras, and reproducible navigation proxy list.
scene.world=bpy.data.worlds.new('Estudio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.17,.22,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((25,-35,45),24000,25),((-20,20,35),19000,20),((30,20,20),12000,15)]:
 d=bpy.data.lights.new('Luz','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new('Luz',d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,10))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camara',bpy.data.cameras.new('Camara'));studio.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=1000
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene['revision']='V2 clan';scene['stairs']='22 treads per side; .15 rise, .32 run';scene['platform_z']=11.2
scene['capacity_note']='Clan social layout; no enforced passenger limit'
bpy.ops.wm.save_as_mainfile(filepath=str(D/'Vigilia-clan-v2.blend'))
# Geo proxies avoid furniture/roof ghost floors: collect only actual walkable floors and walls.
floor_names=['Cubierta_principal','Puente_superior_plano','Escalon_clan_15cm','Galeria_intermedia']
wall_names=['Aposento_pared','Aposento_lateral','Aposento_frente','Dintel_entrada','Baranda_galeria','Testero_galeria','Mamparo_','Parabrisas_','Barandal_intermedio','Pasamanos','Banco_pasajeros','Respaldo_banco','Cama_bastidor','Mesa_habitacion','Cofre_clan','Mesa_estrategia_clan','Consola_navegacion']
deps=bpy.context.evaluated_depsgraph_get();tris=[]
for o in geo.objects:
 if not any(o.name.startswith(n) for n in floor_names+wall_names):continue
 e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles()
 wv=[tuple(o.matrix_world@v.co) for v in me.vertices]
 isfloor=any(o.name.startswith(n) for n in floor_names)
 for t in me.loop_triangles:
  pts=[wv[i] for i in t.vertices]
  a,b,c=map(Vector,pts);normal=(b-a).cross(c-a)
  # Only horizontal top faces for support; walls supply vertical ray blockers.
  if isfloor:
   if normal.z<=.001 or abs(normal.z)<.8*normal.length:continue
  elif abs(normal.z)>.45*normal.length:continue
  tris.append(pts)
 e.to_mesh_clear()
(D/'navigation-source.json').write_text(json.dumps(tris))
for name,loc,target,zoom in [('vista-general',(48,-65,38),(0,0,13),62),('dragon-detalle',(34,-21,16),(19,0,8),17),('cubierta-clan',(24,-32,26),(-3,0,7),36),('aposento',(-1,-9,10),(-10,0,5.5),15),('puente-y-galeria',(12,-30,22),(-3,0,9),33)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=zoom
 scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
print('VIGILIA_CLAN_MODEL_COMPLETE')
