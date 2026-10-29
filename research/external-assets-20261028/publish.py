import pathlib,json,struct,collections,csv,re,hashlib,sys
from inventory import OUT

CAT=pathlib.Path(r'E:\l2-local\research\model-catalog');BATCH='Assets externos · Tanda 3'

def glb_data(p):
    with p.open('rb') as f:
        head=f.read(20);magic,version,total,length,kind=struct.unpack('<4s4I',head)
        if magic!=b'glTF' or kind!=0x4E4F534A:raise ValueError('Invalid GLB')
        return json.loads(f.read(length))

def classification(name):
    name=name.lower()
    if any(x in name for x in ['building','house','cottage','church','shrine','tavern','ancient-ruin','medieval-town','worlds-end']):return 'Escenarios','scene',['Escenario']
    if any(x in name for x in ['sword','bounty-contract','robotic-arm','robotic-eye','airship','sentinel-ship','gun','smg','blaster','cannon','flamethrower','weapon','plants']):return 'Objetos','object',['Objeto']
    if any(x in name for x in ['dragon','demon','abomination','demogorgon','golem','infection','archangel','fallen-angel','mimic','two-headed','lilith','taskmaster','trauma','human-deer','bodyhighjacker','scary-guy','arachnida','monstrosity','abyssal','leocetus','zeromus','maw.zip']):return 'Monstruos','monster',['Criatura externa']
    if any(x in name for x in ['cat','dog','wolf','horse','despair','ruin-darksiders']):return 'Personalizados','creature',['Criatura externa']
    return 'NPC','npc',['Personaje externo']

def main():
    inventory=json.loads((OUT/'inventory.json').read_text('utf-8'))['records'];sources=json.loads((OUT/'sources.json').read_text('utf-8'))
    current=json.loads((CAT/'gallery.json').read_text('utf-8'));existing_by_key={m['key']:m for m in current['models']}
    active_batch=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--batch=')),None)
    entries=[];rows=[];seen={};counts=collections.Counter()
    for r in inventory:
        if r['status']!='source_ready':continue
        source=sources.get(r['file'],r.get('origin',{}));uid=source.get('model_uid')
        if uid and uid in seen:
            aliases=seen[uid]['source']['duplicate_archives']
            if r['file'] not in aliases:aliases.append(r['file'])
            r['duplicate_of']=seen[uid]['key'];counts['duplicates']+=1;continue
        dest=CAT/'exports/external-assets-3'/r['key'];ap=dest/'analysis.json'
        a=json.loads(ap.read_text('utf-8')) if ap.exists() else {'status':'pending','error':'Conversión pendiente o formato no compatible'}
        ready=a.get('status')=='ready' and (dest/'model.glb').exists() and (dest/'thumbnail.png').exists()
        title=source.get('title') or pathlib.Path(r['file']).stem.replace('-',' ').title()
        category,role,types=classification(r['file']);facts={k:a.get(k,0) for k in ['triangles','vertices','bones','armatures','meshes']}
        g=glb_data(dest/'model.glb') if ready else {}
        facts.update(animations=len(g.get('animations',[])),animation_names=[v.get('name','Sin nombre') for v in g.get('animations',[])],source_actions=len(a.get('actions',[])),animation_export_enabled=a.get('animation_export_enabled',True),omitted_preview_objects=a.get('omitted_preview_objects',[]),reconnected_materials=a.get('reconnected_materials',[]),materials=len(g.get('materials',[])),images=len(g.get('images',[])),format=pathlib.Path(a.get('input',r['models'][0])).suffix.lower(),missing_images=a.get('missing_images',[]))
        textured=sum(bool(v.get('pbrMetallicRoughness',{}).get('baseColorTexture') or v.get('normalTexture') or v.get('emissiveTexture')) for v in g.get('materials',[]))
        review='pending' if a.get('missing_images') or (r.get('textures',0)>0 and not textured) else 'complete' if facts['images'] else 'flat_color'
        text={'pending':'Hay referencias de texturas pendientes de reparar','complete':'Texturas incluidas en la vista previa','flat_color':'Vista sin texturas de imagen'}[review]
        license=source.get('license') or {}
        public_source={k:source[k] for k in ['site','url','author','author_url','model_uid','tags'] if source.get(k)}
        public_source.update(license_label=license.get('label','Sin licencia identificada'),license_url=license.get('url'),archive=r['file'],duplicate_archives=[])
        m={'key':r['key'],'mesh':'ExternalAssets.'+r['key'],'package':'Assets externos','title':title,'names':[title,pathlib.Path(r['file']).stem],'category':category,'catalog_role':role,'types':types,'npcs':[],'npc_count':0,'batch':BATCH,'external_source':True,'external_asset':True,'preview_only':True,'status':'ready' if ready else 'failed','source':public_source,'asset_analysis':facts,'material_count':facts['materials'],'textured_materials':textured,'material_review':{'status':review,'text':text,'missing_slots':a.get('missing_images',[])},'note':'Recurso externo para explorar y catalogar. Adaptación al cliente de Interlude pendiente.' if ready else a.get('error','Conversión pendiente')}
        if not facts['animation_export_enabled']:m['note']+=' Vista en pose base: la exportación de animaciones de este recurso superó el límite de procesamiento; el original se conserva.'
        if facts['omitted_preview_objects']:m['note']+=' Se omiten objetos auxiliares o efectos de la vista: '+', '.join(facts['omitted_preview_objects'])+'.'
        visual_notes={
            'abomination-doom-the-dark-ages-rigged.zip':'La pose base necesita revisión antes de reutilizar el rig.',
            'witch-doom-the-dark-ages-rigged.zip':'La pose base aparece plegada; revisar el rig y su pose de enlace.',
            'worlds-end-inn.zip':'La vista importada parece plana; no se validó como edificio tridimensional completo.',
            'angel-of-death-from-hellboy-2-statue-scan.zip':'La malla importada es un busto; comprobar su correspondencia con el título de la publicación.',
            'serephina.zip':'La pose importada presenta deformaciones y una vista base poco visible. El rig y sus componentes requieren revisión antes de reutilizarlo.',
            'reaper-aa-gun.zip':'Los componentes y las transparencias requieren revisión visual; la vista actual no representa un arma ensamblada validada.',
            'ulquiorra-cifer.zip':'Revisar la orientación de la pose base antes de usarlo como personaje.',
            'beyond-resurreccion-grimmjow.zip':'Revisar la orientación de la pose base; sus clips se conservan sin certificar el resultado en otro esqueleto.',
        }
        if r['file'] in visual_notes:m.update(preview_review={'status':'partial','text':visual_notes[r['file']]});m['note']+=' '+visual_notes[r['file']]
        m['batch']=r.get('batch',BATCH)
        if not ready and a.get('status')=='pending':m['status']='pending'
        if ready:m.update(gltf=(dest/'model.glb').relative_to(CAT).as_posix(),thumbnail=(dest/'thumbnail.png').relative_to(CAT).as_posix())
        revision=a.get('texture_revision');old=existing_by_key.get(r['key'],{})
        if ready and revision and hashlib.sha256((dest/'model.glb').read_bytes()).hexdigest()==revision.get('after_sha256'):
            m['material_review']=a.get('current_material_review') or old.get('material_review',m['material_review'])
            m['textured_materials']=old.get('textured_materials',m['textured_materials'])
            if a.get('current_preview_review') or old.get('preview_review'):m['preview_review']=a.get('current_preview_review') or old['preview_review']
            m['asset_analysis']['missing_images']=m['material_review'].get('missing_slots',[])
        if active_batch and r['key'] in existing_by_key and existing_by_key[r['key']].get('batch')!=active_batch:m=existing_by_key[r['key']]
        review=m['material_review']['status']
        entries.append(m)
        if uid:seen[uid]=m
        counts['ready' if ready else 'pending']+=1
        rows.append({'archivo':r['file'],'nombre':title,'estado':'Vista 3D disponible' if ready else 'Pendiente','formato':facts['format'],'triangulos':facts['triangles'],'huesos':facts['bones'],'animaciones':facts['animations'],'texturas':review,'autor':source.get('author',''),'licencia':public_source['license_label'],'origen':source.get('url',''),'key':r['key']})
    previous={m['key']:m for m in current['models'] if not (m.get('external_asset') and m['key'].startswith('ext3_') and m.get('batch','').startswith('Assets externos · Tanda '))}
    old_entries={m['key']:m for m in current['models']}
    for m in entries:
        technical=old_entries.get(m['key'],{}).get('rig_analysis')
        if technical and m.get('gltf') and hashlib.sha256((CAT/m['gltf']).read_bytes()).hexdigest()==technical.get('artifact_sha256'):m['rig_analysis']=technical
        previous[m['key']]=m
    current['models']=list(previous.values())
    temp=CAT/'gallery.external-assets.tmp';temp.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(CAT/'gallery.json')
    (OUT/'catalog-entries.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'INVENTARIO.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (OUT/'summary.json').write_text(json.dumps(dict(counts),indent=2),encoding='utf-8')
    (OUT/'inventory.json').write_text(json.dumps({'records':inventory},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(counts)))

if __name__=='__main__':main()
