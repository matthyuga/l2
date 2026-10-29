from pathlib import Path
import json,shutil,hashlib,datetime,subprocess
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];OUT=ROOT/'showcase'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[]
for prefix in ['server/game','source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
 for src in (OUT/'data').rglob('*'):
  if not src.is_file():continue
  dst=PROJECT/prefix/src.relative_to(OUT);assert not dst.exists(),str(dst);files.append({'stage':str(src),'target':str(dst),'before':None,'after':sha(src)})
 cfg=PROJECT/prefix/'config/Custom/WorldContent.ini';text=cfg.read_text(encoding='utf-8')
 lines=text.splitlines();found=False
 for i,line in enumerate(lines):
  if line.startswith('CustomScriptFolders = '):
   found=True;assert 'EquipmentShowcase' not in line;lines[i]=line+';EquipmentShowcase'
 assert found
 stage=OUT/(str(len(files))+'-WorldContent.ini');stage.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 files.append({'stage':str(stage),'target':str(cfg),'before':sha(cfg),'after':sha(stage)})
assert subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process java -ErrorAction SilentlyContinue){exit 5}'],capture_output=True).returncode==0,'Game server must be stopped for persistent installation'
backup=PROJECT/'backups'/('equipment-showcase-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for idx,f in enumerate(files):
 if f['before']:
  saved=backup/f'{idx}-WorldContent.ini';shutil.copy2(f['target'],saved);f['backup']=str(saved)
(backup/'files.json').write_text(json.dumps(files,indent=2))
written=[]
try:
 for f in files:
  dst=Path(f['target']);assert (sha(dst) if dst.exists() else None)==f['before'],'Concurrent edit: '+str(dst)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f['stage'],dst);written.append(f)
 for f in files:assert sha(f['target'])==f['after']
except Exception:
 for f in reversed(written):
  if sha(f['target'])!=f['after']:continue
  if f['before']:shutil.copy2(f['backup'],f['target'])
  else:Path(f['target']).unlink()
 raise
(OUT/'installation.json').write_text(json.dumps({'status':'installed','backup':str(backup),'files':files},indent=2),encoding='utf-8')
print('INSTALLED',len(files),'files',backup)
