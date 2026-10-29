from pathlib import Path
import hashlib, base64, subprocess, os, json, re
root=Path('E:/l2-local')
def props(path):
    return {k.strip():v.strip() for line in path.read_text(encoding='utf-8-sig').splitlines() if '=' in line and not line.lstrip().startswith(('#',';')) for k,v in [line.split('=',1)]}
private=Path(root/'research/camera-observer/ACCESO-PRIVADO.txt').read_text(encoding='utf-8-sig')
password=re.search(r'^Contrasena:\s*(\S+)\s*$',private,re.M).group(1)
digest=base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
cfg=props(root/'server/game/config/CameraObserver.properties')
outputs={}
for kind in ['login','game']:
    db=props(root/f'server/{kind}/config/Database.ini')
    url=re.search(r'jdbc:mysql://([^:/]+):(\d+)/([^?]+)',db['URL'])
    env=os.environ.copy();env['MYSQL_PWD']=db['Password']
    query="SELECT login,password,accessLevel FROM accounts WHERE login='nexuscamera';"
    proc=subprocess.run([str(root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'),'-h',url[1],'-P',url[2],'-u',db['Login'],'-N','-B',url[3],'-e',query],env=env,capture_output=True,text=True,check=True)
    rows=[line.split('\t') for line in proc.stdout.splitlines()]
    outputs[kind]={'database':url[3],'rows':len(rows),'password_matches_file':len(rows)==1 and rows[0][1]==digest,'access_level':rows[0][2] if rows else None}
print(json.dumps({'password_length':len(password),'file_matches_observer_config':cfg['PasswordHash']==digest,'databases':outputs},indent=2))
