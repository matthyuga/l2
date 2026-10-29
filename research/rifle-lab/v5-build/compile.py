from pathlib import Path
import sys,subprocess,json
from PIL import Image
R=Path(__file__).parent;E=Path(r'E:\l2-local\research\amber-l2\tools\l2editor\L2Editor');sys.path.insert(0,str(R.parent/'v4-motion'));from write_multi_animation import generate
states=json.loads((R/'states.json').read_text());selectors={'peace_idle':['wait_Hand','Wait_1HS'],'combat_idle':['AtkWait_Hand','AtkWait_1HS'],'walk':['walk_hand','Walk_1HS'],'run':['Run_Hand','Run_1HS'],'aim':['Social01','SpWait01'],'fire':['atk01_Hand','Atk01_1HS']};report=generate([{'psa':s['psa'],'name':n} for s in states for n in selectors[s['state']]],R/'HGRifleMotionV5.ukx',R/'RifleNPCV5.psk');(R/'motion-build.json').write_text(json.dumps(report,indent=2));generate([{'psa':str(R/'continuous.psa'),'name':'wait_Hand'}],R/'HGRifleCycleV5.ukx',R/'RifleNPCV5.psk')
Image.open(R.parent/'v4-textures/BodyAtlas.tga').convert('RGB').save(R/'BodyAtlas.tga')
cmds=[]
for name in ['RifleMesh','CycleMesh']:
 cmds += [f'#exec MESH MODELIMPORT MESH={name} MODELFILE="{(R/"RifleNPCV5.psk").as_posix()}" LODSTYLE=0 LODSPECIFY=1',f'#exec MESH LODMODEL MESH={name} LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1',f'#exec MESHMAP SCALE MESHMAP={name} X=1 Y=1 Z=1',f'#exec MESH ORIGIN MESH={name} X=0 Y=0 Z=25 YAW=192']
for mat,path in [('BodyAtlas',R/'BodyAtlas.tga'),('RifleAtlas',R.parent/'build/RifleAtlas.tga')]:cmds.append(f'#exec TEXTURE IMPORT NAME={mat} FILE="{path.as_posix()}" MIPS=ON')
for name in ['RifleMesh','CycleMesh']:
 for i,mat in enumerate(['BodyAtlas','RifleAtlas']):cmds.append(f'#exec MESHMAP SETTEXTURE MESHMAP={name} NUM={i} TEXTURE={mat}')
pkg='HGRifleV5';C=E.parent/pkg/'Classes';C.mkdir(parents=True,exist_ok=True);(C/'AssetActor.uc').write_text('class AssetActor extends Actor;\n'+'\n'.join(cmds)+'\n');(E/(pkg+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={pkg}\n',encoding='latin1');assert not(E/(pkg+'.u')).exists()
with (R/'compile.log').open('w') as log:p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+pkg+'.ini'],cwd=E,stdout=log,stderr=subprocess.STDOUT,timeout=180)
assert p.returncode==0;print('V5_COMPILED')
