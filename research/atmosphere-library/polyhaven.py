import concurrent.futures, json
import download as d
from discover import ROOT,read,run
d.PROGRESS=ROOT/'polyhaven-progress.json'
def prepare(item):
 ident,meta=item
 path=ROOT/'polyhaven'/ident/'files.json'
 if path.exists():files=json.loads(path.read_text(encoding='utf8'))
 else:
  files=json.loads(read('https://api.polyhaven.com/files/'+ident));d.save(path,files)
 jobs=[]
 for kind,entry in [('hdri',files.get('hdri',{}).get('2k',{}).get('hdr')),('tonemapped',files.get('tonemapped'))]:
  if not entry:continue
  name=ident+'_2k.hdr' if kind=='hdri' else ident+'.jpg'
  jobs.append({'path':f'polyhaven/{ident}/{name}','url':entry['url'],'size':entry['size'],'md5':entry.get('md5'),'source':'https://polyhaven.com/a/'+ident,'license':'CC0-1.0'})
 d.save(path.parent/'asset.json',meta)
 return jobs
if __name__=='__main__':
 print('Powered by Poly Haven — public API',flush=True)
 run(('polyhaven-api-terms','https://raw.githubusercontent.com/Poly-Haven/Public-API/master/ToS.md'))
 run(('sonniss-license','https://sonniss.com/gdc-bundle-license/'))
 catalogfile=ROOT/'polyhaven-catalog.json'
 if catalogfile.exists():catalog=json.loads(catalogfile.read_text(encoding='utf8'))
 else:
  catalog=json.loads(read('https://api.polyhaven.com/assets?type=hdris&category=pure-skies'));d.save(catalogfile,catalog)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:jobs=[job for batch in ex.map(prepare,catalog.items()) for job in batch]
 d.save(ROOT/'polyhaven-plan.json',jobs)
 if d.PROGRESS.exists():d.STATE.update(json.loads(d.PROGRESS.read_text(encoding='utf8')).get('items',{}))
 print(f'{len(catalog)} skies, {len(jobs)} files, {sum(j["size"] for j in jobs)/1e9:.2f} GB',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(d.fetch,jobs))
 print('POLYHAVEN QUEUE FINISHED',flush=True)
