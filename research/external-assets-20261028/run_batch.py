import pathlib,json,subprocess,concurrent.futures,time,sys
from inventory import OUT

BLENDER=r'E:\l2-local\tools\blender-portable\blender-5.0.1-windows-x64\blender.exe'
EXPORT=pathlib.Path(r'E:\l2-local\research\model-catalog\exports\external-assets-3')
SUPPORTED=['.glb','.gltf','.fbx','.blend','.obj','.stl','.ply']
TIMEOUT=int(next((s.split('=',1)[1] for s in sys.argv if s.startswith('--timeout=')),'900'))

def convert(r):
    root=pathlib.Path(r['root'])
    candidates=[root/p for p in r['models'] if pathlib.Path(p).suffix.lower() in SUPPORTED]
    if not candidates:return {'key':r['key'],'status':'unsupported','file':r['file']}
    candidates.sort(key=lambda p:(SUPPORTED.index(p.suffix.lower()),len(p.parts),p.name))
    source=candidates[0];dest=EXPORT/r['key'];dest.mkdir(parents=True,exist_ok=True)
    result=dest/'analysis.json'
    if result.exists():
        d=json.loads(result.read_text('utf-8'))
        if d.get('status')=='ready' and '--force' not in sys.argv:return d
    job={'key':r['key'],'input':str(source),'root':str(root),'output':str(dest)}
    jobs=OUT/'jobs';jobs.mkdir(exist_ok=True);jf=jobs/(r['key']+'.json');jf.write_text(json.dumps(job),encoding='utf-8')
    logs=OUT/'logs';logs.mkdir(exist_ok=True)
    start=time.monotonic()
    try:
        with (logs/(r['key']+'.log')).open('w',encoding='utf-8') as log:
            p=subprocess.run([BLENDER,'--background','--factory-startup','--disable-autoexec','--threads','2','--python',str(OUT/'convert_blender.py'),'--',str(jf)],stdout=log,stderr=subprocess.STDOUT,timeout=TIMEOUT)
        d=json.loads(result.read_text('utf-8')) if result.exists() else {'key':r['key'],'status':'failed','error':'Blender exit '+str(p.returncode)}
    except Exception as e:d={'key':r['key'],'status':'failed','error':str(e)}
    print(json.dumps({'file':r['file'],'seconds':round(time.monotonic()-start),'status':d['status'],'error':d.get('error')},ensure_ascii=True),flush=True)
    return d

if __name__=='__main__':
    records=[r for r in json.loads((OUT/'inventory.json').read_text('utf-8'))['records'] if r['status']=='source_ready']
    selected=next((s.split('=',1)[1].split(',') for s in sys.argv if s.startswith('--keys=')),None)
    if selected:records=[r for r in records if r['key'] in selected]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(convert,records))
    (OUT/'conversion-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('CONVERSION_COMPLETE',len(results),sum(x['status']=='ready' for x in results),flush=True)
