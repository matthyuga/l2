"""Build a separate, editable two-rider visual kit; never alters the source mesh."""
from pathlib import Path
import json, math, struct, os, hashlib, random
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/'research/model-catalog'
SOURCE=CAT/'exports/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.gltf'
DEST=CAT/'exports/l2lab-behemoth-two-riders'
DEST.mkdir(parents=True,exist_ok=True)
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
g=json.loads(SOURCE.read_text(encoding='utf8'))
for kind in ('buffers','images'):
    for item in g.get(kind,[]):
        if item.get('uri') and not item['uri'].startswith('data:'):
            item['uri']=os.path.relpath(SOURCE.parent/item['uri'],DEST).replace('\\','/')
original_nodes=g['scenes'][g.get('scene',0)]['nodes'][:]
body=len(g['nodes']);g['nodes'].append({'name':'Behemoth original - escala de prototipo 4x','children':original_nodes,'scale':[4,4,4]})
g['scenes'][0]['nodes']=[body]
data=bytearray();buffer_index=len(g['buffers'])
g['buffers'].append({'uri':'equipment.bin','byteLength':0})

def accessor(values,components,ctype=5126):
    while len(data)%4:data.append(0)
    offset=len(data);fmt='f' if ctype==5126 else 'I'
    data.extend(struct.pack('<'+fmt*len(values),*values))
    view=len(g['bufferViews']);g['bufferViews'].append({'buffer':buffer_index,'byteOffset':offset,'byteLength':len(data)-offset})
    a={'bufferView':view,'componentType':ctype,'count':len(values)//components,'type':{1:'SCALAR',2:'VEC2',3:'VEC3'}[components]}
    if components==3:
        a['min']=[min(values[i::3]) for i in range(3)];a['max']=[max(values[i::3]) for i in range(3)]
    index=len(g['accessors']);g['accessors'].append(a);return index

def grain(name,wood=False):
    rng=random.Random(53 if wood else 19);im=Image.new('RGB',(256,256));p=im.load()
    for y in range(256):
        for x in range(256):
            n=rng.uniform(-9,9)+(7*math.sin(x*.18+math.sin(y*.02)*1.5) if wood else 0)
            base=(111,74,39) if wood else (77,43,27)
            p[x,y]=tuple(max(0,min(255,int(v+n))) for v in base)
    im.save(DEST/name)
    image=len(g['images']);g['images'].append({'uri':name})
    texture=len(g['textures']);g['textures'].append({'source':image,'sampler':0});return texture

def material(name,color,metal=0,texture=None):
    p={'baseColorFactor':[*color,1],'roughnessFactor':.77 if not metal else .42,'metallicFactor':metal}
    if texture is not None:p['baseColorTexture']={'index':texture}
    i=len(g['materials']);g['materials'].append({'name':name,'pbrMetallicRoughness':p,'doubleSided':True});return i
leather=material('Cuero marron - arnes y cinchas',[1,1,1],texture=grain('leather.png'))
wood=material('Madera oscura - plataforma',[1,1,1],texture=grain('wood.png',True))
metal=material('Bronce envejecido - hebillas y remaches',[.47,.32,.14],.72)
iron=material('Hierro oscuro - bastidor',[.14,.16,.17],.7)
pad=material('Acolchado rojo oscuro',[.20,.045,.035])
rope=material('Riendas de cuero',[.19,.09,.038])
parts=[]
def mesh(name,verts,faces,mat,parent):
    # Face normals preserve crisp joinery; UVs are planar per face.
    pos=[];norm=[];uv=[];indices=[]
    for face in faces:
        a,b,c=[verts[i] for i in face[:3]]
        ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
        n=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        l=math.sqrt(sum(v*v for v in n)) or 1;n=[v/l for v in n]
        start=len(pos)//3
        for j,i in enumerate(face):pos.extend(verts[i]);norm.extend(n);uv.extend([(j in (1,2))*1.,(j in (2,3))*1.])
        for j in range(1,len(face)-1):indices.extend([start,start+j,start+j+1])
    mi=len(g['meshes']);g['meshes'].append({'name':name,'primitives':[{'attributes':{'POSITION':accessor(pos,3),'NORMAL':accessor(norm,3),'TEXCOORD_0':accessor(uv,2)},'indices':accessor(indices,1,5125),'material':mat}]})
    ni=len(g['nodes']);g['nodes'].append({'name':name,'mesh':mi});g['nodes'][parent].setdefault('children',[]).append(ni);parts.append(name)
def group(name):
    n=len(g['nodes']);g['nodes'].append({'name':name,'children':[]});g['scenes'][0]['nodes'].append(n);return n
def box(name,center,size,mat,parent):
    x,y,z=center;a,b,c=[v/2 for v in size]
    v=[[x+dx*a,y+dy*b,z+dz*c] for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    mesh(name,v,[[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[0,1,5,4],[3,7,6,2]],mat,parent)
def tube(name,points,r,mat,parent,sides=8):
    verts=[]
    for j,p in enumerate(points):
        t=[points[min(j+1,len(points)-1)][k]-points[max(j-1,0)][k] for k in range(3)];l=math.sqrt(sum(v*v for v in t));t=[v/l for v in t]
        ref=[0,1,0] if abs(t[1])<.9 else [1,0,0]
        a=[t[1]*ref[2]-t[2]*ref[1],t[2]*ref[0]-t[0]*ref[2],t[0]*ref[1]-t[1]*ref[0]];l=math.sqrt(sum(v*v for v in a));a=[v/l for v in a]
        b=[t[1]*a[2]-t[2]*a[1],t[2]*a[0]-t[0]*a[2],t[0]*a[1]-t[1]*a[0]]
        for i in range(sides):
            angle=2*math.pi*i/sides;verts.append([p[k]+r*(a[k]*math.cos(angle)+b[k]*math.sin(angle)) for k in range(3)])
    faces=[]
    for j in range(len(points)-1):
        for i in range(sides):faces.append([j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i])
    faces.extend([list(reversed(range(sides))),list(range((len(points)-1)*sides,len(points)*sides))]);mesh(name,verts,faces,mat,parent)
def strap(name,z,rx,ry,cy,parent,width=.20):
    verts=[];steps=48
    for i in range(steps+1):
        t=2*math.pi*i/steps
        for dz,dr in [(-width/2,0),(width/2,0),(-width/2,.035),(width/2,.035)]:verts.append([(rx+dr)*math.sin(t),cy+(ry+dr)*math.cos(t),z+dz])
    faces=[]
    for i in range(steps):
        a=i*4;b=(i+1)*4;faces.extend([[a,b,b+1,a+1],[a+2,a+3,b+3,b+2],[a,a+2,b+2,b],[a+1,b+1,b+3,a+3]])
    mesh(name,verts,faces,leather,parent)
def buckle(name,x,y,z,parent):
    for dy in [-.13,.13]:box(name+' horizontal',(x,y+dy,z),(.055,.045,.31),metal,parent)
    for dz in [-.13,.13]:box(name+' lateral',(x,y,z+dz),(.055,.30,.045),metal,parent)
    box(name+' aguja',(x+.015,y,z),(.035,.025,.27),metal,parent)

harness=group('01 - Arnes y cinchas')
for label,z,rx,ry,cy in [('delantera',-.1,1.18,1.05,2.20),('trasera',-1.65,1.05,.93,2.12)]:
    strap('Cincha ventral '+label,z,rx,ry,cy,harness)
    for sign in [-1,1]:buckle('Hebilla '+label+str(sign),sign*(rx+.04),cy,z,harness)
for sign in [-1,1]:
    tube('Correa longitudinal '+str(sign),[[sign*1.18,2.2,-.1],[sign*1.15,2.35,-.8],[sign*1.05,2.12,-1.65]],.075,leather,harness)
    tube('Pechera diagonal '+str(sign),[[sign*1.15,2.65,-.1],[sign*.95,2.45,.55],[sign*.55,2.65,1.3]],.09,leather,harness)
    tube('Riendas '+str(sign),[[sign*.55,2.9,1.7],[sign*.65,3.15,1.1],[sign*.42,3.65,.45],[sign*.28,3.95,.15]],.027,rope,harness)

frame=group('02 - Bastidor y apoyos')
box('Manta acolchada bajo montura',(0,3.12,-.78),(1.65,.18,2.75),pad,frame)
for sign in [-1,1]:
    box('Larguero de carga '+str(sign),(sign*.68,3.32,-.85),(.12,.19,3.05),iron,frame)
    for z in [-1.9,-.2]:box('Apoyo acolchado '+str(sign)+str(z),(sign*.70,3.08,z),(.35,.25,.36),leather,frame)
for z in [-2.2,-1.1,.3]:box('Travesano '+str(z),(0,3.37,z),(1.85,.12,.14),iron,frame)

driver=group('03 - Asiento del conductor')
g['nodes'][driver]['translation']=[0,.30,0]
for sign in [-1,1]:box('Soporte elevado asiento '+str(sign),(sign*.33,3.62,.27),(.12,.42,.65),iron,frame)
box('Base asiento',(0,3.54,.27),(.92,.18,.93),wood,driver)
box('Cojin conductor',(0,3.68,.27),(.82,.18,.80),pad,driver)
box('Respaldo bajo',(0,3.94,-.15),(.91,.49,.12),leather,driver)
for sign in [-1,1]:
    tube('Asidero conductor '+str(sign),[[sign*.49,3.65,.45],[sign*.49,4.04,.48],[sign*.49,4.04,.1],[sign*.49,3.65,.1]],.045,metal,driver)
    box('Correa estribo '+str(sign),(sign*.68,3.19,.43),(.08,.82,.08),leather,driver)
    tube('Estribo '+str(sign),[[sign*.68,2.86,.30],[sign*.68,2.71,.30],[sign*.68,2.71,.62],[sign*.68,2.86,.62]],.045,metal,driver)

platform=group('04 - Plataforma de combate - puesto de pie')
for i in range(8):box('Tablon plataforma '+str(i+1),(-.84+i*.24,3.56,-1.52),(.225,.12,1.65),wood,platform)
for sign in [-1,1]:
    box('Borde plataforma '+str(sign),(sign*1.0,3.58,-1.52),(.12,.2,1.85),iron,platform)
    for z in [-2.37,-.70]:tube('Poste baranda '+str(sign)+str(z),[[sign*.99,3.63,z],[sign*.99,4.36,z]],.05,iron,platform)
    tube('Baranda lateral '+str(sign),[[sign*.99,4.36,-2.37],[sign*.99,4.36,-.70]],.055,metal,platform)
    for z in [-2.17,-1.52,-.87]:box('Remache '+str(sign)+str(z),(sign*.91,3.64,z),(.075,.035,.075),metal,platform)
    for z in [-1.98,-1.06]:
        tube('Tirante plataforma '+str(sign)+str(z),[[sign*.99,3.45,z],[sign*.91,2.45,z+.12]],.06,leather,platform)
# Rear opening at center for boarding; rail sections leave room to enter.
for sign in [-1,1]:tube('Baranda posterior '+str(sign),[[sign*.99,4.36,-2.37],[sign*.40,4.36,-2.37]],.055,metal,platform)
for y in [2.5,2.87,3.24]:tube('Peldaño trasero '+str(y),[[-.32,y,-2.57],[.32,y,-2.57]],.045,iron,platform)
for x in [-.36,.36]:tube('Escalera trasera '+str(x),[[x,2.3,-2.57],[x,3.57,-2.57]],.045,iron,platform)

anchors=group('05 - Anclajes de ocupantes - referencia')
for name,position in [('Conductor sentado',[0,4.07,.27]),('Atacante de pie',[0,3.63,-1.52])]:
    ni=len(g['nodes']);g['nodes'].append({'name':name,'translation':position,'extras':{'role':'driver' if 'Conductor' in name else 'gunner','forward':[0,0,1],'visualPrototypeOnly':True}});g['nodes'][anchors]['children'].append(ni)
g['buffers'][buffer_index]['byteLength']=len(data);(DEST/'equipment.bin').write_bytes(data)
g.setdefault('asset',{})['generator']='L2 Lab - two-rider Behemoth visual equipment v1'
g['extras']={'prototype':'visual-only','sourceSHA256':source_hash,'originalAsset':'m0331','bodyScale':4,'forward':'+Z','up':'+Y','occupants':2,'standingPassengerCanWalk':False,'equipmentIsNotAnimationBound':True}
(DEST/'behemoth-two-riders.gltf').write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf8')
asset={'id':'l2lab_behemoth_two_riders','title':'Behemoth - arnes y plataforma para dos','path':'exports/l2lab-behemoth-two-riders/behemoth-two-riders.gltf','thumbnail':'thumbs/l2lab_behemoth_two_riders.png','mesh':'L2Lab.BehemothTwoRiders','category':'Monturas','native':False,'batch':'Prototipos L2 Lab'}
custom=ROOT/'research/scene-editor/custom-assets.json';entries=json.loads(custom.read_text(encoding='utf8')) if custom.exists() else []
entries=[x for x in entries if x['id']!=asset['id']]+[asset];custom.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf8')
catalog=ROOT/'research/scene-editor/data.json';d=json.loads(catalog.read_text(encoding='utf8'));d['assets']=[x for x in d['assets'] if x['id']!=asset['id']]+[asset];catalog.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
report={'sourceUnchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'sourceSHA256':source_hash,'asset':asset,'equipmentParts':len(parts),'parts':parts,'anchors':[{'role':'driver','position':[0,4.07,.27]},{'role':'gunner','position':[0,3.63,-1.52]}],'limitations':['Visual prototype only','No game client files modified','Equipment is static, not weighted to skeleton yet','Animations and two-player control not implemented']}
(DEST/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'parts':len(parts),'sourceUnchanged':report['sourceUnchanged'],'file':str(DEST/'behemoth-two-riders.gltf')}))
