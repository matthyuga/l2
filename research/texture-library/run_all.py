"""Unattended resumable downloads of all three public texture catalogs."""
import json, msvcrt, os, pathlib, subprocess, sys, time
from download import ROOT,atomic_json

lock=(ROOT/'download.lock').open('a+b');lock.seek(0)
if not lock.read(1):lock.write(b'1');lock.flush()
lock.seek(0)
try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
except OSError:print('A full download job is already running.',flush=True);raise SystemExit(0)

commands={
 'ambientcg':[sys.executable,'-u',str(ROOT/'download.py'),'--all','--workers','4'],
 'polyhaven':[sys.executable,'-u',str(ROOT/'download_providers.py'),'polyhaven','--workers','2'],
 'sharetextures':[sys.executable,'-u',str(ROOT/'download_providers.py'),'sharetextures','--workers','2'],
}
logs={};active={};attempts={k:0 for k in commands};finished={};started=time.time()
def launch(name):
 attempts[name]+=1
 if name not in logs:logs[name]=(ROOT/(name+'-download.log')).open('ab',buffering=0)
 active[name]=subprocess.Popen(commands[name],cwd=str(ROOT.parent.parent),stdout=logs[name],stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
def status():
 atomic_json(ROOT/'run.json',{'pid':os.getpid(),'startedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'running':{k:v.pid for k,v in active.items()},'attempts':attempts,'finished':finished,'elapsedSeconds':round(time.time()-started),'state':'running' if active else 'complete' if all(v==0 for v in finished.values()) else 'finished-with-pending'})
try:
 for name in commands:launch(name)
 status()
 while active:
  for name,process in list(active.items()):
   code=process.poll()
   if code is None:continue
   del active[name]
   if code and attempts[name]<3:
    time.sleep(15);launch(name)
   else:finished[name]=code
  status();time.sleep(5)
finally:
 for log in logs.values():log.close()
 lock.close()
