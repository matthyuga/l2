from pathlib import Path
import json,hashlib,datetime,shutil,subprocess,zipfile
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Installation already recorded; retain backups'
for file,count in [('native-test-results.json',20506),('server-test-results.json',16394),('client-test-results.json',30)]:assert json.loads((D/file).read_text())['passed']==count
ps=['powershell','-NoProfile','-Command']
assert not subprocess.check_output(ps+["if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close L2 before install'
log=Path('E:/l2/system-hsl-autoqa-20261026/NexusHairHsl.log').read_text();assert 'PASS native preflight: RGBA texture=1024x512' in log
pid=subprocess.check_output(ps+["Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"],text=True).strip();assert pid.isdigit()
patches=json.loads((D/'client-patches.json').read_text());baseline=json.loads((D/'server-baseline.json').read_text());items=[]
def add(target,data):
 target=Path(target);items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 for name in ['NWindow.dll','engine.dll','NexusHairHslGame.dll']:
  target=Path('E:/l2')/profile/name
  if name in patches:assert sha(target.read_bytes())==patches[name]['before']
  else:assert not target.exists()
  add(target,(D/'stage'/name).read_bytes())
for root in [P/'source/L2J_Mobius_CT_0_Interlude/java',P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java']:
 for src in (D/'server-source').rglob('*.java'):
  rel=src.relative_to(D/'server-source');target=root/rel
  if rel.as_posix() in baseline:assert sha(target.read_bytes())==baseline[rel.as_posix()],target
  else:assert not target.exists(),target
  add(target,src.read_bytes())
for i,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 with zipfile.ZipFile(target) as old,zipfile.ZipFile(D/('GameServer-'+str(i)+'.jar')) as new:
  assert all(old.read(n)==new.read(n) for n in old.namelist() if not n.startswith('org/l2jmobius/gameserver/custom/HairColorHsl') and n not in [r.removesuffix('.java')+'.class' for r in baseline])
 add(target,(D/('GameServer-'+str(i)+'.jar')).read_bytes())
statefile=D.parent/'2026-10-24/current-appearance.json';state=json.loads(statefile.read_text());state.update(hsl_manifest=str(D/'installation.json'),hsl_modes=['classic-A-D','free-HSL'],hsl_visual_validation='pending');add(statefile,json.dumps(state,indent=2).encode())
backup=P/'backups'/('hair-hsl-ingame-v1-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
m=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),game_server_pid=pid,live_installed=False,files=[],visual_validation='pending',existing_characters_unchanged=True)
for i,item in enumerate(items):
 saved=backup/(str(i)+'-'+Path(item['target']).name) if item['before_sha256'] else None
 if saved:shutil.copy2(item['target'],saved)
 m['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved) if saved else None))
def save():
 (D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2))
save();attached=False
try:
 for item in items:
  target=Path(item['target']);assert (sha(target.read_bytes()) if target.exists() else None)==item['before_sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(item['data'])
 java=P/'tools/jdk-25.0.4.1+1/bin/java.exe'
 result=subprocess.run([str(java),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(D/'reload-hsl.jar'),str(D)],capture_output=True,text=True,errors='replace',timeout=60)
 (D/'server-reload.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0 and (D/'live-install-proof.txt').exists(),result.stdout+result.stderr;attached=True
 for item in m['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256']
 m['live_installed']=True;save()
except Exception:
 if attached:subprocess.run([str(java),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(D/'reload-hsl.jar'),str(D)+'|rollback'],capture_output=True,timeout=60)
 for item in reversed(m['files']):
  target=Path(item['target'])
  if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
  elif target.exists():target.unlink()
 m['failed_and_files_restored']=True;save();raise
shutil.copy2('E:/l2/system-hsl-autoqa-20261026/HslNativePanelQA.bmp',D/'native-panel-diagnostic.bmp')
(D/'runtime-preflight.txt').write_text(log[log.rfind('READY HSL ingame v1:'):],encoding='utf-8')
print('INSTALLED both client profiles and live server; backup:',backup)
