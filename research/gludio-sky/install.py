"""Install the validated dock only with client/GameServer closed; record rollback first."""
from package_tools import *
import json,hashlib,shutil,datetime,subprocess,re
D=pathlib.Path(__file__).resolve().parent;CLIENT=ROOT.parent/'l2';stage=D/'stage';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not (D/'installation.json').exists(),'Already installed: review manifest instead of reapplying historical installer.'
check=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){Write-Output 'CLIENT'}; if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){Write-Output 'SERVER'}"],text=True)
assert not check.strip(),'Close client and GameServer before installation: '+check
deps=json.loads((D/'dependency-audit.json').read_text());assert not deps['missing'],deps['missing']
build=json.loads((D/'build-audit.json').read_text());geo=json.loads((D/'geodata-audit.json').read_text())
assert sha(CLIENT/'maps/24_19.unr')==build['source_hashes'][str(CLIENT/'maps/24_19.unr')],'Map changed concurrently'
assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==geo['source_sha256'],'Geo changed concurrently'
for item in json.loads((D/'server-source-hashes.json').read_text()):
    assert sha(ROOT/'server/game'/item['relative'])==item['sha256'],'Server config changed concurrently'
files=[]
for item in json.loads((D/'wrapper-proof.json').read_text()):
    p=D/'client'/item['relative'];assert sha(p)==item['sha256'] and item['crc_verified'] and item['roundtrip']
    target=CLIENT/item['relative'];assert not target.exists() or item['relative']=='Maps/24_19.unr','New package name already exists: '+str(target)
    files.append((target,p.read_bytes()))
files.append((ROOT/'server/game/data/geodata/24_19.l2j',(stage/'Geodata/24_19.l2j').read_bytes()))
for p in (stage/'server').rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(stage/'server');files.append((ROOT/'server/game'/rel,p.read_bytes()))
    for mirror in [ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
        target=mirror/rel;data=p.read_bytes()
        if rel.as_posix()=='config/Custom/StartingLocation.ini' and target.exists():
            text=target.read_text(encoding='utf-8-sig')
            for k,v in [('CustomStartingLocation','True'),('CustomStartingLocX','149000'),('CustomStartingLocY','46700'),('CustomStartingLocZ','12040')]:
                text,n=re.subn(r'(?m)^'+k+r'\s*=.*$',k+' = '+v,text);assert n==1
            data=text.encode('utf-8')
        elif rel.as_posix()=='config/Custom/WorldContent.ini' and target.exists():
            text=target.read_text(encoding='utf-8-sig');assert 'GludioSky' not in text
            text,n=re.subn(r'(?m)^(CustomScriptFolders\s*=\s*)([^\r\n]+)',lambda m:m[1]+m[2]+';GludioSky',text);assert n==1;data=text.encode('utf-8')
        files.append((target,data))
backup=ROOT/'backups'/('gludio-sky-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest={'date':datetime.datetime.now().isoformat(),'backup':str(backup),'files':[],'client_visual_verified':False}
def record():
    text=json.dumps(manifest,indent=2);(backup/'manifest.json').write_text(text);(D/'installation.json').write_text(text)
record()
for target,data in files:
    exists=target.exists();rel=target.relative_to(CLIENT) if target.is_relative_to(CLIENT) else target.relative_to(ROOT)
    saved=backup/('client' if target.is_relative_to(CLIENT) else 'project')/rel
    if exists:saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
    item=dict(target=str(target),existed=exists,backup=str(saved) if exists else None,before_sha256=sha(target) if exists else None,after_sha256=hashlib.sha256(data).hexdigest())
    manifest['files'].append(item);record();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);assert sha(target)==item['after_sha256']
print(json.dumps({'installed':len(files),'backup':str(backup),'spawn':geo['spawn'],'existing_players':'.muelle'},indent=2))
