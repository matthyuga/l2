"""Original procedural airship design, inspired by Kevin's supplied reference."""
import bpy,math,random,pathlib,json
from mathutils import Vector
random.seed(71);D=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
geo=bpy.data.collections.new('01_AERONAVE_EXPORT');scene.collection.children.link(geo)
studio=bpy.data.collections.new('02_ESTUDIO_NO_EXPORTAR');scene.collection.children.link(studio)
def move(o,col=geo):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o
def mat(name,color,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
wood=[]
for i,c in enumerate([(.095,.036,.021),(.14,.055,.027),(.075,.028,.018),(.18,.073,.033)]):
 m=mat('Madera_casco_'+str(i),c,0,.58);nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2;coord=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,32,32);nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],tex.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.05;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal']);wood.append(m)
gold=mat('Bronce_dorado',(.48,.245,.065),.78,.3);edge=mat('Laton_luminoso',(.72,.43,.13),.7,.28);iron=mat('Acero_oscuro',(.035,.048,.049),.78,.36);patina=mat('Bronce_dragon_patinado',(.12,.22,.18),.72,.37);rope=mat('Cuerda_oscura',(.11,.075,.04),0,.85);black=mat('Huecos_negros',(.008,.011,.011),.2,.75);glass=mat('Farol_ambar',(.95,.24,.025),.15,.25,3);eye=mat('Cristal_dragon',(.08,.62,.65),.3,.22,3);ivory=mat('Marfil_metalico',(.55,.43,.25),.48,.32)
reds=[mat('Lona_carmesi_'+str(i),c,0,.82) for i,c in enumerate([(.28,.028,.018),(.4,.049,.025),(.34,.034,.021),(.46,.077,.031)])]
for m in reds:
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=115;b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.025;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
def mesh(name,vs,fs,material):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();o=bpy.data.objects.new(name,data);geo.objects.link(o)
 if material:data.materials.append(material)
 return o
def box(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object);o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:mod=o.modifiers.new('Cantos','BEVEL');mod.width=bevel;mod.segments=1;o.modifiers.new('Normales','WEIGHTED_NORMAL')
 return o
def uv(name,loc,scale,material,segments=16,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc);o=move(bpy.context.object);o.name=name;o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def line(name,pts,radius,material,cyclic=False,res=1):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=res;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,cu);geo.objects.link(o);cu.materials.append(material);return o
def rod(name,a,b,radius,material,verts=10,r2=None):
 a,b=Vector(a),Vector(b);delta=b-a;bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=radius,radius2=radius if r2 is None else r2,depth=delta.length,location=(a+b)/2);o=move(bpy.context.object);o.name=name;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);return o
def ring(name,center,r1,r2,material,axis='X',tube=.055,N=40):
 pts=[]
 for i in range(N):
  t=2*math.pi*i/N;v=(0,r1*math.cos(t),r2*math.sin(t)) if axis=='X' else (r1*math.cos(t),r2*math.sin(t),0);pts.append(tuple(center[j]+v[j] for j in range(3)))
 return line(name,pts,tube,material,True)
# Bow points toward +X. Main deck at Z4.2, clear central passenger route.
stations=[(-15,.35,2.4),(-14,2.1,3.4),(-12,4.15,4.4),(-8,5.1,5.1),(-3,5.45,5.5),(3,5.35,5.5),(8,4.7,4.9),(12,3.55,4.1),(15,1.7,3.0),(16.5,.15,2.0)]
top=4.05;cross=18;verts=[]
for x,w,depth in stations:
 for j in range(cross+1):
  t=-math.pi/2+j*math.pi/cross;verts.append((x,w*math.sin(t),top-depth*math.cos(t)))
faces=[]
for i in range(len(stations)-1):
 for j in range(cross):faces.append((i*(cross+1)+j,(i+1)*(cross+1)+j,(i+1)*(cross+1)+j+1,i*(cross+1)+j+1))
hull=mesh('Casco_curvo_listones',verts,faces,wood[0])
for m in wood[1:]:hull.data.materials.append(m)
for p in hull.data.polygons:p.material_index=(p.index%cross//2)%4
for j in range(1,cross):
 t=-math.pi/2+j*math.pi/cross;line('Junta_liston_casco',[(x,(w+.025)*math.sin(t),top-(depth+.025)*math.cos(t)) for x,w,depth in stations],.025,wood[2])
for x,w,dep in stations[1:-1]:
 pts=[(x,(w+.05)*math.sin(-math.pi/2+j*math.pi/24),top-(dep+.05)*math.cos(-math.pi/2+j*math.pi/24)) for j in range(25)];line('Cuaderna_de_bronce',pts,.095,gold)
outline=[(x,-w,4.15) for x,w,_ in stations]+[(x,w,4.15) for x,w,_ in reversed(stations)]
deck=mesh('Cubierta_principal',outline,[tuple(range(len(outline)))],wood[3]);solid=deck.modifiers.new('Espesor_cubierta','SOLIDIFY');solid.thickness=.18
line('Borda_ornamental',[(x,y,4.28) for x,y,_ in outline],.18,gold,True)
line('Pasamanos',[(x,y,5.35) for x,y,_ in outline],.10,edge,True)
line('Barandal_intermedio',[(x,y,4.83) for x,y,_ in outline],.055,gold,True)
for i in range(len(outline)):
 a=Vector(outline[i]);b=Vector(outline[(i+1)%len(outline)]);n=max(1,int((b-a).length/1.15))
 for j in range(n):
  v=a.lerp(b,j/n);rod('Puntal_baranda',(v.x,v.y,4.18),(v.x,v.y,5.35),.06,gold,8)
def width_at(x):
 for (ax,aw,_),(bx,bw,_) in zip(stations,stations[1:]):
  if ax<=x<=bx:return aw+(bw-aw)*(x-ax)/(bx-ax)
 return .1
for j in range(52):
 x=-14.8+j*.6;w=width_at(x);line('Junta_tablas_cubierta',[(x,-w+.15,4.157),(x,w-.15,4.157)],.012,wood[0],res=0)
# Deep stern cabin with lit windows, an upper helm and two accessible stairways.
box('Cabina_capitan',(-10.1,0,5.65),(6.3,6.6,3.0),wood[1],.18)
for side in [-1,1]:
 for x in [-12,-10.4,-8.8]:
  box('Marco_ventana',(x,side*3.34,5.8),(1.25,.12,1.65),gold,.05);box('Vidrio_ambar',(x,side*3.42,5.8),(1.02,.07,1.4),glass,.03)
  rod('Parteluz',(x,side*3.48,5.08),(x,side*3.48,6.52),.035,iron,6)
 for x in [-13.2,-6.95]:rod('Esquina_reforzada',(x,side*3.4,4.2),(x,side*3.4,7.2),.12,gold)
box('Puerta_capitan',(-6.9,0,5.5),(.10,1.5,2.6),wood[2],.03)
for y in [-.8,.8]:rod('Jamba_puerta',(-6.8,y,4.2),(-6.8,y,6.9),.07,gold)
roofvs=[(-13.8,-3.8,7.25),(-13.8,0,8.15),(-13.8,3.8,7.25),(-6.55,-3.8,7.25),(-6.55,0,8.15),(-6.55,3.8,7.25)]
mesh('Techo_doble_aguas',roofvs,[(0,3,4,1),(1,4,5,2)],reds[0]);line('Cumbrera_capitan',[(-14,0,8.2),(-6.3,0,8.2)],.13,gold)
for side in [-1,1]:line('Alero_capitan',[(-14,side*3.9,7.45),(-13,side*3.6,7.25),(-7.2,side*3.6,7.25),(-6.3,side*3.9,7.45)],.10,gold)
# A small exposed raised helm astern, not on the sloped cabin roof.
box('Plataforma_timon',(-13.2,0,7.35),(3.2,5.7,.22),wood[3],.06)
for side in [-1,1]:
 for j in range(8):box('Escalon_puente',(-7.1+j*.38,side*4.0,7.25-j*.40),(.44,1.0,.20),wood[3],.025)
 line('Pasamano_escalera',[(-7.35,side*4.5,8.2),(-4.1,side*4.5,4.8)],.065,gold)
rod('Soporte_timon',(-13,0,7.4),(-13,0,8.45),.11,gold)
wheel=ring('Rueda_timon',(-12.95,0,8.5),.70,.70,wood[1],tube=.075,N=24)
for j in range(8):
 t=j*math.pi/4;rod('Radio_timon',(-12.95,0,8.5),(-12.95,.9*math.cos(t),8.5+.9*math.sin(t)),.045,gold,6)
# Envelope: broad crimson canvas panels with bronze bands and longitudinal seams.
N=40;K=32;ballvs=[]
def envelope(t,phi):
 radius=max(.025,math.cos(t))**.72;return (19.5*math.sin(t)-1,6.65*radius*math.cos(phi),21+6.15*radius*math.sin(phi))
for i in range(K+1):
 t=-math.pi/2+i*math.pi/K
 for j in range(N):ballvs.append(envelope(t,j*2*math.pi/N))
ballfs=[]
for i in range(K):
 for j in range(N):ballfs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
ball=mesh('Globo_carmesi_panelado',ballvs,ballfs,reds[0])
for m in reds[1:]:ball.data.materials.append(m)
for p in ball.data.polygons:p.material_index=(p.index%N//2)%4;p.use_smooth=True
for j in range(0,N,2):line('Costura_longitudinal',[envelope(-math.pi/2+i*math.pi/48,j*2*math.pi/N) for i in range(49)],.026,gold,res=0)
for x in [-17,-13,-8,-2,4,10,15,17]:
 t=math.asin((x+1)/19.5);rad=math.cos(t)**.72;ring('Cincha_envolvente',(x,0,21),6.69*rad,6.19*rad,gold,tube=.11,N=40)
# Heraldic dragon seal follows the curved canvas rather than floating on a flat
# plane. It gives the flagship a readable identity from either side.
def crest_point(x,z,side):
 t=math.asin((x+1)/19.5);rad=math.cos(t)**.72;y=6.65*math.sqrt(max(.001,rad*rad-((z-21)/6.15)**2))+.055
 return (x,side*y,z)
for side in [-1,1]:
 for radius in [2.45,2.15]:line('Sello_circular_dragon',[crest_point(radius*math.cos(j*2*math.pi/48),21+radius*math.sin(j*2*math.pi/48),side) for j in range(48)],.07,edge,True)
 paths=[[(.4,19.3),(-.65,19.9),(-.9,20.8),(.25,21.3),(.75,22.1),(.25,22.55),(-.3,22.2)],[(.25,21.3),(1.65,21.95),(1.35,20.9),(.65,20.55)],[(-.65,20.9),(-1.75,21.8),(-1.45,20.45),(-.7,20.2)],[(.25,22.55),(.55,23.0)],[(.7,22.05),(1.05,22.35)]]
 for path in paths:line('Heraldica_dragon',[crest_point(x,z,side) for x,z in path],.09,edge)
for x in [-13,-7,0,7,13]:
 w=width_at(x)
 for side in [-1,1]:
  t=math.asin((x+1)/19.5);anchor=envelope(t,-math.pi/3 if side>0 else -2*math.pi/3)
  line('Jarcia_suspension',[(x,side*w,5.45),(x,side*(w+.4),9.4),anchor],.055,rope,res=1)
  uv('Anclaje_bronce',(x,side*w,5.5),(.15,.15,.19),gold,10,6)
# Secondary suspended crimson canopy over the central social space.
canvs=[]
for x in [-3,7]:
 for j in range(9):
  y=-4.1+j*1.025;canvs.append((x,y,11.2-.65*(1-(y/4.1)**2)))
mesh('Toldo_central_carmesi',canvs,[(j,j+1,10+j,9+j) for j in range(8)],reds[1])
for side in [-1,1]:line('Borde_toldo',[(-3,side*4.1,11.2),(7,side*4.1,11.2)],.065,gold)
for x in [-3,7]:
 for side in [-1,1]:line('Tirante_toldo',[(x,side*4.1,11.2),(x,side*4.7,16.7)],.035,rope,res=0)
# Lanterns: warm emissive glass with faceted metal cages.
def lantern(x,y,z,size=.65):
 rod('Gancho_farol',(x,y,z+.7),(x,y,z+.3),.035,iron,6)
 uv('Vidrio_farol',(x,y,z),(size*.45,size*.45,size*.66),glass,8,4)
 for zz in [-.48,.48]:ring('Aro_farol',(x,y,z+zz*size),size*.37,size*.37,gold,axis='Z',tube=.035,N=8)
 for j in range(4):
  a=j*math.pi/2;rod('Jaula_farol',(x+size*.36*math.cos(a),y+size*.36*math.sin(a),z-size*.48),(x+size*.36*math.cos(a),y+size*.36*math.sin(a),z+size*.48),.025,gold,6)
 bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=size*.55,radius2=.08,depth=size*.30,location=(x,y,z+size*.65));o=move(bpy.context.object);o.name='Capucha_farol';o.data.materials.append(gold)
for x in [-12,-6,0,6,12]:
 w=width_at(x)
 for side in [-1,1]:
  line('Brazo_farol',[(x,side*w,4.6),(x,side*(w+.4),7.4),(x,side*(w+1),7.4)],.055,gold)
  lantern(x,side*(w+1),6.35,.8)
# Portholes and articulated bronze lower belly ribs.
for x in [-10,-6,-2,2,6,10]:
 w=width_at(x)
 for side in [-1,1]:
  # A porthole plane lies in XZ; ring helper's X plane is rotated into Y.
  o=ring('Ojo_de_buey',(0,0,0),.43,.43,edge,tube=.085,N=16);o.rotation_euler[2]=math.pi/2;o.location=(x,side*(w*.93),2.8)
  uv('Cristal_ojo_de_buey',(x,side*(w*.93),2.8),(.34,.05,.34),glass,12,6)
# Twin side engines, braces and propellers behind the hull.
for side in [-1,1]:
 y=side*6.3
 rod('Brazo_motor',(-8,side*3.9,2),(-10,y,1.2),.22,gold,10)
 rod('Brazo_motor_inferior',(-5,side*3.6,.8),(-10,y,1.2),.18,iron,10)
 rod('Gondola_motor',(-12,y,1.2),(-8,y,1.2),1.0,iron,16)
 for x in [-11.7,-10.9,-10.1,-9.3,-8.5]:ring('Costilla_motor',(x,y,1.2),1.02,1.02,gold,tube=.075,N=16)
 ring('Nucleo_motor_ambar',(-8.0,y,1.2),.65,.65,glass,tube=.15,N=20)
 rod('Eje_helice',(-13.2,y,1.2),(-11.8,y,1.2),.16,gold)
 for j in range(4):
  a=j*math.pi/2+.35;radial=Vector((0,math.cos(a),math.sin(a)));tangent=Vector((0,-math.sin(a),math.cos(a)));center=Vector((-13.3,y,1.2));pts=[center+radial*.4-tangent*.12,center+radial*2.7-tangent*.4+Vector((.2,0,0)),center+radial*3+tangent*.22+Vector((.2,0,0)),center+radial*.8+tangent*.3]
  mesh('Aspa_helice',[tuple(v) for v in pts],[(0,1,2,3)],wood[1])
 uv('Buje_helice',(-13.45,y,1.2),(.32,.4,.4),gold,12,6)
# Aft fins and heraldic fabric tail.
for side in [-1,1]:
 pts=[(-16,side*2,20),(-22,side*9,20.8),(-20,side*8.4,17.6),(-17,side*3,18.4)];mesh('Aleta_timon_lona',pts,[(0,1,2,3)],reds[0]);line('Marco_aleta',pts,.095,gold,True)
pts=[(-17,0,22),(-23,0,29),(-21,0,25.8),(-23,0,23.4),(-19,0,20)];mesh('Aleta_dorsal',pts,[tuple(range(5))],reds[1]);line('Marco_aleta_dorsal',pts,.08,gold,True)
# Dragon figurehead: faceted bronze anatomy, open jaws, swept horns and small teeth.
neck=[(14.4,0,4.1),(16.7,0,5.0),(18.2,0,6.7),(19.9,0,7.8)]
for i,(a,b) in enumerate(zip(neck,neck[1:])):rod('Cuello_dragon',a,b,1.0-i*.17,patina,10,r2=.9-i*.17)
uv('Craneo_dragon',(20.3,0,8.0),(1.7,1.0,1.05),patina,12,6)
box('Hocico_dragon',(22.0,0,7.8),(2.8,1.4,.85),patina,.3)
box('Boca_sombra',(22.0,0,7.17),(2.65,1.05,.40),black,.12)
jaw=box('Mandibula_dragon',(21.7,0,6.80),(3.3,.95,.34),gold,.16);jaw.rotation_euler[1]=-.10
for side in [-1,1]:
 uv('Cuenca_ojo',(20.75,side*.89,8.15),(.52,.16,.31),iron,12,6);uv('Ojo_dragon',(20.92,side*1.01,8.2),(.18,.085,.13),eye,12,6)
 line('Ceja_dragon',[(20.1,side*.94,8.6),(20.8,side*1.02,8.55),(21.4,side*.84,8.28)],.14,gold)
 horn=[(19.5,side*.70,8.65),(19.1,side*1.15,9.8),(17.7,side*1.5,10.7),(16.8,side*1.5,10.9)]
 for j,(a,b) in enumerate(zip(horn,horn[1:])):rod('Cuerno_dragon',a,b,.31*(1-j/3),gold,8,r2=.31*(1-(j+1)/3))
 for j in range(5):rod('Diente_dragon',(21.0+j*.47,side*.5,7.39),(21.05+j*.47,side*.48,7.02),.10,ivory,5,r2=0)
 uv('Fosa_nasal',(23.15,side*.46,7.99),(.22,.1,.13),black,10,5)
for x,z in [(15.7,5.4),(17.1,6.1),(18.2,7.4),(19.2,8.2)]:rod('Espina_cuello',(x,0,z),(x-.45,0,z+1.1),.22,gold,6,r2=0)
# Wing-shaped filigree along both sides of bow, and central keel ornaments.
for side in [-1,1]:
 for j in range(5):
  x=9+j*.8;w=width_at(x);line('Filigrana_proa',[(x-2,side*(w+.10),1.7),(x,side*(w+.18),2.6),(x+1.3,side*(w-.35),3.6)],.09,gold)
for x in [-7,-4,-1,2,5]:
 line('Costilla_quilla',[(x,-3.4,.4),(x,-2,-1.2),(x,0,-1.8),(x,2,-1.2),(x,3.4,.4)],.14,gold)
# Benches against the sides; central route remains clear.
for side in [-1,1]:
 for x in [-1,5]:
  box('Banco_pasajeros',(x,side*3.9,4.65),(3.4,.75,.17),wood[1],.04)
  for xx in [x-1.2,x+1.2]:rod('Pata_banco',(xx,side*3.9,4.15),(xx,side*3.9,4.6),.075,gold,8)
  box('Respaldo_banco',(x,side*4.15,5.1),(3.4,.14,.65),wood[1],.03)
# Export-oriented metadata and convenient grouped components.
for o in geo.objects:o['asset_role']='airship_visual';o['collision']='pending_native_proxy';o['design']='Vigilia del Dragon V1'
scene['design_name']='Vigilia del Dragon';scene['design_version']='V1 editable prototype';scene['walkable_main_deck_z']=4.15;scene['l2_status']='Not compiled or installed. PBR materials need baking; collision and geodata pending.'
scene.world=bpy.data.worlds.new('Cielo_de_estudio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.095,.16,.20,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,color,size in [('Sol_ambar',(5,-18,38),16000,(1,.74,.43),18),('Contraluz_azul',(-12,16,27),22000,(.32,.64,1),16),('Relleno_proa',(29,-9,15),5500,(1,.49,.22),10)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,12))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camera_presentacion',bpy.data.cameras.new('Camera_presentacion'));studio.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=57;cam.data.clip_end=1000
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
def camera(loc,target,scale):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
camera((48,-64,38),(0,0,13),62)
# Save the editable model before rendering so a render interruption loses no work.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(D/'Vigilia-del-Dragon-v1.blend'))
deps=bpy.context.evaluated_depsgraph_get();triangles=0;objects=0
for o in geo.objects:
 if o.type not in ('MESH','CURVE'):continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);objects+=1;ev.to_mesh_clear()
(D/'design-audit.json').write_text(json.dumps(dict(name='Vigilia del Dragon',objects=objects,evaluated_triangles=triangles,original_airship_unchanged=True,installed_in_l2=False,materials_require_bake=True,collision_pending=True,mobile_transport_pending=True),indent=2))
for name,loc,target,scale in [('vista-principal',(48,-64,38),(0,0,13),62),('vista-cubierta',(33,-44,30),(0,0,6),40),('vista-lateral',(8,-78,23),(0,0,13),56)]:
 camera(loc,target,scale);scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
print('EPIC_AIRSHIP_CREATED',objects,'objects',triangles,'triangles',flush=True)
