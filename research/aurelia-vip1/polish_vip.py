import bpy, json, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
scene=bpy.context.scene;manifest=json.loads((OUT/'design-manifest.json').read_text(encoding='utf-8'))
M={key:bpy.data.materials[value] for key,value in {'pearl':'VIP · Cerámica perla','gold':'VIP · Bronce champagne','navy':'VIP · Terciopelo noche','wood':'VIP · Roble cálido','light':'VIP · Luz cálida','ivory':'VIP · Lino marfil','teal':'VIP · Verde petróleo'}.items()}
for o in list(bpy.data.objects):
    if o.name.startswith('DECOR_'):bpy.data.objects.remove(o,do_unlink=True)
for key,title,deck in [('VIP_A7_Techos','Techos e iluminación de la cubierta A','A'),('VIP_B6_Techos','Techos e iluminación de la cubierta B','B')]:
    if key not in bpy.data.collections:
        c=bpy.data.collections.new(key);scene.collection.children.link(c);r=bpy.data.objects.new(key,None);c.objects.link(r)
    manifest['zones']=[z for z in manifest['zones'] if z['node']!=key];manifest['zones'].append({'node':key,'title':title,'deck':deck,'objects':0})
def put(o,key,mat):
    for c in list(o.users_collection):c.objects.unlink(o)
    bpy.data.collections[key].objects.link(o);o.parent=bpy.data.objects[key];o.data.materials.append(M[mat]);return o
def box(n,loc,size,mat,key,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object,key,mat);o.name='DECOR_'+n;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:mod=o.modifiers.new('Acabado','BEVEL');mod.width=min(bevel,min(size)*.3);mod.segments=2;o.modifiers.new('Normales','WEIGHTED_NORMAL')
    return o
def cyl(n,loc,r,d,mat,key):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc);o=put(bpy.context.object,key,mat);o.name='DECOR_'+n;return o
def wall_art(x,y,z,w,side,key):
    box('Marco de arte',(x,y,z),(w,.10,1.40),'gold',key)
    box('Arte abstracto',(x,y-side*.07,z),(w-.10,.04,1.28),'navy',key,.01)
    for i in range(5):
        h=.30+(i%3)*.24;box('Arte en relieve',(x-w*.32+i*w*.16,y-side*.10,z-.25+h/2),(w*.06,.025,h),'gold' if i%2 else 'teal',key,.01)
for room in manifest['rooms']:
    x,y,z=room['center'];w,d=room['size'];side=1 if y>0 else -1;back=y+side*d/2;key=room['group'];ceiling='VIP_A7_Techos' if room['deck']=='A' else 'VIP_B6_Techos'
    box('Techo de '+room['name'],(x,y,z+3.42),(w+.10,d+.10,.15),'pearl',ceiling)
    for dx in [-w*.28,w*.28]:
        for dy in [-d*.24,d*.24]:cyl('Luminaria empotrada',(x+dx,y+dy,z+3.32),.18,.035,'light',ceiling)
    for sx in [-1,1]:box('Zócalo latón',(x+sx*(w/2-.09),y,z+.13),(.05,d-.20,.20),'gold',key,.01)
    box('Panel de fondo',(x,back-side*.13,z+1.65),(w*.78,.08,2.85),'navy',key)
    if room['name'].startswith('SUITE '):
        wall_art(x,back-side*.20,z+2.55,2.5,side,key)
    else:
        wall_art(x,back-side*.20,z+2.22,min(w*.46,6.0),side,key)
    # Repair the initial negative-side labels before their mesh was baked.
    if side<0:
        for obj in bpy.data.collections[key].objects:
            if obj.name.startswith(room['name']+' · enseigne') and not obj.get('vip_sign_corrected'):
                plane=y-side*d/2-side*.10;center=z+3.06
                for v in obj.data.vertices:v.co.y=2*plane-v.co.y;v.co.z=2*center-v.co.z
                obj['vip_sign_corrected']=True
for side in [-1,1]:box('Paseo de teca',(0,side*8.2,18.045),(38,2.4,.035),'wood','VIP_02_Terraza',.01)
# Back-bar shelves add depth behind the serving aisle.
for z in [11.30,12.15]:box('Estante de bar',(-26,-16.55,z),(13,.50,.09),'gold','VIP_A1_Bar')
for x in [-31.5,-30,-28.5,-27,-25.5,-24,-22.5,-21,-19.5]:
    for z in [11.5,12.35]:cyl('Botella de reserva',(x,-16.55,z),.07,.30,'teal' if x%3 else 'gold','VIP_A1_Bar')
box('Pasillo alfombrado A',(-7.5,0,10.54),(69,4.3,.035),'navy','VIP_A0_Cubierta',.01)
box('Pasillo alfombrado B',(-20.5,0,5.54),(27,3.2,.035),'navy','VIP_B0_Cubierta',.01)
for x in [-5.7,4.7]:cyl('Alfombra de mesa de juego',(x,-10.6,10.56),3.0,.025,'navy','VIP_A2_Casino')

# Move furnishings that the door-clearance audit identified in the entry lanes.
for obj in bpy.data.collections['VIP_B1_Camarotes'].objects:
    if obj.type=='MESH' and obj.name.startswith('Console suite') and not obj.get('vip_route_fixed'):
        for v in obj.data.vertices:v.co.x+=2.5
        obj['vip_route_fixed']=True
for obj in bpy.data.collections['VIP_A6_Suite'].objects:
    if obj.type!='MESH' or obj.get('vip_route_fixed'):continue
    if obj.name.startswith('Bureau propriétaire'):
        for v in obj.data.vertices:
            dx,dy=v.co.x-25,v.co.y-6.5;v.co.x=18-dy;v.co.y=8.2+dx
        obj['vip_route_fixed']=True
    elif obj.name.startswith('Taburete'):
        for v in obj.data.vertices:v.co.x-=5.2;v.co.y+=.2
        obj['vip_route_fixed']=True
for obj in bpy.data.collections['VIP_B3_Vestuarios'].objects:
    if obj.type!='MESH' or obj.get('vip_route_fixed'):continue
    if obj.name.startswith(('Sofá','Cojín marfil')):
        for v in obj.data.vertices:
            dx,dy=v.co.x-12.5,v.co.y+9;v.co.x=8.2+dy;v.co.y=-10.8-dx
        obj['vip_route_fixed']=True
    elif obj.name.startswith('Mesa'):
        for v in obj.data.vertices:v.co.x-=2.5;v.co.y-=.4
        obj['vip_route_fixed']=True

# Bake new pieces consistently; the saved master keeps the complete furniture.
deps=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.data.objects):
    if not o.name.startswith('DECOR_') or o.type!='MESH':continue
    key=o.users_collection[0].name;me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.transform(o.matrix_world)
    name=o.name;ob=bpy.data.objects.new(name,me);bpy.data.collections[key].objects.link(ob);ob.parent=bpy.data.objects[key];bpy.data.objects.remove(o,do_unlink=True)
    uv=me.uv_layers.new(name='UV_VIP')
    for p in me.polygons:
        axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/2.4,v[axes[1]]/2.4)
manifest['objects']=sum(1 for o in bpy.data.objects if o.type=='MESH')
for info in manifest['zones']:info['objects']=sum(1 for o in bpy.data.collections[info['node']].objects if o.type=='MESH')
(OUT/'design-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
print('VIP_POLISHED',manifest['objects'])
