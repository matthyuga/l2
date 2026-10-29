"""Static original organic infestation: grounded tissue colonies and curved thorns."""
from pathlib import Path
import bpy,json,math,random,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parent;C=R.parent/'model-catalog';O=C/'exports/dion-living-v5';O.mkdir(parents=True,exist_ok=True)
import sys
assert not (O/'colonies.glb').exists() or '--refine' in sys.argv,'Preserve existing version'
source=C/'exports/scene-batch1-library_fe488fdfccee/scene.gltf';g=json.loads(source.read_text(encoding='utf-8'))
n=next(n for n in g['nodes'] if 'terrain' in n.get('name','').lower());a=g['accessors'][g['meshes'][n['mesh']]['primitives'][0]['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];buf=(source.parent/g['buffers'][v['buffer']]['uri']).read_bytes();points=np.ndarray((a['count'],3),dtype='<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4))
xs=np.unique(points[:,0]);zs=np.unique(points[:,2]);grid=np.zeros((len(xs),len(zs)));grid[np.searchsorted(xs,points[:,0]),np.searchsorted(zs,points[:,2])]=points[:,1]
def height(x,z):
 i=int(np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2));j=int(np.clip(np.searchsorted(zs,z)-1,0,len(zs)-2));a=float(np.clip((x-xs[i])/(xs[i+1]-xs[i]),0,1));b=float(np.clip((z-zs[j])/(zs[j+1]-zs[j]),0,1));return float((1-a)*((1-b)*grid[i,j]+b*grid[i,j+1])+a*((1-b)*grid[i+1,j]+b*grid[i+1,j+1]))
def coord(x,z,y):return Vector((x,-z,y))
bpy.ops.wm.read_factory_settings(use_empty=True);rng=random.Random(271029)
def material(name,color,roughness):
 m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=roughness
 colors=m.node_tree.nodes.new('ShaderNodeVertexColor');colors.layer_name='TissueTint';m.node_tree.links.new(colors.outputs['Color'],s.inputs['Base Color']);return m
tissue=material('Tejido vivo · granate ceniza',(.18,.045,.065),.64)
horn=material('Quitina · espinas oscuras',(.12,.085,.075),.47)
vein=material('Raíces carnosas',(.23,.075,.09),.56)
counts={'colonies':0,'spines':0,'roots':0}
def mesh(name,verts,faces,mat,color):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();obj=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(obj);m.materials.append(mat)
 tint=m.color_attributes.new(name='TissueTint',type='FLOAT_COLOR',domain='POINT')
 for i,p in enumerate(m.vertices):
  shade=.8+.25*rng.random()+.10*math.sin(p.co.x*6+p.co.y*3);tint.data[i].color=(*(min(1,c*shade) for c in color),1)
 for p in m.polygons:p.use_smooth=True
 return obj
def tube(name,path,radii,mat,color,sides=9):
 verts=[];faces=[]
 for i,(point,radius) in enumerate(zip(path,radii)):
  tangent=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized();axis=tangent.cross(Vector((0,0,1)))
  if axis.length<.01:axis=tangent.cross(Vector((0,1,0)))
  axis.normalize();other=tangent.cross(axis).normalized()
  for j in range(sides):
   angle=j*math.tau/sides;r=radius*(1+.075*math.sin(j*3+i*.7));p=point+(axis*math.cos(angle)+other*math.sin(angle))*r;verts.append(tuple(p))
  if i:
   for j in range(sides):a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides;faces.append((a,b,i*sides+(j+1)%sides,i*sides+j))
 faces.append(tuple(reversed(range(sides))));faces.append(tuple(range((len(path)-1)*sides,len(path)*sides)))
 return mesh(name,verts,faces,mat,color)
sites=[(-13,1,1.2),(14,8,1.45),(35,3,1.05),(50,-20,1.2),(-17,-26,1.25),(5,-49,1.0),(32,-54,1.05),(23,-20,.70)]
for k,(x,z,scale) in enumerate(sites,1):
 y=height(x,z);counts['colonies']+=1
 # Low lobed tissue blends into the terrain instead of standing on a pedestal.
 verts=[tuple(coord(x,z,y+.18*scale))];faces=[];rings=5;sides=36
 for ring in range(1,rings+1):
  radius=ring/rings*2.1*scale
  for j in range(sides):
   angle=j*math.tau/sides;r=radius*(1+.12*math.sin(angle*5+k)+.07*math.sin(angle*9));xx=x+math.cos(angle)*r;zz=z+math.sin(angle)*r
   bulge=(1-(ring/rings)**1.5)*.45*scale+.07*math.sin(angle*7+ring)
   verts.append(tuple(coord(xx,zz,height(xx,zz)+max(.015,bulge))))
  for j in range(sides):
   current=1+(ring-1)*sides+j;next_=1+(ring-1)*sides+(j+1)%sides
   if ring==1:faces.append((0,current,next_))
   else:previous=current-sides;previous_next=next_-sides;faces.append((previous,current,next_,previous_next))
 mesh(f'Colonia {k:02d} · membrana lobulada',verts,[tuple(reversed(f)) for f in faces],tissue,(.12,.024,.041))
 for j in range(7):
  angle=j*math.tau/7+rng.uniform(-.28,.28);length=rng.uniform(2.7,5.2)*scale;path=[];radii=[]
  for i in range(18):
   t=i/17;a=angle+math.sin(t*4+k)*.16;xx=x+math.cos(a)*length*t;zz=z+math.sin(a)*length*t;path.append(coord(xx,zz,height(xx,zz)+.055*scale+math.sin(t*math.pi)*.10));radii.append((.19*(1-t)**1.2+.012)*scale)
  tube(f'Colonia {k:02d} · raíz {j+1}',path,radii,vein,(.22,.064,.080),7);counts['roots']+=1
 for j in range(5):
  angle=j*math.tau/5+rng.uniform(-.35,.35);base_r=rng.uniform(.55,1.2)*scale;xx=x+math.cos(angle)*base_r;zz=z+math.sin(angle)*base_r;yy=height(xx,zz)+.13*scale
  tall=rng.uniform(1.15,2.8)*scale;path=[];radii=[]
  for i in range(18):
   t=i/17;lean=(t*t*1.05-.12*math.sin(t*math.pi))*scale;path.append(coord(xx+math.cos(angle)*lean,zz+math.sin(angle)*lean,yy+t*tall));radii.append(max(.006,(.26*(1-t)**1.1)*scale))
  tube(f'Colonia {k:02d} · espina curva {j+1}',path,radii,horn,(.13,.075,.078));counts['spines']+=1
  # Living collars at the base of each thorn, visually joining horn and tissue.
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=7,location=coord(xx,zz,yy+.03));bulb=bpy.context.object;bulb.name=f'Colonia {k:02d} · nódulo {j+1}';bulb.scale=(.34*scale,.30*scale,.26*scale)
  bulb.data.materials.append(tissue);colors=bulb.data.color_attributes.new(name='TissueTint',type='FLOAT_COLOR',domain='POINT')
  for v in colors.data:v.color=(.24,.065,.085,1)
  for face in bulb.data.polygons:face.use_smooth=True
bpy.ops.export_scene.gltf(filepath=str(O/'colonies.glb'),export_format='GLB',export_animations=False,export_yup=True)
(O/'organic-audit.json').write_text(json.dumps({'counts':counts,'sites':sites,'static':True,'terrainConforming':True,'style':'Original organic dark-fantasy tissue, curved chitin spines, no copied game assets','seed':271029},indent=2))
print('ORGANIC COMPLETE',counts,flush=True)
