from pathlib import Path
import subprocess, os, re, hashlib, json, sys
root=Path(__file__).resolve().parents[2]
cfg=(root/'server/game/config/Database.ini').read_text(encoding='utf-8-sig')
def val(key): return re.search(r'^'+key+r'\s*=\s*(.*)$',cfg,re.M).group(1).strip()
env=os.environ.copy();env['MYSQL_PWD']=val('Password')
cli=root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'
def query(sql):
    return subprocess.run([str(cli),'--host=127.0.0.1','--port=3307','--user='+val('Login'),'-N','-B','l2jmobiusinterlude','-e',sql],env=env,check=True,capture_output=True).stdout
char_id=int(query("SELECT charId FROM characters WHERE char_name='AmberOwnerProbe' AND account_name='ambercontracttest'"))
data={}
for table in ('character_skills','character_subclasses','character_shortcuts'):
    rows=query(f'SELECT * FROM {table} WHERE charId={char_id} ORDER BY 1,2,3')
    data[table]={'rows':len(rows.splitlines()),'sha256':hashlib.sha256(rows).hexdigest()}
target=root/'research/client-comfort/probe-before.json'
if sys.argv[1]=='before': target.write_text(json.dumps(data,indent=2),encoding='utf-8')
else:
    assert data==json.loads(target.read_text()),data
    print('PASS: reserved probe database skills, subclasses and shortcuts unchanged.')
print(json.dumps(data,indent=2))
