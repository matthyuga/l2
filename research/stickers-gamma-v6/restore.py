from pathlib import Path
import subprocess,json,hashlib,shutil
S=Path(__file__).resolve().parent;p=S/'installation.json';m=json.loads(p.read_text());assert m['installed'] and not m.get('restored')
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'Close L2 before restoration'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();target=Path(m['target']);saved=Path(m['backup']);assert sha(target)==m['after_sha256'],'Later texture package change';assert sha(saved)==m['before_sha256']
shutil.copy2(saved,target);assert sha(target)==m['before_sha256'];m['restored']=True;p.write_text(json.dumps(m,indent=2));(saved.parent/'manifest.json').write_text(json.dumps(m,indent=2));print('Restored original sticker colors; attachment fixes and Amber compensation remain.')
