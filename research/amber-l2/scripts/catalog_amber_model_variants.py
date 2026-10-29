from pathlib import Path
import json,copy,subprocess,hashlib
from contract_dat import Catalog
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1];CLIENT=PROJECT.parent/'l2/system-hud';OUT=ROOT/'exports/mmd-variants-20261023';CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
manifest={}
for key,filename,schema in [('npcgrp','npcgrp.dat','npcgrp.xml'),('npcname','NpcName-e.dat','npcname.xml')]:
 before=OUT/(key+'.before.raw');subprocess.run([str(CODEC),'-o',str(before),str(CLIENT/filename)],check=True,capture_output=True)
 pattern='Interlude' if key=='npcgrp' else 'ScionsOfDestiny';idfield='npc_id' if key=='npcgrp' else 'id'
 cat=Catalog(before,schema,pattern);prototype=next(r for r in cat.rows if r[idfield]==59002);assert not any(r[idfield] in (59020,59021) for r in cat.rows),'Display ID collision'
 additions=[]
 for label,display in [('v10',59020),('v14',59021)]:
  row=copy.deepcopy(prototype);row[idfield]=display
  if key=='npcgrp':
   build=json.loads((OUT/label/'build.json').read_text());pkg=build['package']
   assert prototype['class_name']=='AmberActorsV1.AmberArcher','Preserve current actor attachment class'
   row['mesh_name']=pkg+'.AmberNPC';row['texture_name']=8;row['texture_name_items']=[{'param_texture_name':pkg+'.'+m['name']+'Shader'} for m in build['materials']]
   row['texture_name_second']=0;row['texture_name_second_items']=[]
  else:
   print('NPCNAME_FIELDS',list(row))
   row['name']='Amber MMD 1.0' if label=='v10' else 'Amber MMD 1.4'
   # Keep the title/color encoding already used by current Amber.
  additions.append(row)
 raw=OUT/(key+'.raw');cat.append(additions,raw)
 verified=Catalog(raw,schema,pattern);assert verified.count==cat.count+2
 assert verified.data[4:cat.end]==cat.data[4:cat.end] and verified.data[verified.end:]==cat.data[cat.end:]
 assert verified.rows[:cat.count]==cat.rows
 target=OUT/filename;subprocess.run([str(CODEC),'-c','encode','-p','413','-o',str(target),str(raw)],check=True,capture_output=True)
 roundtrip=OUT/(key+'.roundtrip.raw');subprocess.run([str(CODEC),'-o',str(roundtrip),str(target)],check=True,capture_output=True);assert raw.read_bytes()==roundtrip.read_bytes()
 manifest[filename]=dict(original_rows=cat.count,added_displays=[59020,59021],all_original_rows_preserved=True,encoded_roundtrip=True,before_sha256=hashlib.sha256((CLIENT/filename).read_bytes()).hexdigest(),staged_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
 print('PASS',filename,'appended2 records,',cat.count,'existing records preserved; exact413 roundtrip')
(OUT/'catalog-verification.json').write_text(json.dumps(manifest,indent=2))
