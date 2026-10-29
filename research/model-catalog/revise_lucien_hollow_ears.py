"""Repair the fitting scalp; reuse Armor Cat's sculpted crest and add feline ear armor."""
import bpy,bmesh,json,math,ast,copy,uuid
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
OLD=ROOT/'exports/custom/lucien-turnaround-armor'
OUT=ROOT/'exports/custom/lucien-turnaround-r4';OUT.mkdir(parents=True,exist_ok=True)
LIB=ROOT/'exports/armor-editor'
manifest=json.loads((ROOT/'armor-parts.json').read_text(encoding='utf-8'))
project=json.loads((ROOT/'projects/lucien-cinco-vistas.json').read_text(encoding='utf-8'));project['name']='Lucien - Casco con alojamientos para orejas';project['base']='turnaround-r4'
bpy.ops.wm.read_factory_settings(use_empty=True)
helpers=[n for n in ast.parse((ROOT/'fit_lucien_user_armor.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name in ['mat','xyz','mesh','tube','sphere']]
exec(compile(ast.Module(body=helpers,type_ignores=[]),'helpers','exec'))
node=next(n for n in ast.parse((ROOT/'build_armor_parts.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='thumbnail');thumb_ns=dict(bpy=bpy,Vector=Vector,OUT=LIB);exec(compile(ast.Module(body=[node],type_ignores=[]),'thumbnail','exec'),thumb_ns)
steel=mat('Cat helmet satin silver',(.3,.34,.39),.45,.55)
edge=mat('Ear guard silver rim',(.5,.56,.63),.55,.42)
dark=mat('Ear guard inset',(.09,.11,.14),.35,.6)
red=mat('Sculpted crimson crest',(.29,.005,.012),0,.88)
red.node_tree.nodes.get('Principled BSDF').inputs['Specular'].default_value=.2
def import_part(part):
    before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/part['url']))
    objects=[o for o in bpy.context.scene.objects if o not in before]
    for o in objects:
        if o.parent is None:o.location+=Vector(xyz(part.get('position',[0,0,0])))
    bpy.context.view_layer.update();return objects
def export_group(key,title,category,objects,source):
    dg=bpy.context.evaluated_depsgraph_get();copies=[]
    for o in objects:
        if o.type!='MESH':continue
        d=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);d.transform(o.matrix_world);c=bpy.data.objects.new(o.name+' R2',d);bpy.context.collection.objects.link(c);copies.append(c)
    vs=[v.co for o in copies for v in o.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);center=(lo+hi)/2
    for o in copies:o.data.transform(Matrix.Translation(-center))
    bpy.ops.object.select_all(action='DESELECT')
    for o in copies:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(LIB/(key+'.glb')),export_format='GLB',use_selection=True,export_animations=False)
    thumb_ns['thumbnail'](key,copies,max(hi-lo))
    part=dict(id=key,name=title,category=category,url='exports/armor-editor/'+key+'.glb',thumbnail='exports/armor-editor/'+key+'.png',position=[center.x,center.z,-center.y],rotation=[0,0,0],scale=[1,1,1],source=source,provisional=False,triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in copies))
    for o in copies:bpy.data.objects.remove(o,do_unlink=True)
    return part

# Replace the entire altered head with the untouched native Lucien head, UVs included.
base_objects=import_part(manifest['turnaround_base'])
for body in base_objects:
    if body.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(body.data)
    remove=[f for f in bm.faces if any((body.matrix_world@v.co).z>.213 for v in f.verts)]
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(body.data);bm.free()
before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf'))
original=[o for o in bpy.context.scene.objects if o not in before];dg=bpy.context.evaluated_depsgraph_get();ears=[];native_ear_data=[]
for source in original:
    if source.type!='MESH':continue
    data=bpy.data.meshes.new_from_object(source.evaluated_get(dg),depsgraph=dg);data.transform(source.matrix_world)
    head_group=next((g.index for g in source.vertex_groups if g.name.lower()=='bip01 head'),None)
    head_vertices={v.index for v in source.data.vertices if any(g.group==head_group and g.weight>.4 for g in v.groups)}
    # Keep both head partitions byte-for-byte in position and UV; only visibility changes with helmet.
    for upper in [False,True]:
        d=data.copy();bm=bmesh.new();bm.from_mesh(d)
        keep=[f for f in bm.faces if all(v.index in head_vertices for v in f.verts) and (any(v.co.z>.276 for v in f.verts)==upper)]
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f not in keep],context='FACES');bm.to_mesh(d);bm.free()
        if d.polygons:
            o=bpy.data.objects.new('Native Lucien head upper and crown' if upper else 'Native Lucien face unchanged',d);bpy.context.collection.objects.link(o);base_objects.append(o)
            if upper:o['helmet_hide']=True;ears.append(o)
    for side in [-1,1]:
        d=data.copy();bm=bmesh.new();bm.from_mesh(d)
        keep=[]
        for face in bm.faces:
            p=face.calc_center_median()
            if p.z>.281 and side*p.x>.039:keep.append(face)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f not in keep],context='FACES');bm.to_mesh(d);bm.free()
        if d.polygons:native_ear_data.append((side,d))
for o in original:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in base_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-cabeza-original.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
manifest['turnaround_r4_base']=dict(url='exports/custom/lucien-turnaround-r4/Lucien-cabeza-original.glb',position=[0,0,0])

# Use the already downloaded sculpted tuft, isolated from Armor Cat's STL.
# The diagnostic extractor retains only the largest connected crest component.
before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/armor-editor/donor-armorcat-crest.glb'))
crest_objects=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
for o in crest_objects:
    vs=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)])
    root=[p for p in vs if p.z<lo.z+(hi.z-lo.z)*.025];root_center=sum(root,Vector())/len(root)
    rotation=Matrix.Rotation(math.radians(-40),3,'X');anchor=Vector(xyz((0,.335,-.01)))
    for vertex,p in zip(o.data.vertices,vs):
        t=(p.z-lo.z)/(hi.z-lo.z);q=p-root_center;taper=.3+.7*min(1,t/.2)
        q=Vector((q.x*.76*taper,q.y*1.4*taper,q.z*1.6));vertex.co=rotation@q+anchor
    o.matrix_world=Matrix.Identity(4);o.data.materials.clear();o.data.materials.append(red);o.name='Armor Cat sculpted crest - fitted reuse'
    bm=bmesh.new();bm.from_mesh(o.data);bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    boundary=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=boundary,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=True
new_crest=export_group('ref5-plume-armorcat','Penacho esculpido · Armor Cat','Adornos',crest_objects,'Armor Cat · penacho del STL adaptado')

# Add closed triangular ear guards to the existing helmet, with inset panels and rolled rims.
helmet_part=next(p for p in manifest['parts'] if p['id']=='ref5-helmet')
helmet_objects=import_part(helmet_part)
# Hollow, rounded ear housings: two nested tapered shells joined at the open bottom lip.
# Base overlaps the helmet; the interior has space for the original ear rather than a flat plate.
for side in [-1,1]:
    N=48;R=22;vertices=[];faces=[]
    def earpoint(t,a,inside=False):
        width=.023*(1-t)**.83+.001
        depth=.021*(1-t)**.85+.001
        if inside:width=max(.0004,width-.0016);depth=max(.0004,depth-.0016)
        cx=side*(.049+.021*t);height=.284+.073*t
        dent=.007*max(0,math.sin(a))**4*math.sin(math.pi*t)**.8
        return (cx+width*math.cos(a),height,-.001-.015*t+depth*math.sin(a)-dent)
    for inside in [False,True]:
        for j in range(R):
            t=j/(R-1)
            for k in range(N):vertices.append(earpoint(t,k*math.tau/N,inside))
    offset=N*R
    for j in range(R-1):
        for k in range(N):
            a=j*N+k;b=j*N+(k+1)%N
            faces.append((a,b,b+N,a+N));faces.append((offset+a+N,offset+b+N,offset+b,offset+a))
    for k in range(N):
        nxt=(k+1)%N;faces.append((k,offset+k,offset+nxt,nxt))
        a=(R-1)*N+k;b=(R-1)*N+nxt;faces.append((a,b,offset+b,offset+a))
    shell=mesh('Hollow feline ear housing '+str(side),vertices,faces,steel)
    helmet_objects.append(shell)
    # Curved front inset outlines a cat's inner ear while following the outer housing.
    v=[];f=[];L=17;C=18
    for j in range(L):
        t=.13+.74*j/(L-1)
        for k in range(C+1):
            a=.67+(math.pi-1.34)*k/C
            p=Vector(earpoint(t,a));p.z+=.00028;v.append(tuple(p))
    for j in range(L-1):
        for k in range(C):
            a=j*(C+1)+k;f.append((a,a+1,a+C+2,a+C+1))
    inset=mesh('Curved recessed inner-ear panel '+str(side),v,f,dark)
    helmet_objects.append(inset)
    for a in [.67,math.pi-.67]:
        helmet_objects.append(tube('Rounded inner ear border '+str(side),[earpoint(.13+.74*j/24,a) for j in range(25)],.00085,edge))
    helmet_objects.append(tube('Ear inner panel lower border '+str(side),[earpoint(.13,.67+(math.pi-1.34)*j/24) for j in range(25)],.00085,edge))
# Open the underlying helmet dome into the two hollow housings.
for body in helmet_objects:
    if body.type!='MESH' or 'sallet' not in body.name.lower():continue
    bm=bmesh.new();bm.from_mesh(body.data);remove=[]
    for face in bm.faces:
        q=body.matrix_world@face.calc_center_median();t=(q.z-.284)/.073
        if not 0<t<.98:continue
        wx=.023*(1-t)**.83-.001;dz=.021*(1-t)**.85-.001
        for side in [-1,1]:
            cx=side*(.049+.021*t);depth=-.001-.015*t
            if ((q.x-cx)/wx)**2+((-q.y-depth)/dz)**2<.86:remove.append(face);break
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(body.data);bm.free()
new_helmet=export_group('ref5-hollow-ear-helmet','Casco con cavidades para orejas de gato','Cascos',helmet_objects,'Cinco vistas · revisión de casco felino')

# Build the presentation with the repaired base and the other eight existing pieces.
for item in project['items']:
    if item['partId']=='ref5-helmet':part=new_helmet
    elif item['partId']=='ref5-plume':part=new_crest
    else:part=next(p for p in manifest['parts'] if p['id']==item['partId']);import_part(part)
    item.update(partId=part['id'],name=part['name'],position=part['position'],rotation=part['rotation'],scale=part['scale'])
for o in ears:o.hide_render=True;o.hide_viewport=True
manifest['parts']=[p for p in manifest['parts'] if p['id'] not in [new_helmet['id'],new_crest['id']]]+[new_helmet,new_crest]
(ROOT/'armor-parts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'projects/lucien-cinco-vistas-r4.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Lucien-cinco-vistas-r4.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien-cinco-vistas-r4.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type=='MESH' and not o.hide_render:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-cinco-vistas-r4.glb'),export_format='GLB',use_selection=True,export_animations=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
center=Vector((0,-.02,.18))
for pos,power in [((.4,-.65,.65),12),((-.4,-.1,.35),6),((.1,.4,.5),15)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=.45;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=.45;scene.camera=camera
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=-.5;scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for name,pos in [('preview',(.35,-1,.35)),('profile',(1,0,.27)),('back',(0,1,.28))]:
    camera.location=pos;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
# Bare-head verification image, independent of the helmet's occlusion.
for o in helmet_objects+crest_objects:
    o.hide_render=True
for o in ears:o.hide_render=False
camera.location=(.35,-1,.39);camera.rotation_euler=(Vector((0,0,.265))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.22;scene.render.filepath=str(OUT/'head-without-helmet.png');bpy.ops.render.render(write_still=True)
print('HOLLOW_EARS_R4_COMPLETE',flush=True)
