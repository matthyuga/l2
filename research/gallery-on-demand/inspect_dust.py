import sys, pathlib, collections, json
R=pathlib.Path(r'E:\l2-local');sys.path.insert(0,str(R/'research/gludio-sky'))
from package_tools import *
m=Edit(R.parent/'l2/Maps/24_19.unr')
for name in ['HGDust2V2Floor00000','HGDust2ArenaDustPart00','SSQ_ent08','anghel_fog']:
 es=[e for e in m.exports if e['name']==name or name in e['name']]
 for e in es[:2]:
  p=m.props(e);print(e['name'],m.ref(e['cl']),hex(e['flags']),e['size'],{k:v for k,v in p.items() if k in ['Location','DrawScale3D','StaticMesh','CollisionHeight','CollisionRadius','bUseCylinderCollision','DrawScale']})
  r=Reader(m.b,e['offset']);print('frame',r.compact(),r.compact(),r.num('Q'),r.num('i'),r.compact())
for e in m.exports:
 if m.ref(e['cl'])=='Engine.StaticMeshActor' and not e['name'].startswith('HG'):
  p=m.props(e)
  if p.get('StaticMesh')=='deco01.Box02':
   print('original',e['name'],hex(e['flags']),p);break
print('frames',collections.Counter(m.ref(e['cl']) for e in m.exports))
