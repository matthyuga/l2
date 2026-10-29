from pathlib import Path
import subprocess,os,re,sys
root=Path(__file__).resolve().parents[2]
cfg=(root/'server/game/config/Database.ini').read_text(encoding='utf-8-sig')
def value(key):return re.search(r'^'+key+r'\s*=\s*(.*)$',cfg,re.M).group(1).strip()
env=os.environ.copy();env['MYSQL_PWD']=value('Password')
q="SELECT c.char_name,c.clanid,COALESCE(d.clan_name,''),c.online,c.x,c.y,c.z FROM characters c LEFT JOIN clan_data d ON d.clan_id=c.clanid WHERE c.char_name IN ('Hellkevin','ArenaNoctis','Noctis','ArenaRiven')"
if len(sys.argv)>1:q=sys.argv[1]
r=subprocess.run([str(root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'),'--host=127.0.0.1','--port=3307','--user='+value('Login'),'-B','l2jmobiusinterlude','-e',q],env=env,capture_output=True,check=True)
print(r.stdout.decode(errors='replace'))
