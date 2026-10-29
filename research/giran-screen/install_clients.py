from pathlib import Path
import subprocess,sys,json,copy,shutil,hashlib
D=Path(__file__).resolve().parent;root=D.parents[1];client=root.parent/'l2'
sys.path.insert(0,str(root/'research/rifle-lab/items'));from catalog_weapon import Catalog
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
backup=root/'backups/giran-screen-20261016';backup.mkdir(exist_ok=True)
manifest={'clients':[],'original_hud':{}}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['l2.ini','npcgrp.dat','L2.exe']:
 manifest['original_hud'][name]=sha(client/'system-hud'/name)
for role,folder in [('source',client/'system-camera-online'),('viewer',client/'system-screen-lab')]:
 assert (folder/'L2.exe').exists()
 if (folder/'d3d9.dll').exists():raise RuntimeError('Existing d3d9 proxy requires review: '+str(folder))
 saved=backup/role;saved.mkdir(exist_ok=True)
 for name in ['npcgrp.dat','l2.ini']:
  if not (saved/name).exists():shutil.copy2(folder/name,saved/name)
 before=D/(role+'-npcgrp.before.raw');after=D/(role+'-npcgrp.after.raw');encoded=D/(role+'-npcgrp.dat')
 subprocess.run([str(codec),'-o',str(before),str(folder/'npcgrp.dat')],capture_output=True,check=True)
 cat=Catalog(before,'npcgrp.xml','Interlude');assert not any(r['npc_id']==59890 for r in cat.rows)
 row=copy.deepcopy(next(r for r in cat.rows if r['npc_id']==31523))
 row.update(npc_id=59890,mesh_name='NexusTVAssets.Screen',texture_name=2,texture_name_items=[{'param_texture_name':'NexusTVAssets.ScreenMaterial'},{'param_texture_name':'NexusTVAssets.frame'}],deco_effect=0,deco_effect_items=[],attack_effect='')
 cat.append([row],after);verified=Catalog(after,'npcgrp.xml','Interlude')
 assert verified.count==cat.count+1 and after.read_bytes()[4:cat.end]==before.read_bytes()[4:cat.end]
 subprocess.run([str(codec),'-c','encode','-p','413','-o',str(encoded),str(after)],capture_output=True,check=True)
 check=D/(role+'-npcgrp.roundtrip.raw');subprocess.run([str(codec),'-o',str(check),str(encoded)],capture_output=True,check=True);assert check.read_bytes()==after.read_bytes()
 shutil.copy2(encoded,folder/'npcgrp.dat');shutil.copy2(D/'native/build/d3d9.dll',folder/'d3d9.dll')
 (folder/'NexusTV.ini').write_text('[NexusTV]\nMode='+role+'\n',encoding='ascii')
 manifest['clients'].append({'role':role,'folder':str(folder),'catalog_before':sha(saved/'npcgrp.dat'),'catalog_after':sha(folder/'npcgrp.dat'),'new_record':59890,'existing_records_byte_exact':True,'proxy_sha256':sha(folder/'d3d9.dll')})
resources=client/'nexus-tv';resources.mkdir(exist_ok=True)
assert not (resources/'NexusTVAssets.u').exists(),'Resource already exists; review'
shutil.copy2(D/'assets/NexusTVAssets.ukx',resources/'NexusTVAssets.u')
subprocess.run([str(root/'tools/node-v24.22.0-win-x64/node.exe'),str(D/'prepare_client_ini.cjs'),str(client/'system-camera-online'),str(client/'system-screen-lab')],check=True)
for name,digest in manifest['original_hud'].items():assert sha(client/'system-hud'/name)==digest
(D/'client-installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('PASS source/viewer installed; original HUD untouched; existing NPC catalog records preserved.')
