"""Append only new downloaded packages; preserve all prior inventory decisions."""
import pathlib,json,hashlib,concurrent.futures,shutil,collections
from inventory import ROOT,OUT,MODELS,TEXTURES,unpack,origin
from metadata import fetch

ROUND=pathlib.Path(r'E:\l2-local\research\external-assets-round4-20261028')
ROUND.mkdir(exist_ok=True)

def extract(p):
    rel=p.relative_to(ROOT).as_posix();key='ext3_'+hashlib.sha256(rel.encode()).hexdigest()[:14];dest=OUT/'unpacked'/key
    r={'key':key,'file':rel,'bytes':p.stat().st_size,'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'origin':origin(p),'batch':'Assets externos · Tanda 4','root':str(dest)}
    try:
        unpack(p,dest)
        assert p.stat().st_size==r['bytes'],'Download changed during inventory'
        files=[f for f in dest.rglob('*') if f.is_file()]
        r.update(models=[str(f.relative_to(dest)) for f in files if f.suffix.lower() in MODELS],textures=sum(f.suffix.lower() in TEXTURES for f in files),documents=[str(f.relative_to(dest)) for f in files if f.suffix.lower() in {'.txt','.md','.pdf'}])
        r['status']='source_ready' if r['models'] else 'no_supported_model'
    except Exception as e:r.update(status='extract_failed',error=str(e))
    print(json.dumps({'file':rel,'status':r['status'],'formats':sorted({pathlib.Path(m).suffix.lower() for m in r.get('models',[])})},ensure_ascii=True),flush=True)
    return r

if __name__=='__main__':
    inv=json.loads((OUT/'inventory.json').read_text('utf-8'));known={r['file'] for r in inv['records']}
    paths=[p for p in sorted(ROOT.glob('*.zip')) if p.name not in known]
    for name in ['inventory.json','sources.json','catalog-entries.json']:
        if not (ROUND/('before-'+name)).exists():shutil.copy2(OUT/name,ROUND/('before-'+name))
    (ROUND/'downloads.json').write_text(json.dumps([{'file':p.name,'bytes':p.stat().st_size} for p in paths],indent=2),encoding='utf-8')
    # Metadata requests and local decompression are independent; no target scripts execute.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as metadata_pool,concurrent.futures.ThreadPoolExecutor(max_workers=2) as extraction_pool:
        metas=list(metadata_pool.map(fetch,paths));new=list(extraction_pool.map(extract,paths))
    inv['records'].extend(new);sources=json.loads((OUT/'sources.json').read_text('utf-8'));sources.update(dict(metas))
    (OUT/'inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8');(OUT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROUND/'new-records.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROUND/'keys.json').write_text(json.dumps([r['key'] for r in new]),encoding='utf-8')
    print('ROUND4_INVENTORY '+json.dumps(dict(collections.Counter(r['status'] for r in new))),flush=True)
