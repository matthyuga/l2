"""Inventory downloaded packages without changing the originals; unpack ZIP sources safely."""
import pathlib, zipfile, hashlib, json, re, collections, urllib.parse, shutil

ROOT=pathlib.Path(r'E:\l2-local\descarga de assets')
OUT=pathlib.Path(__file__).resolve().parent
MODELS={'.glb','.gltf','.fbx','.blend','.obj','.dae','.stl','.ply','.usd','.usdz','.abc'}
TEXTURES={'.png','.jpg','.jpeg','.tga','.dds','.webp','.bmp','.tif','.tiff'}

def unpack(archive, dest, depth=0):
    if depth>4: return
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if sum(x.file_size for x in z.infolist())>4*1024**3: raise ValueError('Unpacked package exceeds 4 GiB')
        for info in z.infolist():
            name=info.filename.replace('\\','/')
            target=(dest/name).resolve()
            if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe archive path')
            if info.is_dir():target.mkdir(parents=True,exist_ok=True);continue
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists() or target.stat().st_size!=info.file_size:
                with z.open(info) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
    for p in list(dest.rglob('*.zip')):
        if not any('unpacked_' in x for x in p.relative_to(dest).parts):unpack(p,p.parent/('unpacked_'+p.stem),depth+1)

def origin(p):
    # Only retain a public page/model identifier, never signed download query strings.
    try:s=pathlib.Path(str(p)+':Zone.Identifier').read_text(errors='replace')
    except OSError:return {}
    m=re.search(r'/archives/([a-f0-9]{32})/',s)
    if m:return {'site':'Sketchfab','model_uid':m[1],'url':'https://sketchfab.com/3d-models/'+m[1]}
    m=re.search(r'ReferrerUrl=(https?://[^\r\n]+)',s)
    return {'site':urllib.parse.urlparse(m[1]).netloc,'url':m[1].split('?')[0]} if m else {}

def main():
    records=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.zip','.rar','.7z','.glb'}:continue
        rel=p.relative_to(ROOT).as_posix(); key='ext3_'+hashlib.sha256(rel.encode()).hexdigest()[:14]
        record={'key':key,'file':rel,'bytes':p.stat().st_size,'origin':origin(p),'status':'inventoried'}
        if p.parent!=ROOT:
            record['status']='supporting_assets';records.append(record);continue
        if p.suffix.lower()=='.zip':
            dest=OUT/'unpacked'/key
            try:
                unpack(p,dest)
                files=[x for x in dest.rglob('*') if x.is_file()]
                record.update(root=str(dest),models=[str(x.relative_to(dest)) for x in files if x.suffix.lower() in MODELS],textures=sum(x.suffix.lower() in TEXTURES for x in files),documents=[str(x.relative_to(dest)) for x in files if x.suffix.lower() in {'.txt','.md','.pdf'}])
                record['status']='source_ready' if record['models'] else 'no_supported_model'
            except Exception as e:record.update(status='extract_failed',error=str(e))
        elif p.suffix.lower()=='.glb':record.update(status='personal_existing',models=[str(p)])
        else:record['status']='native_or_other_archive'
        records.append(record)
    (OUT/'inventory.json').write_text(json.dumps({'source':str(ROOT),'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'packages':len(records),'status':collections.Counter(r['status'] for r in records),'ready':[{k:r[k] for k in ['file','key','models','textures']} for r in records if r['status']=='source_ready']},ensure_ascii=True),flush=True)

if __name__=='__main__':main()
