"""Repair only the isolated client's Behemoth assets; never rebuild core/server."""
import pathlib,sys,copy,subprocess,shutil,json,hashlib
R=pathlib.Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/amber-l2/scripts'))
from contract_dat import Catalog
codec=LAB/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(args):subprocess.run([str(a) for a in args],check=True,capture_output=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
main=LAB.parent/'l2/system-hud/npcgrp.dat';before=sha(main)
run([codec,'-o',R/'npcgrp.3mat-base.raw',main])
cat=Catalog(R/'npcgrp.3mat-base.raw','npcgrp.xml','Interlude')
assert not any(r['npc_id']==59091 for r in cat.rows)
row=copy.deepcopy(next(r for r in cat.rows if r['npc_id']==29069))
row.update(npc_id=59091,class_name='LineageMonster3.antaras_ex_a',mesh_name='BHMTransport.BehemothMesh',texture_name=3,texture_name_items=[{'param_texture_name':f'BHMTransport.Mat{i}'} for i in range(3)],deco_effect=0,deco_effect_items=[],attack_effect='')
cat.append([row],R/'npcgrp.3mat.raw')
check=Catalog(R/'npcgrp.3mat.raw','npcgrp.xml','Interlude');new=check.rows[-1]
assert new['texture_name']==3 and len(new['texture_name_items'])==3
assert all(check.data[a['_start']:a['_end']]==cat.data[b['_start']:b['_end']] for a,b in zip(check.rows,cat.rows))
run([codec,'-c','encode','-p','413','-o',R/'npcgrp.3mat.dat',R/'npcgrp.3mat.raw'])
run([codec,'-o',R/'npcgrp.3mat-roundtrip.raw',R/'npcgrp.3mat.dat'])
assert (R/'npcgrp.3mat.raw').read_bytes()==(R/'npcgrp.3mat-roundtrip.raw').read_bytes()
system=R/'client-lab/system'
shutil.copy2(R/'npcgrp.3mat.dat',system/'npcgrp.dat');shutil.copy2(R/'BHMTransport.u',system/'BHMTransport.u')
assert before==sha(main)
report={'textureSlots':3,'maximumTextureIndex':2,'clientAssertionLimit':5,'originalRowsPreserved':cat.count,'datRoundtrip':True,'mainClientUnchanged':True,'packageSHA256':sha(R/'BHMTransport.u'),'installedPackageMatches':sha(R/'BHMTransport.u')==sha(system/'BHMTransport.u'),'nativeClientVerified':False}
(R/'texture-limit-fix.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for filename in ['native-build-report.json','client-installation.json']:
 p=R/filename;data=json.loads(p.read_text(encoding='utf-8'));data['textureSlots']=3;data['nativeClientVerified']=False
 if filename=='native-build-report.json':data['sha256']=report['packageSHA256']
 else:data['packageSHA256']=report['packageSHA256']
 p.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(report))
