from pathlib import Path
import os,subprocess,re
root=Path('E:/l2-local');cfg={}
for line in (root/'server/game/config/Database.ini').read_text().splitlines():
    if '=' in line and not line.strip().startswith('#'):
        k,v=line.split('=',1);cfg[k.strip()]=v.strip()
env=os.environ.copy();env['MYSQL_PWD']=cfg['Password']
client=root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'
for sql in ['SHOW FULL PROCESSLIST',"SELECT char_name,online FROM characters WHERE online<>0 ORDER BY account_name,char_name"]:
    r=subprocess.run([str(client),'--host=127.0.0.1','--port=3307','--user='+cfg.get('Login',cfg.get('User','root')),'--batch','--execute',sql,'l2jmobiusinterlude'],env=env,capture_output=True,text=True,timeout=15)
    print(r.stdout);print(r.stderr if r.returncode else '')
