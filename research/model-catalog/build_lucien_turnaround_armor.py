"""Armor study from the user's five-view reference. Original Lucien face is unchanged."""
import bpy,bmesh,math,json,uuid,ast,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'exports/custom/lucien-turnaround-armor';OUT.mkdir(parents=True,exist_ok=True)
LIB=ROOT/'exports/armor-editor'
bpy.ops.wm.read_factory_settings(use_empty=True)
# Shared mesh construction helpers; do not run another model builder.
src=ast.parse((ROOT/'fit_lucien_user_armor.py').read_text(encoding='utf-8'))
helpers=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['mat','xyz','mesh','tube','sphere','ring']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),str(ROOT/'fit_lucien_user_armor.py'),'exec'))
node=next(n for n in ast.parse((ROOT/'build_armor_parts.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='thumbnail')
thumb_ns=dict(bpy=bpy,Vector=Vector,OUT=LIB);exec(compile(ast.Module(body=[node],type_ignores=[]),'part-thumbnail','exec'),thumb_ns)
steel=mat('Pearl satin armor',(.30,.34,.39),.45,.55)
edge=mat('Rolled silver edging',(.5,.56,.63),.55,.42)
engrave=mat('Dark recessed chasing',(.035,.045,.055),.35,.65)
cloth=mat('Ivory quilted side lining',(.48,.46,.41),0,.94)
thread=mat('Quilt seam grey',(.16,.16,.15),0,.96)
red=mat('Crimson feathers',(.42,.008,.015),0,.8)
redlight=mat('Feather lit edges',(.55,.015,.022),0,.85)
redshadow=mat('Feather recessed shafts',(.12,.003,.007),0,.9)
dark=mat('Dark padded joints',(.035,.045,.055),0,.88)
fur=mat('Tail charcoal fur',(.04,.05,.06),0,.94)
whitefur=mat('Tail silver tip',(.42,.44,.42),0,.96)
manifest=json.loads((ROOT/'armor-parts.json').read_text(encoding='utf-8'))
parts=[];project=dict(version=1,kind='l2-armor-project',name='Lucien - Armadura de las cinco vistas',base='turnaround',items=[])
def output(key,name,category,objects):
    dg=bpy.context.evaluated_depsgraph_get();copies=[]
    for o in objects:
        data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);data.transform(o.matrix_world);c=bpy.data.objects.new(o.name+' fit',data);bpy.context.collection.objects.link(c);copies.append(c)
    points=[v.co for o in copies for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2
    for o in copies:o.data.transform(Matrix.Translation(-center));o.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT')
    for o in copies:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(LIB/(key+'.glb')),export_format='GLB',use_selection=True,export_animations=False)
    thumb_ns['thumbnail'](key,copies,max(hi-lo))
    p=dict(id=key,name=name,category=category,url='exports/armor-editor/'+key+'.glb',thumbnail='exports/armor-editor/'+key+'.png',position=[center.x,center.z,-center.y],rotation=[0,0,0],scale=[1,1,1],source='Armadura de cinco vistas',provisional=False,triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in copies))
    parts.append(p);project['items'].append(dict(id=str(uuid.uuid4()),partId=key,name=name,position=p['position'],rotation=p['rotation'],scale=p['scale'],visible=True,tint='#ffffff'))
    for o in copies:bpy.data.objects.remove(o,do_unlink=True)
def stud(objects,p,r=.0011):objects.append(sphere('Silver plate rivet',p,(r,r,r),edge))

# Helmet: a tall shell enclosing the ears, with two faceted frontal plates.
objects=[];v=[];f=[];N=64;R=14
def cap(a,t):
    front=max(0,math.cos(a));bottom=.232+.038*front**1.8;rad=math.cos(t*math.pi/2)*.999+.001
    return (.066*math.sin(a)*rad,bottom+(.333-bottom)*math.sin(t*math.pi/2),-.009+.056*math.cos(a)*rad)
for j in range(R):
    for k in range(N):v.append(cap(k*math.tau/N,j/(R-1)))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
objects.append(mesh('Tall enclosed-ear sallet',v,f,steel,.0016))
objects.append(tube('Helmet lower rolled border',[cap(k*math.tau/N,0) for k in range(N+1)],.0014,edge))
cap_samples=[cap(-math.pi/2+math.pi*k/120,j/100) for k in range(121) for j in range(101)]
def front_point(x,t):
    u=abs(x)/.056
    y0=.272-.01*u;y1=.332-.019*u
    y=y0+(y1-y0)*t
    shell=min(cap_samples,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)
    return (x,y,max(.057-.028*u-.021*t,shell[2]+.0025))
v=[];f=[];M=24;R=10
for j in range(R):
    for k in range(M+1):v.append(front_point(-.056+.112*k/M,j/(R-1)))
for j in range(R-1):
    for k in range(M):i=j*(M+1)+k;f.append((i,i+1,i+M+2,i+M+1))
objects.append(mesh('Two raised brow plates',v,f,steel,.001))
objects.append(tube('Central helmet raised seam',[front_point(0,t) for t in [0,.25,.5,.75,1]],.0008,edge))
objects.append(tube('Arched brow silver rim',[front_point(-.056+.112*k/48,0) for k in range(49)],.0014,edge))
for i,x in enumerate([-.043,-.029,-.015,0,.015,.029,.043]):
    p=Vector(front_point(x,.57));p.z+=.0014;h=.014 if i==3 else .011
    objects.append(tube('Cross-shaped dark vent upright',[p+Vector((0,-h/2,0)),p+Vector((0,h/2,-.002))],.001,engrave,6))
    objects.append(tube('Cross-shaped dark vent arms',[p+Vector((-.0027,.001,0)),p+Vector((.0027,.001,0))],.00085,engrave,6))
for side in [-1,1]:
    v=[(side*.05,.273,.025),(side*.063,.258,.022),(side*.062,.224,.026),(side*.048,.212,.036),(side*.043,.237,.041)]
    objects.append(mesh('Hinged cheek guard '+str(side),v,[(0,1,2,3,4)],steel,.0012));objects.append(tube('Cheek guard silver lip',v+[v[0]],.0011,edge))
    objects.append(sphere('Helmet hinge surround',(side*.059,.267,.029),(.004,.004,.002),edge));objects.append(sphere('Dark hinge center',(side*.059,.267,.031),(.0026,.0026,.001),engrave))
    for y in [.252,.238,.224]:stud(objects,(side*.056,y,.033))
    # Small flared lower side lames, visible from the profiles.
    v=[(side*.059,.25,.018),(side*.069,.24,-.006),(side*.068,.22,-.014),(side*.059,.228,.018)]
    objects.append(mesh('Side flared helmet lame',v,[(0,1,2,3)],steel,.001));objects.append(tube('Side lame hem',v+[v[0]],.0009,edge))
objects.append(sphere('Plume socket',(0,.334,-.008),(.008,.005,.008),edge))
output('ref5-helmet','Casco cerrado · cinco vistas','Cascos',objects)

# The reference plume is a cascade of broad overlapping leaves, not a loop of hair.
objects=[]
def feather(root,tip,width,index):
    root=Vector(root);tip=Vector(tip);axis=tip-root;side=Vector((1,0,0));v=[];f=[];L=12;C=8
    for j in range(L+1):
        t=j/L;w=width*math.sin(math.pi*t)**.68
        for k in range(C+1):
            u=k/C*2-1;p=root+axis*t+side*(u*w)
            p.z-=.003*math.sin(t*math.pi)*(1-u*u);p.y+=(.045-.0015*index)*math.sin(t*math.pi)*(1-.3*u*u)
            v.append(p)
    for j in range(L):
        for k in range(C):i=j*(C+1)+k;f.append((i,i+1,i+C+2,i+C+1))
    objects.append(mesh('Layered red plume leaf %02d'%index,v,f,redlight if index%4==0 else red,.0006))
    objects.append(tube('Feather central shaft',[root+axis*t+Vector((0,.001+(.045-.0015*index)*math.sin(t*math.pi),-.003*math.sin(t*math.pi))) for t in [0,.2,.4,.6,.8,.98]],.00035,redshadow,5))
for row in range(6):
    t=row/5;rooty=.338-.084*t;rootz=-.008-.073*t
    for col in [-1,0,1]:
        root=(col*.004,rooty,rootz)
        tip=(col*(.022+.004*t),rooty-.041-.009*t,rootz-.055+.008*abs(col))
        feather(root,tip,.013+.003*(1-t),row*3+col+1)
core=[];faces=[];N=20;R=20
for j in range(R):
    t=j/(R-1);center=Vector((0,.337-.13*t,-.009-.10*t));rx=(.012+.009*math.sin(t*math.pi))*(1-.9*t**5)
    for k in range(N):a=k*math.tau/N;core.append(center+Vector((rx*math.sin(a),0,.009*math.cos(a))))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;faces.append((a,b,b+N,a+N))
objects.append(mesh('Continuous crimson plume underlayer',core,faces,red))
output('ref5-plume','Penacho de plumas en capas','Adornos',objects)

# Cuirass and scalloped gorget, shaped around Lucien's existing torso.
objects=[];N=48;rings=[(.12,.031,.03),(.137,.038,.035),(.161,.041,.036),(.18,.033,.028),(.192,.022,.023)];v=[];f=[]
for y,rx,rz in rings:
    for k in range(N):a=k*math.tau/N;v.append((rx*math.sin(a),y,rz*math.cos(a)))
for j in range(len(rings)-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
objects.append(mesh('Fitted ridged breastplate',v,f,steel,.0012))
objects.append(tube('Cuirass center ridge',[(0,.121,.031),(0,.139,.037),(0,.165,.037),(0,.184,.028)],.00085,edge))
for side in [-1,1]:
    objects.append(tube('Cuirass swept waist flute',[(side*.028,.179,.02),(side*.03,.158,.024),(side*.019,.139,.031),(side*.013,.126,.029)],.0005,engrave,6))
# Collar lays over the breastplate, with a scalloped lower front edge.
v=[];f=[];N=64
for ringi in range(3):
    t=ringi/2
    for k in range(N):
        a=k*math.tau/N;rx=.02+.019*t;rz=.021+.011*t;y=.202-.016*t
        if ringi==2:y-=.004*(.5+.5*math.cos(8*a))
        v.append((rx*math.sin(a),y,rz*math.cos(a)))
for j in range(2):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
objects.append(mesh('Scalloped engraved gorget',v,f,steel,.001));objects.append(tube('Scalloped collar hem',v[-N:]+[v[-N]],.001,edge))
for side in [-1,1]:
    for j in range(3):stud(objects,(side*(.009+j*.006),.189+.002*(j%2),.032-j*.001),.0008)
output('ref5-chest','Pechera y gorjal festoneado','Pecheras',objects)

# Rounded leaf-edged shoulder plates, two articulated lames under each cap.
for side,label in [(1,'L'),(-1,'R')]:
    objects=[];cx=side*.049
    for layer in range(3):
        v=[];f=[];N=48;R=7
        for j in range(R):
            t=j/(R-1);radius=.004+.022*t
            for k in range(N):
                a=k*math.tau/N;y=.194-layer*.005-.012*t-.003*t*max(0,math.cos(3*a))
                v.append((cx+radius*math.sin(a),y,-.005+radius*math.cos(a)))
        for j in range(R-1):
            for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
        f.append(tuple(range(N-1,-1,-1)))
        objects.append(mesh('Reference shoulder cap '+label+str(layer),v,f,steel,.001))
        objects.append(tube('Shoulder scalloped border',v[-N:]+[v[-N]],.0011,edge))
    for dx in [-.013,0,.013]:stud(objects,(cx+dx,.181,.018),.0011)
    # Fine symmetrical botanical chasing at the front of the cap.
    for sign in [-1,1]:
        pts=[]
        for k in range(30):
            t=k/29;a=sign*math.tau*t;r=.005*(1-.85*t)
            pts.append((cx+sign*.006+r*math.cos(a),.187+r*math.sin(a),.017))
        objects.append(tube('Pauldron botanical engraving',pts,.0004,engrave,5))
    output('ref5-shoulder-'+label,'Hombrera festoneada '+('izquierda' if side==1 else 'derecha'),'Hombreras',objects)

# Vambraces follow Lucien's actual sloping forearms rather than standing vertically.
for side,label in [(1,'L'),(-1,'R')]:
    objects=[];start=Vector((side*.054,.151,-.006));end=Vector((side*.079,.119,-.006));direction=(end-start).normalized();a=Vector((0,0,1));b=direction.cross(a).normalized();v=[];f=[];N=32;R=5
    for j in range(R):
        t=j/(R-1);center=start.lerp(end,t);rx=.014-.002*t
        for k in range(N):ang=k*math.tau/N;v.append(center+rx*(math.cos(ang)*a+math.sin(ang)*b))
    for j in range(R-1):
        for k in range(N):i=j*N+k;z=j*N+(k+1)%N;f.append((i,z,z+N,i+N))
    objects.append(mesh('Sloping forearm armor '+label,v,f,steel,.0012))
    objects.append(tube('Vambrace upper rolled lip',v[:N]+[v[0]],.0012,edge));objects.append(tube('Vambrace wrist rolled lip',v[-N:]+[v[-N]],.001,edge))
    for t in [.12,.85]:
        center=start.lerp(end,t)
        for dx in [-.007,.007]:stud(objects,(center.x+dx,center.y,center.z+.014),.001)
    output('ref5-vambrace-'+label,'Brazal inclinado '+('izquierdo' if side==1 else 'derecho'),'Guantes y brazales',objects)

objects=[];N=48;v=[];f=[]
for y in [.121,.132]:
    for k in range(N):a=k*math.tau/N;v.append((.037*math.sin(a),y,.034*math.cos(a)))
for k in range(N):f.append((k,(k+1)%N,(k+1)%N+N,k+N))
objects.append(mesh('Silver fitted belt',v,f,steel,.001))
for y in [.121,.132]:objects.append(ring('Belt rolled edge',y,.037,.034,edge,radius=.0008))
objects.append(tube('Angular belt buckle',[(-.009,.12,.037),(-.012,.126,.037),(-.008,.134,.037),(.009,.134,.037),(.012,.126,.037),(.008,.12,.037),(-.009,.12,.037)],.0013,edge))
objects.append(tube('Belt buckle tongue',[(-.007,.127,.038),(.007,.127,.038)],.0008,engrave))
for x in [-.026,.026]:stud(objects,(x,.126,.024),.0009)
output('ref5-belt','Cinturón de plata y hebilla','Cintura',objects)

# Skirt silhouette: broad quilted side panels and longer central hanging plates.
objects=[]
def skirt(a,t,offset=0):return Vector(((.037+.025*math.sin(t*math.pi/2)+offset)*math.sin(a),.121-.073*t,(.034+.014*math.sin(t*math.pi/2)+offset)*math.cos(a)))
for side in [-1,1]:
    angle=side*math.pi/2;v=[];f=[];C=14;R=16
    for j in range(R):
        t=j/(R-1)
        for k in range(C+1):
            u=k/C;span=.12+.58*math.sin(t*math.pi/2);p=skirt(angle+(u-.5)*span*2,t)
            p.y+=.008*t**4*abs(2*u-1);v.append(p)
    for j in range(R-1):
        for k in range(C):i=j*(C+1)+k;f.append((i,i+1,i+C+2,i+C+1))
    objects.append(mesh('Quilted rounded hip panel '+str(side),v,f,cloth,.001))
    border=[v[j*(C+1)] for j in range(R)]+v[-C-1:]+[v[j*(C+1)+C] for j in range(R-1,-1,-1)]
    objects.append(tube('Side panel metal binding',border,.0012,edge))
    # Diamond seams are clipped to the panel width at each height.
    for sign in [-1,1]:
        for line in range(-5,6):
            points=[]
            for j in range(70):
                t=j/69;delta=line*.16+sign*t*.8;span=.12+.58*math.sin(t*math.pi/2)
                if abs(delta)<span-.025:
                    p=skirt(angle+delta,t,.001);p.y+=.008*t**4*abs(delta/span);points.append(p)
            if len(points)>1:objects.append(tube('Quilt diamond diagonal',points,.0003,thread,4))
# Three front and two back panels. The gap between the back panels is the tail opening.
for angle in [-.42,0,.42,math.pi-.40,math.pi+.40]:
    v=[];f=[];R=16;C=12
    for j in range(R):
        t=j/(R-1)
        for k in range(C+1):
            u=k/C;wav=.028*math.sin(t*math.pi*2) if abs(angle)<.1 else 0
            p=skirt(angle+(u-.5)*.43+wav,t,.0015)
            if j==R-1:p.y-=.005*math.sin(u*math.pi)
            v.append(p)
    for j in range(R-1):
        for k in range(C):i=j*(C+1)+k;f.append((i,i+1,i+C+2,i+C+1))
    objects.append(mesh('Long scalloped skirt panel '+str(angle),v,f,steel,.001))
    path=[v[j*(C+1)] for j in range(R)]+v[-C-1:]+[v[j*(C+1)+C] for j in range(R-1,-1,-1)]
    objects.append(tube('Scalloped skirt rolled lip',path,.0009,edge))
    for offset in [-.13,.13]:
        for t in [.12,.9]:stud(objects,skirt(angle+offset,t,.003),.0011)
# Crimson pointed lining visible under the armor, but with the same tail gap.
for k in range(14):
    angle=k*math.tau/14
    if abs(angle-math.pi)<.3:continue
    v=[skirt(angle-.2,.15,-.002),skirt(angle+.2,.15,-.002),skirt(angle+.18,.99,-.002),skirt(angle,1.10,-.002),skirt(angle-.18,.99,-.002)]
    objects.append(mesh('Crimson underskirt pointed tab',v,[(0,1,2,3,4)],red,.0005))
output('ref5-skirt','Faldón largo, acolchado y abertura de cola','Pantalón y faldones',objects)

# Reuse the successful folded red bow, at the reference's neckline.
bow=next(p for p in manifest['parts'] if p['id']=='v2-bow');before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/bow['url']))
objects=[]
for o in bpy.context.scene.objects:
    if o not in before:
        if o.parent is None:o.location+=Vector(xyz(bow['position']))
        if o.type=='MESH':objects.append(o)
bpy.context.view_layer.update();output('ref5-bow','Lazo carmesí del cuello','Adornos',objects)

# Dedicated fitting base without shield, weapon, metal boots or exposed original ears.
armor_objects=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(ROOT/manifest['fitted_base']['url']))
base_objects=[o for o in bpy.context.scene.objects if o not in armor_objects]
# Recover source bone labels by nearest original vertex, to identify the old cuff decorations.
source_path=ROOT/'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf';source=json.loads(source_path.read_text());raw=(source_path.parent/source['buffers'][0]['uri']).read_bytes()
def accessor(index):
    a=source['accessors'][index];view=source['bufferViews'][a['bufferView']];fmt={5126:'f',5123:'H',5121:'B'}[a['componentType']];n={'VEC3':3,'VEC4':4}[a['type']];offset=view.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*n,raw,offset+i*struct.calcsize(fmt)*n) for i in range(a['count'])]
labels=[];positions=[];joints=source['skins'][0]['joints']
for primitive in source['meshes'][0]['primitives']:
    attr=primitive['attributes'];ps=accessor(attr['POSITION']);js=accessor(attr['JOINTS_0']);ws=accessor(attr['WEIGHTS_0'])
    for p,j,w in zip(ps,js,ws):positions.append(xyz(p));labels.append(source['nodes'][joints[j[max(range(4),key=lambda i:w[i])]]]['name'])
tree=KDTree(len(positions))
for i,p in enumerate(positions):tree.insert(p,i)
tree.balance();bpy.context.view_layer.update()
for o in list(base_objects):
    if o.type!='MESH':continue
    # The source sword is a separate primitive with 180 triangles.
    if 'king_of_cat' in o.name.lower() and len(o.data.polygons)<220:
        bpy.data.objects.remove(o,do_unlink=True);base_objects.remove(o);continue
    if not o.name.lower().startswith('king_of_cat'):continue
    bm=bmesh.new();bm.from_mesh(o.data);remove=[]
    for face in bm.faces:
        c=o.matrix_world@face.calc_center_median()
        material=o.data.materials[face.material_index] if face.material_index<len(o.data.materials) else None
        decorations=0
        for vertex in face.verts:
            p,index,distance=tree.find(o.matrix_world@vertex.co)
            if distance<.0001 and labels[index].startswith('Bone'):decorations+=1
        if (material and 'king_of_cat_t01' in material.name) or (abs(c.x)>.05 and decorations>0) or (abs(c.x)>.055 and ((c.z>.118 and c.z<.16) or (c.y>.028 and .075<c.z<.14))):remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
for side in [-1,1]:
    leg=sphere('Exposed fur lower leg '+str(side),(side*.026,.033,0),(.015,.021,.016),fur);base_objects.append(leg)
# Bushy tail is an optional fitting element, leaving the face untouched.
points=[(0,.092,-.029),(.01,.08,-.05),(.035,.08,-.075),(.055,.095,-.10),(.06,.11,-.11)]
tail=tube('Reference fitting tail',points,.011,fur,16);base_objects.append(tail)
tip=sphere('Silver fur tail tip',(.06,.108,-.109),(.011,.016,.011),whitefur);base_objects.append(tip)
bpy.ops.object.select_all(action='DESELECT')
for o in base_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-base-encaje.glb'),export_format='GLB',use_selection=True,export_animations=False)
manifest['turnaround_base']=dict(url='exports/custom/lucien-turnaround-armor/Lucien-base-encaje.glb',position=[0,0,0])
manifest['parts']=[p for p in manifest['parts'] if not p['id'].startswith('ref5-')]+parts
(ROOT/'armor-parts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'projects/lucien-cinco-vistas.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Lucien-cinco-vistas.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien-cinco-vistas.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-cinco-vistas.glb'),export_format='GLB',export_animations=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
center=Vector((0,-.02,.17))
for pos,power in [((.4,-.65,.65),12),((-.4,-.1,.35),6),((.1,.4,.5),15)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=.45;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=.43;scene.camera=camera
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=-.5;scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for name,pos in [('front',(0,-1,.26)),('left',(1,0,.26)),('back',(0,1,.26)),('right',(-1,0,.26)),('preview',(.35,-1,.34))]:
    camera.location=pos;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('TURNAROUND_ARMOR_COMPLETE',len(parts),flush=True)
