"""Original shipwright's figurehead: carved hull wood and its existing aged bronze.
Red Dragon is a visual/anatomical guide, not a transplanted creature mesh.
"""
from pathlib import Path
HELPERS=Path(__file__).resolve().parents[1]/'vigilia-dragon-sculpt-20261020/recreate_dragon.py'
prefix=HELPERS.read_text(encoding='utf-8').split('# Continuous anatomy:')[0]
prefix=prefix.replace('exports/vigilia-dragon-sculpt','exports/vigilia-mascaron')
exec(compile(prefix,str(HELPERS),'exec'))
collection.name='VIG_16_Mascaron';parent.name='VIG_16_Mascaron'
wood=bpy.data.materials['Clan · Roble restaurado'].copy();wood.name='Mascaron · madera del casco'
walnut=bpy.data.materials['Clan · Nogal oscuro'].copy();walnut.name='Mascaron · talla en nogal'
brass=bpy.data.materials['Clan · Bronce envejecido'].copy();brass.name='Mascaron · bronce del barco'
black=bpy.data.materials['Clan · Hierro negro'].copy();black.name='Mascaron · hierro de las juntas'
gem=bpy.data.materials['Clan · Farol ámbar'].copy();gem.name='Mascaron · incrustacion de ambar';gem.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.35

def loft(name,rings,material,profile=None,steps=4):
 # Ring fields: X, Z, half-width, half-height. A chamfered profile reads as carving.
 profile=profile or [(math.cos(math.tau*j/16),math.sin(math.tau*j/16)) for j in range(16)]
 n=len(profile);samples=[]
 for k in range(len(rings)-1):
  for j in range(steps):
   t=j/steps;samples.append(tuple(rings[k][i]*(1-t)+rings[k+1][i]*t for i in range(4)))
 samples.append(rings[-1]);vs=[];fs=[]
 for k,(x,z,ry,rz) in enumerate(samples):
  for y,zz in profile:vs.append((x,y*ry,z+zz*rz))
  if k:
   for j in range(n):a=(k-1)*n+j;b=(k-1)*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(samples)-1)*n+j for j in range(n))]);return mesh(name,vs,fs,material)

# A continuous S-shaped wooden stem rises from the bow, with a smaller head.
neck=loft('Madera · cuello tallado',[(14.15,4.20,.88,.90),(14.8,4.38,.90,.95),(15.7,4.9,.83,1.0),(16.7,5.8,.73,.96),(17.5,6.7,.67,.87),(18.4,7.35,.74,.76),(19.45,7.6,.79,.68)],wood)
profile=[(0,1),(.62,.91),(.94,.55),(1,.05),(.91,-.55),(.52,-.87),(0,-.94),(-.52,-.87),(-.91,-.55),(-1,.05),(-.94,.55),(-.62,.91)]
loft('Madera · craneo y hocico',[(18.7,7.68,.56,.61),(19.35,7.92,.88,.73),(20.05,7.96,.96,.74),(20.75,7.86,.77,.56),(21.45,7.72,.59,.40),(22.2,7.67,.49,.30),(22.8,7.69,.35,.23),(23.02,7.72,.12,.14)],wood,profile)
# A narrow, architectural mouth; its dark slot has no tongue or fleshy gums.
loft('Madera · mandibula',[(19.35,6.95,.51,.21),(20.2,6.80,.59,.18),(21.15,6.83,.51,.15),(22.1,6.99,.40,.11),(22.72,7.17,.18,.08)],walnut,profile)
loft('Hierro · sombra de la boca',[(19.85,7.18,.50,.19),(20.8,7.14,.47,.20),(21.8,7.24,.36,.15),(22.55,7.40,.18,.07)],black)

for side in [-1,1]:
 # Horns borrowed in silhouette from Red Dragon, reinterpreted as cast bronze fittings.
 sweep('Bronce · cuerno largo de proa',[(19.45,side*.70,8.32),(18.82,side*1.16,8.62),(17.65,side*1.50,8.85),(16.8,side*1.64,9.18),(16.55,side*1.54,9.73)],[.24,.24,.18,.10,0],brass,14,9)
 sweep('Madera · cuerno de mejilla',[(19.55,side*.70,7.62),(18.8,side*1.06,7.73),(18.0,side*1.30,7.95),(17.65,side*1.34,8.25)],[.21,.17,.095,0],walnut,12,8)
 # Two swept cheek blades echo the dragon's frills, shaped like the ship's timbers.
 for j in range(2):
  a=Vector((19.55-j*.14,side*.72,7.53-j*.37));b=Vector((17.75-j*.28,side*1.08,7.65-j*.43));c=Vector((18.25-j*.25,side*1.10,7.13-j*.43));d=Vector((19.60-j*.16,side*.68,7.10-j*.35))
  o=mesh('Madera · aleta tallada de mejilla',[tuple(a),tuple(b),tuple(c),tuple(d)],[(0,1,2,3)],wood);solid=o.modifiers.new('Espesor de talla','SOLIDIFY');solid.thickness=.12;be=o.modifiers.new('Canto de talla','BEVEL');be.width=.065;be.segments=3
  sweep('Bronce · perfil de aleta',[tuple(b),tuple(a.lerp(b,.5)),tuple(a)],[.025,.03,.022],brass,8,6)
 # Recessed amber inlays replace the biological eye.
 ellipsoid('Hierro · cajeado del ojo',(20.30,side*.925,8.03),(.31,.065,.13),black,(0,.28,0))
 ellipsoid('Ambar · ojo incrustado',(20.35,side*.983,8.04),(.17,.035,.060),gem,(0,.28,0))
 sweep('Madera · ceja tallada',[(19.70,side*.83,8.40),(20.12,side*.99,8.32),(20.55,side*.87,8.16),(20.85,side*.69,7.94)],[.13,.14,.10,.035],walnut,12,8)
 sweep('Bronce · ceja incisa',[(19.75,side*.94,8.44),(20.1,side*1.08,8.35),(20.48,side*.97,8.20)],[.024,.028,.012],brass,8,6)
 ellipsoid('Hierro · narina tallada',(22.43,side*.355,7.81),(.17,.035,.075),black,(0,-.2,0))
 sweep('Bronce · labio superior',[(20.35,side*.70,7.44),(21.15,side*.54,7.38),(22.0,side*.43,7.41),(22.78,side*.18,7.56)],[.042,.038,.03,.016],brass,10,8)
 sweep('Bronce · filo de mandibula',[(19.60,side*.50,6.98),(20.4,side*.57,6.76),(21.65,side*.43,6.94),(22.62,side*.18,7.16)],[.04,.045,.03,.016],brass,10,8)
 # Sparse cast teeth, the same material as the ship's metalwork.
 for j in range(5):
  x=20.55+j*.40;z=7.39+max(0,j-2)*.04;h=.28 if j in (0,3) else .19
  sweep('Bronce · diente de mascaron',[(x,side*.43,z),(x+.03,side*.41,z-h*.65),(x+.10,side*.39,z-h)],[.065,.037,0],brass,9,5)

# A strong central nasal crest and three rear spines retain the red dragon's identity.
sweep('Nogal · cresta del hocico',[(22.35,0,7.90),(22.58,0,8.38),(22.35,0,8.72)],[.20,.14,0],walnut,12,9)
sweep('Bronce · arista de cresta',[(22.51,0,8.10),(22.65,0,8.40),(22.35,0,8.72)],[.028,.02,0],brass,8,8)
for j in range(3):
 x=17.0+j*.68;z=6.8+j*.57;sweep('Nogal · espina dorsal',[(x,0,z),(x-.14,0,z+.51),(x-.57,0,z+.86)],[.17,.11,0],walnut,12,8)

# Broad wooden scale reliefs, deliberately sparse so the carving reads from the deck.
for side in [-1,1]:
 for row in range(7):
  t=row/6;x=15.0+t*3.6;z=4.62+t*2.85;r=.84-t*.12
  for band in range(3):
   angle=(band-1)*.48;yy=side*r*math.cos(angle);zz=z+r*.83*math.sin(angle)
   armor('Roble · escama en bajorrelieve',(x,yy,zz),(0,side*math.cos(angle),math.sin(angle)),(1,0,.6),.73,.48,.035,wood)
 for row in range(4):
  x=19.05+row*.43
  for band in range(2):
   if row>=2 and band==1:continue
   armor('Nogal · placa de sien',(x,side*(.77+math.sin(row*.8)*.12),7.82+(band-.5)*.33),(0,side,0),(1,0,.15),.60,.36,.045,walnut)
 # Carved curls use the same bronze strips as the hull's bow ornament.
 sweep('Bronce · voluta del cuello',[(15.3,side*.87,4.90),(16.1,side*.86,5.43),(16.8,side*.79,6.12),(17.3,side*.78,6.62),(17.8,side*.80,6.71),(17.91,side*.81,6.47),(17.65,side*.82,6.38)],[.024]*7,brass,8,8)
 sweep('Nogal · nervio de garganta',[(14.8,side*.38,3.79),(16.0,side*.42,4.32),(17.45,side*.35,5.90),(19.0,side*.33,6.78)],[.06,.065,.055,.025],walnut,10,9)

# Visible flanges make the head an installed piece of the ship rather than a creature.
def band(name,center,normal,radius,tube,material,ellipse=1):
 n=Vector(normal).normalized();u=n.cross(Vector((0,1,0))).normalized();v=n.cross(u);c=Vector(center);points=[tuple(c+u*radius*math.cos(math.tau*j/48)+v*radius*ellipse*math.sin(math.tau*j/48)) for j in range(49)];return sweep(name,points,[tube]*len(points),material,8,1)
for x,z,r in [(14.3,4.26,.91),(14.58,4.39,.96)]:band('Bronce · collar de anclaje',(x,0,z),(1,0,.48),r,.065,brass)
for side in [-1,1]:
 sweep('Hierro · tirante del mascaron',[(13.7,side*.90,3.85),(14.4,side*.85,4.26),(15.15,side*.68,4.71)],[.10,.11,.08],black,10,8)
 for j in range(3):ellipsoid('Bronce · perno de montaje',(14.25+j*.23,side*.94,4.08+j*.18),(.055,.035,.055),brass)

# Planar grain projection in the carving follows the hull's own oak texture.
for obj in collection.objects:
 if obj.type!='MESH':continue
 me=obj.data
 if not me.uv_layers:uv=me.uv_layers.new(name='Veta de roble tallado')
 else:uv=me.uv_layers.active
 for poly in me.polygons:
  axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in poly.loop_indices:
   co=obj.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/3.2,co[axes[1]]/3.2)

assert all(signature(bpy.data.objects[n])==h for n,h in preserved.items())
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sourcehash
scene['figurehead_design']='Original carved-oak and aged-bronze figurehead, visually guided by Red Dragon.'
scene['figurehead_status']='Editor study; no native game installation.'
head_parts=sum(o.type=='MESH' for o in collection.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-mascaron.blend'))
for key in ['VIG_00_Casco','VIG_16_Mascaron']:
 col=bpy.data.collections[key];items=[o for o in col.objects if o.type in {'MESH','CURVE'}];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();bpy.context.object.name=key+'_Malla'
bpy.ops.object.select_all(action='DESELECT')
for key in ['VIG_00_Casco','VIG_16_Mascaron']:
 for o in bpy.data.collections[key].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'mascaron.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'mascaron.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name'] or m['name']=='Mascaron · madera del casco':m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
g['asset']['copyright']='Original figurehead geometry for Vigilia. Visual guide: Red Dragon by GadgetHamster, character design Alexander Ostrowski (CC BY 4.0); no source mesh used.'
(EXP/'mascaron.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
report={'sourceShipHash':sourcehash,'preservedShipMeshes':len(preserved),'otherShipGeometryUnchanged':True,'newParts':head_parts,'exportTriangles':triangles,'design':'Carved hull oak, walnut, original ship bronze and amber inlay','sourceMeshUsed':False,'visualGuide':'GadgetHamster Red Dragon','gameInstalled':False}
(OUT/'design-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('FIGUREHEAD_READY',report,flush=True)
