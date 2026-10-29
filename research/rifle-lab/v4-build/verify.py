import sys,subprocess,json
from pathlib import Path
from PIL import Image
R=Path(__file__).parent;sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native');from write_l2_animation import psa,chunks
U=r'E:\l2-local\research\amber-l2\tools\umodel.exe';states=json.loads((R/'states.json').read_text());selectors={'peace_idle':['wait_Hand','Wait_1HS'],'combat_idle':['AtkWait_Hand','AtkWait_1HS'],'walk':['walk_hand','Walk_1HS'],'run':['Run_Hand','Run_1HS'],'aim':['Social01','SpWait01'],'fire':['atk01_Hand','Atk01_1HS']}
reports=[]
for pkg,mesh in [('HGRifleV4','RifleMesh'),('HGRifleMotionV4',None)]+[(s['package'],None) for s in states]:
 args=[U,'-game=l2','-path='+str(R),'-out='+str(R/'roundtrip'),'-export',str(R/(pkg+'.ukx'))]+([mesh] if mesh else [])
 p=subprocess.run(args,capture_output=True,text=True,timeout=90);(R/(pkg+'-verify.log')).write_text(p.stdout+p.stderr);assert p.returncode==0 and '*** ERROR' not in p.stdout+p.stderr,pkg
 if mesh:
  c=chunks(R/'roundtrip'/pkg/'SkeletalMesh/RifleMesh.psk');a=chunks(R.parent/'v4-textures/RifleNPCV4.psk');assert c['FACE0000'][1]==a['FACE0000'][1] and c['REFSKELT'][2]==a['REFSKELT'][2]
  for mat,source in [('BodyAtlas',R.parent/'v4-textures/BodyAtlas.tga'),('RifleAtlas',R.parent/'build/RifleAtlas.tga')]:
   x=Image.open(source).convert('RGBA');y=Image.open(R/'roundtrip'/pkg/'Texture'/(mat+'.tga')).convert('RGBA');assert x.tobytes()==y.tobytes(),mat
  reports.append({'package':pkg,'faces':c['FACE0000'][1],'bones':c['REFSKELT'][1],'textures_rgba_exact':True})
 else:
  path=R/'roundtrip'/pkg/'MeshAnimation/Dust2Motion.psa'
  entries=[(s,n) for s in states for n in selectors[s['state']]] if pkg=='HGRifleMotionV4' else [(next(s for s in states if s['package']==pkg),'wait_Hand')]
  for s,n in entries:
   a=psa(s['psa']);b=psa(path,n);assert len(a['frames'])==len(b['frames']) and a['fps']==b['fps'];err=max(abs(x-y) for f,g in zip(a['frames'],b['frames']) for k in ['positions','rotations'] for v,w in zip(f[k],g[k]) for x,y in zip(v,w));assert err<1e-6,(pkg,n,err);reports.append({'package':pkg,'sequence':n,'frames':len(a['frames']),'max_transform_error':err})
(R/'native-validation.json').write_text(json.dumps(reports,indent=2));print('V4_NATIVE_PASS',len(reports),'checks')
