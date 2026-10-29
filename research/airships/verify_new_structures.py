from pathlib import Path
import subprocess,json,urllib.request,urllib.parse,re,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];CAT=ROOT/'research/model-catalog';D=ROOT/'research/airships'
report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
models=[m for m in report['models'] if m['key'].startswith(('superion_','airship_scene_'))]
assert len(models)>=167
links=0
for m in models:
 assert (CAT/m['thumbnail']).is_file(),m['key']
 Image.open(CAT/m['thumbnail']).verify()
 path=CAT/m['gltf'];data=json.loads(path.read_text())
 assert data.get('meshes')
 for item in data.get('buffers',[])+data.get('images',[]):
  if item['uri'].startswith('data:'):continue
  target=(path.parent/urllib.parse.unquote(item['uri'])).resolve()
  assert target.is_relative_to(CAT.resolve()) and target.is_file(),str(target)
  links+=1
audit_path=D/'new-structures-verification.json'
audit=json.loads(audit_path.read_text()) if audit_path.exists() else {}
audit.update(models=len(models),links_checked=links,thumbnails_checked=len(models))
audit_path.write_text(json.dumps(audit,indent=2))
print('RESOURCE_PASS',len(models),'models',links,'links',flush=True)
if '--resources-only' in sys.argv:sys.exit(0)
chrome='C:/Program Files/Google/Chrome/Application/chrome.exe'
keys=['airship_scene_gludio','airship_scene_keucereus','superion_superion_s_superion_20_landmark_01_vc1','superion_superion_du_s_superion_boss_main01']
shots=[]
for key in keys:
 url='http://127.0.0.1:32280/?model='+key+'&view=3d'
 args=[chrome,'--headless=new','--no-first-run','--user-data-dir='+str(D/'qa-new-structures'),'--window-size=1440,1100','--screenshot='+str(D/(key+'-web.png')),'--dump-dom','--virtual-time-budget=10000',url]
 try:
  p=subprocess.run(args,capture_output=True,text=True,errors='replace',timeout=45)
  output=p.stdout;timed_out=False;assert p.returncode==0
 except subprocess.TimeoutExpired as e:
  output=e.stdout or '';output=output.decode('utf-8',errors='replace') if isinstance(output,bytes) else output;timed_out=True
 assert '<canvas' in output and 'No se pudo abrir la vista 3D.' not in output,key
 assert 'Cargando modelo 3D' not in re.sub(r'<script.*?</script>','',output,flags=re.S),key
 shots.append({'key':key,'webgl':'pass','screenshot':key+'-web.png','chrome_exit_timeout':timed_out})
 print('WEBGL_PASS',key,flush=True)
(D/'new-structures-verification.json').write_text(json.dumps(dict(models=len(models),links_checked=links,webgl=shots),indent=2))
print('PASS',len(models),'models,',links,'resource links, four WebGL views')
