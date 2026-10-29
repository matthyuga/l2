from pathlib import Path
import subprocess,concurrent.futures,json
ROOT=Path(r'E:\l2-local');stage=ROOT/'research/npc-batch2';folders=list((stage/'packages').glob('*/plan.json'))
def run(p):
 r=subprocess.run(['python',str(stage/'export_archive.py'),p.parent.name],capture_output=True,timeout=900)
 (p.parent/'export-process.log').write_bytes(r.stdout+r.stderr)
 return p.parent.name,r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for i,(id,code) in enumerate(ex.map(run,folders),1):
  if i%10==0 or code:print('EXPORTED',i,'/',len(folders),'exit',code,id,flush=True)
print('DONE',flush=True)
