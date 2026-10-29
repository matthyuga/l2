"""Download complete public texture catalogs in 2K from Poly Haven / ShareTextures."""
import argparse, concurrent.futures, hashlib, json, pathlib, re, time, urllib.request, xml.etree.ElementTree as ET, zipfile, shutil
from PIL import Image
from download import ROOT, fetch, atomic_json

HEADERS={'User-Agent':'Mozilla/5.0 (compatible; L2LabTextureLibrary/1.0; public CC0 asset download)'}
DEST=ROOT.parent/'model-catalog'/'exports'/'cc0-textures'
TRANSLATIONS={'Stone':'Piedra','Brick & Block':'Ladrillos y bloques','Ground & Terrain':'Suelos y terrenos','Wood':'Madera','Concrete':'Hormigón','Textiles & Leather':'Telas y cuero','Ceramic':'Cerámica','Metal':'Metal','Asphalt & Bitumen':'Asfalto','Organic':'Orgánicos','Plastic & Rubber':'Plástico y goma','Paper & Card':'Papel y cartón','Nature':'Naturaleza','Abstract':'Abstractos','Ground':'Terrenos','Fabric':'Tela','Leather':'Cuero','Bricks':'Ladrillos','Roof':'Tejados','Tiles':'Baldosas','Marble':'Mármol','Carpet':'Alfombras','Rock':'Rocas','Plaster':'Revoque','Plastic':'Plástico'}

def read_url(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=35) as r:return r.read()
        except Exception:
            if attempt==3:raise
            time.sleep(2**attempt*2)

def safe_name(value):return re.sub('[^A-Za-z0-9_-]+','_',value).strip('_') or 'texture'

def image_info(file):
    with Image.open(file) as im:im.verify()
    with Image.open(file) as im:return list(im.size)

def finish(provider,ident,original,category,color,maps,source,extra):
    folder=DEST/provider/ident
    file=ROOT.parent/'model-catalog'/color
    resolution=image_info(file)
    with Image.open(file) as im:im.thumbnail((160,160));im.convert('RGB').save(folder/'preview.jpg',quality=85)
    prefix='ph_' if provider=='polyhaven' else 'st_'
    category=TRANSLATIONS.get(category,category)
    result={'id':prefix+ident,'title':category+' · '+original,'original':original,'category':category,'path':color,'thumbnail':(folder/'preview.jpg').relative_to(ROOT.parent/'model-catalog').as_posix(),'resolution':resolution,'maps':maps,'provider':'Poly Haven' if provider=='polyhaven' else 'ShareTextures','license':'CC0-1.0','licenseUrl':'https://polyhaven.com/license' if provider=='polyhaven' else 'https://www.sharetextures.com/about','source':source,**extra}
    atomic_json(folder/'source.json',result)
    return result

def existing(provider,ident):
    file=DEST/provider/ident/'source.json'
    if file.exists():
        try:
            record=json.loads(file.read_text(encoding='utf8'))
            if all((ROOT.parent/'model-catalog'/p).is_file() for p in record['maps'].values()):return record
        except Exception:pass

def polyhaven(job):
    ident,meta=job
    if not re.fullmatch('[a-zA-Z0-9_-]+',ident):raise ValueError('Invalid ID')
    result=existing('polyhaven',ident)
    if result:return result
    folder=DEST/'polyhaven'/ident;folder.mkdir(parents=True,exist_ok=True)
    metadata=folder/'files.json'
    if metadata.exists():files=json.loads(metadata.read_text(encoding='utf8'))
    else:
        files=json.loads(read_url('https://api.polyhaven.com/files/'+ident));atomic_json(metadata,files)
    maps={};checksums={};bytes_total=0
    for kind in ['Diffuse','diffuse','nor_gl','nor_dx','Rough','rough','AO','Displacement','Metal','metal','Opacity','Mask']:
        options=files.get(kind,{}).get('2k',{})
        chosen=options.get('jpg') or options.get('png')
        if not chosen:continue
        url=chosen['url']
        if not url.startswith('https://dl.polyhaven.org/'):raise ValueError('Unexpected asset host')
        target=folder/(safe_name(kind)+pathlib.PurePosixPath(url).suffix)
        fetch(url,target,chosen.get('size'))
        md5=hashlib.md5(target.read_bytes()).hexdigest()
        if chosen.get('md5') and md5!=chosen['md5']:
            target.unlink();raise ValueError('Provider checksum mismatch; retry required')
        image_info(target);maps[kind]=target.relative_to(ROOT.parent/'model-catalog').as_posix();checksums[kind]=md5;bytes_total+=target.stat().st_size
    color=maps.get('Diffuse') or maps.get('diffuse')
    if not color:raise ValueError('No public 2K diffuse map')
    return finish('polyhaven',ident,meta['name'],meta.get('category','Other').split('/')[0],color,maps,'https://polyhaven.com/a/'+ident,{'tags':meta.get('tags',[]),'authors':meta.get('authors',{}),'downloadBytes':bytes_total,'md5':checksums})

def sharetextures(url):
    ident=url.rstrip('/').split('/')[-1]
    if not re.fullmatch('[a-zA-Z0-9_-]+',ident):raise ValueError('Invalid ID')
    result=existing('sharetextures',ident)
    if result:return result
    folder=DEST/'sharetextures'/ident;folder.mkdir(parents=True,exist_ok=True)
    metadata=folder/'item.json'
    if metadata.exists():item=json.loads(metadata.read_text(encoding='utf8'))
    else:
        html=read_url(url).decode('utf8');match=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',html,re.S)
        if not match:raise ValueError('Public item metadata missing')
        data=json.loads(match.group(1))['props']['pageProps'];item=data['itemDetail']['data'];atomic_json(metadata,item)
    link=next((x for x in item.get('downloadLinks',[]) if x.get('title','').strip().upper().replace(' ','') in ['2K','2K-JPG','2KPNG']),None)
    if not link:raise ValueError('No public 2K ZIP link (manual resolution/account review required)')
    download=link['value']
    if not download.startswith('https://files.sharetextures.com/'):raise ValueError('2K link requires a different/manual download provider')
    archives=ROOT/'sharetextures'/'archives';archives.mkdir(parents=True,exist_ok=True)
    archive=archives/(ident+'_2K.zip');fetch(download,archive)
    maps={};color=None
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError('ZIP CRC failed')
        for i,m in enumerate(z.infolist()):
            if m.is_dir():continue
            # Keep the original bundle; extract images under sanitized names for the local web server.
            suffix=pathlib.PurePosixPath(m.filename).suffix.lower()
            if suffix not in ['.png','.jpg','.jpeg','.tif','.tiff','.exr']:continue
            target=folder/(str(i)+'_'+safe_name(pathlib.PurePosixPath(m.filename).stem)+suffix)
            with z.open(m) as src,target.open('wb') as out:shutil.copyfileobj(src,out)
            name=pathlib.PurePosixPath(m.filename).stem
            if suffix in ['.png','.jpg','.jpeg']:
                image_info(target);relative=target.relative_to(ROOT.parent/'model-catalog').as_posix();maps[name]=relative
                if re.search(r'diff|albedo|base.?color|(?:^|[_ -])colou?r(?:[_ -]|$)',name,re.I):color=relative
    if not color:raise ValueError('Bundle downloaded; color map could not be identified automatically')
    return finish('sharetextures',ident,item['title'],item.get('category',{}).get('name','Other'),color,maps,url,{'tags':[t.get('text','') for t in item.get('tags',[])],'download':download,'archiveBytes':archive.stat().st_size,'archive':'sharetextures/archives/'+archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('provider',choices=['polyhaven','sharetextures']);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--limit',type=int);args=parser.parse_args()
    provider=args.provider;output=ROOT/provider;output.mkdir(exist_ok=True)
    if provider=='polyhaven':
        catalog=ROOT/'polyhaven-catalog.json'
        if not catalog.exists():catalog.write_bytes(read_url('https://api.polyhaven.com/assets?t=textures'))
        jobs=list(json.loads(catalog.read_text(encoding='utf8')).items());worker=polyhaven
    else:
        sitemap=ROOT/'share-sitemap.xml'
        if not sitemap.exists():sitemap.write_bytes(read_url('https://www.sharetextures.com/sitemap_assets.xml'))
        tree=ET.fromstring(sitemap.read_bytes());jobs=list(dict.fromkeys(a.text for a in tree.findall('{*}url/{*}loc') if '/textures/' in a.text or '/atlases/' in a.text));worker=sharetextures
    if args.limit:jobs=jobs[:args.limit]
    results=[];pending=[];errors=[];started=time.time()
    for j in jobs:
        ident=j[0] if provider=='polyhaven' else j.rstrip('/').split('/')[-1]
        result=existing(provider,ident)
        if result:results.append(result)
        else:pending.append(j)
    def publish():
        atomic_json(output/'catalog.json',sorted(results,key=lambda r:r['id']))
        atomic_json(output/'progress.json',{'provider':provider,'complete':len(results),'total':len(jobs),'failed':errors,'downloadBytes':sum(r.get('archiveBytes',r.get('downloadBytes',0)) for r in results),'elapsedSeconds':round(time.time()-started),'finished':len(results)+len(errors)==len(jobs)})
    publish();print(provider,'PLAN',len(jobs),'materials',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.workers,8))) as pool:
        futures={pool.submit(worker,j):j for j in pending}
        for future in concurrent.futures.as_completed(futures):
            job=futures[future]
            try:results.append(future.result())
            except Exception as e:errors.append({'id':job[0] if provider=='polyhaven' else job,'error':str(e)})
            publish();print(provider,len(results),'/',len(jobs),'OK;',len(errors),'failed',flush=True)
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
