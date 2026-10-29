"""Install reviewed stage with hash guards, backups and rollback on copy failure."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
CLIENT=PROJECT.parent/'l2/system-hud'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def client_closed():
    p=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){exit 5}"],capture_output=True)
    assert p.returncode==0,'Close L2 before installing client catalogs'

def main():
    client_closed()
    manifest=json.loads((ROOT/'manifest.json').read_text())
    changes=[]
    for name,entry in manifest['catalogs'].items():
        target=CLIENT/(name+'.dat');assert sha(target)==entry['before_encoded_sha256'],f'Concurrent edit: {target}'
        stage=ROOT/'stage'/(name+'.dat');assert sha(stage)==entry['after_encoded_sha256']
        changes.append((stage,target))
    for asset in (ROOT/'System_Fafurion_Weapons/System').glob('*.u'):
        target=CLIENT/asset.name;assert not target.exists(),f'Asset already exists: {target}'
        changes.append((asset,target))
    for folder in ['server/game/data/stats/items','source/L2J_Mobius_CT_0_Interlude/dist/game/data/stats/items',
                   'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/stats/items']:
        target=PROJECT/folder/'54100-54199.xml';assert not target.exists(),f'XML already exists: {target}'
        changes.append((ROOT/'stage/54100-54199.xml',target))
    backup=PROJECT/'backups'/('fafurion-weapons-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True)
    records=[]
    for i,(stage,target) in enumerate(changes):
        previous=None
        if target.exists():
            previous=backup/f'{i:02d}-{target.name}';shutil.copy2(target,previous)
        records.append({'target':str(target),'backup':str(previous) if previous else None,
                        'before_sha256':sha(target) if previous else None,'after_sha256':sha(stage)})
    (backup/'files.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    try:
        client_closed()
        for (stage,target),record in zip(changes,records):
            assert (sha(target) if target.exists() else None)==record['before_sha256'],f'Concurrent edit: {target}'
        for stage,target in changes:
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage,target)
        for record in records:assert sha(record['target'])==record['after_sha256']
    except Exception:
        for record in reversed(records):
            target=Path(record['target'])
            if target.exists() and sha(target)==record['after_sha256']:
                if record['backup']:shutil.copy2(record['backup'],target)
                else:target.unlink()
        raise
    (ROOT/'installation.json').write_text(json.dumps({'backup':str(backup),'files':records},indent=2),encoding='utf-8')
    print('INSTALLED '+str(backup))

if __name__=='__main__':main()
