from pathlib import Path
import sys,json,subprocess,struct,collections
from PIL import Image
R=Path(__file__).parent;sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native');from write_l2_animation import psa,chunks
U=r'E:\l2-local\research\amber-l2\tools\umodel.exe';states=json.loads((R/'states.json').read_text());sel={'peace_idle':['wait_Hand','Wait_1HS'],'combat_idle':['AtkWait_Hand','AtkWait_1HS'],'walk':['walk_hand','Walk_1HS'],'run':['Run_Hand','Run_1HS'],'aim':['Social01','SpWait01'],'fire':['atk01_Hand','Atk01_1HS']};reports=[]
for pkg,obj in [('HGRifleV5','CycleMesh'),('HGRifleMotionV5',None),('HGRifleCycleV5',None)]:
 p=subprocess.run([U,'-game=l2','-path='+str(R),'-out='+str(R/'roundtrip'),'-export',str(R/(pkg+'.ukx'))]+([obj] if obj else []),capture_output=True,text=True,timeout=120);(R/(pkg+'-verify.log')).write_text(p.stdout+p.stderr);assert p.returncode==0 and '*** ERROR' not in p.stdout+p.stderr
 if obj:
  a=chunks(R/'RifleNPCV5.psk');b=chunks(R/'roundtrip'/pkg/'SkeletalMesh/CycleMesh.psk');assert a['REFSKELT'][2]==b['REFSKELT'][2] and a['FACE0000'][1]==b['FACE0000'][1]
  size,n,data=b['RAWWEIGHTS'];sums=collections.defaultdict(float)
  for i in range(n):v,p,bone=struct.unpack_from('<fii',data,i*size);sums[p]+=v
  assert len(sums)==b['PNTS0000'][1] and max(abs(v-1) for v in sums.values())<.0001
  for mat,src in [('BodyAtlas',R/'BodyAtlas.tga'),('RifleAtlas',R.parent/'build/RifleAtlas.tga')]:assert Image.open(src).convert('RGB').tobytes()==Image.open(R/'roundtrip'/pkg/'Texture'/(mat+'.tga')).convert('RGB').tobytes()
  reports.append({'package':pkg,'faces':b['FACE0000'][1],'wedges':b['VTXW0000'][1],'every_vertex_weight_sum_one':True,'texture_rgb_exact':True})
 else:
  target=R/'roundtrip'/pkg/'MeshAnimation/Dust2Motion.psa';entries=[(s['psa'],n) for s in states for n in sel[s['state']]] if pkg=='HGRifleMotionV5' else [(str(R/'continuous.psa'),'wait_Hand')]
  for path,name in entries:
   a=psa(path);b=psa(target,name);assert len(a['frames'])==len(b['frames']) and a['fps']==b['fps'];err=max(abs(x-y) for f,g in zip(a['frames'],b['frames']) for k in ['positions','rotations'] for v,w in zip(f[k],g[k]) for x,y in zip(v,w));assert err<1e-6;reports.append({'package':pkg,'sequence':name,'frames':len(a['frames']),'transform_error':err})
(R/'native-validation.json').write_text(json.dumps(reports,indent=2));print('V5_VALIDATED',len(reports))
