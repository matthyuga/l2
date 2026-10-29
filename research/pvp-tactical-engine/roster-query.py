from pathlib import Path
import os,subprocess
r=Path('E:/l2-local');cfg={}
for line in (r/'server/game/config/Database.ini').read_text().splitlines():
 if '=' in line and not line.strip().startswith('#'):
  k,v=line.split('=',1);cfg[k.strip()]=v.strip()
env=os.environ.copy();env['MYSQL_PWD']=cfg['Password']
sql="SELECT c.charId,c.char_name,c.classid,c.online FROM characters c WHERE c.account_name LIKE 'telemetry%' AND (EXISTS(SELECT 1 FROM lab_normal_npc_profiles p WHERE p.char_id=c.charId) OR EXISTS(SELECT 1 FROM lab_real_human_pilots p WHERE p.char_id=c.charId)) ORDER BY c.classid,c.charId"
x=subprocess.run([str(r/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'),'--host=127.0.0.1','--port=3307','--user='+cfg.get('Login','root'),'--batch','--execute',sql,'l2jmobiusinterlude'],env=env,capture_output=True,text=True,timeout=15)
print(x.stdout);assert x.returncode==0,x.stderr
