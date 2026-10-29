"""Branching terrain-conforming roots for every new V6 spine variation."""
from pathlib import Path
import bpy,json,math,random,numpy as np,ast
from mathutils import Vector
R=Path(__file__).resolve().parent;C=R.parent/'model-catalog';O=C/'exports/dion-infestation-v7';O.mkdir(parents=True,exist_ok=True)
assert not (O/'roots.glb').exists(),'Preserve existing version'
source=C/'exports/scene-batch1-library_fe488fdfccee/scene.gltf';g=json.loads(source.read_text(encoding='utf-8'));n=next(n for n in g['nodes'] if 'terrain' in n.get('name','').lower());a=g['accessors'][g['meshes'][n['mesh']]['primitives'][0]['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];buf=(source.parent/g['buffers'][v['buffer']]['uri']).read_bytes();points=np.ndarray((a['count'],3),dtype='<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4))
xs=np.unique(points[:,0]);zs=np.unique(points[:,2]);grid=np.zeros((len(xs),len(zs)));grid[np.searchsorted(xs,points[:,0]),np.searchsorted(zs,points[:,2])]=points[:,1]
bpy.ops.wm.read_factory_settings(use_empty=True);rng=random.Random(271031)
# Reuse the checked tube builder and native heightfield sampler without running
# the old scene producer or altering any of its outputs.
tree=ast.parse((R/'build-dion-living-v5.py').read_text(encoding='utf-8'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=nodes,type_ignores=[]),'root-helpers','exec'),globals())
flesh=material('Raíces vivas · invasión',(.16,.035,.055),.62)
placements=json.loads((C/'exports/dion-spines-v6/placements.json').read_text())
count=0;report=[]
for k,(kind,x,z,scale) in enumerate(placements,1):
 lengthscale=1.5 if kind=='giant' else 1.25 if kind in ['interlaced','branched'] else scale
 for j in range(6):
  angle=j*math.tau/6+rng.uniform(-.3,.3);length=rng.uniform(3,5.5)*lengthscale;path=[];radii=[]
  for i in range(26):
   t=i/25;angle_t=angle+.16*math.sin(t*5+k)+.1*math.sin(t*11+j);r=.15+length*t
   xx=x+math.cos(angle_t)*r;zz=z+math.sin(angle_t)*r
   # Buttress starts against the thorn's collar, then sinks into the soil.
   rise=.5*scale*(1-t)**5+.065*lengthscale
   path.append(coord(xx,zz,height(xx,zz)+rise));radii.append((.23*(1-t)**1.4+.008)*lengthscale)
  tube(f'Espina {k} · raíz principal {j+1}',path,radii,flesh,(.16,.035,.055),8);count+=1
  for fork in range(2):
   index=11+fork*6;start=path[index];sx,sz=start.x,-start.y;fa=angle+(-1 if fork==0 else 1)*rng.uniform(.5,1.0);fl=length*rng.uniform(.3,.48);child=[];cr=[]
   for i in range(16):
    t=i/15;xx=sx+math.cos(fa+t*.22)*fl*t;zz=sz+math.sin(fa+t*.22)*fl*t;child.append(coord(xx,zz,height(xx,zz)+.055*lengthscale));cr.append((.09*(1-t)**1.3+.005)*lengthscale)
   tube(f'Espina {k} · ramificación {j+1}-{fork+1}',child,cr,flesh,(.14,.028,.046),6);count+=1
 report.append({'kind':kind,'x':x,'z':z,'rootBranches':18})
bpy.ops.export_scene.gltf(filepath=str(O/'roots.glb'),export_format='GLB',export_animations=False,export_yup=True)
(O/'root-audit.json').write_text(json.dumps({'rootBranches':count,'sites':report,'static':True,'seed':271031,'grounding':'Bilinear native heightfield sampling; static visual roots, no growth simulation'},indent=2))
print('ROOTS COMPLETE',count,flush=True)
