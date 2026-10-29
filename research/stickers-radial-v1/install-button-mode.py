from pathlib import Path
import json,hashlib,subprocess,datetime
S=Path(__file__).resolve().parent;R=S.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S/'installation.json').read_text())
assert not m.get('rolled_back') and not m.get('timer_disabled')
raw=(S/'client-verification.txt').read_bytes();proof=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig')
assert 'PASS: OnTimer is return-only; no keyboard/native calls.' in proof
assert 'PASS: no timer registration remains in OnEvent.' in proof
assert proof.rstrip().endswith('PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 8 finite one-shot emitters and actor trail actions.')
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto'}"],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
for item in m['files']:assert sha(Path(item['target']))==item['after_sha256'],'Concurrent edit: '+item['target']
target=R.parent/'l2/system-hud/Interface.u';assert sha(target)==sha(S/'timer-crash-v2/Interface.u')
entry=next(item for item in m['files'] if Path(item['target'])==target)
old=entry['after_sha256'];target.write_bytes((S/'Interface.u').read_bytes());entry['after_sha256']=sha(target)
m['timer_byte_fix']['runtime_verification']='FAILED: user reported same crash in OnTimer after this correction.'
m['timer_disabled']={'date':datetime.datetime.now().isoformat(),'old_sha256':old,'new_sha256':entry['after_sha256'],'mode':'button-only','change':'Removed SetUITimer/KillUITimer calls and reduced OnTimer to Return(Nothing). No periodic keyboard polling.','runtime_verification':'pending in-game'}
m['visual_verification']='Two user-reported OnTimer crashes. Timer now removed; button-only recovery pending in-game check.'
text=json.dumps(m,indent=2);(S/'installation.json').write_text(text);(Path(m['backup'])/'manifest.json').write_text(text)
(S/'final-verification.json').write_text(json.dumps({'installed_files_verified':len(m['files']),'keyboard_polling_removed':True,'input_mode':'button-only','in_game_verification':'pending'},indent=2))
print('INSTALLED: no timer registration, return-only OnTimer. Button-only recovery; in-game result not yet verified.')
