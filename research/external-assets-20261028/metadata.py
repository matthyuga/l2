import pathlib,json,urllib.request,concurrent.futures,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from inventory import ROOT,OUT,origin

def fetch(p):
    o=origin(p)
    if not o.get('model_uid'):return p.name,o
    try:
        req=urllib.request.Request('https://api.sketchfab.com/v3/models/'+o['model_uid'],headers={'User-Agent':'Mozilla/5.0'})
        d=json.load(urllib.request.urlopen(req,timeout=20))
        o.update(title=d.get('name'),url=d.get('viewerUrl',o['url']),author=d.get('user',{}).get('displayName'),author_url=d.get('user',{}).get('profileUrl'),license=d.get('license'),description=d.get('description'),face_count=d.get('faceCount'),vertex_count=d.get('vertexCount'),animation_count=d.get('animationCount'),tags=[t['name'] for t in d.get('tags',[])])
    except Exception as e:o['metadata_error']=str(e)
    return p.name,o

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:data=dict(pool.map(fetch,ROOT.glob('*.zip')))
    (OUT/'sources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'identified':sum(bool(v.get('title')) for v in data.values()),'total':len(data),'errors':sum(bool(v.get('metadata_error')) for v in data.values())}))
