"""Finish the first build: open handrail passages, then export a batched copy."""
import bpy, math, json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];EXPORT=ROOT/'research/model-catalog/exports/aurelia-vip1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
root=bpy.data.objects['VIP_B5_Mirador'];col=root.users_collection[0];gold=bpy.data.materials['VIP · Bronce champagne']
for o in list(col.objects):
    if o.name.startswith(('Baranda lateral del mirador','Poste de mirador')):bpy.data.objects.remove(o,do_unlink=True)
for y in [-4.4,4.4]:
    for a,b in [(-6.4,-4.2),(-1.8,6.4)]:
        c=bpy.data.curves.new('Baranda lateral del mirador','CURVE');c.dimensions='3D';c.bevel_depth=.05;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(1);s.points[0].co=(a,y,6.6,1);s.points[1].co=(b,y,6.6,1);c.materials.append(gold);o=bpy.data.objects.new('Baranda lateral del mirador',c);col.objects.link(o);o.parent=root
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
    for x in [-6.4,-4.2,-1.8,2.4,6.4]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.04,depth=1.05,location=(x,y,6.03));o=bpy.context.object;o.name='Poste de mirador';
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o.data.materials.append(gold);o.parent=root
for im in bpy.data.images:
    if im.source=='FILE' and im.users:
        if im.size[0]>1024:im.scale(1024,1024)
        im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
for col in bpy.data.collections:
    meshes=[o for o in col.objects if o.type=='MESH']
    if not col.name.startswith('VIP_') or len(meshes)<2:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=col.name+'_Mobiliario'
bpy.ops.object.select_all(action='DESELECT')
for col in bpy.data.collections:
    if col.name.startswith('VIP_'):
        for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXPORT/'aurelia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
file=EXPORT/'aurelia.gltf';g=json.loads(file.read_text(encoding='utf-8'))
for m in g['materials']:
    if 'Vidrio mirador' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True;m['pbrMetallicRoughness']['baseColorFactor']=[.20,.52,.62,.20]
    if 'Agua estática' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True
file.write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
print('BATCHED_EXPORT',len(g['meshes']),sum(len(m['primitives']) for m in g['meshes']))
