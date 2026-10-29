"""Clean fitting rebuild from the user's saved v1 montage; preserves the original JSON."""
import bpy,bmesh,math,json,copy,uuid,ast
from pathlib import Path
from mathutils import Vector,Matrix,Euler
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]/'descarga de assets/Mi-armadura-de-Lucienv1.json'
OUT=ROOT/'exports/custom/lucien-user-v1-fitted';OUT.mkdir(parents=True,exist_ok=True)
LIB=ROOT/'exports/armor-editor';LIB.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'armor-parts.json').read_text(encoding='utf-8'))
user=json.loads(PROJECT.read_text(encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metal=.65,rough=.42):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
steel=mat('Satin silver plate',(.52,.59,.66));edge=mat('Rolled bright silver',(.78,.83,.88),.78,.32)
dark=mat('Recessed dark steel',(.045,.06,.075),.55,.52);gold=mat('Small brass fasteners',(.48,.31,.12),.7,.4)
red=mat('Crimson padded lining',(.36,.012,.025),0,.85)
new_parts=[];project=copy.deepcopy(user);project['name']='Mi armadura de Lucien v1 - ajustada'
project['items']=[];project['base']='fitted'
# Reuse the isolated thumbnail renderer without running the library-building module.
node=next(n for n in ast.parse((ROOT/'build_armor_parts.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='thumbnail')
thumb_ns=dict(bpy=bpy,Vector=Vector,OUT=LIB)
exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/'build_armor_parts.py'),'exec'),thumb_ns)
def xyz(p):return (p[0],-p[2],p[1])
def mesh(name,vs,fs,material,thickness=0):
    data=bpy.data.meshes.new(name);data.from_pydata([xyz(v) for v in vs],[],fs);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.data.materials.append(material)
    for f in data.polygons:f.use_smooth=True
    if thickness:
        mod=o.modifiers.new('Actual plate wall','SOLIDIFY');mod.thickness=thickness
        mod=o.modifiers.new('Soft manufactured rim','BEVEL');mod.width=.0006;mod.segments=2
    return o
def tube(name,points,r,material,sides=8):
    v=[];f=[];points=[Vector(p) for p in points]
    for i,p in enumerate(points):
        direction=(points[min(len(points)-1,i+1)]-points[max(0,i-1)]).normalized();a=direction.cross(Vector((0,1,0)))
        if a.length<.01:a=direction.cross(Vector((1,0,0)))
        a.normalize();b=direction.cross(a).normalized()
        for k in range(sides):v.append(p+r*(a*math.cos(k*math.tau/sides)+b*math.sin(k*math.tau/sides)))
    for i in range(len(points)-1):
        for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;f.append((a,b,b+sides,a+sides))
    return mesh(name,v,f,material)
def sphere(name,p,s,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=xyz(p));o=bpy.context.object;o.name=name;o.scale=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
    for f in o.data.polygons:f.use_smooth=True
    return o
def ring(name,y,rx,rz,material,center=(0,0,0),radius=.001):
    return tube(name,[(center[0]+rx*math.sin(k*math.tau/48),y,center[2]+rz*math.cos(k*math.tau/48)) for k in range(49)],radius,material)
def export_group(key,name,category,objects):
    dg=bpy.context.evaluated_depsgraph_get();copies=[]
    for o in objects:
        data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);data.transform(o.matrix_world);c=bpy.data.objects.new(o.name+' fitting copy',data);bpy.context.collection.objects.link(c);copies.append(c)
    points=[v.co for o in copies for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2
    for o in copies:o.data.transform(Matrix.Translation(-center));o.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT')
    for o in copies:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(LIB/(key+'.glb')),export_format='GLB',use_selection=True,export_animations=False)
    part=dict(id=key,name=name,category=category,url='exports/armor-editor/'+key+'.glb',position=[center.x,center.z,-center.y],rotation=[0,0,0],scale=[1,1,1],source='Lucien v1 · ajuste personalizado',provisional=False,triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in copies))
    thumb_ns['thumbnail'](key,copies,max(hi-lo));part['thumbnail']='exports/armor-editor/'+key+'.png'
    new_parts.append(part)
    original=next((i for i in user['items'] if i['partId']==mapping[key]),None)
    project['items'].append(dict(id=original['id'] if original else str(uuid.uuid4()),partId=key,name=name,position=part['position'],rotation=[0,0,0],scale=[1,1,1],visible=True,tint='#ffffff'))
    for o in copies:bpy.data.objects.remove(o,do_unlink=True)
mapping={'fitv1-helmet':'donor-armor-cat-helmet','fitv1-shoulder-L':'donor-armor-cat-shoulderL','fitv1-shoulder-R':'donor-armor-cat-shoulderR','fitv1-waist':'donor-armor-cat-waist','fitv1-skirt':'donor-armor-cat-legs','fitv1-boot-L':'donor-armor-cat-bootL','fitv1-boot-R':'donor-armor-cat-bootR'}

# Rebuild the donor's feline helmet as armor only: no donor face or eyeballs.
objects=[];N=64;R=12;v=[];f=[]
def helm(a,t):
    front=max(0,math.cos(a));bottom=.235+.041*front**2
    rad=math.cos(t*math.pi/2)*.998+.002
    return (.060*math.sin(a)*rad,bottom+(.307-bottom)*math.sin(t*math.pi/2),-.007+.052*math.cos(a)*rad)
for j in range(R):
    for k in range(N):v.append(helm(k*math.tau/N,j/(R-1)))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
objects.append(mesh('Fitted feline helmet shell',v,f,steel,.0015))
objects.append(tube('Helmet opening rolled rim',[helm(k*math.tau/N,0) for k in range(N+1)],.0016,edge))
# Triangular ear caps sit over Lucien's own ear silhouettes, not the larger donor ears.
for side in [-1,1]:
    v=[(side*.025,.275,-.003),(side*.064,.278,-.009),(side*.059,.328,-.025),(side*.043,.307,.014)]
    objects.append(mesh('Feline ear cap '+str(side),v,[(0,1,3),(1,2,3),(2,0,3)],steel,.0012))
    objects.append(tube('Ear cap reinforced outer rim '+str(side),[v[i] for i in [0,2,1]],.0015,edge))
    objects.append(tube('Ear cap inset panel '+str(side),[(side*.035,.283,.004),(side*.056,.315,-.015),(side*.057,.284,.001)],.0007,dark))
    # Articulated cheek guards follow the outside of the face, leaving both eyes and muzzle open.
    v=[(side*.049,.270,.021),(side*.061,.259,.023),(side*.061,.223,.024),(side*.046,.215,.037),(side*.043,.237,.038)]
    objects.append(mesh('Fitted cheek plate '+str(side),v,[(0,1,2,3,4)],steel,.0014))
    objects.append(tube('Cheek plate edge '+str(side),v+[v[0]],.001,edge))
    objects.append(sphere('Cheek hinge '+str(side),(side*.059,.257,.027),(.0027,.0027,.0016),gold))
    for j in range(3):objects.append(tube('Cheek breath slit',[(side*.051,.238-j*.004,.037),(side*.057,.24-j*.004,.034)],.00065,dark))
# Arched brow replaces the sliced donor eye region with a continuous metal plate.
v=[(-.044,.278,.027),(-.026,.285,.041),(0,.293,.048),(.026,.285,.041),(.044,.278,.027),(.027,.267,.041),(0,.260,.051),(-.027,.267,.041)]
# Keep the brow clearly outside the curved shell to avoid coplanar flicker in WebGL.
samples=[helm(-math.pi/2+math.pi*k/160,j/100) for k in range(161) for j in range(101)]
def front_surface_depth(x,y):
    p=min(samples,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)
    return p[2]
v=[(x,y,max(z,front_surface_depth(x,y)+.0025)) for x,y,z in v]
objects.append(mesh('Arched brow - donor eye fragments removed',v,[(0,1,2,6,7),(2,3,4,5,6)],steel,.0011))
objects.append(tube('Arched brow lower rim',[v[i] for i in [0,7,6,5,4]],.0012,edge))
for side in [-1,1]:
    for j in range(3):
        x=side*(.014+j*.009);objects.append(tube('Brow recessed detail',[(x,.282,.044-j*.003),(x,.289,.043-j*.003)],.0006,dark))
objects.append(tube('Helmet crest mounting rail',[(0,.303,.02),(0,.312,0),(0,.306,-.032)],.003,edge))
export_group('fitv1-helmet','Casco felino ajustado a Lucien','Cascos',objects)

# Replace incomplete donor shoulder slices with small rounded overlapping guards.
for side,label in [(1,'L'),(-1,'R')]:
    objects=[];cx=side*.048
    for layer in range(3):
        v=[];f=[];M=40
        for ringi in range(6):
            t=ringi/5;radius=.009+.015*t
            for k in range(M):
                a=k*math.tau/M
                v.append((cx+radius*math.sin(a),.191-layer*.005-.012*t,-.006+radius*math.cos(a)))
        for j in range(5):
            for k in range(M):a=j*M+k;b=j*M+(k+1)%M;f.append((a,b,b+M,a+M))
        objects.append(mesh('Shoulder floating lame '+label+str(layer),v,f,steel,.001))
        objects.append(tube('Shoulder lame hem',v[-M:]+[v[-M]],.001,edge))
    objects.append(sphere('Shoulder pivot cap '+label,(cx,.192,-.006),(.012,.004,.012),steel))
    for dx in [-.01,.01]:objects.append(sphere('Shoulder mounting rivet',(cx+dx,.181,.014),(.0013,.0013,.001),gold))
    export_group('fitv1-shoulder-'+label,'Hombrera felina '+('izquierda' if side==1 else 'derecha'),'Hombreras',objects)

# A real belt and articulated fauld replaces the fragments originally laid across the hips.
objects=[];N=48
for layer in range(3):
    v=[];f=[]
    for h,rx,rz in [(.127-layer*.006,.038+layer*.002,.035+layer*.0015),(.12-layer*.006,.04+layer*.002,.037+layer*.0015)]:
        for k in range(N):a=k*math.tau/N;v.append((rx*math.sin(a),h,rz*math.cos(a)))
    for k in range(N):f.append((k,(k+1)%N,(k+1)%N+N,k+N))
    objects.append(mesh('Articulated waist band '+str(layer),v,f,steel,.001))
    objects.append(ring('Fauld rolled lower hem',.12-layer*.006,.04+layer*.002,.037+layer*.0015,edge))
objects.append(tube('Open angular belt buckle',[(-.009,.122,.041),(-.011,.127,.041),(-.008,.132,.041),(.009,.132,.041),(.011,.127,.041),(.008,.122,.041),(-.009,.122,.041)],.0011,edge))
objects.append(tube('Buckle pin',[(-.006,.127,.042),(.007,.127,.042)],.0007,dark))
export_group('fitv1-waist','Cintura articulada ajustada','Cintura',objects)

objects=[]
# Continuous cloth under the separate tassets prevents open gaps into the mannequin.
v=[];f=[];N=48
for h,rx,rz in [(.114,.041,.037),(.052,.051,.044)]:
    for k in range(N):a=k*math.tau/N;v.append((rx*math.sin(a),h,rz*math.cos(a)))
for k in range(N):f.append((k,(k+1)%N,(k+1)%N+N,k+N))
objects.append(mesh('Crimson underlay between tassets',v,f,red,.0006))
for panel in range(6):
    a=panel*math.tau/6;v=[];f=[];C=10;R=8
    for j in range(R):
        t=j/(R-1)
        for k in range(C+1):
            u=k/C;angle=a+(u-.5)*.78;h=.113-.058*t
            if j==R-1:h-=.003*math.cos((u-.5)*math.pi)
            v.append(((.042+.012*t)*math.sin(angle),h,(.038+.009*t)*math.cos(angle)))
    for j in range(R-1):
        for k in range(C):i=j*(C+1)+k;f.append((i,i+1,i+C+2,i+C+1))
    objects.append(mesh('Fitted short tasset '+str(panel),v,f,steel,.0012))
    path=[v[j*(C+1)] for j in range(R)]+v[-(C+1):]+[v[j*(C+1)+C] for j in range(R-1,-1,-1)]
    objects.append(tube('Tasset raised hem',path,.001,edge))
    for offset in [-.28,.28]:objects.append(sphere('Tasset fastening',((.044)*math.sin(a+offset),.107,.04*math.cos(a+offset)),(.0014,.0014,.0014),gold))
export_group('fitv1-skirt','Faldón corto adaptado a Lucien','Pantalón y faldones',objects)

# Open-front armored boots preserve Lucien's claws and the spacing of his feet.
for side,label in [(1,'L'),(-1,'R')]:
    objects=[];cx=side*.026;v=[];f=[];N=40
    for h,rx,rz in [(.012,.019,.024),(.027,.018,.02),(.052,.017,.018)]:
        for k in range(N):
            a=k*math.tau/N;v.append((cx+rx*math.sin(a),h,-.001+rz*math.cos(a)))
    for j in range(2):
        for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
    objects.append(mesh('Fitted ankle greave '+label,v,f,steel,.001))
    objects.append(ring('Greave upper rolled edge',.052,.017,.018,edge,(cx,0,-.001)))
    # Dorsal plate covers the top of the foot while leaving the toe tips uncovered.
    v=[(cx-.018,.021,.007),(cx+.018,.021,.007),(cx+.019,.014,.022),(cx,.017,.028),(cx-.019,.014,.022)]
    objects.append(mesh('Foot articulated instep '+label,v,[(0,1,2,3,4)],steel,.001))
    objects.append(tube('Foot plate rim',v+[v[0]],.0008,edge))
    for h in [.025,.04]:objects.append(tube('Greave transverse chasing',[(cx-.011,h,.017),(cx+.011,h,.017)],.0006,dark))
    export_group('fitv1-boot-'+label,'Bota ajustada '+('izquierda' if side==1 else 'derecha'),'Botas',objects)

# Keep the four V2 pieces chosen by the user, at their known fitted coordinates.
for old in user['items']:
    if old['partId'].startswith('v2-'):
        part=next(p for p in manifest['parts'] if p['id']==old['partId']);item=copy.deepcopy(old)
        item.update(position=part['position'],rotation=part['rotation'],scale=part['scale']);project['items'].append(item)
        if old['partId']=='v2-plume':item['position']=list(part['position']);item['position'][1]-=.013
        old_objects=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/part['url']))
        imported=[o for o in bpy.context.scene.objects if o not in old_objects]
        p=item['position']
        for o in imported:
            if o.parent is None:o.location+=Vector(xyz(p))

# The fitting base retains the same source Lucien used in the saved project.
before=set(bpy.context.scene.objects);base=manifest['fitting_base'];bpy.ops.import_scene.gltf(filepath=str(ROOT/base['url']))
clean_base=[]
for o in bpy.context.scene.objects:
    if o not in before and o.parent is None:o.location+=Vector(xyz(base['position']))
    if o not in before and o.type=='MESH':clean_base.append(o)
bpy.context.view_layer.update()
for o in clean_base:
    if not o.name.lower().startswith('king_of_cat'):continue
    bm=bmesh.new();bm.from_mesh(o.data);remove=[]
    for face in bm.faces:
        c=o.matrix_world@face.calc_center_median()
        if (.020<c.z<.11 and abs(c.x)<.067) or (c.z>.282 and abs(c.x)>.029) or (c.z>.258 and abs(c.x)<.024 and c.y<-.016):remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
for side in [-1,1]:clean_base.append(sphere('Fitted dark trouser leg '+str(side),(side*.025,.058,0),(.016,.029,.017),dark))
# Bake the refined body into a dedicated base so other editor projects stay unchanged.
dg=bpy.context.evaluated_depsgraph_get();copies=[]
for o in clean_base:
    data=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);data.transform(o.matrix_world);c=bpy.data.objects.new(o.name+' cleaned copy',data);bpy.context.collection.objects.link(c);copies.append(c)
bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(LIB/'lucien-user-clean-base.glb'),export_format='GLB',use_selection=True,export_animations=False)
for o in copies:bpy.data.objects.remove(o,do_unlink=True)
manifest['fitted_base']=dict(url='exports/armor-editor/lucien-user-clean-base.glb',position=[0,0,0])
manifest['parts']=[p for p in manifest['parts'] if not p['id'].startswith('fitv1-')]+new_parts
(ROOT/'armor-parts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Mi-armadura-de-Lucienv1-ajustada.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
projects=ROOT/'projects';projects.mkdir(exist_ok=True);(projects/'lucien-v1-ajustada.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien-v1-ajustada.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-v1-ajustada.glb'),export_format='GLB',export_animations=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
center=Vector((0,-.015,.17))
for pos,power in [((.4,-.65,.65),12),((-.4,-.1,.35),6),((.1,.4,.5),15)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=.45;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.3,-.95,.37));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=.43;scene.camera=camera
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for name,location in [('preview',(.3,-.95,.37)),('front',(0,-1,.27)),('back',(.3,1,.34))]:
    camera.location=location;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('USER_ARMOR_FITTED_COMPLETE',len(project['items']),flush=True)
