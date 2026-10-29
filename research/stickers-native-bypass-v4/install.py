from pathlib import Path
import json,hashlib,datetime,subprocess,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];V1=R/'research/stickers-radial-v1';JAVA=R/'tools/jdk-25.0.4.1+1/bin/java.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ps(code):
 p=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
assert not (S/'installation.json').exists(),'Already installed'
assert 'PASS: fresh JVM startup agent' in (S/'cold-start-verification.txt').read_text()
master=json.loads((V1/'installation.json').read_text());assert not master.get('rolled_back')
for item in master['files']:assert sha(Path(item['target']))==item['after_sha256'],'Concurrent installed file change: '+item['target']
assert sha(R/'server/libs/GameServer.jar')==master['core_jar_sha256']
for n,digest in json.loads((S/'input-hashes.json').read_text()).items():assert sha(Path(n))==digest,'Concurrent source change '+n
pid=ps("Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique")
assert pid.isdigit() and int((R/'run/game.pid').read_text(encoding='utf-8-sig').strip())==int(pid)
assert Path(ps(f'(Get-Process -Id {pid}).Path')).resolve()==JAVA.resolve()
relative=Path('org/l2jmobius/gameserver/network/serverpackets/SkillCatalogView.java')
patched=(S/'source'/relative).read_text();a=patched.index('    public static boolean nativeWindowAction(String action)');b=patched.index('    private static final Map',a);method=patched[a:b]
items=[(R/'server/agents/sticker-native-actions-v4.jar',(S/'native-actions-agent.jar').read_bytes())]
assert not items[0][0].exists(),'Startup agent target already exists'
for base in [R/'source/L2J_Mobius_CT_0_Interlude/java',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java']:
 p=base/relative
 if p.exists():
  raw=p.read_bytes();text=raw.decode('utf-8-sig');a=text.index('    public static boolean nativeWindowAction(String action)');b=text.index('    private static final Map',a)
  text=text[:a]+method+text[b:];items.append((p,text.encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8')))
needle="-ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn',$RaceVerificationOption"
replacement="-ArgumentList '-server',('-javaagent:\"'+(Join-Path $Root 'server/agents/sticker-native-actions-v4.jar')+'\"'),'-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn',$RaceVerificationOption"
for p in [R/'Start-L2Local.ps1',R/'cloud-repo/Start-L2Local.ps1']:
 if p.exists():
  raw=p.read_bytes();text=raw.decode('utf-8-sig');assert text.count(needle)==1,'Unexpected GameServer launch signature: '+str(p)
  new=text.replace(needle,replacement);encoded=new.encode('utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8');items.append((p,encoded))
  syntax=S/('validate-'+str(len(items))+'.ps1');syntax.write_bytes(encoded)
  ps("$stickerTokens=$null;$stickerErrors=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('"+str(syntax)+"',[ref]$stickerTokens,[ref]$stickerErrors);if($stickerErrors.Count){throw ($stickerErrors|Out-String)}")
backup=R/'backups'/('stickers-native-bypass-v4-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
records=[]
for i,(target,data) in enumerate(items):
 assert target.resolve().is_relative_to(R.resolve())
 saved=backup/(str(i)+'-'+target.name)
 if target.exists():shutil.copy2(target,saved)
 records.append({'target':str(target),'before_sha256':sha(target) if target.exists() else None,'after_sha256':hashlib.sha256(data).hexdigest(),'backup':str(saved) if target.exists() else None})
manifest={'backup':str(backup),'files':records,'live_installed':False,'game_jar_unchanged':True,'world_render':'pending next real click'}
def save():
 text=json.dumps(manifest,indent=2);(S/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
save();written=[]
try:
 for (p,data),record in zip(items,records):
  assert (sha(p) if p.exists() else None)==record['before_sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);written.append(record);assert sha(p)==record['after_sha256']
 run=subprocess.run([str(JAVA),'-cp',str(V1/'agent'),'AttachStickers',pid,str(S/'native-actions-agent.jar'),str(S)],capture_output=True,text=True,timeout=90)
 (S/'agent-install.log').write_text(run.stdout+run.stderr);assert run.returncode==0,'Live native action patch failed; see agent-install.log'
 assert 'all 19 exact sticker selections accepted' in (S/'live-verification.txt').read_text()
 manifest['live_installed']=True;save()
except BaseException:
 for item in reversed(written):
  p=Path(item['target']);assert sha(p)==item['after_sha256']
  if item['backup']:shutil.copy2(item['backup'],p)
  else:p.unlink()
 manifest['files_restored_after_failure']=True;save();raise
for item in records:
 old=next((x for x in master['files'] if x['target']==item['target']),None)
 if old:old['after_sha256']=item['after_sha256']
 else:master['files'].append(item)
master['native_bypass_v4']={'stage':str(S),'backup':str(backup),'exact_actions':19,'live_and_next_start_verified':True,'startup_agent':str(R/'server/agents/sticker-native-actions-v4.jar')}
master['visual_verification']='Root dispatch blocker confirmed: native whitelist rejected sticker actions. Exact 1..19 actions now allowed in live JVM and cold startup test; next real click/render pending.'
text=json.dumps(master,indent=2);(V1/'installation.json').write_text(text);(Path(master['backup'])/'manifest.json').write_text(text)
assert sha(R/'server/libs/GameServer.jar')==master['core_jar_sha256']
print('INSTALLED: exact sticker native actions enabled live and persisted for next startup. No client/server restart, active sessions unchanged. Backup:',backup)
