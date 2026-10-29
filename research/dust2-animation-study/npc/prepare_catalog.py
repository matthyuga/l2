import pathlib,sys,subprocess,copy,json,shutil,hashlib
R=pathlib.Path(__file__).parent;L=R.parent/'client-lab';S=L/'system';sys.path.insert(0,r'E:\l2-local\research\amber-l2\scripts')
from contract_dat import Catalog
codec=r'E:\l2-local\tools\open-l2encdec-1.3.9\l2encdec_win.exe'
def run(args):subprocess.run(args,check=True,capture_output=True)
run([codec,'-o',str(R/'npcgrp.before.raw'),str(S/'npcgrp.dat')]);cat=Catalog(R/'npcgrp.before.raw','npcgrp.xml','Interlude')
assert not any(r['npc_id']==59080 for r in cat.rows)
row=copy.deepcopy(next(r for r in cat.rows if r['npc_id']==59001))
row.update(npc_id=59080,class_name='LineageNPC.a_traderB_FHuman',mesh_name='Dust2DemoNPC.DemoMesh',texture_name=1,texture_name_items=[{'param_texture_name':'Dust2DemoNPC.DemoClay'}],texture_name_second=0,texture_name_second_items=[])
cat.append([row],R/'npcgrp.after.raw')
run([codec,'-c','encode','-p','413','-o',str(R/'npcgrp.dat'),str(R/'npcgrp.after.raw')]);run([codec,'-o',str(R/'npcgrp.roundtrip.raw'),str(R/'npcgrp.dat')]);assert (R/'npcgrp.roundtrip.raw').read_bytes()==(R/'npcgrp.after.raw').read_bytes()
# Only lab profile, client is closed before installation.
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-Process -Name L2 -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True);assert check.stdout.strip()=='0','Close L2 before lab files change'
shutil.copy2(S/'npcgrp.dat',R/'npcgrp.before.dat');shutil.copy2(R/'npcgrp.dat',S/'npcgrp.dat')
for name in ['Dust2DemoNPC.ukx','Dust2DemoMotion.ukx']:shutil.copy2(R/name,L/'animations'/name)
(R/'client-installation.json').write_text(json.dumps({'npc_display_id':59080,'original_count':cat.count,'records_added':1,'all_previous_record_bytes_preserved':True,'only_lab_profile':True,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'npcgrp.dat',L/'animations/Dust2DemoNPC.ukx',L/'animations/Dust2DemoMotion.ukx']}},indent=2))
print('Installed isolated NPC display59080, prior records preserved',cat.count)
