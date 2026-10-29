"""Task-owned REA stdio session; no Codex or REA registration/config changes."""
from pathlib import Path
import subprocess,os,json,threading,queue,sys,time
S=Path(__file__).resolve().parent;R=S.parents[1]
env=os.environ.copy();env['JAVA_HOME']=str(R/'tools/jdk-25.0.4.1+1');env['GHIDRA_INSTALL_DIR']=str(R/'tools/ghidra_12.1.4_PUBLIC')
env['PATH']=str(R/'tools/node-v24.22.0-win-x64')+os.pathsep+str(R/'tools/jdk-25.0.4.1+1/bin')+os.pathsep+env.get('PATH','')
env['REA_ANALYSIS_PROVIDER']='ghidra';env['REA_GHIDRA_STARTUP_TIMEOUT_MS']='1200000'
env['REA_GHIDRA_DISABLED_ANALYZERS']='Decompiler Parameter ID,Stack,Decompiler Switch Analysis'
stderr=(S/'session-stderr.log').open('w',encoding='utf-8')
p=subprocess.Popen([str(R/'tools/node-v24.22.0-win-x64/node.exe'),str(R/'tools/rea-runtime/node_modules/rea-agents/scripts/rea.mjs'),'mcp'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,encoding='utf-8',bufsize=1,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
q=queue.Queue()
def reader():
 for line in p.stdout:
  try:q.put(json.loads(line))
  except ValueError:
   with (S/'non-json-stdout.log').open('a',encoding='utf-8') as f:f.write(line)
 q.put({'process_exit':p.poll()})
threading.Thread(target=reader,daemon=True).start()
serial=0
def send(obj):p.stdin.write(json.dumps(obj)+'\n');p.stdin.flush()
def request(method,params,label,timeout=1250):
 global serial
 serial+=1;ident=serial;send({'jsonrpc':'2.0','id':ident,'method':method,'params':params});start=time.monotonic()
 while True:
  try:message=q.get(timeout=20)
  except queue.Empty:
   print(json.dumps({'waiting':label,'seconds':round(time.monotonic()-start)}),flush=True)
   if time.monotonic()-start>timeout:raise TimeoutError(label)
   continue
  if message.get('id')==ident:
   (S/(label+'.json')).write_text(json.dumps(message,ensure_ascii=False,indent=2),encoding='utf-8')
   return message
  if 'process_exit' in message:raise RuntimeError(message)
  with (S/'notifications.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(message)+'\n')
try:
 init=request('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'l2-sticker-investigation','version':'1'}},'initialize')
 send({'jsonrpc':'2.0','method':'notifications/initialized'})
 opened=request('tools/call',{'name':'open_binary','arguments':{'path':'E:\\l2\\system-hud\\Engine.dll','provider_id':'ghidra'}},'engine-open')
 print(json.dumps({'opened':opened.get('result',opened)},ensure_ascii=False),flush=True)
 result=request('tools/call',{'name':'search_procedures','arguments':{'pattern':'MagicSkill','case_sensitive':False}},'magic-procedures')
 print(json.dumps(result,ensure_ascii=False),flush=True)
 print('REA_READY: reading task-owned commands.jsonl; {quit:true} closes the owned session.',flush=True)
 processed=0;stop=False
 while not stop:
  commands=S/'commands.jsonl'
  lines=commands.read_text(encoding='utf-8').splitlines() if commands.exists() else []
  for line in lines[processed:]:
   command=json.loads(line);processed+=1
   if command.get('quit'):stop=True;break
   reply=request('tools/call',{'name':command['tool'],'arguments':command.get('arguments',{})},command['label'])
   body=reply.get('result',{}).get('structuredContent')
   if not body and reply.get('result',{}).get('content'):
    try:body=json.loads(reply['result']['content'][0]['text'])
    except Exception:body=reply
   print(json.dumps({'completed':command['label'],'result':body.get('normalized_result',body) if isinstance(body,dict) else body},ensure_ascii=False),flush=True)
  if not stop:time.sleep(.5)
finally:
 p.terminate()
 try:p.wait(timeout=20)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 stderr.close()
