import sys,json,subprocess,shutil
from pathlib import Path
R=Path(__file__).parent;P=R.parent;M=P/'v4-motion';T=P/'v4-textures';B=P/'build';E=Path(r'E:\l2-local\research\amber-l2\tools\l2editor\L2Editor')
sys.path.insert(0,str(M));from write_multi_animation import generate
states=json.loads((M/'states.json').read_text());selectors={'peace_idle':['wait_Hand','Wait_1HS'],'combat_idle':['AtkWait_Hand','AtkWait_1HS'],'walk':['walk_hand','Walk_1HS'],'run':['Run_Hand','Run_1HS'],'aim':['Social01','SpWait01'],'fire':['atk01_Hand','Atk01_1HS']}
entries=[{'psa':s['psa'],'name':n} for s in states for n in selectors[s['state']]]
report=generate(entries,R/'HGRifleMotionV4.ukx',T/'RifleNPCV4.psk');(R/'motion-build.json').write_text(json.dumps(report,indent=2))
for s in states:
 s['package']='HGRifle'+''.join(x.title() for x in s['state'].split('_'))+'V4';s['mesh']='Mesh'+''.join(x.title() for x in s['state'].split('_'))
 generate([{'psa':s['psa'],'name':'wait_Hand'}],R/(s['package']+'.ukx'),T/'RifleNPCV4.psk')
(R/'states.json').write_text(json.dumps(states,indent=2))
cmds=[]
for name in ['RifleMesh']+[s['mesh'] for s in states]:
 cmds += [f'#exec MESH MODELIMPORT MESH={name} MODELFILE="{(T/"RifleNPCV4.psk").as_posix()}" LODSTYLE=0 LODSPECIFY=1',f'#exec MESH LODMODEL MESH={name} LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1',f'#exec MESHMAP SCALE MESHMAP={name} X=1 Y=1 Z=1',f'#exec MESH ORIGIN MESH={name} X=0 Y=0 Z=25 YAW=192']
cmds += [f'#exec TEXTURE IMPORT NAME=BodyAtlas FILE="{(T/"BodyAtlas.tga").as_posix()}" MIPS=ON FLAGS=2',f'#exec TEXTURE IMPORT NAME=RifleAtlas FILE="{(B/"RifleAtlas.tga").as_posix()}" MIPS=ON']
for name in ['RifleMesh']+[s['mesh'] for s in states]:
 for i,mat in enumerate(['BodyAtlas','RifleAtlas']):cmds.append(f'#exec MESHMAP SETTEXTURE MESHMAP={name} NUM={i} TEXTURE={mat}')
pkg='HGRifleV4';C=E.parent/pkg/'Classes';C.mkdir(parents=True,exist_ok=True);(C/'AssetActor.uc').write_text('class AssetActor extends Actor;\n'+'\n'.join(cmds)+'\n')
(E/(pkg+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={pkg}\n',encoding='latin1');assert not(E/(pkg+'.u')).exists()
with (R/'compile.log').open('w') as log:p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+pkg+'.ini'],cwd=E,stdout=log,stderr=subprocess.STDOUT,timeout=180)
assert p.returncode==0;print('COMPILED V4 mesh7 + animations7')
