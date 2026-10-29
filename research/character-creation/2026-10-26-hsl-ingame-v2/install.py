from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
D=Path(__file__).resolve().parent;V1=D.parent/'2026-10-26-hsl-ingame-v1';P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists()
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client'
assert json.loads((D/'native-test-results.json').read_text())['passed']==20506
assert json.loads((D/'preview-test-results.json').read_text())['passed']==183
assert json.loads((D/'performance-results.json').read_text())['passed']
log=Path('E:/l2/system-hsl-autoqa-20261026/NexusHairHsl.log').read_text();assert 'PASS native preflight:' in log[log.rfind('READY HSL ingame'):]
assert sha(Path('E:/l2/system-hsl-autoqa-20261026/NexusHairHslGame.dll').read_bytes())==sha((D/'stage/NexusHairHslGame.dll').read_bytes())
v1=json.loads((V1/'installation.json').read_text());assert v1['live_installed'];items=[]
def add(target,data):
 target=Path(target);items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()),after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 target=Path('E:/l2')/profile/'NexusHairHslGame.dll';e=next(x for x in v1['files'] if x['target']==str(target));assert sha(target.read_bytes())==e['after_sha256'];data=(D/'stage/NexusHairHslGame.dll').read_bytes();add(target,data);e['after_sha256']=sha(data)
statepath=D.parent/'2026-10-24/current-appearance.json';state=json.loads(statepath.read_text());state['hsl_performance_manifest']=str(D/'installation.json');state['hsl_visual_validation']='v1 visible and working; user reports original flash and lag; v2 confirmation pending';data=json.dumps(state,indent=2).encode();add(statepath,data);next(x for x in v1['files'] if x['target']==str(statepath))['after_sha256']=sha(data)
v1['performance_v2']=str(D/'installation.json')
for target in [V1/'installation.json',Path(v1['backup'])/'manifest.json']:add(target,json.dumps(v1,indent=2).encode())
backup=P/'backups'/('hair-hsl-ingame-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
m=dict(backup=str(backup),live_installed=False,files=[],client_binary_hooks_unchanged=True,server_unchanged=True,visual_validation='pending')
for i,item in enumerate(items):
 saved=backup/(str(i)+'-'+Path(item['target']).name);shutil.copy2(item['target'],saved);m['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved)))
def save():
 (D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2))
save()
try:
 for item in items:
  target=Path(item['target']);assert sha(target.read_bytes())==item['before_sha256'];target.write_bytes(item['data'])
 for item in m['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256']
 m['live_installed']=True;save()
except Exception:
 for item in reversed(m['files']):Path(item['target']).write_bytes(Path(item['backup']).read_bytes())
 m['failed_and_restored']=True;save();raise
(D/'runtime-preflight.txt').write_text(log[log.rfind('READY HSL ingame'):])
print('INSTALLED optimized DLL in both profiles; native hooks and server unchanged. Backup:',backup)
