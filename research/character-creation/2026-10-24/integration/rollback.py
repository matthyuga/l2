"""Restore only installation-manifest files, refusing any later modifications."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
D=Path(__file__).resolve().parent;P=D.parents[3];manifest=json.loads((D/'installation.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert not manifest.get('rolled_back'),'Already restored'
check=subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True);assert not check.strip(),'Close L2 first'
for item in manifest['files']:
 target=Path(item['target']);assert target.exists() and sha(target.read_bytes())==item['after_sha256'],('Modified since installation; manual review required',target)
 if item['backup']:assert sha(Path(item['backup']).read_bytes())==item['before_sha256']
runtime=next(i for i in manifest['files'] if i['target'].replace('\\','/').endswith('/server/libs/GameServer.jar'))
working=D/'rollback-runtime';rel='org/l2jmobius/gameserver/network/clientpackets/CharacterCreate.class';target=working/'compiled'/rel;target.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(runtime['backup']) as jar:target.write_bytes(jar.read(rel))
listening=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"],text=True).strip()
if listening:
 subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio',listening,str(D/'reload-appearance.jar'),str(working)],check=True)
for item in reversed(manifest['files']):
 target=Path(item['target'])
 if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
 else:target.unlink()
manifest['rolled_back']=True;(D/'installation.json').write_text(json.dumps(manifest,indent=2));print('RESTORED all original files and server validation')
