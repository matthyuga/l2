"""Resumable official ambientCG 2K material downloads for L2 Lab (CC0)."""
import argparse, concurrent.futures, hashlib, json, os, pathlib, re, shutil, socket, threading, time, urllib.request, zipfile
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parent
DEST=ROOT.parent/'model-catalog'/'exports'/'cc0-textures'/'ambientcg'
CATEGORIES={'Grass':'Pasto','Moss':'Musgo','Ground':'Tierra y arena','Gravel':'Grava','Rock':'Piedra','Rocks':'Rocas','Paving Stones':'Adoquines','Bricks':'Ladrillos','Wood':'Madera','Wood Floor':'Piso de madera','Planks':'Tablones','Metal':'Metal','Painted Metal':'Metal pintado','Rust':'Óxido'}
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; L2LabTextureLibrary/1.0; public CC0 asset download)','Referer':'https://ambientcg.com/'}

# Avoid repeated DNS requests for every individual map. No system network settings change.
_resolve=socket.getaddrinfo;_dns={};_dns_lock=threading.Lock()
def cached_resolve(host,port,*args,**kwargs):
    key=(host,port,args,tuple(sorted(kwargs.items())))
    with _dns_lock:
        saved=_dns.get(key)
        if saved and time.monotonic()-saved[0]<300:return saved[1]
        try:result=_resolve(host,port,*args,**kwargs)
        except OSError as e:
            if saved and time.monotonic()-saved[0]<1800:return saved[1]
            raise OSError(str(host)+': '+str(e)) from e
        _dns[key]=(time.monotonic(),result);return result
socket.getaddrinfo=cached_resolve

def find_download(v):
    if isinstance(v,dict):
        if v.get('attribute')=='2K-JPG':return v
        children=v.values()
    elif isinstance(v,list):children=v
    else:return None
    for x in children:
        result=find_download(x)
        if result:return result

def atomic_json(file,data):
    tmp=file.with_suffix('.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(tmp,file)

def fetch(url,target,expected=None):
    if target.exists() and (expected is None or target.stat().st_size==expected):return
    tmp=target.with_suffix(target.suffix+'.part')
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=45) as r, tmp.open('wb') as out:
                shutil.copyfileobj(r,out,1024*1024)
            if expected and tmp.stat().st_size!=expected:raise ValueError('Incomplete download')
            os.replace(tmp,target)
            return
        except Exception:
            if attempt==3:raise
            time.sleep(2**attempt*2)

def material(asset):
    ident=asset['assetId']
    if not re.fullmatch(r'[A-Za-z0-9_-]+',ident):raise ValueError('Invalid asset ID')
    folder=DEST/ident;folder.mkdir(parents=True,exist_ok=True)
    record=folder/'source.json'
    if record.exists():
        result=json.loads(record.read_text(encoding='utf-8'))
        if (ROOT.parent/'model-catalog'/result['path']).is_file():return result
    d=find_download(asset.get('downloadFolders'))
    if d['fileName']!=ident+'_2K-JPG.zip':raise ValueError('Unexpected archive name')
    archive=ROOT/'archives'/d['fileName']
    fetch(d['downloadLink'],archive,d['size'])
    checksum=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(archive.read_bytes()).hexdigest()
    maps={}
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError('ZIP CRC failed')
        for member in z.infolist():
            if member.is_dir():continue
            target=(folder/member.filename).resolve()
            if not target.is_relative_to(folder.resolve()):raise ValueError('Unsafe ZIP entry')
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(member) as src,target.open('wb') as out:shutil.copyfileobj(src,out)
            if target.suffix.lower() in ['.jpg','.jpeg','.png']:
                with Image.open(target) as im:im.verify()
                name=target.stem.split('_2K-JPG_')[-1]
                maps[name]=target.relative_to(ROOT.parent/'model-catalog').as_posix()
    color=maps.get('Color')
    if not color:raise ValueError('Missing color image')
    with Image.open(ROOT.parent/'model-catalog'/color) as im:
        dimensions=list(im.size);im.thumbnail((160,160));im.convert('RGB').save(folder/'preview.jpg',quality=85)
    category=CATEGORIES[asset['displayCategory']]
    result={'id':'acg_'+ident,'title':category+' '+ident,'category':category,'original':asset['displayName'],'path':color,'thumbnail':(folder/'preview.jpg').relative_to(ROOT.parent/'model-catalog').as_posix(),'maps':maps,'resolution':dimensions,'license':'CC0-1.0','licenseUrl':'https://docs.ambientcg.com/license/','source':asset['shortLink'],'provider':'ambientCG','download':d['downloadLink'],'archive':str(archive.relative_to(ROOT)),'archiveBytes':archive.stat().st_size,'sha256':checksum,'tags':asset.get('tags',[])}
    atomic_json(record,result)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=8,choices=range(1,17),help='Concurrent downloads (1-16)')
    parser.add_argument('--all',action='store_true',help='All material categories from the catalog')
    args=parser.parse_args()
    (ROOT/'archives').mkdir(exist_ok=True)
    assets=json.loads((ROOT/'ambientcg-catalog.json').read_text(encoding='utf-8'))
    if args.all:
        translations={'Tiles':'Baldosas','Fabric':'Tela','Concrete':'Hormigón','Leather':'Cuero','Asphalt':'Asfalto','Road':'Carreteras','Roofing Tiles':'Tejas','Facade':'Fachadas','Marble':'Mármol','Snow':'Nieve','Plastic':'Plástico','Bark':'Corteza','Painted Wood':'Madera pintada','Granite':'Granito','Ice':'Hielo','Painted Plaster':'Revoque pintado','Painted Bricks':'Ladrillo pintado','Plaster':'Revoque','Clay':'Arcilla','Carpet':'Alfombra','Scattered Leaves':'Hojas caídas','Wood Siding':'Revestimiento de madera','Surface Imperfections':'Imperfecciones','Corrugated Steel':'Chapa ondulada','Metal Plates':'Placas de metal','Diamond Plate':'Chapa antideslizante','Metal Walkway':'Pasarela metálica','Wicker':'Mimbre','Sheet Metal':'Chapa','Fence':'Vallas','Wood Chips':'Virutas','Tree End':'Corte de tronco','Logs':'Troncos','Pathway':'Senderos'}
        for a in assets:CATEGORIES.setdefault(a['displayCategory'],translations.get(a['displayCategory'],a['displayCategory']))
    selected=[a for a in assets if a['displayCategory'] in CATEGORIES and find_download(a.get('downloadFolders'))]
    order=list(CATEGORIES)
    selected.sort(key=lambda a:(order.index(a['displayCategory']),-a.get('popularityScore',0)))
    results=[];errors=[];started=time.time();pending=[]
    for a in selected:
        record=DEST/a['assetId']/'source.json'
        if record.exists():
            try:results.append(material(a));continue
            except Exception:pass
        pending.append(a)
    # Interleave categories so the editor gets usable variety before the full batch finishes.
    buckets={category:[a for a in pending if a['displayCategory']==category] for category in order}
    pending=[bucket[i] for i in range(max((len(b) for b in buckets.values()),default=0)) for bucket in buckets.values() if i<len(bucket)]
    total_bytes=sum(find_download(a['downloadFolders'])['size'] for a in selected)
    atomic_json(ROOT/'plan.json',{'materials':len(selected),'catalogTotal':len(assets),'unavailable2K':[a['assetId'] for a in assets if a['displayCategory'] in CATEGORIES and not find_download(a.get('downloadFolders'))],'archiveBytes':total_bytes,'categories':CATEGORIES,'scope':'All available 2K-JPG ambientCG materials' if args.all else 'All available 2K-JPG ambientCG materials in the listed categories'})
    print(f'PLAN {len(selected)} materials, {total_bytes/1e9:.2f} GB archives',flush=True)
    def publish():
        atomic_json(ROOT/'catalog.json',sorted(results,key=lambda r:(order.index(next(k for k,v in CATEGORIES.items() if v==r['category'])),r['id'])))
        atomic_json(ROOT/'progress.json',{'complete':len(results),'total':len(selected),'failed':errors,'archiveBytes':sum(r['archiveBytes'] for r in results),'elapsedSeconds':round(time.time()-started),'finished':len(results)+len(errors)==len(selected)})
    publish()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(material,a):a for a in pending}
        for future in concurrent.futures.as_completed(futures):
            a=futures[future]
            try:results.append(future.result())
            except Exception as e:errors.append({'id':a['assetId'],'error':str(e)})
            publish()
            print(f'{len(results)}/{len(selected)} OK, {len(errors)} failed: {a["assetId"]}',flush=True)
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
