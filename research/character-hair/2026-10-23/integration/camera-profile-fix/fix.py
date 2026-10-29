"""Add only the thirteen hair records to the observer profile's own catalogs.

The running client keeps its already loaded catalogs until the next launch.
No client or server process is stopped by this script.
"""
from pathlib import Path
import subprocess,hashlib,json,struct,datetime,shutil,os

ROOT=Path(__file__).resolve().parent
INTEGRATION=ROOT.parent
PROJECT=INTEGRATION.parents[3]
CLIENT=PROJECT.parent/'l2'
TARGET=CLIENT/'system-camera-online'
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
DISASM=PROJECT/'tools-src/L2FileEdit/data/l2asm-disasm/l2disasm.exe'
FOOT=b'\x0cSafePackage\0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,timeout=90)
 assert r.returncode==0,(args,r.stdout,r.stderr)
def rows(p):return [line.split('\t') for line in p.read_text(encoding='utf-8-sig').splitlines()[1:] if line.strip()]
def main():
 assert not (ROOT/'installation.json').exists(),'Fix already installed; use verification, not reinstallation'
 changes=[];catalogs={}
 for name,idx in [('armorgrp',1),('itemname-e',0)]:
  dst=TARGET/(name+'.dat');before_hash=sha(dst)
  before_raw=ROOT/(name+'.before.raw');before_txt=ROOT/(name+'.before.txt')
  run([CODEC,'-o',before_raw,dst]);run([DISASM,'-d',INTEGRATION/(name+'.ddf'),'-o','e',before_raw,before_txt])
  before_rows=rows(before_txt);existing={int(r[idx]) for r in before_rows};wanted=set(range(28000,28013))
  assert not (existing & wanted),('ID collision or partial previous installation',name,existing & wanted)
  old=before_raw.read_bytes();extra=(INTEGRATION/'stage'/(name+'.add.raw')).read_bytes()
  assert old.endswith(FOOT) and extra.endswith(FOOT) and struct.unpack_from('<I',extra)[0]==13
  count=struct.unpack_from('<I',old)[0]
  merged=struct.pack('<I',count+13)+old[4:-len(FOOT)]+extra[4:-len(FOOT)]+FOOT
  assert merged[4:len(old)-len(FOOT)]==old[4:-len(FOOT)]
  raw=ROOT/(name+'.after.raw');raw.write_bytes(merged)
  txt=ROOT/(name+'.after.txt');run([DISASM,'-d',INTEGRATION/(name+'.ddf'),'-o','e',raw,txt])
  after_rows=rows(txt);assert after_rows[:len(before_rows)]==before_rows
  assert after_rows[len(before_rows):]==rows(INTEGRATION/'stage'/(name+'.add.txt'))
  encoded=ROOT/(name+'.dat');run([CODEC,'-c','encode','-p','413','-o',encoded,raw])
  check=ROOT/(name+'.check.raw');run([CODEC,'-o',check,encoded]);assert check.read_bytes()==merged
  changes.append(dict(target=str(dst),stage=str(encoded),before=before_hash,after=sha(encoded)))
  catalogs[name]=dict(existing_records_preserved=count,added=13,existing_record_bytes_preserved=True)
 # All resources are shared by both profiles through ../Animations and ../SysTextures.
 m=json.loads((INTEGRATION/'installation.json').read_text(encoding='utf8'))
 for asset in m['assets']:
  dst=CLIENT/('Animations' if asset['name'].endswith('.ukx') else 'SysTextures')/asset['name']
  assert sha(dst)==asset['sha256'],dst
 backup=PROJECT/'backups'/('hair-camera-profile-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
 for c in changes:
  assert sha(c['target'])==c['before'],('Concurrent edit',c['target'])
  saved=backup/Path(c['target']).name;shutil.copy2(c['target'],saved);c['backup']=str(saved)
 (backup/'files.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
 installed=[]
 try:
  for c in changes:
   dst=Path(c['target']);assert sha(dst)==c['before']
   pending=dst.with_name(dst.name+'.hair-fix.pending');shutil.copy2(c['stage'],pending)
   assert sha(pending)==c['after'];os.replace(pending,dst);installed.append(c)
  for c in changes:assert sha(c['target'])==c['after']
 except BaseException:
  for c in reversed(installed):
   if sha(c['target'])==c['after']:
    pending=Path(c['target']+'.hair-fix.restore');shutil.copy2(c['backup'],pending);os.replace(pending,c['target'])
  raise
 report=dict(status='installed-on-disk',profile=str(TARGET),files=changes,catalogs=catalogs,shared_resource_hashes_checked=20,client_restart_required=True,in_game_visual_check='pending',client_or_server_stopped=False)
 (ROOT/'installation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
