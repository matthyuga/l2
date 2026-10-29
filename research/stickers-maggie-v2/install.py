from pathlib import Path
import hashlib,json,subprocess,datetime,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];V1=R/'research/stickers-radial-v1';C=R.parent/'l2/system-hud'
JAVA=R/'tools/jdk-25.0.4.1+1/bin/java.exe';JAR=JAVA.with_name('jar.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def log(name):
    b=(S/name).read_bytes();return b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8-sig')
def ps(code):
    r=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;return r.stdout.strip()
if (S/'installation.json').exists():
    prior=json.loads((S/'installation.json').read_text());assert prior.get('files_restored_after_failure'),'Already installed'
assert log('client-verification.txt').rstrip().endswith('PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 19 finite one-shot emitters and actor trail actions.')
assert 'PASS: no timer registration remains in OnEvent.' in log('client-verification.txt')
assert 'all 140 unrelated windows byte identical' in log('xdat-build.txt')
ps("if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto'};if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay jugadores conectados'}")
for name,digest in json.loads((S/'input-hashes.json').read_text()).items():assert sha(Path(name))==digest,'Concurrent client edit '+name
m=json.loads((V1/'installation.json').read_text());assert m.get('timer_disabled') and not m.get('rolled_back')
for item in m['files']:assert sha(Path(item['target']))==item['after_sha256'],'Concurrent installed edit '+item['target']
pid=ps("Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique")
assert pid.isdigit() and int((R/'run/game.pid').read_text(encoding='utf-8-sig').strip())==int(pid),'Expected live project GameServer'
assert Path(ps(f'(Get-Process -Id {pid}).Path')).resolve()==JAVA.resolve()
items=[]
for name in ['Interface.xdat','skillgrp.dat','skillname-e.dat']:items.append((C/name,S/name))
items.extend([(C/'NexusStickersV2.u',S/'NexusStickersV2.u'),(R.parent/'l2/animations/NexusStickerEffectsV2.usk',S/'NexusStickerEffectsV2.usk')])
for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
    items.append((base/'data/scripts/custom/StickerEmotes/StickerEmotes.java',S/'StickerEmotes.java'))
    items.append((base/'data/scripts/custom/StickerEmotes/MaggieStickerEmotes.java',S/'MaggieStickerEmotes.java'))
for target,source in items:
    assert source.exists()
    if target.name in ['NexusStickersV2.u','NexusStickerEffectsV2.usk']:assert not target.exists(),'New package conflict'
mf=S/'reload-v2.mf';mf.write_text('Manifest-Version: 1.0\nAgent-Class: ActivateMaggieStickersV2\n\n',encoding='ascii')
subprocess.run([str(JAR),'--create','--file',str(S/'reload-v2.jar'),'--manifest',str(mf),'-C',str(S/'classes'),'ActivateMaggieStickersV2.class'],check=True,capture_output=True)
backup=R/'backups'/('stickers-maggie-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
records=[]
for i,(target,source) in enumerate(items):
    old=backup/(str(i)+'-'+target.name)
    if target.exists():shutil.copy2(target,old)
    records.append({'target':str(target),'source':str(source),'before_sha256':sha(target) if target.exists() else None,'after_sha256':sha(source),'backup':str(old) if target.exists() else None})
manifest={'backup':str(backup),'files':records,'live_installed':False,'visual_verification':'pending in-game','input_mode':'button-only','count':19}
def save():
    text=json.dumps(manifest,indent=2);(S/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
save();written=[]
try:
    for item in records:
        target=Path(item['target']);assert (sha(target) if target.exists() else None)==item['before_sha256']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(Path(item['source']).read_bytes());written.append(item);assert sha(target)==item['after_sha256']
    result=subprocess.run([str(JAVA),'-cp',str(V1/'agent'),'AttachStickers',pid,str(S/'reload-v2.jar'),str(S)],capture_output=True,text=True,timeout=90)
    (S/'reload.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and '19 actual live numeric/name selections' in (S/'live-verification.txt').read_text(),'Live reload failed; see reload.log'
    manifest['live_installed']=True;save()
except BaseException:
    for item in reversed(written):
        target=Path(item['target']);assert sha(target)==item['after_sha256']
        if item['backup']:shutil.copy2(item['backup'],target)
        else:target.unlink()
    manifest['files_restored_after_failure']=True;save();raise
# Preserve the original full-system rollback: original pre-V1 backups remain the
# restore source, while guards track the currently installed artwork revisions.
for item in records:
    old=next((r for r in m['files'] if r['target']==item['target']),None)
    if old:old['after_sha256']=item['after_sha256']
    else:m['files'].append({'target':item['target'],'before_sha256':None,'after_sha256':item['after_sha256'],'backup':None})
m['maggie_v2']={'stage':str(S),'backup':str(backup),'count':19,'wheel_count':8,'input_mode':'button-only'}
m['visual_verification']='Maggie artwork installed, 19 live selections verified; keyboard timer removed; in-game recovery and rendering pending.'
text=json.dumps(m,indent=2);(V1/'installation.json').write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
assert sha(R/'server/libs/GameServer.jar')==m['core_jar_sha256']
print('INSTALLED: 19 artwork stickers, 8 wheel buttons, live handler reloaded. Keyboard timer absent. Backup:',backup)
