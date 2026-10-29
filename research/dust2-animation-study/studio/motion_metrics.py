import json, math
from pathlib import Path
p=Path(__file__).parent
def mul(a,b):
 x,y,z,w=a; X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def rotate(q,v):return mul(mul(q,v+[0]),[-q[0],-q[1],-q[2],q[3]])[:3]
def world(bones,ts):
 out=[]
 for b,t in zip(bones,ts):
  if b['parent']<0:out.append(t);continue
  par=out[b['parent']];delta=rotate(par['rotation'],[v*s for v,s in zip(t['position'],par['scale'])]);out.append({'position':[a+c for a,c in zip(par['position'],delta)],'rotation':mul(par['rotation'],t['rotation']),'scale':[a*c for a,c in zip(par['scale'],t['scale'])]})
 return out
for fn in p.glob('*.motion.json'):
 d=json.loads(fn.read_text());bones=d['bones']; rest=world(bones,[b['rest'] for b in bones]); metrics={}
 for name in ['cf_j_hips','cf_j_hand_L','cf_j_hand_R','cf_j_foot_L','cf_j_foot_R']:
  i=next(i for i,b in enumerate(bones) if b['name']==name);vals=[world(bones,f['transforms'])[i]['position'] for f in d['frames']]
  metrics[name]={'rest_world_position':rest[i]['position'],'first_world_position':vals[0],'world_min':[min(v[k] for v in vals) for k in range(3)],'world_max':[max(v[k] for v in vals) for k in range(3)]}
 (p/(fn.stem+'.metrics.json')).write_text(json.dumps(metrics,indent=2));print(fn.name,metrics['cf_j_hips'])
