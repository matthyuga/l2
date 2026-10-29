from pathlib import Path
import sys,subprocess,json,hashlib
R=Path(__file__).parent;P=R.parents[2];L=P/'research/dust2-animation-study/client-lab';B=R/'stage';B.mkdir(exist_ok=True);target=L/'system/npcgrp.dat'
sys.path.insert(0,str(R.parent/'items'));from catalog_weapon import Catalog
codec=str(P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):subprocess.run(a,capture_output=True,check=True)
expected=json.loads((R.parent/'v4-build/installation.json').read_text())['after_sha256'];assert sha(target)==expected,'Concurrent catalog edits'
run([codec,'-o',str(B/'npcgrp.before.raw'),str(target)]);cat=Catalog(B/'npcgrp.before.raw','npcgrp.xml','Interlude');data=cat.data
for id,mesh in [(59084,'CycleMesh'),(59083,'RifleMesh')]:
 row=next(x for x in cat.rows if x['npc_id']==id);row.update(mesh_name='HGRifleV5.'+mesh,texture_name=2,texture_name_items=[{'param_texture_name':'HGRifleV5.BodyAtlas'},{'param_texture_name':'HGRifleV5.RifleAtlas'}]);data=data[:row['_start']]+cat.encode(row)+data[row['_end']:]
(B/'npcgrp.after.raw').write_bytes(data);test=Catalog(B/'npcgrp.after.raw','npcgrp.xml','Interlude');assert test.count==cat.count
for a,b in zip(cat.rows,test.rows):
 if a['npc_id'] not in [59083,59084]:assert cat.data[a['_start']:a['_end']]==test.data[b['_start']:b['_end']]
run([codec,'-c','encode','-p','413','-o',str(B/'npcgrp.dat'),str(B/'npcgrp.after.raw')]);run([codec,'-o',str(B/'npcgrp.check.raw'),str(B/'npcgrp.dat')]);assert(B/'npcgrp.check.raw').read_bytes()==data
files=[{'source':str(R/(n+'.ukx')),'target':str(L/'animations'/(n+'.ukx')),'sha256':sha(R/(n+'.ukx'))} for n in ['HGRifleV5','HGRifleMotionV5','HGRifleCycleV5']]
m={'client_catalog':str(target),'before_sha256':expected,'after_sha256':sha(B/'npcgrp.dat'),'source':str(B/'npcgrp.dat'),'previous_rows':cat.count,'new_rows':0,'only_existing_rows_changed':[59083,59084],'other_records_byte_exact':True,'files':files,'runtime_validated':False};(R/'stage-manifest.json').write_text(json.dumps(m,indent=2));print('V5_STAGED 2rows only')
