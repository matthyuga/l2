from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1];rows=[]
for root in ['server/game','source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
 for name in ['GludioSky.java','VigiliaCrew.java']:
  rel=Path(root)/'data/scripts/custom/GludioSky'/name;p=ROOT/rel;s=p.read_text(encoding='utf8')
  if name=='GludioSky.java':
   assert 'dx=145500;dz=12384' in s and 'dx=145650' in s
   s=s.replace('dx=145500;dz=12384','dx=145350;dz=12184').replace('dx=145650','dx=145450').replace('Vigilia del Dragon V2','Vigilia del Dragon V3')
  else:
   assert '{145450,52100,12384}' in s
   s=s.replace('{145450,52100,12384}','{145350,52100,12184}').replace('x=145500;z=12384','x=145350;z=12184').replace('x=145650','x=145450').replace('VigiliaCrew V2','VigiliaCrew V3').replace('>140','>80')
  q=D/'stage/project'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s,encoding='utf8');rows.append(dict(relative=str(rel),before=hashlib.sha256(p.read_bytes()).hexdigest()))
(D/'server-source-hashes.json').write_text(json.dumps(rows,indent=2));print('V3 handler and crew: new cabin and captain heights; original gallery preserved.')
