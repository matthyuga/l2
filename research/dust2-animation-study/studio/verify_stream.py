import json,sys,math
sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\studio')
from extract_motion import parse_stream
c=json.load(open(r'E:\l2-local\research\dust2-animation-study\studio\squat_raw.json'))
curves,t=parse_stream(c['m_MuscleClip']['m_Clip']['data']['m_StreamedClip'])
errors=[]
for keys in curves:
 for (ta,co),(tb,cb) in zip(keys,keys[1:]):
  if ta<0 or tb>3.001: continue
  dt=tb-ta;pred=((co[0]*dt+co[1])*dt+co[2])*dt+co[3]
  errors.append(abs(pred-cb[3]))
print('cubic endpoint continuity',len(errors),max(errors),sum(errors)/len(errors))
