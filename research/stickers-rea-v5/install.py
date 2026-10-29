from pathlib import Path
import hashlib,json,subprocess,shutil,datetime
S=Path(__file__).resolve().parent;R=S.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Already installed'
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}"],capture_output=True)
assert check.returncode==0,'Close L2 before replacing a loaded package'
target=R.parent/'l2/animations/NexusStickerEffectsV3.usk'
source=S/target.name
master_path=R/'research/stickers-radial-v1/installation.json'
master=json.loads(master_path.read_text());item=next(x for x in master['files'] if Path(x['target'])==target)
assert sha(target)==item['after_sha256'],'Concurrent change'
backup=R/'backups'/('stickers-rea-v5-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
saved=backup/target.name;shutil.copy2(target,saved)
manifest={'target':str(target),'backup':str(saved),'before_sha256':sha(target),'after_sha256':sha(source),'change':'19 actions: Bip01_head plus bAbsolute=true; position pending visual check','render_confirmed':'Visible beside character with head-name-only runtime test; above-head position not confirmed'}
target.write_bytes(source.read_bytes());assert sha(target)==manifest['after_sha256']
item['after_sha256']=manifest['after_sha256']
master['rea_v5']={'stage':str(S),'backup':str(backup),'root_cause':'AttachToBone rejects NPC neck bone for player; confirmed with REA live trace','runtime_attachment_passed':True,'world_render':'User sees sticker beside character with head-name-only fix; bAbsolute position fix pending visual check'}
master_path.write_text(json.dumps(master,indent=2));(Path(master['backup'])/'manifest.json').write_text(json.dumps(master,indent=2))
(S/'installation.json').write_text(json.dumps(manifest,indent=2));(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Installed 19 corrected attachments; backup:',backup)
