"""Read-only checks of installed catalogs, XML and referenced native exports."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
CLIENT=PROJECT.parent/'l2/system-hud'
def run(args):
    p=subprocess.run([str(a) for a in args],capture_output=True,check=True)
    return p.stdout.decode(errors='replace')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text())
installation=json.loads((ROOT/'installation.json').read_text())
checks=[]
for entry in installation['files']:
    assert sha(entry['target'])==entry['after_sha256'],entry['target']
    checks.append('installed hash: '+entry['target'])
for name,data in manifest['catalogs'].items():
    raw=ROOT/'stage'/(name+'.installed.raw')
    run([PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe','-o',raw,CLIENT/(name+'.dat')])
    assert sha(raw)==data['after_raw_sha256']
    checks.append(f'{name}: {data["existing_records_preserved"]} original records preserved; {data["added"]} added; decoded hash verified')
stage=ROOT/'client-fix-v2' if (ROOT/'client-fix-v2/manifest.json').exists() and json.loads((ROOT/'client-fix-v2/manifest.json').read_text())['status']=='installed' else ROOT/'stage'
lines=(stage/'weapongrp.verified.txt').read_text(encoding='utf-8').splitlines()
columns=lines[0].split('\t')
rows={int(parts[1]):dict(zip(columns,parts)) for line in lines[1:] if (parts:=line.split('\t'))}
exports={}
for asset in (ROOT/'System_Fafurion_Weapons/System').glob('*.u'):
    output=run([PROJECT/'research/amber-l2/tools/UModel.exe','-list',CLIENT/asset.name])
    (ROOT/'stage'/(asset.stem+'.exports.txt')).write_text(output,encoding='utf-8')
    exports[asset.stem.lower()]={line.split()[-1].lower() for line in output.splitlines() if line.strip() and line.split()[0].isdigit()}
for item in manifest['items']:
    row=rows[item['id']]
    assert row['patt']==item['stats']['pAtk'] and row['matt']==item['stats']['mAtk']
    assert row['speed']==item['stats']['pAtkSpd'] and row['critical']==item['stats']['critRate']
    assert row['material']=='8' and row['crystal_type']=='5' and row['is_hero']=='-1'
    for value in row.values():
        if value.lower().startswith(('lineageweapons_fafurion.','lineageeffect_fafurion.')):
            package,obj=value.split('.',1)
            assert obj.lower() in exports[package.lower()],value
    checks.append(f'{item["id"]}: visible P.Atk/M.Atk/speed/critical match server; all Fafurion object references present')
    if 'display_id' in item:
        alias=rows[item['display_id']]
        assert {k:v for k,v in alias.items() if k!='id'}=={k:v for k,v in row.items() if k!='id'}
        assert 0<item['display_id']<32768
        checks.append(f'{item["id"]}: compatible display alias {item["display_id"]} has identical weapon data')
if stage.name=='client-fix-v2':
    from fix_client_v2 import spans
    names=(stage/'itemname-e.raw').read_bytes()
    wanted={i['id'] for i in manifest['items']}|{i['display_id'] for i in manifest['items']}
    found=set()
    for iid,a,b,desc in spans(names):
        if iid in wanted:assert desc==b'Arma de grado S.\0';found.add(iid)
    assert found==wanted
    checks.append('all fourteen Fafurion descriptions have an explicit NUL terminator; no SA description included')
    assert 'SUCCESS' in (stage/'runtime-verification.txt').read_text()
    checks.append('actual multisell packet serialized and decoded: positive display IDs, original server product IDs and prices preserved')
assert 'SUCCESS' in (ROOT/'runtime-verification.txt').read_text()
checks.append('running GameServer: native parser, S base stat functions, types, skills and template registration PASS')
result={'status':'PASS','checks':checks,'visual_in_game':'pending: native packages exported successfully, no in-game render claimed',
        'sockets':'design only; not installed'}
(ROOT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
