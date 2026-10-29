from pathlib import Path
import json,hashlib,struct,subprocess,copy
from contract_dat import Catalog
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1];OUT=ROOT/'exports/mmd-variants-fix4-20261023';CLIENT=PROJECT.parent/'l2/system-hud';CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
before=OUT/'npcgrp.before.raw';subprocess.run([str(CODEC),'-o',str(before),str(CLIENT/'npcgrp.dat')],check=True,capture_output=True)
cat=Catalog(before,'npcgrp.xml','Interlude');chunks=[cat.data[:4]];changed=[]
for old in cat.rows:
 if old['npc_id'] not in (59020,59021):chunks.append(cat.data[old['_start']:old['_end']]);continue
 label='v10' if old['npc_id']==59020 else 'v14';build=json.loads((OUT/label/'build.json').read_text());row=copy.deepcopy(old);pkg=build['package']
 assert row['mesh_name']==pkg+'.AmberNPC'
 row['texture_name']=4;row['texture_name_items']=[{'param_texture_name':pkg+'.'+m['name']+'Shader'} for m in build['materials']]
 chunks.append(cat.encode(row));changed.append(old['npc_id'])
assert changed==[59020,59021]
chunks.append(cat.data[cat.end:]);raw=OUT/'npcgrp.raw';raw.write_bytes(b''.join(chunks));verified=Catalog(raw,'npcgrp.xml','Interlude');assert cat.count==verified.count
for old,new in zip(cat.rows,verified.rows):
 if old['npc_id'] not in changed:assert cat.data[old['_start']:old['_end']]==verified.data[new['_start']:new['_end']]
 else:assert new['texture_name']==4 and len(new['texture_name_items'])==4 and new['texture_name_second']==0
subprocess.run([str(CODEC),'-c','encode','-p','413','-o',str(OUT/'npcgrp.dat'),str(raw)],check=True,capture_output=True);roundtrip=OUT/'npcgrp.roundtrip.raw';subprocess.run([str(CODEC),'-o',str(roundtrip),str(OUT/'npcgrp.dat')],check=True,capture_output=True);assert raw.read_bytes()==roundtrip.read_bytes()
report=dict(changed_records=changed,record_count=cat.count,other_rows_preserved=cat.count-2,roundtrip=True,client_material_index_limit=5,before_sha256=hashlib.sha256((CLIENT/'npcgrp.dat').read_bytes()).hexdigest(),staged_sha256=hashlib.sha256((OUT/'npcgrp.dat').read_bytes()).hexdigest())
(OUT/'catalog-verification.json').write_text(json.dumps(report,indent=2));print('PASS: only2 Amber display records changed to4 slots; all other records preserved; exact413 roundtrip.')
