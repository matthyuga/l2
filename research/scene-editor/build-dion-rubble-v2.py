"""Art-directed damage on the frozen house pieces. No live physics or source edits."""
from pathlib import Path
import bpy,bmesh,json,math,random,hashlib,argparse,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog'
parser=argparse.ArgumentParser();parser.add_argument('--source-dir');parser.add_argument('--output',default='dion-rubble-v2');parser.add_argument('--houses',nargs='+',type=int,default=[1,2,3]);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SRC=Path(args.source_dir) if args.source_dir else CAT/'exports/dion-ruins-blocks-v1';OUT=CAT/'exports'/args.output;OUT.mkdir(parents=True,exist_ok=True)
assert all(not (OUT/f'house{i}.glb').exists() for i in args.houses),'Do not overwrite an existing version'
rng=random.Random(271026)
def texture_material(name,folder,color=(1,1,1,1)):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=color;shader.inputs['Roughness'].default_value=.95
    file=next((CAT/'exports/cc0-textures/ambientcg'/folder).glob('*_Color.jpg'))
    image=bpy.data.images.load(str(file),check_existing=True);image.scale(512,512)
    texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
    mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    return mat
def uv_project(obj,material_filter=None):
    mesh=obj.data;uv=mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        if material_filter is not None and face.material_index not in material_filter:continue
        n=face.normal;axis=max(range(3),key=lambda k:abs(n[k]));a,b=[k for k in range(3) if k!=axis]
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p[a]*1.5,p[b]*1.5)
def irregular_box(name,size,location,material,rotation=(0,0,0),jitter=.1):
    sx,sy,sz=size
    # Multiple uneven points along the ends produce snapped, splintered outlines.
    verts=[]
    for z in [-1,1]:
        for x,y in [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]:
            verts.append((x*sx/2+rng.uniform(-jitter,jitter)*min(sx,.4),y*sy/2+rng.uniform(-jitter,jitter)*min(sy,.4),z*sz/2+rng.uniform(-jitter,jitter)*min(sz,.4)))
    faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.location=location;obj.rotation_euler=rotation;mesh.materials.append(material);uv_project(obj)
    return obj
reports=[]
for house in args.houses:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source=SRC/f'house{house}.glb';before=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.import_scene.gltf(filepath=str(source));bpy.context.view_layer.update()
    roots=[o for o in bpy.context.view_layer.objects if o.parent is None and o.name.startswith(('Techo','Pared'))]
    keep={o for root in roots for o in [root]+list(root.children_recursive)}
    for o in list(bpy.data.objects):
        if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
    brick=texture_material('Mampostería expuesta · ambientCG Bricks001','Bricks001')
    wood=texture_material('Madera astillada · ambientCG Planks001','Planks001')
    tile=bpy.data.materials.new('Terracota rota');tile.diffuse_color=(.39,.12,.055,1);tile.use_nodes=True;tile.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.39,.12,.055,1)
    holes=0;modified=0;small=[]
    for idx,root in enumerate(roots):
        meshes=[o for o in [root]+list(root.children_recursive) if o.type=='MESH']
        if not meshes:continue
        name=root.name;roof='Techo' in name
        # Merge the material primitives of one fragment, keeping that fragment
        # independent from every other wall/roof section.
        bpy.ops.object.select_all(action='DESELECT')
        for o in meshes:o.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0]
        if len(meshes)>1:bpy.ops.object.join()
        obj=bpy.context.object
        matrix=obj.matrix_world.copy();obj.parent=None;obj.matrix_world=matrix
        for empty in list(bpy.context.scene.objects):
            if empty.type=='EMPTY' and not empty.children:bpy.data.objects.remove(empty,do_unlink=True)
        obj.name=('Tejado roto' if roof else 'Muro quebrado')+f' {idx+1:02d}'
        obj.data=obj.data.copy()
        cap_ids={i for i,m in enumerate(obj.data.materials) if m and 'Interior' in m.name}
        for i in cap_ids:obj.data.materials[i]=wood if roof else brick
        bm=bmesh.new();bm.from_mesh(obj.data)
        # Extra vertices on cut edges make chips visible in the silhouette.
        edges=[e for e in bm.edges if e.calc_length()>.23 and any(f.material_index in cap_ids for f in e.link_faces)]
        if edges:bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=True)
        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            boundary=any(f.material_index in cap_ids for f in v.link_faces)
            if not boundary:continue
            x,y,z=v.co;strength=.045 if roof else .065
            v.co+=Vector((math.sin(x*17+y*11+z*7),math.sin(x*9-y*19+z*13),math.sin(x*13+y*7-z*17)))*strength
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update();uv_project(obj,cap_ids)
        # Cut actual openings through selected large faces. Irregular cutters
        # preserve an uneven perimeter rather than merely painting dark spots.
        candidates=[p for p in obj.data.polygons if p.material_index not in cap_ids and p.area>.045]
        if candidates and idx%4==0:
            face=max(candidates,key=lambda p:p.area)
            center=obj.matrix_world@face.center;radius=min(.34,max(.12,math.sqrt(face.area)*.32))
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius,location=center)
            cutter=bpy.context.object;cutter.name='Cortador temporal';cutter.data.materials.append(wood if roof else brick)
            for v in cutter.data.vertices:v.co*=rng.uniform(.83,1.17)
            bpy.context.view_layer.objects.active=obj
            modifier=obj.modifiers.new('Agujero y bordes arrancados','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
            old_count=len(obj.data.polygons)
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                if len(obj.data.polygons)>0 and len(obj.data.polygons)!=old_count:holes+=1
            except RuntimeError:
                if modifier.name in obj.modifiers:obj.modifiers.remove(modifier)
            bpy.data.objects.remove(cutter,do_unlink=True)
        # Chamfer tiny sharp edges without turning chunks into smooth stones.
        bevel=obj.modifiers.new('Cantos astillados','BEVEL');bevel.width=.012 if roof else .018;bevel.segments=1;bevel.affect='EDGES';bevel.limit_method='ANGLE';bevel.angle_limit=.6
        try:bpy.ops.object.modifier_apply(modifier=bevel.name)
        except RuntimeError:obj.modifiers.remove(bevel)
        modified+=1
    # Scatter smaller remnants close to the original house footprint, not
    # throughout the whole exhibition floor.
    for i in range(24):
        x,y=rng.uniform(-4.4,4.4),rng.uniform(-3.5,3.5)
        sx,sy,sz=rng.uniform(.12,.31),rng.uniform(.1,.21),rng.uniform(.07,.14)
        small.append(irregular_box(f'Ladrillo desprendido {i+1:02d}',(sx,sy,sz),(x,y,sz/2+.025),brick,(0,0,rng.random()*math.tau),.26))
    for i in range(14):
        x,y=rng.uniform(-4,4),rng.uniform(-3.3,3.3)
        small.append(irregular_box(f'Astilla de viga {i+1:02d}',(rng.uniform(.5,1.5),.085,.07),(x,y,.07),wood,(rng.uniform(-.06,.06),rng.uniform(-.05,.05),rng.random()*math.tau),.35))
    # A recognizable smashed door: separate boards, missing ends and broken rails.
    door_center=Vector((3.7,-2.4,.13));angle=.3
    for i in range(6):
        length=rng.uniform(.65,1.35);dx=(i-2.5)*.15
        p=door_center+Vector((dx*math.cos(angle),dx*math.sin(angle),rng.uniform(0,.035)))
        small.append(irregular_box(f'Puerta destrozada · tabla {i+1}',(.135,length,.055),p,wood,(0,rng.uniform(-.06,.06),angle),.4))
    for i in range(2):
        p=door_center+Vector((0,(-.35 if i==0 else .35),.065))
        small.append(irregular_box(f'Puerta destrozada · travesaño {i+1}',(.8,.09,.05),p,wood,(0,0,angle),.3))
    for i in range(18):
        x,y=rng.uniform(-4.3,4.3),rng.uniform(-3.5,3.5)
        small.append(irregular_box(f'Teja desprendida {i+1:02d}',(rng.uniform(.12,.22),rng.uniform(.18,.28),.035),(x,y,.04),tile,(rng.uniform(-.12,.12),rng.uniform(-.12,.12),rng.random()*math.tau),.28))
    bpy.ops.object.select_all(action='DESELECT')
    # Remove stray empty roots left by material joining; preserve every actual fragment.
    for o in list(bpy.context.scene.objects):
        if o.type=='EMPTY' and not o.children:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/f'house{house}.glb'),export_format='GLB',export_animations=False,export_yup=True)
    reports.append({'house':house,'sourceSha256':before,'sourceUnchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,'roughenedFragments':modified,'booleanOpenings':holes,'smallDebris':len(small),'animations':0})
    print('HOUSE COMPLETE',json.dumps(reports[-1]),flush=True)
(OUT/'damage-audit.json').write_text(json.dumps({'houses':reports,'seed':271026,'materials':['Original house textures','ambientCG Bricks001','ambientCG Planks001','Terracotta'],'notes':'Art-directed chipping and boolean openings applied after the original collapse; not re-simulated. Fracture interiors and some debris use box-projected texture UVs.'},ensure_ascii=False,indent=2),encoding='utf-8')
