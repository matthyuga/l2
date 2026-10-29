"""Isolated Blender worker: source mesh -> portable GLB + thumbnail and measured facts."""
import bpy,sys,pathlib,json,math,traceback,re
from mathutils import Vector

job=pathlib.Path(sys.argv[sys.argv.index('--')+1]);j=json.loads(job.read_text('utf-8'))
out=pathlib.Path(j['output']);out.mkdir(parents=True,exist_ok=True)
result={'key':j['key'],'input':j['input']}
try:
    src=pathlib.Path(j['input']);suffix=src.suffix.lower()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if suffix in {'.glb','.gltf'}:bpy.ops.import_scene.gltf(filepath=str(src))
    elif suffix=='.fbx':
        try:bpy.ops.import_scene.fbx(filepath=str(src),use_anim=True)
        except RuntimeError:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.wm.fbx_import(filepath=str(src))
    elif suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
    elif suffix=='.obj':bpy.ops.wm.obj_import(filepath=str(src))
    elif suffix=='.stl':bpy.ops.wm.stl_import(filepath=str(src))
    elif suffix=='.ply':bpy.ops.wm.ply_import(filepath=str(src))
    else:raise ValueError('Unsupported source '+suffix)
    if j.get('action_names'):
        result['source_action_names_before_filter']=[a.name for a in bpy.data.actions]
        active={o.animation_data.action.name for o in bpy.context.scene.objects if o.animation_data and o.animation_data.action}
        keep=set(j['action_names'])|active
        result['active_actions_preserved']=sorted(active)
        for action in list(bpy.data.actions):
            if action.name not in keep:bpy.data.actions.remove(action)
    omit={'ext3_6664043e5c5bc3':{'Sphere'},'ext3_29e41a305cd84c':{'boot3_shadow'},'ext3_94be31d26c08d8':{'Cone','Hologram'}}.get(j['key'],set())
    result['omitted_preview_objects']=[o.name for o in bpy.context.scene.objects if o.name in omit]
    for o in list(bpy.context.scene.objects):
        if o.name in omit:bpy.data.objects.remove(o,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
    if not meshes:raise ValueError('No mesh objects')
    # Repair stale absolute texture paths by exact basename within this package.
    texture_files={p.name.casefold():p for p in pathlib.Path(j['root']).rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.tga','.dds','.bmp','.webp','.tif','.tiff'}}
    missing=[]
    for image in bpy.data.images:
        if image.source!='FILE' or image.packed_file:continue
        if pathlib.Path(bpy.path.abspath(image.filepath)).exists():continue
        name=pathlib.PurePosixPath(image.filepath.replace('\\','/')).name.casefold()
        replacement=texture_files.get(name)
        if not replacement:
            replacement=next((p for n,p in texture_files.items() if n==name+'.png' or n==name+'.jpg'),None)
        if not replacement:
            replacement=next((p for p in texture_files.values() if p.stem.casefold()==pathlib.Path(name).stem.casefold()),None)
        if not replacement:
            # Documented material-to-texture aliases in the Darksiders source packages.
            alias=name.replace('m_abaddon_','t_dragon_').replace('m_lilith_','t_lilitha')
            if alias!=name:replacement=next((p for n,p in texture_files.items() if n==alias+'_diff.tga.png'),None)
            elif name.endswith('_inst'):replacement=texture_files.get(name[:-5]+'_d.png')
        if not replacement:
            label=pathlib.Path(name).stem
            aliases={
                'm_trauma_body':'trauma_body_diff.png','m_trauma_body_cloth':'trauma_body_diff.png','m_trauma_head':'trauma_head_diff.png',
                'm_taskmaster_01':'t_taskmaster_diff.png','m_taskmaster_02':'t_taskmaster_diff.png','m_taskmaster_hammer':'t_taskmaster_hammer_diff.png','m_taskmaster_sword':'t_taskmaster_sword_diff.png',
                'ruin_inst_armor_a':'ruin_armor_a_d.png','ruin_inst_body_a':'ruin_body_a_d.png','ruin_inst_hair_a':'ruin_hair_d.png',
                'angelofdeath':'angelofdeath2.jpg',
            }
            replacement=texture_files.get(aliases.get(label,''))
        if not replacement and (match:=re.search(r'drago_(\d{4})_(diffuse|metallic|normal)',name)):
            tile,channel=match.groups();channel={'diffuse':'basecolor','metallic':'metallic','normal':'normal'}[channel]
            replacement=next((p for n,p in texture_files.items() if ('_'+channel) in n and ('.'+tile+'.') in n),None)
        if replacement:
            image.filepath=str(replacement)
            try:image.reload()
            except Exception:missing.append(image.name)
        else:missing.append(image.name)
    # Some FBX exporters keep the textures but omit their material connections.
    # Reconnect only base-color candidates whose names identify the material/atlas.
    def norm(s):return re.sub('[^a-z0-9]','',s.casefold())
    base_candidates=[]
    for path in texture_files.values():
        stem=path.stem.casefold()
        matched=re.search(r'(?i)(.*?)(?:_base_?colou?r|_diffuse|_diff|_color|_d)(?:\.\d{4})?$',stem)
        if matched:base_candidates.append((path,norm(matched[1])))
        elif stem in {'color','basecolor'}:base_candidates.append((path,''))
        elif re.fullmatch(r'abomination(?:_cloth)?_\d{4}',stem):base_candidates.append((path,norm(stem)))
    repaired=[]
    for mat in {s.material for o in meshes for s in o.material_slots if s.material}:
        if not mat.use_nodes:mat.use_nodes=True
        shader=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if not shader:continue
        socket=shader.inputs['Base Color'];linked=socket.links[0].from_node if socket.is_linked else None
        if linked and linked.type=='TEX_IMAGE' and linked.image and linked.image.size[0]>0:continue
        material_name=re.sub(r'\.\d{3}$','',mat.name).casefold();mn=norm(material_name)
        matches=[(p,k) for p,k in base_candidates if k and len(k)>=6 and (k in mn or mn in k)]
        if material_name.startswith('mi_1056501_'):
            prefix=material_name.replace('mi_','t_',1)
            if '_hair_' in prefix:prefix='t_1056501_hair'
            if '_eyes_' in prefix:prefix='t_1056501_head'
            exact=texture_files.get(prefix+'_d.png')
            if exact:matches=[(exact,prefix)]
        if not matches and len(base_candidates)==1 and not base_candidates[0][1]:matches=base_candidates
        if not matches:continue
        path=max(matches,key=lambda item:len(item[1]))[0]
        node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.label='Recovered source base color';node.image=bpy.data.images.load(str(path),check_existing=False)
        mat.node_tree.links.new(node.outputs['Color'],socket);repaired.append({'material':mat.name,'texture':path.name})
    result['reconnected_materials']=repaired
    used_images={n.image for mat in {s.material for o in meshes for s in o.material_slots if s.material} if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and any(output.is_linked for output in n.outputs)}
    missing=[im.name for im in used_images if not im.size[0]]
    bpy.context.view_layer.update()
    result.update(meshes=len(meshes),vertices=sum(len(o.data.vertices) for o in meshes),triangles=sum(sum(max(len(p.vertices)-2,0) for p in o.data.polygons) for o in meshes),armatures=sum(o.type=='ARMATURE' for o in bpy.context.scene.objects),bones=sum(len(o.data.bones) for o in bpy.context.scene.objects if o.type=='ARMATURE'),actions=[a.name for a in bpy.data.actions],materials=len({s.material.name for o in meshes for s in o.material_slots if s.material}),images=len(bpy.data.images),missing_images=missing)
    # Keep original dimensions and skeleton; scene cameras and lights are not part of the asset.
    for o in list(bpy.context.scene.objects):
        if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
    result['animation_export_enabled']=j.get('export_animations',True)
    if j.get('narrow_animation_sampling'):
        # Stock Blender samples the union of every action's timeline for EACH take.
        # For a single armature with no other animated objects/drivers/shapekeys,
        # each take needs only its own declared range. Keyframes/times stay untouched.
        import hashlib
        from io_scene_gltf2.blender.exp.animation.sampled import sampling_cache
        animated=[o for o in bpy.context.scene.objects if o.animation_data and (o.animation_data.action or len(o.animation_data.drivers) or len(o.animation_data.nla_tracks))]
        if len(animated)!=1 or animated[0].type!='ARMATURE' or len(animated[0].animation_data.drivers) or bpy.data.shape_keys:
            raise ValueError('Narrow sampling requires one armature, no other animated objects, drivers or shape keys')
        original_range=sampling_cache.get_range;seen_ranges=set()
        def exact_action_range(obj_uuid,key,settings):
            entry=settings.get('ranges',{}).get(obj_uuid,{}).get(key)
            if entry and settings['gltf_animation_mode']=='ACTIONS':
                if key not in seen_ranges:print('ACTION_SAMPLING '+str(key)+' '+str(entry['start'])+' '+str(entry['end']),flush=True);seen_ranges.add(key)
                return entry['start'],entry['end']
            return original_range(obj_uuid,key,settings)
        sampling_cache.get_range=exact_action_range
        result['sampling_optimization']={'mode':'single-armature-per-action-range','keyframes_modified':False,'source_times_modified':False,'blender_gltf_sampling_source_sha256':hashlib.sha256(pathlib.Path(sampling_cache.__file__).read_bytes()).hexdigest(),'validation_required':'Compare shared clips and geometry against unmodified exporter output'}
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_animations=result['animation_export_enabled'],export_yup=True,export_cameras=False,export_lights=False,use_visible=True,use_renderable=True)
    # Render the exported representation, so the thumbnail matches the web viewer.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
    bpy.context.view_layer.update()
    points=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
    if not all(math.isfinite(v) for v in (*lo,*hi)):raise ValueError('Non-finite bounds')
    center=(lo+hi)/2;scale=max(max(hi-lo),.01)
    result['bounds_blender']=[list(lo),list(hi)]
    bpy.ops.object.camera_add(location=center+Vector((1,-2.8,.65)).normalized()*scale*3)
    cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO'
    rot=cam.rotation_euler.to_matrix().transposed();ps=[rot@(p-center) for p in points]
    cam.data.ortho_scale=max(max(p.y for p in ps)-min(p.y for p in ps),(max(p.x for p in ps)-min(p.x for p in ps))*420/384,.02)*1.16
    cam.data.clip_start=max(scale*.0001,.00001);cam.data.clip_end=scale*30
    scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.world=bpy.data.worlds.new('External asset studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.22,.27,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    for direction,energy in [((1,-3,4),450),((-3,-1,2),260),((1,3,3),380)]:
        bpy.ops.object.light_add(type='AREA',location=center+Vector(direction)*scale)
        light=bpy.context.object;light.data.energy=energy*scale*scale;light.data.shape='DISK';light.data.size=scale*3;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    scene.view_settings.view_transform='Standard';scene.render.resolution_x=384;scene.render.resolution_y=420;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'thumbnail.png')
    bpy.ops.render.render(write_still=True)
    result['status']='ready'
except Exception as e:result.update(status='failed',error=str(e),traceback=traceback.format_exc())
(out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('ASSET_RESULT '+json.dumps({k:v for k,v in result.items() if k in ['key','status','error','triangles','bones']},ensure_ascii=True),flush=True)
