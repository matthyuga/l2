from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];V1=R/'research/stickers-radial-v1';V2=R/'research/stickers-maggie-v2';C=R.parent/'l2/system-hud'
JAVA=R/'tools/jdk-25.0.4.1+1/bin/java.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def log(n):
 b=(S/n).read_bytes();return b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig')
def ps(code):
 p=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
assert not (S/'installation.json').exists(),'Already installed'
assert log('client-verification.txt').rstrip().endswith('PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 19 finite one-shot emitters and neck attachment actions.')
assert 'all 140 unrelated windows byte identical' in log('xdat-build.txt')
ps("if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto'};if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay jugadores conectados'}")
for n,digest in json.loads((S/'input-hashes.json').read_text()).items():assert sha(Path(n))==digest,'Concurrent client change '+n
master=json.loads((V1/'installation.json').read_text());assert not master.get('rolled_back')
for item in master['files']:assert sha(Path(item['target']))==item['after_sha256'],'Concurrent installed change '+item['target']
pid=ps("Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique")
assert pid.isdigit() and int((R/'run/game.pid').read_text(encoding='utf-8-sig').strip())==int(pid)
assert Path(ps(f'(Get-Process -Id {pid}).Path')).resolve()==JAVA.resolve()
items=[(C/'Interface.xdat',S/'Interface.xdat'),(C/'skillgrp.dat',S/'skillgrp.dat'),(C/'NexusStickersV3.u',S/'NexusStickersV3.u'),(R.parent/'l2/animations/NexusStickerEffectsV3.usk',S/'NexusStickerEffectsV3.usk')]
for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:items.append((base/'data/scripts/custom/StickerEmotes/MaggieStickerEmotes.java',S/'MaggieStickerEmotes.java'))
for target,source in items:
 assert source.exists()
 if target.name in ['NexusStickersV3.u','NexusStickerEffectsV3.usk']:assert not target.exists(),'New package conflict'
mf=S/'diagnostics.mf';mf.write_text('Manifest-Version: 1.0\nAgent-Class: EnableStickerDiagnosticsV3\nCan-Redefine-Classes: true\n\n')
subprocess.run([str(JAVA.with_name('jar.exe')),'--create','--file',str(S/'diagnostics.jar'),'--manifest',str(mf),'-C',str(S/'classes'),'EnableStickerDiagnosticsV3.class'],check=True,capture_output=True)
backup=R/'backups'/('stickers-overhead-v3-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
records=[]
for i,(target,source) in enumerate(items):
 saved=backup/(str(i)+'-'+target.name)
 if target.exists():shutil.copy2(target,saved)
 records.append({'target':str(target),'source':str(source),'before_sha256':sha(target) if target.exists() else None,'after_sha256':sha(source),'backup':str(saved) if target.exists() else None})
manifest={'backup':str(backup),'files':records,'live_installed':False,'input_mode':'button-only','visual_verification':'User reported V2 menu only, no overhead sticker. V3 neck attachment/UV fixes pending in-game verification.'}
def save():
 text=json.dumps(manifest,indent=2);(S/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
save();written=[]
try:
 for item in records:
  p=Path(item['target']);assert (sha(p) if p.exists() else None)==item['before_sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(Path(item['source']).read_bytes());written.append(item);assert sha(p)==item['after_sha256']
 run=subprocess.run([str(JAVA),'-cp',str(V1/'agent'),'AttachStickers',pid,str(S/'diagnostics.jar'),str(S)],capture_output=True,text=True,timeout=90)
 (S/'diagnostics.log').write_text(run.stdout+run.stderr);assert run.returncode==0,'Script redefinition failed; inspect diagnostics.log'
 assert 'PASS: only existing sticker script class redefined' in (S/'live-verification.txt').read_text()
 manifest['live_installed']=True;save()
except BaseException:
 for item in reversed(written):
  p=Path(item['target']);assert sha(p)==item['after_sha256']
  if item['backup']:shutil.copy2(item['backup'],p)
  else:p.unlink()
 manifest['files_restored_after_failure']=True;save();raise
for item in records:
 found=next((x for x in master['files'] if x['target']==item['target']),None)
 if found:found['after_sha256']=item['after_sha256']
 else:master['files'].append({'target':item['target'],'before_sha256':None,'after_sha256':item['after_sha256'],'backup':None})
master['overhead_v3']={'stage':str(S),'backup':str(backup),'attachment':'Bip01 Neck1','keyboard_timer':False,'world_render':'pending real game check'}
master['visual_verification']=manifest['visual_verification']
text=json.dumps(master,indent=2);(V1/'installation.json').write_text(text);(Path(master['backup'])/'manifest.json').write_text(text)
assert sha(R/'server/libs/GameServer.jar')==master['core_jar_sha256']
print('INSTALLED: neck attachment, native-size wheel textures and accepted-send feedback. No keyboard timer. In-game verification pending. Backup:',backup)
