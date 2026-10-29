from pathlib import Path
import json,math,numpy as np
D=Path(__file__).resolve().parent;V7=D.parent/'dust2-camera-v7';V8=D.parent/'dust2-camera-v8'
enabled=set(json.loads((V8/'verification.json').read_text())['enabled']);old=[b for b in json.loads((V7/'bounds-audit.json').read_text()) if b['name'] in enabled]
# Include the unchanged physical walls, which also block camera sweeps.
for axis,line,start,z,h,length in json.loads((D.parent/'dust2-stairs-v4/native-walls/walls.json').read_text()):
 if axis==0:lo=[131072+line*16-1,32768+start*16-.1,z-43.35-4];hi=[lo[0]+2,32768+(start+length)*16+.1,z-43.35+h]
 else:lo=[131072+start*16-.1,32768+line*16-1,z-43.35-4];hi=[131072+(start+length)*16+.1,lo[1]+2,z-43.35+h]
 old.append(dict(min=lo,max=hi))
new=json.loads((D/'bounds-audit.json').read_text());results={}
for name,x,y,foot in [('latest_user',142557,54506,8052),('previous_user',142414,56349,7958),('ct',141448,54536,7874),('stairs',141320,55440,8000)]:
 result={}
 for version,boxes in [('v8',old),('v9',old+new)]:
  lo=np.array([b['min'] for b in boxes])-np.array([.1,.1,5]);hi=np.array([b['max'] for b in boxes])+np.array([.1,.1,5]);origin=np.array([x,y,foot+50]);miss=[];dist=[]
  for pitch in [15,30,45,60,85]:
   for yaw in range(0,360,5):
    p=math.radians(pitch);a=math.radians(yaw);direction=np.array([math.cos(p)*math.cos(a),math.cos(p)*math.sin(a),math.sin(p)]);direction[np.abs(direction)<1e-10]=1e-10
    t1=(lo-origin)/direction;t2=(hi-origin)/direction;near=np.minimum(t1,t2).max(axis=1);far=np.maximum(t1,t2).min(axis=1);hits=near[(far>=np.maximum(near,0)) & (near>0) & (near<=1800)]
    if len(hits):dist.append(float(hits.min()))
    else:miss.append([yaw,pitch])
  result[version]=dict(tested=360,unbounded_rays=len(miss),unbounded_directions=miss,max_first_hit_distance=max(dist) if dist else None)
 results[name]=result
(D/'ray-audit.json').write_text(json.dumps(results,indent=2));print(json.dumps({k:{v:{f:n for f,n in r.items() if f!='unbounded_directions'} for v,r in a.items()} for k,a in results.items()},indent=2))
