"""Editable Lucien knight study; never modifies the original client assets."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'exports/custom/lucien-knight'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
base = [o for o in bpy.context.scene.objects if o.type == 'MESH']

def material(name, color, metal=0, rough=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
silver=material('Forged pearl silver',(.63,.7,.77),.78,.3)
edge=material('Polished silver edges',(.88,.91,.95),.8,.23)
dark=material('Dark steel joints',(.075,.095,.12),.7,.42)
red=material('Crimson cloth',(.48,.012,.027),0,.75)
redlight=material('Scarlet plume highlights',(.72,.025,.045),0,.62)
gold=material('Warm brass rivets',(.59,.38,.13),.75,.3)

def xyz(p): return (p[0],-p[2],p[1])
def bind(obj, bone):
    # Armor has rigid weights on the existing skeleton, in the original rest pose.
    group=obj.vertex_groups.new(name=bone);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    mod=obj.modifiers.new('Lucien original skeleton','ARMATURE');mod.object=rig
    obj.parent=rig
    return obj
def mesh(name,verts,faces,mat,bone):
    data=bpy.data.meshes.new(name);data.from_pydata([xyz(v) for v in verts],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    return bind(obj,bone)
def tube(name,points,radius,mat,bone,sides=8):
    points=[Vector(p) for p in points];vs=[];fs=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        a=tangent.cross(Vector((0,1,0)))
        if a.length<.01:a=tangent.cross(Vector((1,0,0)))
        a.normalize();b=tangent.cross(a).normalized()
        for k in range(sides):vs.append(p+radius*(math.cos(k*math.tau/sides)*a+math.sin(k*math.tau/sides)*b))
    for i in range(len(points)-1):
        for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;fs.append((a,b,b+sides,a+sides))
    return mesh(name,vs,fs,mat,bone)
def ellipsoid(name,center,scale,mat,bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,location=xyz(center))
    o=bpy.context.object;o.name=name;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return bind(o,bone)

# Remove the crown spikes only. Keep the original face, ears, sword and skin weights.
for obj in base:
    bm=bmesh.new();bm.from_mesh(obj.data);remove=[]
    for f in bm.faces:
        center=obj.matrix_world@f.calc_center_median()
        if center.z>.276 and abs(center.x)<.033:remove.append(f)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(obj.data);bm.free()

HEAD='Bip01 head';SPINE='bip01 spine2';PELVIS='Bip01 Pelvis'
# Open-face helmet: its front rim rises above the eyes, rear shell protects the neck.
verts=[];faces=[];N=48;R=9
for j in range(R):
    t=j/(R-1)
    for k in range(N):
        a=math.tau*k/N;front=max(0,math.cos(a));bottom=.237+.043*front**1.5
        radius=math.cos(t*math.pi/2)*.99+.01
        verts.append((.059*math.sin(a)*radius,bottom+(.316-bottom)*math.sin(t*math.pi/2),-.004+.053*math.cos(a)*radius))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;faces.append((a,b,b+N,a+N))
helmet=mesh('Open face sallet',verts,faces,silver,HEAD)
sol=helmet.modifiers.new('Hammered shell thickness','SOLIDIFY');sol.thickness=.0018
tube('Helmet rolled rim',[verts[k] for k in range(N)]+[verts[0]],.0019,edge,HEAD)
for side in [-1,1]:
    v=[(side*.048,.278,.026),(side*.062,.266,.025),(side*.06,.222,.031),(side*.046,.217,.039),(side*.044,.24,.042)]
    plate=mesh('Cheek guard '+str(side),v,[(0,1,2,3,4)],silver,HEAD)
    plate.modifiers.new('Cheek thickness','SOLIDIFY').thickness=.002
    tube('Cheek rolled edge '+str(side),v+[v[0]],.0014,edge,HEAD)
    ellipsoid('Helmet hinge '+str(side),(side*.059,.263,.029),(.003,.003,.002),gold,HEAD)
# Brow plate covers the gold forehead ornament built into Lucien's original head.
v=[(-.033,.283,.043),(0,.291,.051),(.033,.283,.043),(.026,.272,.046),(0,.263,.054),(-.026,.272,.046)]
mesh('Crowned brow replacement',v,[(0,1,4,5),(1,2,3,4)],silver,HEAD)
tube('Brow lower rolled edge',[v[i] for i in [5,4,3]],.0011,edge,HEAD)

# Segmented breastplate, rounded around the original belly.
def shell(name,rings,mat,bone,n=40):
    v=[];f=[]
    for y,rx,rz in rings:
        for k in range(n):a=k*math.tau/n;v.append((rx*math.sin(a),y,rz*math.cos(a)))
    for j in range(len(rings)-1):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;f.append((a,b,b+n,a+n))
    return mesh(name,v,f,mat,bone)
shell('Rounded knight breastplate',[(.119,.035,.034),(.135,.042,.039),(.159,.041,.038),(.181,.034,.03),(.192,.022,.024)],silver,SPINE)
for h,rx,rz in [(.12,.036,.035),(.185,.03,.028)]:
    tube('Cuirass rolled border '+str(h),[(rx*math.sin(k*math.tau/40),h,rz*math.cos(k*math.tau/40)) for k in range(41)],.0017,edge,SPINE)
tube('Breastplate central ridge',[(0,.124,.036),(0,.15,.041),(0,.18,.033)],.0012,edge,SPINE)
# Red padded waist and articulated tassets leave the feet uncovered.
shell('Crimson padded skirt',[(.121,.039,.034),(.08,.055,.042),(.056,.049,.04)],red,PELVIS)
for k in range(8):
    a=k*math.tau/8;v=[]
    for h,rx,rz in [(.12,.04,.036),(.086,.056,.044),(.06,.05,.042)]:
        for da in [-.32,0,.32]:v.append((rx*math.sin(a+da),h-(.006 if da==0 and h==.06 else 0),rz*math.cos(a+da)))
    mesh('Separate skirt plate %02d'%k,v,[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)],silver,PELVIS)
    tube('Tasset edging %02d'%k,[v[i] for i in [0,3,6,7,8,5,2]],.0012,edge,PELVIS)
shell('Dark belt',[(.12,.042,.037),(.129,.042,.037)],dark,PELVIS)
ellipsoid('Belt buckle',(0,.124,.039),(.008,.006,.002),gold,PELVIS)
for side,label in [(-1,'R'),(1,'L')]:
    bone='Bip01 '+label+' UpperArm'
    ellipsoid('Rounded pauldron '+label,(side*.048,.179,-.007),(.026,.019,.027),silver,bone)
    for h in [.169,.176]:
        pts=[(side*.048+.025*math.sin(a),h,-.007+.025*math.cos(a)) for a in [k*math.pi/20 for k in range(-15,16)]]
        tube('Pauldron edge '+label+str(h),pts,.0013,edge,bone)
    ellipsoid('Red arm tie '+label,(side*.051,.16,.012),(.012,.008,.005),red,bone)

# Scarlet horsehair crest, swept back in a fan of individually modeled strands.
for i in range(11):
    offset=(i-5)*.0019;v=[]
    for j in range(13):
        t=j/12;y=.313+.049*math.sin(t*math.pi*.94)-.052*t*t;z=-.005-.108*t
        width=.0045*(1-.85*t)
        v.extend([(offset-width,y,z),(offset+width,y,z),(offset,y+.003,z-.001)])
    f=[]
    for j in range(12):
        for k in range(3):a=j*3+k;b=j*3+(k+1)%3;f.append((a,b,b+3,a+3))
    mesh('Crimson crest strand %02d'%i,v,f,redlight if i%3==0 else red,HEAD)
tube('Crest steel spine',[(0,.314,.023),(0,.321,0),(0,.316,-.035)],.004,dark,HEAD)
# Small red throat bow.
for side in [-1,1]:
    mesh('Crimson throat bow '+str(side),[(0,.195,.031),(side*.017,.204,.033),(side*.016,.185,.035)],[(0,1,2)],red,SPINE)
ellipsoid('Bow knot',(0,.195,.035),(.005,.005,.003),redlight,SPINE)

# Heater shield, held on the free left arm; a raised paw badge gives the unit an identity.
bone='Bip01 L Hand';cx=.101;cy=.125;cz=.035
outline=[(-.026,.032),(.026,.032),(.03,.009),(.021,-.024),(0,-.044),(-.021,-.024),(-.03,.009)]
v=[(cx+x,cy+y,cz) for x,y in outline]+[(cx,cy,cz+.009)]
mesh('Silver heater shield',v,[(i,(i+1)%7,7) for i in range(7)],silver,bone)
tube('Shield thick rim',v[:7]+[v[0]],.0024,edge,bone)
mesh('Crimson shield field',[(cx+x*.79,cy+y*.8,cz+.009) for x,y in outline],[(0,1,2,3,4,5,6)],red,bone)
ellipsoid('Paw emblem pad',(cx,cy-.005,cz+.012),(.009,.009,.0018),edge,bone)
for dx,dy in [(-.009,.009),(-.003,.015),(.005,.014),(.011,.007)]:
    ellipsoid('Paw emblem toe',(cx+dx,cy+dy,cz+.012),(.0036,.0045,.0018),edge,bone)

# Save clean edit project and self-contained glTF before adding presentation lights.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien_Crimson_Knight.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien_Crimson_Knight.glb'),export_format='GLB',export_animations=False)

scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
center=Vector((0,-.018,.17))
for pos,power,size in [((.4,-.65,.65),12,.5),((-.4,-.1,.35),6,.4),((.1,.4,.5),15,.3)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.37,-.95,.40));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.44;scene.camera=camera
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Lucien_Crimson_Knight.png');bpy.ops.render.render(write_still=True)
print('LUCIEN_KNIGHT_COMPLETE',flush=True)
