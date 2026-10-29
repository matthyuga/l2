"""Small, reproducible Bullet rigid-body proof using an intact Dion house.

Run with the existing Blender executable. Never changes source assets or V1.
"""
from pathlib import Path
import bpy, bmesh, json, math, hashlib, argparse, sys
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
CAT=ROOT.parent/'model-catalog'
parser=argparse.ArgumentParser();parser.add_argument('--output',default='dion-collapse-demo-v1');parser.add_argument('--actors',nargs=2,default=['StaticMeshActor34_0','StaticMeshActor129_0']);parser.add_argument('--static',action='store_true');parser.add_argument('--source')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert args.output.replace('-','').replace('_','').isalnum()
OUT=CAT/'exports'/args.output
SOURCE=Path(args.source) if args.source else ROOT.parent/'scenario-batches/library_fe488fdfccee/scene-with-terrain.blend'
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/('ruins.glb' if args.static else 'collapse.glb')
if target.exists():
    raise RuntimeError('Demo output exists; preserve it and build a new version.')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
selected=[o for o in bpy.data.objects if o.name in args.actors]
assert len(selected)==2,[(o.name) for o in selected]
for obj in list(bpy.data.objects):
    if obj not in selected:bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
world_points=[obj.matrix_world@Vector(c) for obj in selected for c in obj.bound_box]
low=Vector(tuple(min(v[i] for v in world_points) for i in range(3)))
high=Vector(tuple(max(v[i] for v in world_points) for i in range(3)))
center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
for obj in selected:
    # Apply native placement into vertex coordinates, then center the house.
    obj.data=obj.data.copy()
    matrix=obj.matrix_world.copy()
    for v in obj.data.vertices:v.co=matrix@v.co-center
    obj.matrix_world.identity()
print('HOUSE bounds',list(high-low),flush=True)

cap=bpy.data.materials.new('Interior de mampostería rota');cap.diffuse_color=(.22,.18,.13,1);cap.use_nodes=True
cap.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22,.18,.13,1)
cap.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
fragments=[]
def clip_mesh(source,name,minimum,maximum):
    bm=bmesh.new();bm.from_mesh(source.data)
    for axis in range(3):
        for boundary,sign in [(minimum[axis],1),(maximum[axis],-1)]:
            point=Vector((0,0,0));point[axis]=boundary
            normal=Vector((0,0,0));normal[axis]=sign
            if not bm.faces:break
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_inner=True,clear_outer=False)
    if len(bm.faces)<2:bm.free();return None
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free();mesh.update()
    for mat in source.data.materials:mesh.materials.append(mat)
    mesh.materials.append(cap)
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    # The L2 architecture is a surface shell. Give fragments real thickness.
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    modifier=obj.modifiers.new('Espesor para colisión','SOLIDIFY');modifier.thickness=.10;modifier.offset=0;modifier.material_offset=len(mesh.materials)-1
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    points=[v.co for v in obj.data.vertices]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    if min(hi-lo)<.02:
        bpy.data.objects.remove(obj,do_unlink=True);return None
    pivot=(lo+hi)/2
    for v in obj.data.vertices:v.co-=pivot
    obj.location=pivot
    bpy.ops.rigidbody.object_add()
    rb=obj.rigid_body;rb.collision_shape='CONVEX_HULL';rb.use_margin=True;rb.collision_margin=.012
    rb.friction=.85;rb.restitution=.03;rb.linear_damping=.2;rb.angular_damping=.3
    rb.mass=max(.5,(hi.x-lo.x)*(hi.y-lo.y)*(hi.z-lo.z)*25)
    rb.kinematic=True;rb.keyframe_insert('kinematic',frame=1);rb.keyframe_insert('kinematic',frame=30)
    rb.kinematic=False;rb.keyframe_insert('kinematic',frame=31)
    obj.select_set(False);fragments.append(obj);return obj

for source in selected:
    roof=source.name==args.actors[1]
    points=[v.co for v in source.data.vertices]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    counts=(4,3,1) if roof else (4,3,3)
    for x in range(counts[0]):
        for y in range(counts[1]):
            for z in range(counts[2]):
                indexes=(x,y,z)
                a=Vector(tuple(lo[i]+(hi[i]-lo[i])*indexes[i]/counts[i]-.001 for i in range(3)))
                b=Vector(tuple(lo[i]+(hi[i]-lo[i])*(indexes[i]+1)/counts[i]+.001 for i in range(3)))
                clip_mesh(source,('Techo' if roof else 'Pared')+f'_{x}_{y}_{z}',a,b)
    bpy.data.objects.remove(source,do_unlink=True)

# Static floor is the only permanent support after the release at 1.25 seconds.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.32))
floor=bpy.context.object;floor.name='Suelo · soporte fijo';floor.dimensions=(32,32,.6)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
floor_mat=bpy.data.materials.new('Losas de piedra');floor_mat.use_nodes=True
shader=floor_mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=1
paving=CAT/'exports/scene-giran-city/Giran_floor04a.png'
if paving.exists():
    texture=floor_mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(paving));floor_mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    for uv in floor.data.uv_layers.active.data:uv.uv*=10
floor.data.materials.append(floor_mat)
bpy.ops.rigidbody.object_add();floor.rigid_body.type='PASSIVE';floor.rigid_body.friction=.9
scene.frame_start=1;scene.frame_end=216;scene.render.fps=24;scene.gravity=(0,0,-9.81)
world=scene.rigidbody_world;world.substeps_per_frame=8;world.solver_iterations=30
world.point_cache.frame_start=1;world.point_cache.frame_end=216
initial={o.name:o.matrix_world.copy() for o in fragments}
frames={o.name:[] for o in fragments}
for frame in range(1,217):
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
    if frame%2==1 or frame==216:
        for obj in fragments:frames[obj.name].append((frame,obj.evaluated_get(deps).matrix_world.copy()))
    if frame%36==0:print('SIMULATED',frame,'/',216,flush=True)
audit=[]
for obj in fragments:
    end=frames[obj.name][-1][1]
    audit.append({'piece':obj.name,'travel':(end.translation-initial[obj.name].translation).length,'initialZ':initial[obj.name].translation.z,'finalZ':end.translation.z})
for obj in fragments:
    bpy.context.view_layer.objects.active=obj
    bpy.ops.rigidbody.object_remove()
    obj.animation_data_clear();obj.rotation_mode='QUATERNION'
    if args.static:
        obj.location,obj.rotation_quaternion,obj.scale=frames[obj.name][-1][1].decompose()
        continue
    for frame,matrix in frames[obj.name]:
        obj.location, obj.rotation_quaternion, obj.scale=matrix.decompose()
        obj.keyframe_insert('location',frame=frame,group='Derrumbe físico')
        obj.keyframe_insert('rotation_quaternion',frame=frame,group='Derrumbe físico')
    obj.animation_data.action.name='Derrumbe_Fisico'
scene.frame_set(1)
if not args.static:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'simulation.blend'))
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',export_yup=True,export_animations=not args.static,export_animation_mode='SCENE',export_frame_range=True,export_frame_step=2,export_force_sampling=True)
proof={'source':str(SOURCE),'actors':args.actors,'static':args.static,'engine':'Blender Bullet rigid-body simulation','trigger':'All prepared fragments held kinematic until frame 30, released at frame 31; gravity and contacts determine subsequent motion. This does not infer structural strength.','fragments':len(fragments),'fps':24,'frames':216,'duration':9,'gravity':list(scene.gravity),'pieces':audit,'sourceUnmodified':True}
(OUT/'simulation-audit.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print('COMPLETE',json.dumps({'fragments':len(fragments),'moved':sum(p['travel']>.3 for p in audit),'output':str(target)}),flush=True)
