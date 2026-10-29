"""Second design pass: gothic barding, articulated plates and tailored textiles.

Reuses the original build helpers, but writes a separate v2 project and asset.
No downloaded third-party meshes are used.
"""
from pathlib import Path
source=Path(__file__).with_name('build_lucien_knight.py')
exec(compile(source.read_text(encoding='utf-8').split('# Save clean edit project')[0],str(source),'exec'))
OUT=ROOT/'exports/custom/lucien-knight-v2';OUT.mkdir(parents=True,exist_ok=True)

def delete_prefixes(prefixes):
    for o in list(bpy.context.scene.objects):
        if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)

delete_prefixes(['Open face sallet','Helmet rolled rim','Crowned brow replacement','Brow lower',
                 'Crimson crest strand','Crest steel spine','Separate skirt plate','Tasset edging',
                 'Crimson padded skirt','Rounded pauldron','Pauldron edge','Red arm tie',
                 'Crimson throat bow','Bow knot','Dark belt','Belt buckle'])
engrave=material('Recessed charcoal engraving',(.035,.048,.06),.55,.55)
ivory=material('Ivory padded linen',(.65,.63,.55),0,.93)
stitch=material('Linen seams',(.27,.22,.17),0,1)
silver.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.46
edge.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.36

# Retire the original high golden collar, green sleeves and balloon trousers.
# Keep the original head and paws. Exposed lower legs are neutral fur-colored.
fur=material('Charcoal leg fur',(.12,.14,.15),0,.95)
for obj in base:
    bm=bmesh.new();bm.from_mesh(obj.data);remove=[]
    deform=bm.verts.layers.deform.active
    names={v.index:v.name for v in obj.vertex_groups}
    obj.data.materials.append(fur);fur_slot=len(obj.data.materials)-1
    for face in bm.faces:
        center=obj.matrix_world@face.calc_center_median()
        weights={}
        if deform:
            for v in face.verts:
                for idx,w in v[deform].items():weights[idx]=weights.get(idx,0)+w
        bone=names.get(max(weights,key=weights.get),'') if weights else ''
        wardrobe=('Spine' in bone or 'spine' in bone or bone in ['Bone06','Bone03','Bone04','Bone09','Bip01 Pelvis'] or 'Thigh' in bone or 'UpperArm' in bone or ('Forearm' in bone and center.z>.133))
        if wardrobe and .062<center.z<.244:remove.append(face)
        elif 'Calf' in bone and center.z>.025:face.material_index=fur_slot
        # The small gold forehead pendant sits below the crown's original spikes.
        if bone=='Bip01 head' and center.z>.259 and abs(center.x)<.028 and center.y<-.015:
            if face not in remove:remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(obj.data);bm.free()

def solid(obj,thick=.001):
    mod=obj.modifiers.new('Plate thickness','SOLIDIFY');mod.thickness=thick
    bevel=obj.modifiers.new('Hand finished edge bevel','BEVEL');bevel.width=.00065;bevel.segments=2
    return obj

def rivet(name,p,bone,r=.0014):
    return ellipsoid(name,p,(r,r,r*.65),gold,bone)

# Taller sallet, with a raised central comb and an arched face aperture.
N=64;R=13;vs=[];fs=[]
def helm_point(a,t):
    front=max(0,math.cos(a));bottom=.236+.043*front**1.8
    radial=math.cos(t*math.pi/2)*.998+.002
    y=bottom+(.327-bottom)*math.sin(t*math.pi/2)
    ridge=.0025*max(0,1-abs(math.sin(a))*7)*math.sin(t*math.pi)
    return (.061*math.sin(a)*radial,y+ridge,-.007+.054*math.cos(a)*radial)
for j in range(R):
    for k in range(N):vs.append(helm_point(math.tau*k/N,j/(R-1)))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
solid(mesh('V2 gothic sallet shell',vs,fs,silver,HEAD),.0014)
for t in [0,.045]:
    tube('Sallet double rolled rim '+str(t),[helm_point(k*math.tau/64,t) for k in range(65)],.00085,edge,HEAD)
# Closely fitted central forehead plate covers the old crown cutout.
v=[(-.039,.283,.042),(0,.301,.052),(.039,.283,.042),(.029,.269,.045),(0,.254,.054),(-.029,.269,.045)]
solid(mesh('V2 arched forehead plate',v,[(0,1,4,5),(1,2,3,4)],silver,HEAD),.001)
tube('Forehead scalloped border',[v[i] for i in [0,5,4,3,2]],.001,edge,HEAD)
# Dark pierced-looking ventilation crosses sit on the curved forehead surface.
for i,a in enumerate([-.55,-.28,0,.28,.55]):
    p=Vector(helm_point(a,.43));p.z+=.0012
    height=.012 if i==2 else .009
    tube('Sallet vertical vent %02d'%i,[p+Vector((0,-height/2,0)),p+Vector((0,height/2,0))],.00105,engrave,HEAD,6)
    tube('Sallet transverse vent %02d'%i,[p+Vector((-.0026,.001,0)),p+Vector((.0026,.001,0))],.0008,engrave,HEAD,6)
for side in [-1,1]:
    # Engraved S-scrolls, hinge hardware and rivets on the hanging cheek plates.
    for j in range(3):rivet('Cheek rivet',(side*.057,.247-j*.008,.035),HEAD,.0012)
    pts=[]
    for j in range(32):
        t=j/31;a=math.tau*1.2*t;r=.006*(1-.7*t)
        pts.append((side*(.052+r*math.cos(a)*.4),.239+r*math.sin(a),.0405))
    tube('Cheek etched spiral '+str(side),pts,.00045,engrave,HEAD,5)

# Horsehair fan: broad and layered, rather than a narrow looping strip.
for i in range(27):
    f=i/26;offset=(f-.5)*.03;verts=[]
    for j in range(19):
        t=j/18
        y=.326+.045*math.sin(t*math.pi*.92)-.077*t*t+(1-abs(f-.5)*2)*.003
        z=-.01-.105*t
        x=offset*(.45+.75*t)+.0018*math.sin(t*math.pi*3+f*4)
        width=.0018*(1-.8*t)
        verts.extend([(x-width,y,z),(x+width,y,z),(x,y+.0012,z-.001)])
    faces=[]
    for j in range(18):
        for k in range(3):a=j*3+k;b=j*3+(k+1)%3;faces.append((a,b,b+3,a+3))
    mesh('V2 separate horsehair lock %02d'%i,verts,faces,redlight if i%4==0 else red,HEAD)
tube('Plume mounting comb',[(0,.323,.019),(0,.332,-.005),(0,.323,-.039)],.0032,edge,HEAD)
for z in [.01,-.009,-.027]:rivet('Comb fastening',(0,.333,z),HEAD,.0018)

# Layered, scalloped gorget replaces Lucien's standing gold collar.
for j in range(3):
    h=.19+j*.005
    shell('Overlapping neck lame %d'%j,[(h,.025-j*.002,.026-j*.001),(h+.006,.022-j*.002,.024-j*.001)],silver,SPINE)
    tube('Gorget raised edge %d'%j,[( (.025-j*.002)*math.sin(a),h,(.026-j*.001)*math.cos(a)) for a in [k*math.tau/40 for k in range(41)]],.0008,edge,SPINE)

# More structured pauldrons: scalloped articulated lames on a domed shoulder cap.
for side,label in [(-1,'R'),(1,'L')]:
    bone='Bip01 '+label+' UpperArm';cx=side*.05
    ellipsoid('Padded dark undersleeve '+label,(side*.046,.163,-.006),(.013,.026,.015),dark,bone)
    for j in range(3):
        v=[];f=[]
        for ring in range(6):
            t=ring/5
            for k in range(33):
                a=k*math.tau/32
                rad=.013+.013*t+j*.001
                yy=.19-j*.006-.011*t
                if ring==5:yy-=.002*max(0,math.cos(5*a))
                v.append((cx+rad*math.sin(a),yy,-.006+rad*math.cos(a)))
        for ring in range(5):
            for k in range(32):idx=ring*33+k;f.append((idx,idx+1,idx+34,idx+33))
        solid(mesh('Articulated pauldron %s lame %d'%(label,j),v,f,silver,bone),.0009)
        tube('Pauldron scalloped edge %s %d'%(label,j),v[-33:],.001,edge,bone)
        if j==0:
            for k in range(0,32,4):rivet('Shoulder rivet',v[-33+k],bone,.0012)
    ellipsoid('Shoulder upper dome '+label,(cx,.191,-.006),(.014,.005,.014),silver,bone)
    # Engraved curls on the front of each shoulder.
    for sign in [-1,1]:
        pts=[]
        for k in range(26):
            t=k/25;a=sign*t*math.tau;r=.005*(1-.8*t)
            pts.append((cx+sign*.006+r*math.cos(a),.184+r*math.sin(a),.018))
        tube('Pauldron curl',pts,.00045,engrave,bone,5)
    # Layered steel forearm vambrace, leaving the white furry cuffs and paws exposed.
    for j in range(2):
        ellipsoid('Forearm plate '+label+str(j),(side*(.053+j*.006),.151-j*.008,-.006),(.014,.01,.018),silver,'Bip01 '+label+' Forearm')

# Breastplate borders, fasteners, chasing, and a restrained heraldic motif.
for side in [-1,1]:
    tube('Breastplate swept flute '+str(side),[(side*.027,.18,.026),(side*.03,.164,.03),(side*.023,.145,.036),(side*.013,.13,.037)],.00065,engrave,SPINE)
    for k in range(7):
        y=.132+k*.007;rivet('Cuirass side fastening',(side*.034,y,.024),SPINE,.001)
    for j in range(2):
        pts=[]
        for k in range(38):
            t=k/37;a=side*math.tau*1.2*t;r=.007*(1-.85*t)
            x=side*(.015+j*.007)+r*math.cos(a);y=.162-j*.012+r*math.sin(a)
            z=.038*math.sqrt(max(.1,1-(x/.043)**2))+.001
            pts.append((x,y,z))
        tube('Cuirass chased scroll '+str(side)+str(j),pts,.00045,engrave,SPINE,5)
# Emblem is small enough to read as armor engraving, not another large button.
mesh('Cuirass pointed heraldic badge',[(-.008,.181,.033),(.008,.181,.033),(.007,.169,.038),(0,.163,.04),(-.007,.169,.038)],[(0,1,2,3,4)],dark,SPINE)
for a in [0,math.pi/2,math.pi,math.pi*1.5]:
    tube('Heraldic fleur leaf',[(0,.174,.040),(.003*math.sin(a),.174+.004*math.cos(a),.040)],.00075,edge,SPINE,6)

# Tailored red underskirt with modeled diamond quilting between the steel plates.
def skirt_surface(a,t,offset=0):
    rx=.041+.022*math.sin(t*math.pi/2);rz=.036+.016*math.sin(t*math.pi/2)
    return Vector(((rx+offset)*math.sin(a),.121-.071*t,(rz+offset)*math.cos(a)))
v=[];f=[];N=64;R=12
for j in range(R):
    for k in range(N):v.append(skirt_surface(k*math.tau/N,j/(R-1)))
for j in range(R-1):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
mesh('V2 tailored crimson gambeson',v,f,red,PELVIS)
for slope in [-1,1]:
    for j in range(36):
        pts=[]
        for k in range(35):
            t=k/34;a=j*math.tau/36+slope*t*.9;pts.append(skirt_surface(a,t,.0007))
        tube('Quilt diamond stitch',pts,.00028,stitch,PELVIS,4)
# Six wider gothic tassets with scalloped, rolled hems.
for panel in range(6):
    a=panel*math.tau/6;v=[];f=[];C=10;R=12
    for j in range(R):
        t=j/(R-1)
        for k in range(C+1):
            u=k/C;angle=a+(u-.5)*.78
            p=skirt_surface(angle,t,.0027)
            if j==R-1:p.y-=.004*(.5+.5*math.cos(u*math.pi*4))
            # Central chased ridge and softly fluted edges.
            p+=Vector((math.sin(angle),0,math.cos(angle)))*(.0015*math.cos((u-.5)*math.pi)**8)
            v.append(p)
    for j in range(R-1):
        for k in range(C):i=j*(C+1)+k;f.append((i,i+1,i+C+2,i+C+1))
    solid(mesh('V2 gothic tasset %02d'%panel,v,f,silver,PELVIS),.001)
    path=[v[j*(C+1)] for j in range(R)]+v[-(C+1):]+[v[j*(C+1)+C] for j in range(R-1,-1,-1)]
    tube('Gothic tasset rolled border %02d'%panel,path,.001,edge,PELVIS)
    for sign in [-1,1]:
        # Fine ornamental line follows the plate surface near its inner edges.
        pts=[]
        for k in range(35):
            t=.12+.73*k/34;p=skirt_surface(a+sign*.29,t,.004);pts.append(p)
        tube('Tasset fine inset line',pts,.00038,engrave,PELVIS,5)
        rivet('Tasset upper rivet',skirt_surface(a+sign*.29,.1,.004),PELVIS,.0014)
        # Etched scroll at the lower end of each plate.
        pts=[]
        for k in range(30):
            t=k/29;r=.065*(1-.8*t);ang=math.tau*1.1*t
            p=skirt_surface(a+sign*.18+r*math.cos(ang),.77+r*math.sin(ang),.004)
            pts.append(p)
        tube('Tasset lower spiral',pts,.00042,engrave,PELVIS,5)
    for offset in [-.22,0,.22]:rivet('Hem ornament',skirt_surface(a+offset,.96,.004),PELVIS,.00125)

shell('V2 leather waist belt',[(.12,.044,.039),(.131,.044,.039)],dark,PELVIS)
for y in [.121,.13]:tube('Belt stitched edge',[(.0445*math.sin(a),y,.0395*math.cos(a)) for a in [k*math.tau/50 for k in range(51)]],.0005,stitch,PELVIS)
# True open buckle, tongue and leather tail instead of the oval sphere.
tube('Angular silver buckle',[(-.009,.12,.042),(-.012,.125,.042),(-.008,.132,.042),(.009,.132,.042),(.012,.126,.042),(.008,.12,.042),(-.009,.12,.042)],.0014,edge,PELVIS)
tube('Buckle tongue',[(-.006,.126,.043),(.007,.126,.043)],.0009,edge,PELVIS)
for x in [.018,.024,.03]:rivet('Belt perforation',(x,.126,.034),PELVIS,.0007)

# Sculpted folded bow: curved lobes, a knot and two hanging tails.
for side in [-1,1]:
    v=[];f=[]
    for j in range(9):
        t=j/8
        for k in range(9):
            u=k/8;x=side*(.003+.017*t);y=.199+(u-.5)*(.005+.015*t)
            z=.033+.006*math.sin(u*math.pi)*math.sin(t*math.pi)
            v.append((x,y,z))
    for j in range(8):
        for k in range(8):i=j*9+k;f.append((i,i+1,i+10,i+9))
    solid(mesh('V2 folded silk bow '+str(side),v,f,red,SPINE),.0004)
    mesh('V2 bow ribbon tail '+str(side),[(side*.002,.197,.035),(side*.009,.197,.035),(side*.013,.179,.034),(side*.007,.182,.035),(side*.003,.18,.035)],[(0,1,2,3,4)],redlight,SPINE)
ellipsoid('V2 fabric bow knot',(0,.199,.038),(.004,.004,.003),red,SPINE)

# Shield now has small studs and ornamental bordering to match the plate set.
cx=.101;cy=.125;cz=.035;bone='Bip01 L Hand'
for i,p in enumerate(outline):rivet('Shield rim stud %d'%i,(cx+p[0]*.94,cy+p[1]*.94,cz+.002),bone,.0014)
tube('Shield inset engraved line',[(cx+x*.87,cy+y*.87,cz+.010) for x,y in outline+[outline[0]]],.00065,engrave,'Bip01 L Hand')

# Polished objects contain true detail geometry; no shader-only features are lost in GLB.
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Lucien_Crimson_Knight_v2.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Lucien_Crimson_Knight_v2.glb'),export_format='GLB',export_animations=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=96;scene.eevee.use_gtao=True
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
center=Vector((0,-.018,.17))
for pos,power,size in [((.4,-.65,.65),12,.5),((-.4,-.1,.35),6,.4),((.1,.4,.5),15,.3)]:
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.3,-.95,.38));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.44;scene.camera=camera
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
scene.render.resolution_x=1100;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Lucien_Crimson_Knight_v2.png');bpy.ops.render.render(write_still=True)
print('LUCIEN_V2_COMPLETE',flush=True)
