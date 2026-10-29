import bpy,pathlib,json
from mathutils import Vector
root=pathlib.Path(__file__).parent
inv=json.loads((root/'inventory.json').read_text('utf-8'))['records']
targets=['lamprey-mermay.zip','hologram-police-robots.zip','infection-spreader.zip','stella.zip','mule-robot.zip','robotic-eye.zip','abomination-doom-the-dark-ages-rigged.zip','iovar.zip','arlo.zip','angela-season-5.zip']
results=[]
for r in inv:
 if r['file'] not in targets:continue
 p=pathlib.Path(r['root'])/r['models'][0];bpy.ops.wm.read_factory_settings(use_empty=True)
 try:
  if p.suffix.lower()=='.fbx':
   try:bpy.ops.import_scene.fbx(filepath=str(p))
   except:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.fbx_import(filepath=str(p))
  else:bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  bpy.context.view_layer.update()
  objs=[]
  for o in bpy.context.scene.objects:
   if o.type!='MESH':continue
   ps=[o.matrix_world@Vector(v) for v in o.bound_box]
   lo=[min(v[i] for v in ps) for i in range(3)];hi=[max(v[i] for v in ps) for i in range(3)]
   objs.append({'name':o.name,'verts':len(o.data.vertices),'hidden':[o.hide_render,o.hide_viewport,o.hide_get()],'bounds':[lo,hi],'materials':[m.name for m in o.data.materials if m]})
  mats=[{'name':m.name,'images':[(n.image.name,n.image.filepath) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image],'links':[(n.from_node.name,n.to_node.name,n.to_socket.name) for n in m.node_tree.links]} for m in bpy.data.materials if m.use_nodes]
  results.append({'file':r['file'],'key':r['key'],'objects':objs,'materials':mats})
 except Exception as e:results.append({'file':r['file'],'error':str(e)})
(root/'scene-inspection.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('SCENE_INSPECTION_COMPLETE',flush=True)
