"""Read the downloaded FBX with Blender; never save or alter the source scene."""
import bpy,pathlib,json,hashlib,collections,math

OUT=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path(r'E:\l2-local\research\external-assets-20261028\unpacked\ext3_02b86c82826120\source\Sett-1.fbx')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(SRC),use_anim=True)
bpy.context.view_layer.update()

def matrix(m):return [[float(v) for v in row] for row in m]
arms=[]
for obj in bpy.context.scene.objects:
    if obj.type!='ARMATURE':continue
    bones=[]
    for i,b in enumerate(obj.data.bones):
        bones.append({'index':i,'name':b.name,'parent':b.parent.name if b.parent else None,'children':[c.name for c in b.children],'head_armature':list(b.head_local),'tail_armature':list(b.tail_local),'length_armature_units':b.length,'matrix_armature_row_major':matrix(b.matrix_local),'use_deform':b.use_deform,'inherit_scale':b.inherit_scale,'connected':b.use_connect})
    arms.append({'name':obj.name,'matrix_world_row_major':matrix(obj.matrix_world),'bones':bones})
meshes=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or not obj.visible_get():continue
    weights=collections.defaultdict(lambda:{'vertices':0,'sum':0.,'min':1.,'max':0.})
    influence_counts=collections.Counter();bad_sums=0
    for v in obj.data.vertices:
        influences=[g for g in v.groups if g.weight>1e-8];influence_counts[len(influences)]+=1
        if influences and abs(sum(g.weight for g in influences)-1)>1e-4:bad_sums+=1
        for g in influences:
            w=weights[obj.vertex_groups[g.group].name];w['vertices']+=1;w['sum']+=g.weight;w['min']=min(w['min'],g.weight);w['max']=max(w['max'],g.weight)
    meshes.append({'name':obj.name,'vertices':len(obj.data.vertices),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'vertex_groups':[g.name for g in obj.vertex_groups],'weighted_groups':dict(weights),'influence_histogram':dict(influence_counts),'non_normalized_vertices_tolerance_1e_4':bad_sums,'armature_modifiers':[m.object.name if m.object else None for m in obj.modifiers if m.type=='ARMATURE']})
actions=[]
for action in bpy.data.actions:
    curves=[];seen=set()
    if hasattr(action,'fcurves'):curves.extend(action.fcurves)
    else:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag=strip.channelbag(slot)
                    if bag:curves.extend(bag.fcurves)
    summary=[]
    for c in curves:
        identity=c.as_pointer()
        if identity in seen:continue
        seen.add(identity);keys=c.keyframe_points
        values=[float(k.co.y) for k in keys];frames=[float(k.co.x) for k in keys]
        summary.append({'data_path':c.data_path,'array_index':c.array_index,'keyframes':len(keys),'frame_min':min(frames) if frames else None,'frame_max':max(frames) if frames else None,'value_min':min(values) if values else None,'value_max':max(values) if values else None,'varying_tolerance_1e_6':bool(values and max(values)-min(values)>1e-6),'interpolations':dict(collections.Counter(k.interpolation for k in keys)),'modifiers':[m.type for m in c.modifiers]})
    actions.append({'name':action.name,'frame_range':list(action.frame_range),'curves':summary,'curve_count':len(summary),'keyframe_count':sum(c['keyframes'] for c in summary)})
report={'schema_version':1,'authority':'format-aware-import-observation','parser':'Blender FBX importer','blender_version':bpy.app.version_string,'source_path':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'scene_fps':bpy.context.scene.render.fps,'scene_fps_base':bpy.context.scene.render.fps_base,'unit_system':bpy.context.scene.unit_settings.system,'unit_scale':bpy.context.scene.unit_settings.scale_length,'armatures':arms,'meshes':meshes,'actions':actions,'limitations':['Coordinates and curves are Blender importer results, not a direct dump of original FBX byte records.','A bone name does not establish anatomy or gameplay purpose.','Import and export can resample or convert representations.']}
(OUT/'sett-fbx-observation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'bones':sum(len(a['bones']) for a in arms),'actions':len(actions),'fps':report['scene_fps'],'curves':sum(a['curve_count'] for a in actions),'keys':sum(a['keyframe_count'] for a in actions)},ensure_ascii=True),flush=True)
