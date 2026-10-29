"""Inspect material declarations without animation import or source modification."""
import bpy,pathlib,json,sys,hashlib,re,traceback,gc
OUT=pathlib.Path(__file__).resolve().parent;(OUT/'sources').mkdir(exist_ok=True);(OUT/'packed').mkdir(exist_ok=True)
sys.path.insert(0,str(pathlib.Path(bpy.utils.script_path_user() or '.')))

def decode(v):return v.decode('utf-8',errors='replace').split('\x00')[0] if isinstance(v,bytes) else v
def raw_fbx(path):
    try:
        from io_scene_fbx import parse_fbx
        root,version=parse_fbx.parse(str(path));objects=next(e for e in root.elems if e.id==b'Objects');connections=next(e for e in root.elems if e.id==b'Connections')
        objs={int(e.props[0]):e for e in objects.elems if e.props and isinstance(e.props[0],int)};mats={i:decode(e.props[1]) for i,e in objs.items() if e.id==b'Material'};relations=[]
        for c in connections.elems:
            if c.id!=b'C' or len(c.props)<3:continue
            kind,src,dst,*property=c.props
            if dst not in mats or src not in objs or objs[src].id not in {b'Texture',b'LayeredTexture'}:continue
            texture=objs[src];paths=[]
            for e in texture.elems:
                if e.id in {b'FileName',b'RelativeFilename'} and e.props:paths.append(decode(e.props[0]))
            for vc in connections.elems:
                if vc.id==b'C' and len(vc.props)>=3 and vc.props[2]==src and vc.props[1] in objs:
                    video=objs[vc.props[1]]
                    if video.id==b'Video':
                        for e in video.elems:
                            if e.id in {b'Filename',b'FileName',b'RelativeFilename'} and e.props:paths.append(decode(e.props[0]))
            relations.append({'material':mats[dst],'texture':decode(texture.props[1]),'property':decode(property[0]) if property else None,'filenames':list(dict.fromkeys(paths))})
        return {'binary_version':version,'relations':relations}
    except Exception as e:return {'limitations':['Raw FBX parser: '+str(e)]}

def upstream(socket,seen=None):
    seen=set(seen or []);images=[]
    for link in socket.links:
        node=link.from_node
        if node.as_pointer() in seen:continue
        seen.add(node.as_pointer())
        if node.type=='TEX_IMAGE' and node.image:images.append(node.image)
        else:
            for s in node.inputs:
                if s.is_linked:images.extend(upstream(s,seen))
    return list({i.name:i for i in images}.values())

slots=['Base Color','Metallic','Roughness','Normal','Emission Color','Emission Strength','Alpha']
for job in json.loads((OUT/'jobs.json').read_text('utf-8')):
    target=OUT/'sources'/(job['key']+'.json')
    if target.exists():continue
    src=pathlib.Path(job['source']);report={'key':job['key'],'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'authority':'source-material-declaration','blender_version':bpy.app.version_string}
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if src.suffix.lower()=='.fbx':
            report['fbx']=raw_fbx(src)
            try:bpy.ops.import_scene.fbx(filepath=str(src),use_anim=False,use_image_search=False)
            except RuntimeError:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.fbx_import(filepath=str(src),use_anim=False)
        elif src.suffix.lower()=='.obj':bpy.ops.wm.obj_import(filepath=str(src))
        elif src.suffix.lower()=='.blend':bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
        report['materials']=[];image_report={}
        used={s.material for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() for s in o.material_slots if s.material}
        for mat in used:
            shader=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
            record={'name':mat.name,'slots':{}}
            if shader:
                for name in slots:
                    socket=shader.inputs.get(name)
                    if not socket:continue
                    images=upstream(socket)
                    value=socket.default_value
                    record['slots'][name]={'linked':socket.is_linked,'direct_node':socket.links[0].from_node.type if socket.is_linked else None,'images':[im.name for im in images],'value':list(value) if hasattr(value,'__len__') else value}
                    for im in images:
                        info={'name':im.name,'filepath':im.filepath,'source':im.source,'size':list(im.size),'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name}
                        if im.packed_file and im.packed_file.size>128:
                            data=bytes(im.packed_file.data);sha=hashlib.sha256(data).hexdigest();ext=pathlib.Path(im.filepath).suffix.lower() or '.bin';packed=OUT/'packed'/(sha+ext)
                            if not packed.exists():packed.write_bytes(data)
                            info.update(packed_path=str(packed),packed_sha256=sha)
                        image_report[im.name]=info
            report['materials'].append(record)
        report['images']=image_report;report['status']='inspected'
    except Exception as e:report.update(status='failed',error=str(e),traceback=traceback.format_exc())
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('MATERIAL_SOURCE '+json.dumps({'key':job['key'],'status':report['status'],'materials':len(report.get('materials',[]))},ensure_ascii=True),flush=True);gc.collect()
