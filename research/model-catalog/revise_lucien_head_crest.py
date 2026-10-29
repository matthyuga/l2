"""Repair the fitting scalp; reuse Armor Cat's sculpted crest and add feline ear armor."""
import bpy,bmesh,json,math,ast,copy,uuid
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
OLD=ROOT/'exports/custom/lucien-turnaround-armor'
OUT=ROOT/'exports/custom/lucien-turnaround-r2';OUT.mkdir(parents=True,exist_ok=True)
LIB=ROOT/'exports/armor-editor'
manifest=json.loads((ROOT/'armor-parts.json').read_text(encoding='utf-8'))
project=json.loads((ROOT/'projects/lucien-cinco-vistas.json').read_text(encoding='utf-8'));project['name']='Lucien - Casco felino y penacho esculpido';project['base']='turnaround-r2'
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

# Restore a fur-textured closed top to the exact base used in the five-view montage.
base_objects=import_part(manifest['turnaround_base'])
fur_material=next(m for o in base_objects if o.type=='MESH' for m in o.data.materials if 'king_of_cat_t00' in m.name)
# Follow the actual open crown-removal boundary, rather than overlaying a cap.
for body in base_objects:
    if body.type!='MESH' or not body.name.lower().startswith('king_of_cat'):continue
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    candidates={e for e in bm.edges if e.is_boundary}
    groups=[]
    while candidates:
        todo=[candidates.pop()];group=[]
        while todo:
            e=todo.pop();group.append(e)
            for v in e.verts:
                for neighbor in v.link_edges:
                    if neighbor in candidates:candidates.remove(neighbor);todo.append(neighbor)
        groups.append(group)
    for group in groups:
        vertices=set(v for e in group for v in e.verts)
        if min((body.matrix_world@v.co).z for v in vertices)<.245:continue
        if len(group)!=len(vertices):continue
        start=next(iter(vertices));ordered=[start];previous=None;current=start
        while True:
            neighbors=[e.other_vert(current) for e in group if current in e.verts and e.other_vert(current)!=previous]
            nxt=next((v for v in neighbors if v not in ordered),None)
            if nxt is None:break
            ordered.append(nxt);previous,current=current,nxt
        if len(ordered)!=len(vertices):continue
        world=[body.matrix_world@v.co for v in ordered]
        center=sum(world,Vector())/len(world)
        if len(group)>10:center.z=.294
        else:center.z+=.001
        points=[];faces=[];count=len(world);rings=6
        for j in range(rings):
            t=j/rings
            for p in world:
                q=p.lerp(center,t);q.z+=.004*math.sin(t*math.pi)
                points.append((q.x,q.z,-q.y))
        for j in range(rings-1):
            for k in range(count):
                u=j*count+k;v=j*count+(k+1)%count;faces.append((u,v,v+count,u+count))
        pole=len(points);points.append((center.x,center.z,-center.y))
        for k in range(count):faces.append(((rings-1)*count+k,(rings-1)*count+(k+1)%count,pole))
        scalp=mesh('Fur repair following original scalp boundary',points,faces,fur_material)
        uv=scalp.data.uv_layers.new(name='Native Lucien dark fur')
        for polygon in scalp.data.polygons:
            for loop in polygon.loop_indices:
                q=scalp.data.vertices[scalp.data.loops[loop].vertex_index].co
                uv.data[loop].uv=(.80+.18*(q.x/.06+1)/2,.76+.20*(q.y/.06+1)/2)
        nb=bmesh.new();nb.from_mesh(scalp.data);bmesh.ops.recalc_face_normals(nb,faces=list(nb.faces));nb.to_mesh(scalp.data);nb.free()
        base_objects.append(scalp)
    bm.free()
# Recover the original fur ears as an independently hideable fitting element.
before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf'))
original=[o for o in bpy.context.scene.objects if o not in before];dg=bpy.context.evaluated_depsgraph_get();ears=[]
for source in original:
    if source.type!='MESH':continue
    data=bpy.data.meshes.new_from_object(source.evaluated_get(dg),depsgraph=dg);data.transform(source.matrix_world)
    bm=bmesh.new();bm.from_mesh(data);remove=[]
    for face in bm.faces:
        p=face.calc_center_median()
        layer=bm.loops.layers.uv.active
        # Native ear UVs occupy the upper-left fur atlas; crown spikes use gold elsewhere.
        uv_center=sum((loop[layer].uv for loop in face.loops),Vector((0,0)))/len(face.loops) if layer else Vector((0,0))
        if not(p.z>.282 and abs(p.x)>.035 and uv_center.y>.65 and uv_center.x<.4):remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(data);bm.free()
    if data.polygons:
        o=bpy.data.objects.new('Lucien restored exposed ears',data);o['helmet_hide']=True;bpy.context.collection.objects.link(o);ears.append(o)
for o in original:bpy.data.objects.remove(o,do_unlink=True)
# Keep upper native fur visible bareheaded, but prevent it piercing the helmet shell.
for body in list(base_objects):
    if body.type!='MESH' or not body.name.lower().startswith('king_of_cat'):continue
    data=body.data.copy();bm=bmesh.new();bm.from_mesh(data)
    upper=[face for face in bm.faces if any((body.matrix_world@v.co).z>.276 for v in face.verts)]
    if upper:
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f not in upper],context='FACES');bm.to_mesh(data)
        top=bpy.data.objects.new('Native upper fur hidden inside helmet',data);top.matrix_world=body.matrix_world.copy();top['helmet_hide']=True;bpy.context.collection.objects.link(top);ears.append(top)
    bm.free();bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.delete(bm,geom=[face for face in bm.faces if any((body.matrix_world@v.co).z>.276 for v in face.verts)],context='FACES');bm.to_mesh(body.data);bm.free()
for obj in base_objects:
    if obj.name.startswith('Fur repair'):obj['helmet_hide']=True;ears.append(obj)
base_objects+=ears
bpy.ops.object.select_all(action='DESELECT')
for o in base_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-cabeza-reparada.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
manifest['turnaround_r2_base']=dict(url='exports/custom/lucien-turnaround-r2/Lucien-cabeza-reparada.glb',position=[0,0,0])

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
for side in [-1,1]:
    a=(side*.03,.301,.008);b=(side*.067,.295,-.008);tip=(side*.064,.352,-.02)
    v=[a,b,tip,(a[0],a[1]-.002,a[2]-.02),(b[0],b[1]-.002,b[2]-.02),(tip[0],tip[1]-.002,tip[2]-.012)]
    o=mesh('Closed feline ear guard '+str(side),v,[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],steel);helmet_objects.append(o)
    helmet_objects.append(tube('Ear guard rolled rim '+str(side),[a,tip,b,a],.0012,edge))
    v=[(side*.039,.306,.009),(side*.061,.342,-.012),(side*.06,.304,-.001)]
    helmet_objects.append(mesh('Inset triangular ear panel '+str(side),v,[(0,1,2)],dark,.0006))
    for p in [a,b]:helmet_objects.append(sphere('Ear guard rivet',p,(.0012,.0012,.0012),edge))
new_helmet=export_group('ref5-cat-helmet','Casco felino con orejas cerradas','Cascos',helmet_objects,'Cinco vistas · revisión de casco felino')

# Build the presentation with the repaired base and the other eight existing pieces.
for item in project['items']:
    if item['partId']=='ref5-helmet':part=new_helmet
    elif item['partId']=='ref5-plume':part=new_crest
    else:part=next(p for p in manifest['parts'] if p['id']==item['partId']);import_part(part)
    item.update(partId=part['id'],name=part['name'],position=part['position'],rotation=part['rotation'],scale=part['scale'])
for o in ears:o.hide_render=True;o.hide_viewport=True
manifest['parts']=[p for p in manifest['parts'] if p['id'] not in [new_helmet['id'],new_crest['id']]]+[new_helmet,new_crest]
(ROOT/'armor-parts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'projects/lucien-cinco-vistas-r2.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Lucien-cinco-vistas-r2.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien-cinco-vistas-r2.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type=='MESH' and not o.hide_render:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-cinco-vistas-r2.glb'),export_format='GLB',use_selection=True,export_animations=False)
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
print('HEAD_AND_CREST_R2_COMPLETE',flush=True)
