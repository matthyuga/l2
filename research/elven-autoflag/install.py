from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess
ROOT=Path('E:/l2-local');STAGE=Path(__file__).resolve().parent
manifest=STAGE/'installation.json'
if manifest.exists():raise SystemExit('Already installed; refusing baseline overwrite')
baseline=json.loads((STAGE/'baseline.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for r in baseline['files']:
    p=Path(r['path'])
    if p.exists()!=r['existed'] or (p.exists() and sha(p)!=r['before_sha256']):raise RuntimeError('Concurrent modification: '+str(p))
# Refuse to patch a JAR in use; command-line text stays private.
r=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -match 'GameServer\\.jar' }).Count"],capture_output=True,text=True)
if r.returncode or r.stdout.strip()!='0':raise RuntimeError('GameServer running or process check failed')
jar=ROOT/'server/libs/GameServer.jar';candidate=STAGE/'GameServer.candidate.jar'
classes={p.relative_to(STAGE/'compiled').as_posix():p for p in (STAGE/'compiled/org').rglob('*.class')}
assert set(classes)=={'org/l2jmobius/gameserver/entity/actor/Player.class','org/l2jmobius/gameserver/entity/actor/Player$1.class','org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager.class','org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager$SingletonHolder.class','org/l2jmobius/gameserver/entity/zone/type/FlagPvPZone.class'},set(classes)
with zipfile.ZipFile(jar) as old,zipfile.ZipFile(candidate,'w') as new:
    for entry in old.infolist():new.writestr(entry,classes[entry.filename].read_bytes() if entry.filename in classes else old.read(entry))
with zipfile.ZipFile(candidate) as z:
    assert z.testzip() is None
    for name,p in classes.items():assert z.read(name)==p.read_bytes()
    with zipfile.ZipFile(jar) as old:
        unchanged=[name for name in old.namelist() if name not in classes]
        assert all(z.read(name)==old.read(name) for name in unchanged)
rows=[]
for r in baseline['files']:
    p=Path(r['path'])
    if p==jar:src=candidate
    elif p.name=='PvpRooms.java':src=STAGE/'PvpRooms.java'
    else:
        rel=p.as_posix().split('L2J_Mobius_CT_0_Interlude/',1)[1]
        src=STAGE/'src'/rel
    p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p)
    rows.append({**r,'installed_sha256':sha(p)})
manifest.write_text(json.dumps({'backup':baseline['backup'],'files':rows,'core_class_entries':list(classes),'unchanged_jar_entries_verified':len(unchanged)},indent=2),encoding='utf-8')
print('Installed',len(rows),'files; replaced',len(classes),'core class entries; preserved',len(unchanged),'other entries')
