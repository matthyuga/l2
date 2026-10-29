import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(__file__).resolve().parent;R=OUT.parents[1];EXPORT=R/'research/model-catalog/exports/vigilia-renovada1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Vigilia-renovada1.blend'))
wood=bpy.data.materials['Clan · Roble restaurado'];nodes=wood.node_tree.nodes;links=wood.node_tree.links;bs=nodes.get('Principled BSDF');tex=next(n for n in nodes if n.type=='TEX_IMAGE')
mix=nodes.get('Acabado oscuro') or nodes.new('ShaderNodeMixRGB');mix.name='Acabado oscuro';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.42,.29,.19,1);links.new(tex.outputs['Color'],mix.inputs[1]);links.new(mix.outputs[0],bs.inputs['Base Color'])
for o in list(bpy.data.objects):
 if o.name.startswith(('Junta_tablas_cubierta','Junta fina de cubierta')):bpy.data.objects.remove(o,do_unlink=True)
stations=[(-15,.35),(-14,2.1),(-12,4.15),(-8,5.1),(-3,5.45),(3,5.35),(8,4.7),(12,3.55),(15,1.7),(16.5,.15)]
def width(x):
 for (a,w),(b,v) in zip(stations,stations[1:]):
  if a<=x<=b:return w+(v-w)*(x-a)/(b-a)
 return .1
col=bpy.data.collections['VIG_02_Cubierta'];root=bpy.data.objects['VIG_02_Cubierta'];m=bpy.data.materials['Clan · Nogal oscuro']
for j in range(174):
 x=-14.85+j*.18;w=width(x)-.08
 if w<=.02:continue
 c=bpy.data.curves.new('Junta fina de cubierta','CURVE');c.dimensions='3D';c.bevel_depth=.002;c.bevel_resolution=1;s=c.splines.new('POLY');s.points.add(1);s.points[0].co=(x,-w,4.154,1);s.points[1].co=(x,w,4.154,1);c.materials.append(m);o=bpy.data.objects.new('Junta fina de cubierta',c);col.objects.link(o);o.parent=root
# Keep a dark framed rear wall in the captain's quarters.
for name in ['Aposento_popa_V3','Mamparo bajo','Mamparo de proa']:
 for o in bpy.data.objects:
  if o.name==name or o.name.startswith(name+'.'):
   for slot in o.material_slots:slot.material=bpy.data.materials['Clan · Nogal oscuro']
# Move the old port bench away from the three new cantina seats.
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith(('Banco_clan_V3','Pata_clan_V3','Respaldo_clan_V3')):continue
 pts=[v.co for v in o.data.vertices]
 if not pts:continue
 center=sum(pts,Vector())/len(pts)
 if 0<center.x<1 and -4.1<center.y<-3.5:
  for v in o.data.vertices:v.co.x-=1.7
# Bake only the newly created joint curves; other pieces already have world vertices.
deps=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.data.objects):
 if o.type!='CURVE':continue
 c=o.users_collection[0];name=o.name;parent=o.parent;me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.transform(o.matrix_world);ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.parent=parent;bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-renovada1.blend'))
for col in bpy.data.collections:
 if not col.name.startswith('VIG_'):continue
 meshes=[o for o in col.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 if len(meshes)>1:bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=col.name+'_Mobiliario'
bpy.ops.object.select_all(action='DESELECT')
for col in bpy.data.collections:
 if col.name.startswith('VIG_'):
  for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT/'vigilia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
file=EXPORT/'vigilia.gltf';g=json.loads(file.read_text(encoding='utf-8'))
for m in g['materials']:
 if 'Parabrisas transparente' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
file.write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
print('POLISHED_EXPORT',sum(len(m['primitives']) for m in g['meshes']))
