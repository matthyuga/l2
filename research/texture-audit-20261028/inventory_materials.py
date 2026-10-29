import pathlib,json,struct,sys,collections
ROOT=pathlib.Path(__file__).resolve().parent;CAT=pathlib.Path(r'E:\l2-local\research\model-catalog')
sys.path.insert(0,r'E:\l2-local\research\external-assets-20261028')
from publish import glb_data

def main():
    catalog=json.loads((CAT/'gallery.json').read_text('utf-8'))['models'];inventory=json.loads(pathlib.Path(r'E:\l2-local\research\external-assets-20261028\inventory.json').read_text('utf-8'))['records'];by={r['key']:r for r in inventory}
    rows=[];jobs=[]
    for m in catalog:
        if not m.get('external_asset') or m.get('status')!='ready':continue
        g=glb_data(CAT/m['gltf']);r=by[m['key']];root=pathlib.Path(r['root']);materials=[]
        for i,mat in enumerate(g.get('materials',[])):
            pbr=mat.get('pbrMetallicRoughness',{});materials.append({'index':i,'name':mat.get('name',''),'base_color_texture':pbr.get('baseColorTexture'),'normal_texture':mat.get('normalTexture'),'metallic_roughness_texture':pbr.get('metallicRoughnessTexture'),'occlusion_texture':mat.get('occlusionTexture'),'emissive_texture':mat.get('emissiveTexture'),'base_color_factor':pbr.get('baseColorFactor',[1,1,1,1]),'alpha_mode':mat.get('alphaMode','OPAQUE')})
        src=pathlib.Path(json.loads((CAT/m['gltf']).with_name('analysis.json').read_text('utf-8'))['input'])
        files=[str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.tga','.dds','.bmp','.tif','.tiff','.webp','.exr'}]
        row={'key':m['key'],'title':m['title'],'gltf':m['gltf'],'source':str(src),'root':str(root),'files':files,'materials':materials,'previous_review':m.get('material_review'),'batch':m['batch']};rows.append(row)
        if src.suffix.lower() in {'.fbx','.obj','.blend'} and (m.get('material_review',{}).get('status')=='pending' or (files and any(not v['base_color_texture'] for v in materials))):jobs.append(row)
    ROOT.mkdir(exist_ok=True)
    (ROOT/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');(ROOT/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'models_audited':len(rows),'materials':sum(len(r['materials']) for r in rows),'source_jobs':len(jobs)}))
if __name__=='__main__':main()
