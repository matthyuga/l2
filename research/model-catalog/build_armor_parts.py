"""Bake fitting copies and preliminary donor cuts; preserve source models."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'exports/armor-editor';OUT.mkdir(parents=True,exist_ok=True)
parts=[]

def thumbnail(key,objects,extent):
    ss=bpy.data.scenes.new('Part studio');ss.render.engine='BLENDER_EEVEE';ss.eevee.taa_render_samples=16;ss.eevee.use_gtao=True
    ss.world=bpy.data.worlds.new('Part world');ss.world.use_nodes=True;ss.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.14,.18,.23,1)
    ss.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
    size=max(extent,.03);helpers=[]
    for o in objects:ss.collection.objects.link(o)
    data=bpy.data.cameras.new('Part camera');camera=bpy.data.objects.new('Part camera',data);ss.collection.objects.link(camera);helpers.append(camera)
    camera.location=Vector((.5,-1.5,.45))*size;camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=size*1.35;ss.camera=camera
    for pos,power in [((1,-2,3),200),((-2,-1,1),130),((1,2,2),220)]:
        data=bpy.data.lights.new('Part light','AREA');data.energy=power*size*size;data.size=size*2
        o=bpy.data.objects.new('Part light',data);ss.collection.objects.link(o);helpers.append(o);o.location=Vector(pos)*size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    ss.view_settings.view_transform='Standard';ss.render.resolution_x=256;ss.render.resolution_y=220;ss.render.resolution_percentage=100
    ss.render.image_settings.file_format='PNG';ss.render.filepath=str(OUT/(key+'.png'));bpy.ops.render.render(write_still=True,scene=ss.name)
    for o in helpers:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(ss)

def export_piece(key,title,category,objects,source,provisional=False,target=None):
    if not objects:return
    copies=[];dg=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg)
        mesh.transform(obj.matrix_world)
        copy=bpy.data.objects.new(obj.name+' fit',mesh);bpy.context.collection.objects.link(copy);copies.append(copy)
    points=[v.co for o in copies for v in o.data.vertices]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
    center=(lo+hi)/2
    for o in copies:
        o.data.transform(Matrix.Translation(-center));o.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT')
    for o in copies:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(key+'.glb')),export_format='GLB',use_selection=True,export_animations=False)
    position=list(target) if target else [center.x,center.z,-center.y]
    record=dict(id=key,name=title,category=category,url='exports/armor-editor/'+key+'.glb',position=position,rotation=[0,0,0],scale=[1,1,1],source=source,provisional=provisional,triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in copies))
    if category!='Base':
        thumbnail(key,copies,max(hi-lo));record['thumbnail']='exports/armor-editor/'+key+'.png'
    parts.append(record)
    for o in copies:bpy.data.objects.remove(o,do_unlink=True)

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports/custom/lucien-knight-v2/Lucien_Crimson_Knight_v2.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
groups={}
for o in meshes:
    n=o.name.lower();slot=None
    if n.startswith('king_of_cat'):continue
    if any(s in n for s in ['horsehair','plume mounting','comb fastening']):slot=('v2-plume','Penacho carmesí V2','Adornos')
    elif any(s in n for s in ['sallet','forehead','cheek','helmet','brow']):slot=('v2-helmet','Casco gótico V2','Cascos')
    elif any(s in n for s in ['pauldron','shoulder']):
        side='left' if o.location.x>0 else 'right'
        # Most manually built meshes have identity transforms; inspect geometry center.
        if o.data.vertices:
            cx=sum((o.matrix_world@v.co).x for v in o.data.vertices)/len(o.data.vertices);side='left' if cx>0 else 'right'
        slot=('v2-shoulder-'+side,'Hombrera V2 '+('izquierda' if side=='left' else 'derecha'),'Hombreras')
    elif any(s in n for s in ['forearm plate']):
        side='L' if ' L' in o.name else 'R';slot=('v2-bracer-'+side,'Brazal V2 '+('izquierdo' if side=='L' else 'derecho'),'Guantes y brazales')
    elif any(s in n for s in ['undersleeve']):continue
    elif any(s in n for s in ['gorget','neck lame']):slot=('v2-gorget','Gorjal articulado V2','Cuello')
    elif any(s in n for s in ['tasset','gambeson','quilt','hem ornament']):slot=('v2-skirt','Faldón gótico V2','Pantalón y faldones')
    elif any(s in n for s in ['belt','buckle']):slot=('v2-belt','Cinturón y hebilla V2','Cintura')
    elif any(s in n for s in ['bow','ribbon']):slot=('v2-bow','Lazo de seda V2','Adornos')
    elif any(s in n for s in ['shield','paw emblem']):slot=('v2-shield','Escudo de la huella V2','Escudos')
    else:slot=('v2-chest','Pechera grabada V2','Pecheras')
    groups.setdefault(slot,[]).append(o)
for slot,objects in groups.items():export_piece(*slot,objects,'Lucien Carmesí V2')

# Clean fitting body: original head/paws/sword with a neutral torso under armor.
body=[o for o in meshes if o.name.lower().startswith('king_of_cat') or 'undersleeve' in o.name.lower()]
mat=bpy.data.materials.new('Neutral padded fitting body');mat.diffuse_color=(.065,.08,.1,1)
for center,scale in [((0,0,.151),(.035,.031,.05)),((0,0,.097),(.032,.027,.03))]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=center);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);body.append(o)
export_piece('lucien-fitting','Lucien para probar armaduras','Base',body,'Lucien, copia de ajuste')

# The STL donor is fused. Spatial cuts are explicitly marked preliminary.
bpy.ops.wm.read_factory_settings(use_empty=True)
inv=json.loads((ROOT.parent/'cat-assets-20261023/inventory.json').read_text())
donor=next(a for a in inv if a['archive']=='armor-cat.zip')
bpy.ops.import_mesh.stl(filepath=donor['source']);obj=bpy.context.object
verts=[v.co for v in obj.data.vertices];lo=Vector([min(v[i] for v in verts) for i in range(3)]);hi=Vector([max(v[i] for v in verts) for i in range(3)])
height=hi.z-lo.z;middle=(lo+hi)/2
facegroups={};specs={
 'helmet':('Casco Armor Cat · corte inicial','Cascos',[0,.265,0]),
 'chest':('Pechera Armor Cat · corte inicial','Pecheras',[0,.16,0]),
 'waist':('Cintura Armor Cat · corte inicial','Cintura',[0,.12,0]),
 'legs':('Faldón Armor Cat · corte inicial','Pantalón y faldones',[0,.085,0]),
 'bootL':('Bota Armor Cat izquierda · corte inicial','Botas',[.026,.025,0]),
 'bootR':('Bota Armor Cat derecha · corte inicial','Botas',[-.026,.025,0]),
 'shoulderL':('Hombrera Armor Cat izquierda · corte inicial','Hombreras',[.052,.18,0]),
 'shoulderR':('Hombrera Armor Cat derecha · corte inicial','Hombreras',[-.052,.18,0]),
 'gloveL':('Guante Armor Cat izquierdo · corte inicial','Guantes y brazales',[.082,.11,0]),
 'gloveR':('Guante Armor Cat derecho · corte inicial','Guantes y brazales',[-.082,.11,0]),
}
for p in obj.data.polygons:
    c=p.center;h=(c.z-lo.z)/height;x=(c.x-middle.x)/height
    if h>.63:key='helmet'
    elif h<.18:key='bootL' if x>0 else 'bootR'
    elif .46<h<.65 and abs(x)>.14:key='shoulderL' if x>0 else 'shoulderR'
    elif .29<h<.46 and abs(x)>.15:key='gloveL' if x>0 else 'gloveR'
    elif h>.43:key='chest'
    elif h>.34:key='waist'
    else:key='legs'
    facegroups.setdefault(key,[]).append(tuple(p.vertices))
for key,faces in facegroups.items():
    used=sorted(set(i for face in faces for i in face));lookup={old:i for i,old in enumerate(used)}
    vs=[(obj.data.vertices[i].co-middle)*(.32/height) for i in used]
    data=bpy.data.meshes.new(key);data.from_pydata(vs,[],[tuple(lookup[i] for i in face) for face in faces]);data.update()
    piece=bpy.data.objects.new(key,data);bpy.context.collection.objects.link(piece)
    for p in data.polygons:p.use_smooth=True
    title,cat,pos=specs[key];export_piece('donor-armor-cat-'+key,title,cat,[piece],'Armor Cat · STL fusionado',True,pos)
    bpy.data.objects.remove(piece,do_unlink=True)
catalog=dict(version=1,base='lucien-fitting',categories=['Cascos','Hombreras','Guantes y brazales','Pecheras','Cintura','Botas','Pantalón y faldones','Cuello','Adornos','Escudos'],parts=[p for p in parts if p['category']!='Base'],fitting_base=next(p for p in parts if p['category']=='Base'))
(ROOT/'armor-parts.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
print('ARMOR_PARTS_COMPLETE',len(catalog['parts']),flush=True)
