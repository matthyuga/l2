import bpy,json,sys,collections
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent
for ident,radius in [('r4_arena',10000),('canon_cathedral',6000)]:
 folder=D/ident;j=json.loads((folder/'manifest.json').read_text(encoding='utf-8'));audit=json.loads((folder/'audit.json').read_text(encoding='utf-8'))
 bins=collections.Counter((round(a.get('Location',[0,0,0])[0]/5000),round(a.get('Location',[0,0,0])[1]/5000)) for a in j['actors']);cell=bins.most_common(1)[0][0];center=[v*5000 for v in cell]
 actors={a['actor'] for a in j['actors'] if sum((a.get('Location',[0,0,0])[i]-center[i])**2 for i in range(2))<radius**2}
 bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(c) for o in bpy.data.objects if o.type=='MESH' and o.name.rsplit('_',1)[0] in actors for c in o.bound_box]
 assert points
 lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 p=folder/'model.json';m=json.loads(p.read_text(encoding='utf-8'));m['view_bounds']=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]];m['note']+=' Encuadre inicial centrado en la zona principal; el archivo conserva otras salas/piezas separadas del mapa.'
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print('FOCUS',ident,len(actors),m['view_bounds'],flush=True)
