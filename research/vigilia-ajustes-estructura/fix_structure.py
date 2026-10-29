import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];SOURCE=ROOT/'research/vigilia-turbinas/Vigilia-turbinas.blend'
EXP=ROOT/'research/model-catalog/exports/vigilia-estructura';EXP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
def sig(o):
 return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],list(o.matrix_world))).encode()).hexdigest()
changed=['VIG_00_Casco','VIG_05_Techo','VIG_15_Azotea']
preserved={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and not any(c.name in changed for c in o.users_collection)}
wood=next(m for m in bpy.data.materials if 'Clan' in m.name and 'Roble restaurado' in m.name)
bronze=next(m for m in bpy.data.materials if 'Clan' in m.name and 'Bronce envejecido' in m.name)
def mesh(name,vs,fs,mat,key):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);bpy.data.collections[key].objects.link(o);o.parent=bpy.data.objects[key];return o
def rod(name,a,b,r,mat,key):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[key].objects.link(o);o.parent=bpy.data.objects[key];o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o
# Complete both open hull end sections with welded tapering fans.
hull=next(o for o in bpy.data.objects if o.name.startswith('Casco_curvo_listones'))
bm=bmesh.new();bm.from_mesh(hull.data);bm.verts.ensure_lookup_table()
ends=[]
for x,tipx in [(-15,-15.5),(16.5,16.8)]:
 ring=sorted([v for v in bm.verts if abs(v.co.x-x)<.001],key=lambda v:math.atan2(v.co.y,4.05-v.co.z))
 tip=bm.verts.new((tipx,0,4.05))
 for j in range(len(ring)-1):
  f=bm.faces.new((ring[j],ring[j+1],tip));f.material_index=(j//2)%len(hull.data.materials)
 ends.append({'x':x,'tip':[tipx,0,4.05],'ringVertices':len(ring)})
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(hull.data);bm.free()
# Extend the deck's top over the small new taper; no unsupported open wedge.
for x,tipx,w in [(-15,-15.5,.35),(16.5,16.8,.15)]:
 o=mesh('Remate de cubierta',[(x,-w,4.15),(tipx,0,4.15),(x,w,4.15)],[(0,1,2)],wood,'VIG_00_Casco');o.modifiers.new('Espesor','SOLIDIFY').thickness=.18
 for sy in [-1,1]:rod('Remate de borda',(x,sy*w,4.28),(tipx,0,4.28),.10,bronze,'VIG_00_Casco')
# Replace intersecting rectangles with a single continuous L-shaped slab.
for o in list(bpy.data.objects):
 if o.name.startswith(('Techo_rectangular_V3','Pasarela a azotea')):bpy.data.objects.remove(o,do_unlink=True)
outline=[(-12.35,-1.6),(-9,-1.6),(-9,1.6),(-11.85,1.6),(-11.85,1.84),(-13.25,1.84),(-13.25,1.30),(-12.35,1.30)]
n=len(outline);vs=[(x,y,z) for z in [6.36,6.44] for x,y in outline]
fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
slab=mesh('Techo y desembarco continuo',vs,fs,wood,'VIG_05_Techo')
# Match the cornice to the new outline; its top remains flush with the walking surface.
for o in list(bpy.data.collections['VIG_05_Techo'].objects):
 if not o.name.startswith('Cornisa'):continue
 for v in o.data.vertices:
  if o.name.startswith('Cornisa_extremo') and v.co.x<-12:
   v.co.y=-1.6+(v.co.y+1.6)*(2.9/3.2)
  elif o.name.startswith('Cornisa_V3') and v.co.y>0:
   v.co.x=-11.85+(v.co.x+12.35)*(2.85/3.35)
  v.co.z-=.03
# Rail return closes the exposed upper landing edge, joining the stair handrail.
rod('Retorno baranda desembarco',(-13.29,1.36,6.75),(-13.25,1.84,6.78),.009,bronze,'VIG_15_Azotea')
# Planar UVs keep the same hull/roof timber texture.
for o in [hull,slab]+[o for o in bpy.data.objects if o.name.startswith('Remate de cubierta')]:
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for p in o.data.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/3.2,co[axes[1]]/3.2)
assert all(sig(bpy.data.objects[n])==h for n,h in preserved.items())
# Check landing/roof support height, including the former seam and former overlap.
from mathutils.bvhtree import BVHTree
slab.data.calc_loop_triangles();bvh=BVHTree.FromPolygons([v.co for v in slab.data.vertices],[tuple(t.vertices) for t in slab.data.loop_triangles],all_triangles=True)
samples=[]
for x,y in [(-13.0,1.38),(-12.6,1.5),(-12.35,1.5),(-12.1,1.5),(-11.9,1.7),(-10,.5)]:
 hit=bvh.ray_cast(Vector((x,y,6.6)),Vector((0,0,-1)))[0];assert hit and abs(hit.z-6.44)<.0001;samples.append(list(hit))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-estructura.blend'))
for key in changed:
 items=[o for o in bpy.data.collections[key].objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=key+'_Malla'
bpy.ops.object.select_all(action='DESELECT')
for key in changed:
 for o in bpy.data.collections[key].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'estructura.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
g=json.loads((EXP/'estructura.gltf').read_text(encoding='utf-8'))
for m in g.get('materials',[]):
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
(EXP/'estructura.gltf').write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
(OUT/'geometry-audit.json').write_text(json.dumps({'passed':True,'closedEnds':ends,'continuousRoofLanding':True,'supportSamples':samples,'unchangedMeshes':len(preserved)},indent=2),encoding='utf-8')
print('STRUCTURE_FIXED',flush=True)
