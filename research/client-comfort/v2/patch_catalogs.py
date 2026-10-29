from pathlib import Path
import sys,struct,subprocess,hashlib,json
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'research/amber-l2/scripts'))
from contract_dat import Catalog
client=root.parent/'l2/system-hud';stage=Path(__file__).resolve().parent
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';report={}
def run(*args):subprocess.run([str(codec),*map(str,args)],check=True,capture_output=True)
for name,schema in [('skillgrp','skillgrp.xml'),('skillname-e','skillname.xml')]:
    before=stage/(name+'.before.raw');run('-o',before,client/(name+'.dat'));cat=Catalog(before,schema,'ScionsOfDestiny')
    wanted=[r for r in cat.rows if r['skill_id']==19014 and r['skill_level']==1];assert len(wanted)==1
    record=dict(wanted[0])
    if name=='skillgrp':record['icon']='AmberAssistIconsV1.Assist'
    else:record['desc']='IA de Amber: un clic enciende y otro apaga. Protege al amo, prioriza summons del agresor y evalua curanderos. Icono IA visible tambien en el summon. Sin coste de MP; Seguir/Detener la apagan.'
    out=bytearray(cat.data[:4])
    for row in cat.rows:out+=cat.encode(record) if row is wanted[0] else cat.data[row['_start']:row['_end']]
    out+=cat.data[cat.end:];raw=stage/(name+'.raw');raw.write_bytes(out)
    encoded=stage/(name+'.dat');run('-c','encode','-p','413','-o',encoded,raw)
    roundtrip=stage/(name+'.roundtrip.raw');run('-o',roundtrip,encoded);assert roundtrip.read_bytes()==out
    verified=Catalog(roundtrip,schema,'ScionsOfDestiny');assert verified.count==cat.count
    for old,new in zip(cat.rows,verified.rows):
        if old['skill_id']!=19014:assert cat.data[old['_start']:old['_end']]==verified.data[new['_start']:new['_end']]
    report[name]={'count':cat.count,'only_changed_skill':19014,'other_records_identical':True,'roundtrip':True,'sha256':hashlib.sha256(encoded.read_bytes()).hexdigest()}
(stage/'catalog-verification.json').write_text(json.dumps(report,indent=2));print('PASS: only Amber IA icon/tooltip changed; all previous skills/V10 effects preserved byte for byte.')
