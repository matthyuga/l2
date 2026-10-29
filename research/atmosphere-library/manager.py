import datetime,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parent
def save(obj):
 tmp=ROOT/'run.tmp';tmp.write_text(json.dumps(obj,indent=2),encoding='utf8');tmp.replace(ROOT/'run.json')
if __name__=='__main__':
 state={'pid':os.getpid(),'started':datetime.datetime.now().isoformat(),'status':'running','workers':[]}
 workers=[]
 for name in ['download','polyhaven']:
  log=(ROOT/(name+'.log')).open('a',encoding='utf8')
  p=subprocess.Popen([sys.executable,'-u',str(ROOT/(name+'.py'))],cwd=str(ROOT),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  workers.append((name,p,log));state['workers'].append({'name':name,'pid':p.pid})
 save(state)
 while any(p.poll() is None for _,p,_ in workers):time.sleep(2)
 for name,p,log in workers:
  log.close()
  for record in state['workers']:
   if record['name']==name:record['exit_code']=p.returncode
 state['status']='finished';state['finished']=datetime.datetime.now().isoformat();save(state)
