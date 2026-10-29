"""Link the TV to a valid L2 fixed pose without moving skeletal payload offsets."""
from pathlib import Path
import sys,struct,json
D=Path(__file__).resolve().parent
sys.path.insert(0,r'E:\l2-local\research\gludio-sky');from package_tools import Edit,ci
sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native');from write_l2_animation import generate
from read_map import Reader
src={'bones':[{'name':'root','parent':0}],'fps':30,'frames':[{'positions':[[0,0,0]],'rotations':[[0,0,0,1]]} for _ in range(2)]}
proof=generate(src,D/'assets/NexusTVMotion4.ukx','wait')
p=Edit(D/'assets/NexusTVPanel4.ukx');ref=p.imp('NexusTVMotion4.Dust2Motion','Engine.MeshAnimation');e=next(e for e in p.exports if e['name']=='Screen');raw=p.b[e['offset']:e['offset']+e['size']];hits=[]
for i in range(len(raw)-60):
 try:
  r=Reader(raw,i)
  if r.compact()!=1:continue
  if p.names[r.compact()]!='root':continue
  r.read(56);at=r.p
  if r.compact()==0:hits.append(at)
 except (IndexError,AssertionError,struct.error):pass
assert len(hits)==1 and len(ci(ref))==1,hits
p.data[e['offset']+hits[0]]=ci(ref)[0];p.save(D/'assets/NexusTVPanel4-linked.ukx')
proof.update(animation_reference=ref,bind_offset=e['offset']+hits[0],mesh='NexusTVPanel4.Screen');(D/'animation-link.json').write_text(json.dumps(proof,indent=2))
print('PASS TV root pose linked; original payload offsets preserved')
