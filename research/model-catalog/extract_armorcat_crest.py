import bpy,json,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/l2-local/research/model-catalog');OUT=ROOT/'exports/armor-editor';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
inv=json.loads((ROOT.parent/'cat-assets-20261023/inventory.json').read_text());a=next(x for x in inv if x['archive']=='armor-cat.zip');bpy.ops.import_mesh.stl(filepath=a['source']);o=bpy.context.object
vs=[v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);height=hi.z-lo.z;mid=(lo+hi)/2
faces=[tuple(p.vertices) for p in o.data.polygons if (p.center.z-lo.z)/height>.84 and abs(p.center.x-mid.x)/height<.11];adj={}
for index,face in enumerate(faces):
 for vertex in face:adj.setdefault(vertex,[]).append(index)
remaining=set(range(len(faces)));components=[]
while remaining:
 todo=[remaining.pop()];group=[]
 while todo:
  index=todo.pop();group.append(index)
  for vertex in faces[index]:
   for neighbor in adj[vertex]:
    if neighbor in remaining:remaining.remove(neighbor);todo.append(neighbor)
 components.append(group)
print('COMPONENTS',sorted([len(c) for c in components],reverse=True)[:10]);largest=max(components,key=len);faces=[faces[i] for i in largest]
used=sorted(set(i for f in faces for i in f));ids={v:i for i,v in enumerate(used)};v=[(o.data.vertices[i].co-mid)/height*.32 for i in used]
lo=Vector([min(p[i] for p in v) for i in range(3)]);hi=Vector([max(p[i] for p in v) for i in range(3)]);center=(lo+hi)/2
mesh=bpy.data.meshes.new('Donor sculpted crest');mesh.from_pydata([p-center for p in v],[],[tuple(ids[i] for i in f) for f in faces]);mesh.update();obj=bpy.data.objects.new('Donor sculpted crest',mesh);bpy.context.collection.objects.link(obj)
for p in mesh.polygons:p.use_smooth=True
source=ast.parse((ROOT/'build_armor_parts.py').read_text());node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='thumbnail');exec(compile(ast.Module(body=[node],type_ignores=[]),'thumbnail','exec'));thumbnail('donor-armorcat-crest',[obj],max(hi-lo));bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'donor-armorcat-crest.glb'),export_format='GLB',use_selection=True);print('CREST_BOUNDS',list(hi-lo),'faces',len(faces))
