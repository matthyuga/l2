import bpy,pathlib,json,math
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent/'fantasy-steampunk-airship'
bpy.ops.wm.open_mainfile(filepath=str(D/'airship02/airship02.blend'),load_ui=False,use_scripts=False)
print('OPENED',bpy.app.version_string,flush=True)
scene=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
objects=[]
for o in scene.objects:
    if o.type!='MESH':continue
    mesh=o.evaluated_get(deps).to_mesh();mesh.calc_loop_triangles()
    edges={}
    for p in mesh.polygons:
        for key in p.edge_keys:edges[key]=edges.get(key,0)+1
    objects.append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),evaluated_triangles=len(mesh.loop_triangles),dimensions=list(o.dimensions),location=list(o.location),scale=list(o.scale),uv_layers=[u.name for u in mesh.uv_layers],materials=[m.name if m else None for m in o.data.materials],modifiers=[dict(type=m.type,name=m.name) for m in o.modifiers],boundary_edges=sum(v==1 for v in edges.values()),nonmanifold_edges=sum(v>2 for v in edges.values()),zero_area_faces=sum(p.area<1e-10 for p in mesh.polygons),hidden=o.hide_render))
    o.evaluated_get(deps).to_mesh_clear()
images=[]
for i in bpy.data.images:
    images.append(dict(name=i.name,source=i.source,path=i.filepath,packed=bool(i.packed_file),size=list(i.size),has_data=i.has_data))
    if i.packed_file:
        dest=D/'packed-textures';dest.mkdir(exist_ok=True)
        (dest/pathlib.Path(i.filepath or i.name).name).write_bytes(i.packed_file.data)
materials=[]
for m in bpy.data.materials:
    materials.append(dict(name=m.name,nodes=[dict(name=n.name,type=n.type,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes] if m.use_nodes else [],diffuse=list(m.diffuse_color)))
report=dict(blender=bpy.app.version_string,units=scene.unit_settings.system,unit_scale=scene.unit_settings.scale_length,objects=objects,images=images,materials=materials,triangles=sum(o['evaluated_triangles'] for o in objects),animations=[a.name for a in bpy.data.actions])
(D/'full-audit.json').write_text(json.dumps(report,indent=2));print('AUDIT',len(objects),'meshes',report['triangles'],'triangles',len(images),'images',flush=True)
# Render the source, preserving its materials, with an isolated inspection setup.
for o in list(scene.objects):
    if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
meshes=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2;radius=(hi-lo).length/2
scene.world=bpy.data.worlds.new('AuditWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.20,.25,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for offset,power,size in [((1,-1,2),1800,1.4),((-1,-.3,1),1000,1.2),((0,1,1.5),1500,1)]:
    data=bpy.data.lights.new('AuditLight','AREA');data.energy=power*radius*radius/20;data.shape='DISK';data.size=radius*size;obj=bpy.data.objects.new('AuditLight',data);scene.collection.objects.link(obj);obj.location=center+Vector(offset)*radius;obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('AuditCamera',bpy.data.cameras.new('AuditCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=radius*2.35;cam.data.clip_end=max(1000,radius*20)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
scene.render.resolution_x=1100;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for name,direction in [('source-perspective',(1,-1,.7)),('source-deck',(0,-.4,1.4))]:
    cam.location=center+Vector(direction).normalized()*radius*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'airship-audit-working.blend'))
