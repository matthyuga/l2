from pathlib import Path
import sys,json,subprocess,hashlib,copy,struct
R=Path(__file__).parent;P=R.parents[2];L=P/'research/dust2-animation-study/client-lab';S=L/'system';B=R/'stage';B.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'items'));from catalog_weapon import Catalog
codec=str(P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run(a):subprocess.run(a,capture_output=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original=sha(S/'npcgrp.dat');expected=next(x for x in json.loads((R.parent/'build/mesh-v3-installation.json').read_text())['files'] if x['file']=='npcgrp')['after'];assert original==expected,'Concurrent catalog changes'
run([codec,'-o',str(B/'npcgrp.before.raw'),str(S/'npcgrp.dat')]);cat=Catalog(B/'npcgrp.before.raw','npcgrp.xml','Interlude');row=next(x for x in cat.rows if x['npc_id']==59083);row.update(mesh_name='HGRifleV4.RifleMesh',texture_name=2,texture_name_items=[{'param_texture_name':'HGRifleV4.BodyAtlas'},{'param_texture_name':'HGRifleV4.RifleAtlas'}]);raw=cat.data[:row['_start']]+cat.encode(row)+cat.data[row['_end']:];(B/'npcgrp.base.raw').write_bytes(raw);base=Catalog(B/'npcgrp.base.raw','npcgrp.xml','Interlude');parent=next(x for x in base.rows if x['npc_id']==59083);states=json.loads((R/'states.json').read_text());added=[]
for i,s in enumerate(states):
 id=59084+i;assert not any(x['npc_id']==id for x in base.rows);new=copy.deepcopy(parent);new.update(npc_id=id,mesh_name='HGRifleV4.'+s['mesh']);added.append(new);s['display_id']=id
base.append(added,B/'npcgrp.after.raw');run([codec,'-c','encode','-p','413','-o',str(B/'npcgrp.dat'),str(B/'npcgrp.after.raw')]);run([codec,'-o',str(B/'npcgrp.check.raw'),str(B/'npcgrp.dat')]);assert (B/'npcgrp.check.raw').read_bytes()==(B/'npcgrp.after.raw').read_bytes();after=Catalog(B/'npcgrp.after.raw','npcgrp.xml','Interlude');assert after.count==cat.count+6
for a,b in zip(cat.rows,after.rows):
 if a['npc_id']!=59083:assert cat.data[a['_start']:a['_end']]==after.data[b['_start']:b['_end']]
(R/'states.json').write_text(json.dumps(states,indent=2));files=[{'source':str(R/(n+'.ukx')),'target':str(L/'animations'/(n+'.ukx')),'sha256':sha(R/(n+'.ukx'))} for n in ['HGRifleV4','HGRifleMotionV4']+[s['package'] for s in states]]
manifest={'client_catalog':str(S/'npcgrp.dat'),'before_sha256':original,'after_sha256':sha(B/'npcgrp.dat'),'source':str(B/'npcgrp.dat'),'previous_rows':cat.count,'new_rows':6,'only_existing_row_changed':59083,'other_records_byte_exact':True,'files':files,'runtime_validated':False};(R/'stage-manifest.json').write_text(json.dumps(manifest,indent=2));print('STAGED',cat.count,'->',after.count)
