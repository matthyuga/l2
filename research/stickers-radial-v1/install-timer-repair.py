from pathlib import Path
import hashlib,json,subprocess,datetime,shutil
S=Path(__file__).resolve().parent;R=S.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S/'installation.json').read_text())
assert not m.get('rolled_back') and not m.get('timer_byte_fix')
verification=(S/'client-verification.txt').read_bytes()
text=verification.decode('utf-16' if verification.startswith(b'\xff\xfe') else 'utf-8-sig')
assert 'PASS: native IsKeyDown byte-enum parameters use ByteConst' in text
assert text.rstrip().endswith('PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 8 finite one-shot emitters and actor trail actions.')
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto'}"],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
for item in m['files']:assert sha(Path(item['target']))==item['after_sha256'],'Concurrent edit: '+item['target']
target=R.parent/'l2/system-hud/Interface.u'
assert sha(target)==sha(S/'timer-crash-v1/Interface.u')
entry=next(item for item in m['files'] if Path(item['target'])==target)
old=entry['after_sha256'];target.write_bytes((S/'Interface.u').read_bytes())
entry['after_sha256']=sha(target)
m['timer_byte_fix']={'date':datetime.datetime.now().isoformat(),'old_sha256':old,'new_sha256':entry['after_sha256'],'crashing_package':str(S/'timer-crash-v1/Interface.u'),'change':'3 key arguments changed from EX_IntConstByte (int32) to EX_ByteConst (byte), matching native EInputKey signature','runtime_verification':'pending in-game'}
m['visual_verification']='Initial client crash in StickerRadialUI.OnTimer reported by user; corrected byte enum parameters installed; pending in-game retry.'
text=json.dumps(m,indent=2);(S/'installation.json').write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
(S/'final-verification.json').write_text(json.dumps({'installed_files_verified':len(m['files']),'live_handler_registered':m['live_installed'],'timer_byte_fix_installed':True,'in_game_verification':'pending retry after user-reported crash'},indent=2))
print('INSTALLED: three-byte keyboard argument fix. Original rollback remains intact. Runtime retry pending.')
