"""Headless QA browser with real-time wait for finished GLTF loading."""
import pathlib,subprocess,urllib.request,json,time,websocket,base64,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/airships';CAT=ROOT/'research/model-catalog'
chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';port=9327
proc=subprocess.Popen([chrome,'--headless=new','--no-first-run','--remote-allow-origins=*',f'--remote-debugging-port={port}','--user-data-dir='+str(D/'qa-cdp'),'--window-size=1440,1100','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 deadline=time.monotonic()+30
 while True:
  try:targets=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'));break
  except Exception:
   assert time.monotonic()<deadline;time.sleep(.2)
 ws=websocket.create_connection(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'),timeout=40)
 seq=0
 def call(method,params=None):
  global seq
  seq+=1;ident=seq;ws.send(json.dumps(dict(id=ident,method=method,params=params or {})))
  while True:
   r=json.loads(ws.recv())
   if r.get('id')==ident:
    assert 'error' not in r,r;return r.get('result',{})
 def evaluate(expr):return call('Runtime.evaluate',dict(expression=expr,returnByValue=True)).get('result',{}).get('value')
 results=[]
 keys=sys.argv[1:] or ['airship_scene_gludio','airship_scene_keucereus','superion_superion_s_superion_20_landmark_01_vc1','superion_superion_du_s_superion_boss_main01']
 for key in keys:
  call('Page.navigate',dict(url='http://127.0.0.1:32280/?model='+key+'&view=3d'));deadline=time.monotonic()+40
  while not evaluate("!!document.querySelector('#view3d canvas') && document.getElementById('show3d').textContent==='Ver imagen' && document.getElementById('viewstatus').textContent===''"):
   assert time.monotonic()<deadline,key;time.sleep(.25)
  time.sleep(.3)
  screenshot=call('Page.captureScreenshot',dict(format='png'))['data'];(D/(key+'-web.png')).write_bytes(base64.b64decode(screenshot))
  results.append(dict(key=key,webgl='pass'));print('WEBGL_PASS',key,flush=True)
 audit_path=D/'new-structures-verification.json';previous=json.loads(audit_path.read_text()).get('webgl',[]) if audit_path.exists() else []
 merged={r['key']:r for r in previous+results}
 report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
 count=sum(m['key'].startswith(('superion_','airship_scene_')) for m in report['models'])
 audit_path.write_text(json.dumps(dict(models=count,webgl=list(merged.values())),indent=2))
 call('Browser.close');ws.close()
finally:
 try:proc.wait(timeout=5)
 except subprocess.TimeoutExpired:proc.terminate()
