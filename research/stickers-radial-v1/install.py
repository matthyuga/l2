"""Guarded local installation with a complete file manifest and live script activation."""
from pathlib import Path
import hashlib,json,shutil,datetime,subprocess,re
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud'
JAVA=R/'tools/jdk-25.0.4.1+1/bin/java.exe';JAR=JAVA.with_name('jar.exe')
sha=lambda data:hashlib.sha256(data).hexdigest()
def log(name):
    b=(S/name).read_bytes()
    return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def ps(code):
    p=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True)
    assert p.returncode==0,(p.stdout+p.stderr).strip()
    return p.stdout.strip()
def attach(pid,jar):
    p=subprocess.run([str(JAVA),'-cp',str(S/'agent'),'AttachStickers',str(pid),str(jar),str(S)],capture_output=True,text=True,timeout=90)
    (S/'activation.log').write_text(p.stdout+p.stderr)
    assert p.returncode==0,'Live activation failed: see activation.log'

assert not (S/'installation.json').exists(),'Already installed; inspect manifest before updating'
assert log('client-verification.txt').rstrip().endswith('PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 8 finite one-shot emitters and actor trail actions.')
assert 'all 140 previous windows byte identical' in log('xdat-build.txt')
catalog=json.loads((S/'catalog-verification.json').read_text());assert catalog['skillgrp']['added']==8 and catalog['skillname-e']['added']==8
ps("if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto'}; if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay clientes conectados'}")
inputs=json.loads((S/'input-hashes.json').read_text())
for name,digest in inputs.items():assert sha(Path(name).read_bytes())==digest,'Changed after staging: '+name
pid=ps("$p=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue; if($p){$p.OwningProcess | Select-Object -Unique}")
if pid:
    assert pid.isdigit() and int((R/'run/game.pid').read_text(encoding='utf-8-sig').strip())==int(pid),'GameServer PID does not match this project'
    executable=ps(f"(Get-Process -Id {int(pid)}).Path")
    assert Path(executable).resolve()==JAVA.resolve(),'GameServer executable does not match this project'

items=[]
def add(target,data,new=False):
    if new:assert not target.exists(),'New target already exists: '+str(target)
    items.append({'target':str(target),'data':data,'before_sha256':sha(target.read_bytes()) if target.exists() else None,'after_sha256':sha(data)})
for name in ['Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat']:add(C/name,(S/name).read_bytes())
add(C/'NexusStickersV1.u',(S/'NexusStickersV1.u').read_bytes(),True)
add(R.parent/'l2/animations/NexusStickerEffectsV1.usk',(S/'NexusStickerEffectsV1.usk').read_bytes(),True)
for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
    add(base/'data/scripts/custom/StickerEmotes/StickerEmotes.java',(S/'StickerEmotes.java').read_bytes(),True)
    cfg=base/'config/Custom/WorldContent.ini'
    if cfg.exists():
        raw=cfg.read_bytes();text=raw.decode('utf-8-sig')
        match=re.search(r'(?m)^(CustomScriptFolders\s*=\s*)([^\r\n]+)',text);assert match,'No script whitelist in '+str(cfg)
        assert 'StickerEmotes' not in match[2].split(';'),'Script already whitelisted'
        text=text[:match.end(2)]+';StickerEmotes'+text[match.end(2):]
        add(cfg,text.encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'))

for agent in ['ActivateStickers','DeactivateStickers']:
    mf=S/(agent+'.mf');mf.write_text('Manifest-Version: 1.0\nAgent-Class: '+agent+'\n\n',encoding='ascii')
    subprocess.run([str(JAR),'--create','--file',str(S/(agent+'.jar')),'--manifest',str(mf),'-C',str(S/'agent'),agent+'.class'],check=True,capture_output=True)

backup=R/'backups'/('stickers-radial-v1-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
manifest={'backup':str(backup),'files':[],'live_installed':False,'game_pid':int(pid) if pid else None,'visual_verification':'pending in-game','core_jar_sha256':sha((R/'server/libs/GameServer.jar').read_bytes())}
def save():
    text=json.dumps(manifest,indent=2);(S/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
for i,item in enumerate(items):
    target=Path(item['target']);assert (sha(target.read_bytes()) if target.exists() else None)==item['before_sha256']
    saved=backup/(str(i)+'-'+target.name)
    if target.exists():shutil.copy2(target,saved)
    item['backup']=str(saved) if target.exists() else None
    data=item.pop('data');manifest['files'].append(item);save()
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);assert sha(target.read_bytes())==item['after_sha256']
try:
    if pid:
        attach(int(pid),S/'ActivateStickers.jar')
        assert 'PASS: exact monotonic 5-second cooldown boundary' in (S/'live-verification.txt').read_text()
        manifest['live_installed']=True
    assert sha((R/'server/libs/GameServer.jar').read_bytes())==manifest['core_jar_sha256'],'Core changed during installation'
    save()
except BaseException:
    for item in reversed(manifest['files']):
        target=Path(item['target']);assert sha(target.read_bytes())==item['after_sha256']
        if item['backup']:shutil.copy2(item['backup'],target)
        else:target.unlink()
    manifest['files_restored_after_failure']=True;save();raise
(backup/'Restore.cmd').write_text('@echo off\r\npython "'+str(S/'rollback.py')+'"\r\npause\r\n',encoding='utf-8')
print('INSTALLED',len(items),'files. Live handler:',manifest['live_installed'],'Backup:',backup)
