"""A separate female Lucien derivative, retaining the original skeleton and armor anchors."""
import bpy,bmesh,math,json,copy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'exports/custom/lucien-female';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
base=[o for o in bpy.context.scene.objects if o.type=='MESH']
def xyz(p):return (p[0],-p[2],p[1])
def mat(name,color,metal=0,rough=.6):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
hair=mat('Ash charcoal hair',(.012,.017,.025),0,.88)
hairlight=mat('Ash hair highlights',(.028,.036,.048),0,.82)
for material in [hair,hairlight]:material.node_tree.nodes.get('Principled BSDF').inputs['Specular'].default_value=.16
dark=mat('Midnight padded underarmor',(.045,.06,.085),0,.82)
cloth=mat('Burgundy cloth accents',(.19,.018,.038),0,.85)
silver=mat('Small silver clasps',(.45,.51,.6),.7,.35)
black=mat('Soft dark eyelash',(.015,.02,.025),0,.8)
chinfur=mat('Soft cream chin fur',(.42,.43,.40),0,.95)
neckfur=mat('Charcoal neck fur',(.035,.044,.05),0,.95)

def bind(o,bone):
    group=o.vertex_groups.new(name=bone);group.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Original Lucien skeleton','ARMATURE');mod.object=rig;o.parent=rig;return o
def mesh(name,v,f,material,bone):
    data=bpy.data.meshes.new(name);data.from_pydata([xyz(p) for p in v],[],f);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(material)
    for p in data.polygons:p.use_smooth=True
    return bind(o,bone)
def ellipsoid(name,center,scale,material,bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=xyz(center));o=bpy.context.object;o.name=name;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return bind(o,bone)
def strand(name,points,width,material,bone='Bip01 head',flatten=1):
    v=[];f=[];points=[Vector(p) for p in points];N=10
    for i,p in enumerate(points):
        t=i/(len(points)-1);direction=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();a=direction.cross(Vector((0,1,0)))
        if a.length<.01:a=direction.cross(Vector((1,0,0)))
        a.normalize();b=direction.cross(a).normalized();r=width*(.25+.75*math.sin(math.pi*t)**.65)
        for k in range(N):angle=k*math.tau/N;v.append(p+r*(flatten*math.cos(angle)*a+math.sin(angle)*b))
    for i in range(len(points)-1):
        for k in range(N):a=i*N+k;b=i*N+(k+1)%N;f.append((a,b,b+N,a+N))
    f.extend([tuple(range(N-1,-1,-1)),tuple((len(points)-1)*N+k for k in range(N))])
    return mesh(name,v,f,material,bone)

# Remove clothing and crown geometry, and the small separate chin-beard cards.
removed_beard=0
for o in base:
    o.data.materials.append(chinfur);chin_slot=len(o.data.materials)-1
    bm=bmesh.new();bm.from_mesh(o.data);deform=bm.verts.layers.deform.active;names={g.index:g.name for g in o.vertex_groups};remove=[]
    for f in bm.faces:
        c=o.matrix_world@f.calc_center_median();weights={}
        if deform:
            for v in f.verts:
                for idx,w in v[deform].items():weights[idx]=weights.get(idx,0)+w
        bone=names.get(max(weights,key=weights.get),'') if weights else ''
        if bone=='Bip01 head':
            if c.z>.276 and abs(c.x)<.034:remove.append(f)
            elif c.z<.218 and abs(c.x)<.017 and c.y<-.014:remove.append(f);removed_beard+=1
            elif c.z>.258 and abs(c.x)<.027 and c.y<-.018:remove.append(f)
        wardrobe=('spine' in bone.lower() or 'Pelvis' in bone or 'Thigh' in bone or 'Calf' in bone or 'UpperArm' in bone or ('Forearm' in bone and c.z>.126) or bone in ['Bone06','Bone03','Bone04','Bone09','Bone01','Bone02','Bone07','Bone08'])
        if wardrobe and f not in remove:remove.append(f)
    bmesh.ops.delete(bm,geom=remove,context='FACES')
    # Subtle cheek refinement; the eye spacing and attachment anchors remain unchanged.
    for v in bm.verts:
        c=o.matrix_world@v.co
        if .215<c.z<.245 and abs(c.x)<.06:
            c.x*=.96;v.co=o.matrix_world.inverted()@c
    bm.to_mesh(o.data);bm.free()
    # Separate the exposed fur of the ears so the armor editor can tuck it under a helmet.
    if o==base[0]:
        ear=o.copy();ear.data=o.data.copy();ear.name='Female exposed ears';ear['helmet_hide']=True;bpy.context.collection.objects.link(ear)
        for object,is_ear in [(o,False),(ear,True)]:
            bm=bmesh.new();bm.from_mesh(object.data);remove=[]
            for face in bm.faces:
                c=object.matrix_world@face.calc_center_median();belongs=c.z>.282 and abs(c.x)>.029
                if belongs!=is_ear:remove.append(face)
            bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(object.data);bm.free()

# Neutral fitted clothing keeps the familiar chibi proportions and existing armor fit.
rings=[(.078,.031,.025),(.102,.036,.029),(.125,.029,.027),(.15,.031,.029),(.177,.035,.027),(.191,.023,.023),(.199,.018,.02)]
v=[];f=[];N=40
for y,rx,rz in rings:
    for k in range(N):a=k*math.tau/N;v.append((rx*math.sin(a),y,rz*math.cos(a)))
for j in range(len(rings)-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
torso=mesh('Tailored neutral underarmor',v,f,dark,'Bip01 Spine')
for g in list(torso.vertex_groups):torso.vertex_groups.remove(g)
for j,(y,rx,rz) in enumerate(rings):
    bone='Bip01 Pelvis' if y<.115 else 'Bip01 Spine' if y<.145 else 'bip01 spine2'
    group=torso.vertex_groups.get(bone) or torso.vertex_groups.new(name=bone);group.add(list(range(j*N,(j+1)*N)),1,'REPLACE')
for side,label in [(-1,'R'),(1,'L')]:
    ellipsoid('Padded sleeve '+label,(side*.048,.165,-.006),(.014,.027,.015),dark,'Bip01 '+label+' UpperArm')
    ellipsoid('Fitted forearm '+label,(side*.06,.138,-.008),(.013,.019,.016),dark,'Bip01 '+label+' Forearm')
    ellipsoid('Fitted trouser leg '+label,(side*.025,.058,0),(.017,.036,.019),dark,'Bip01 '+label+' Calf')
    # A restrained side stripe makes the unarmored base read as a finished outfit.
    strand('Burgundy sleeve seam '+label,[(side*.057,.181,.002),(side*.061,.159,.006),(side*.068,.14,.004)],.001,cloth,'Bip01 '+label+' UpperArm')

HEAD='Bip01 head'
ellipsoid('Soft neck under the chin',(0,.207,0),(.017,.015,.018),neckfur,'Bip01 Neck')
# Rebuilt lower muzzle closes the beard-card openings with a rounded, un-bearded chin.
ellipsoid('Rounded cream lower muzzle',(0,.219,.037),(.022,.0105,.010),chinfur,HEAD)
for side in [-1,1]:ellipsoid('Soft muzzle lobe '+str(side),(side*.0085,.224,.039),(.012,.006,.007),chinfur,HEAD)
strand('Muzzle center line',[(0,.228,.046),(0,.223,.047)],.00048,black)
for side in [-1,1]:strand('Small feline smile '+str(side),[(0,.223,.047),(side*.004,.220,.047),(side*.009,.221,.044)],.00045,black)
# Hair cap follows the head and stops above the eyes. Ears remain fully feline.
v=[];f=[];N=64;R=12
for j in range(R):
    t=j/(R-1)
    for k in range(N):
        a=k*math.tau/N;front=max(0,math.cos(a));bottom=.225+.039*front**2;rad=math.cos(t*math.pi/2)*.998+.002
        v.append((.055*math.sin(a)*rad,bottom+(.298-bottom)*math.sin(t*math.pi/2),-.006+.048*math.cos(a)*rad))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
mesh('Short layered hair cap',v,f,hair,HEAD)
# Swept fringe, with individual tapered locks rather than a flat block.
for i in range(5):
    shift=(i-2)*.003
    points=[]
    for j in range(13):
        t=j/12;x=-.026+.059*t+shift*(1-t);y=.29-.031*t+shift*.6;z=.03+.017*math.sin(t*math.pi/2)
        points.append((x,y,z))
    o=strand('Side-swept fringe %02d'%i,points,.005,hairlight if i==2 else hair,flatten=.35);o['helmet_hide']=True
# Side locks sit behind the cheek guards, leaving the eyes, nose and muzzle exposed.
for side in [-1,1]:
    for i in range(4):
        strand('Tucked side lock %s %d'%(side,i),[(side*(.046+i*.002),.28,-.009-i*.004),(side*(.056+i*.001),.25,-.023-i*.003),(side*(.051+i*.001),.22,-.035-i*.003)],.0038,hairlight if i==0 else hair,flatten=.45)
# Low braided ponytail remains behind the helmet and collar.
for braid in range(3):
    points=[]
    for j in range(30):
        t=j/29;a=t*math.tau*2.3+braid*math.tau/3;r=.005*(1-.7*t)
        points.append((r*math.cos(a),.258-.06*t,-.057-.018*math.sin(t*math.pi)+r*math.sin(a)))
    strand('Low woven braid '+str(braid),points,.0036,hairlight if braid==1 else hair)
ellipsoid('Braid silver tie',(0,.251,-.064),(.007,.004,.004),silver,HEAD)
# Small swept outer lashes, without changing Lucien's green eyes.
for side in [-1,1]:
    for i in range(2):
        strand('Outer eyelash '+str(side)+str(i),[(side*.035,.249+i*.0015,.039),(side*.041,.251+i*.002,.035),(side*.043,.253+i*.002,.034)],.00055,black)
    o=ellipsoid('Small silver ear stud '+str(side),(side*.047,.283,.005),(.0018,.0018,.0018),silver,HEAD);o['helmet_hide']=True

# Save the actual editable derivative before importing the armor preview.
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien-femenina-base.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-femenina-base.glb'),export_format='GLB',export_animations=False,export_extras=True)
base_objects=list(bpy.context.scene.objects)

def studio():
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True
    scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    center=Vector((0,-.012,.16))
    for pos,power in [((.4,-.65,.65),12),((-.4,-.1,.35),6),((.1,.4,.5),15)]:
        bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=.45;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(.3,-.95,.35));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=.4;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
    scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    return scene,camera,center
scene,camera,center=studio()
for name,location in [('base-preview',(.3,-.95,.35)),('base-front',(0,-1,.25)),('base-back',(.3,1,.32))]:
    camera.location=location;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
# Reuse the user's adjusted armor at the same anchors, as a separate preview project.
project=json.loads((ROOT/'projects/lucien-v1-ajustada.json').read_text(encoding='utf-8'));project['base']='female';project['name']='Lucien femenina - armadura ajustada'
manifest=json.loads((ROOT/'armor-parts.json').read_text(encoding='utf-8'))
for o in base_objects:
    if o.get('helmet_hide'):o.hide_render=True;o.hide_viewport=True
for item in project['items']:
    part=next(p for p in manifest['parts'] if p['id']==item['partId']);before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/part['url']))
    for o in bpy.context.scene.objects:
        if o not in before and o.parent is None:o.location+=Vector(xyz(item['position']))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in ['MESH','ARMATURE','EMPTY'] and not o.hide_render:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien-femenina-armadura.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
camera.location=(.3,-.95,.37);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.43;scene.render.filepath=str(OUT/'armored-preview.png');bpy.ops.render.render(write_still=True)
manifest['female_base']=dict(url='exports/custom/lucien-female/Lucien-femenina-base.glb',position=[0,0,0])
(ROOT/'armor-parts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'projects/lucien-femenina.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Lucien-femenina-armadura.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
print('LUCIEN_FEMALE_COMPLETE',removed_beard,flush=True)
