"""Extract read-only native resources and prepare a portable gallery with representative textures."""
from pathlib import Path
import argparse, collections, json, re, subprocess, os

ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; CLIENT=ROOT.parent/'l2'
UMODEL=ROOT/'research/amber-l2/tools/umodel.exe'
EXPORT=OUT/'exports'; EXPORT.mkdir(exist_ok=True)
LOGS=OUT/'build-logs'; LOGS.mkdir(exist_ok=True)
OPTIONS=['-game=l2','-path='+str(CLIENT)]
texture_cache={}; cache_file=OUT/'texture-cache.json'
if cache_file.exists(): texture_cache={k:v for k,v in json.loads(cache_file.read_text(encoding='utf-8')).items() if v and (OUT/v.get('file','')).is_file()}

def run(args):
    p=subprocess.run([str(UMODEL),*args,*OPTIONS],capture_output=True,text=True,errors='replace',timeout=100)
    if p.returncode: raise RuntimeError((p.stderr+'\n'+p.stdout)[-1500:])
    return p.stdout+'\n'+p.stderr

def texture(ref, seen=None):
    seen=set() if seen is None else seen
    key=ref.lower()
    if key in seen or '.' not in ref: return None
    if key in texture_cache: return texture_cache[key]
    seen.add(key); package, obj=ref.split('.',1); obj=obj.split('.')[-1]
    try:
        info=run(['-dump','-noanim','-nomesh','-nostat',package,obj])
        kind=re.search(r'ClassName:\s*(\S+)',info)
        if kind and kind[1]=='Texture':
            data=run(['-export','-png','-noanim','-nomesh','-nostat','-out='+str(EXPORT),package,obj])
            candidates=list(EXPORT.glob('*/Texture/'+obj+'.png'))
            found=next((p for p in candidates if p.parents[1].name.lower()==package.lower()),None)
            if not found: raise ValueError('No exported PNG: '+ref)
            result={'file':str(found.relative_to(OUT)).replace('\\','/'),
            'alpha':bool(re.search(r'bMasked = true',info)), 'source':ref}
        else:
            diffuse=re.search(r'(?:Diffuse|Material|Material1|FallbackMaterial)\s*=\s*\w+\x27([^\x27]+)\x27',info)
            if not diffuse:
                first_texture=next(((name,path) for name,path in re.findall(r'Loading Texture (\S+) from package ([^\r\n]+)',info)),None)
                if first_texture:
                    result=texture(Path(first_texture[1]).stem+'.'+first_texture[0],seen)
                    texture_cache[key]=result
                    return result
            if not diffuse: raise ValueError('No diffuse material: '+ref)
            # UObject dumps use group.object for grouped textures. The load log identifies the actual package.
            child=diffuse[1];child_name=child.split('.')[-1]
            loaded=re.findall(r'Loading \w+ (\S+) from package ([^\r\n]+)',info)
            actual=next((Path(path).stem+'.'+name for name,path in loaded if name.lower()==child_name.lower()),child)
            result=texture(actual,seen)
            if result:
                result=dict(result)
                result['alpha']=bool(re.search(r'AlphaTest = true|OB_Masked|OB_Translucent|OB_Additive',info))
        texture_cache[key]=result
        return result
    except Exception as e:
        texture_cache[key]=None
        with (LOGS/'textures.log').open('a',encoding='utf-8') as f:f.write(ref+': '+str(e)+'\n')
        return None

def prepare(m):
    package,obj=m['mesh'].split('.',1)
    text=run(['-export','-gltf','-noanim','-out='+str(EXPORT),package+'.ukx',obj])
    (LOGS/(m['key']+'.log')).write_text(text,encoding='utf-8')
    files=list(EXPORT.glob('*/SkeletalMesh/'+obj+'.gltf'))+list(EXPORT.glob('*/StaticMesh/'+obj+'.gltf'))
    gltf=next((p for p in files if p.parents[1].name.lower()==package.lower()),None)
    if not gltf: raise ValueError('No exported glTF')
    data=json.loads(gltf.read_text(encoding='utf-8'))
    loaded={name.lower():Path(path).stem+'.'+name for name,path in re.findall(r'Loading \w+ (\S+) from package ([^\r\n]+)',text)}
    override=m['npcs'][0].get('textures',[]) if m['npcs'] else []
    mats=data.get('materials',[]); assigned=0
    data['images']=[]; data['textures']=[]; data['samplers']=[{'wrapS':10497,'wrapT':10497,'magFilter':9729,'minFilter':9987}]
    for i,mat in enumerate(mats):
        slot_match=re.fullmatch(r'dummy_material_(\d+)',mat.get('name',''))
        slot=int(slot_match[1]) if slot_match else i
        ref=override[slot] if slot<len(override) else loaded.get(mat.get('name','').lower())
        tex=texture(ref) if ref else None
        if not tex:
            native=loaded.get(mat.get('name','').lower())
            tex=texture(native) if native and native!=ref else None
        if not tex: continue
        image=len(data['images']); file=OUT/tex['file']; uri=os.path.relpath(file,gltf.parent).replace('\\','/')
        data['images'].append({'uri':uri}); data['textures'].append({'source':image,'sampler':0})
        mat['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':image},'metallicFactor':0,'roughnessFactor':.9}
        mat['doubleSided']=True
        if tex['alpha']:mat['alphaMode']='MASK';mat['alphaCutoff']=tex.get('alpha_cutoff',.35)
        if m.get('self_illuminated'):
            mat.setdefault('extensions',{})['KHR_materials_unlit']={}
            if 'KHR_materials_unlit' not in data.setdefault('extensionsUsed',[]):data['extensionsUsed'].append('KHR_materials_unlit')
        assigned+=1
    if not data['images']:
        for k in ('images','textures','samplers'):data.pop(k,None)
    gltf.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    m.update(gltf=str(gltf.relative_to(OUT)).replace('\\','/'),thumbnail='thumbs/'+m['key']+'.png',status='ready',textured_materials=assigned,material_count=len(mats))
    m.pop('note',None)
    if assigned<len(mats):m['note']='Algunos materiales se muestran sin textura.'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sample',action='store_true');parser.add_argument('--retry',action='store_true');args=parser.parse_args()
    inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
    groups={m['mesh'].lower():dict(m) for m in inventory['models']}
    for p in inventory['native_packages']:
        for name in p['meshes']:
            mesh=p['package']+'.'+name
            groups.setdefault(mesh.lower(),{'mesh':mesh,'package':p['package'],'npc_count':0,'texture_variants':0,'npcs':[]})
    ordered=sorted(groups.values(),key=lambda m:m['mesh'].lower())
    previous={m['mesh'].lower():m for m in json.loads((OUT/'gallery.json').read_text(encoding='utf-8')).get('models',[])} if (OUT/'gallery.json').exists() else {}
    for i,m in enumerate(ordered):
        m['key']='m'+str(i).zfill(4)
        m['category']='Monstruos' if m['package'].lower().startswith('lineagemonsters') else 'NPC' if m['package'].lower().startswith('lineagenpc') else 'Objetos'
        m['names']=list(dict.fromkeys(x.get('name','') for x in m['npcs'] if x.get('name')))
        m['title']=m['names'][0] if m['names'] else m['mesh'].split('.',1)[1]
        m['types']=sorted({x.get('type','') for x in m['npcs'] if x.get('type')})
        old=previous.get(m['mesh'].lower())
        if old:
            for k in ('gltf','thumbnail','status','note','textured_materials','material_count'): 
                if k in old:m[k]=old[k]
    customs=[m for m in previous.values() if m.get('category')=='Personalizados']
    report={'baseline_npc_rows':6519,'model_count':len(ordered)+len(customs),'models':ordered+customs,'preview':'Malla en pose base; materiales y variantes representativos, sin efectos del cliente.'}
    target={'lineagemonsters.gremlin_m00','lineagenpcs.a_traderb_fhuman_m00','lineagemonsters.baium_m00','lineagemonsters2.ahrimanes_m00','lineagemonsters3.cannibal_stakato_leader_tran_m00','lineagenpcsev.azit_contest_pile_e_m00'}
    for i,m in enumerate(ordered):
        if args.sample and m['mesh'].lower() not in target:continue
        if m.get('status')=='ready' and (OUT/m['gltf']).exists() and m.get('textured_materials',0)==m.get('material_count',0):continue
        if m.get('status')=='failed' and not args.retry:continue
        try:prepare(m)
        except Exception as e:m.update(status='failed',error=str(e));print('FAILED '+m['mesh']+' '+str(e)[-200:],flush=True)
        if i%10==0 or args.sample:
            (OUT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            cache_file.write_text(json.dumps(texture_cache,indent=2),encoding='utf-8')
            print('EXTRACT '+str(i+1)+'/'+str(len(ordered))+' '+m['mesh'],flush=True)
    (OUT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    cache_file.write_text(json.dumps(texture_cache,indent=2),encoding='utf-8')
    print('Extraction: '+str(collections.Counter(m.get('status','pending') for m in ordered)),flush=True)
if __name__=='__main__':main()
