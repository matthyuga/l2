import sys,pathlib,struct,json,hashlib
R=pathlib.Path(__file__).parent;sys.path.insert(0,str(R.parent/'native'))
from inspect_package import Package,Reader
from write_l2_animation import ci,psa,generate
P=struct.pack
src=psa(str(R.parent/'retarget/Dust2_BombWork_FFighter.psa'));src['from_psa']=True
# Restore authoritative skeleton parents from existing rig inventory.
rig=json.loads((R.parent/'retarget/rig-inventory.json').read_text())['l2'][0]['bones'];indices={b['name']:i for i,b in enumerate(rig)}
for b in src['bones']:b['parent']=indices[rig[indices[b['name']]]['parent']] if rig[indices[b['name']]]['parent'] else 0
generate(src,R/'Dust2DemoMotion.ukx','wait_Hand')
p=Package(r'E:\l2-local\research\amber-l2\tools\l2editor\L2Editor\Dust2DemoNPC.u');names=list(p.names)
def nr(s):
 if s not in names:names.append(s)
 return ci(names.index(s))
imports=list(p.imports)
imports.append(dict(cls_pkg=names.index('Core'),cls=names.index('Package'),outer=0,name=len(names)));nr('Dust2DemoMotion')
pkgref=-len(imports)
imports.append(dict(cls_pkg=names.index('Engine'),cls=names.index('MeshAnimation') if 'MeshAnimation' in names else len(names),outer=pkgref,name=len(names)+(0 if 'MeshAnimation' in names else 1)))
nr('MeshAnimation');nr('Dust2Motion');animref=-len(imports)
e=next(e for e in p.exports if p.names[e['name']]=='DemoMesh');raw=p.d[e['offset']:e['offset']+e['size']]
expected=[b['name'] for b in src['bones']];matches=[]
for pos in range(len(raw)-2):
 try:
  r=Reader(raw,pos)
  if r.ci()!=len(expected):continue
  for name in expected:
   if p.names[r.ci()]!=name:raise ValueError()
   r.p+=56
  old=r.ci()
  if old==0:matches.append((pos,r.p-1,r.p))
 except (IndexError,ValueError,struct.error):pass
assert len(matches)==1,matches
_,pos,end=matches[0];raw=raw[:pos]+ci(animref)+raw[end:]
off=e['offset'];assert len(raw)==e['size'],'In-place patch must preserve payload size';data=bytearray(p.d);data[off:off+len(raw)]=raw
nameoff=len(data)
# Keep original name entry flags, extending only with new names.
r=Reader(p.d,struct.unpack_from('<I',p.d,16)[0])
for _ in p.names:r.string();r.u()
oldstart=struct.unpack_from('<I',p.d,16)[0];data+=p.d[oldstart:r.p]
for name in names[len(p.names):]:b=name.encode()+b'\0';data+=ci(len(b))+b+P('<I',0x70010)
importoff=len(data)
for i in imports:data+=ci(i['cls_pkg'])+ci(i['cls'])+P('<i',i['outer'])+ci(i['name'])
exportoff=len(data)
for v in p.exports:
 size,offset=(len(raw),off) if v is e else (v['size'],v['offset'])
 data+=ci(v['cls'])+ci(v['super'])+P('<i',v['outer'])+ci(v['name'])+P('<I',v['flags'])+ci(size)+(ci(offset) if size else b'')
struct.pack_into('<6I',data,12,len(names),nameoff,len(p.exports),exportoff,len(imports),importoff)
(R/'Dust2DemoNPC.ukx').write_bytes(data)
q=Package(R/'Dust2DemoNPC.ukx');assert q.obj(animref)=='Dust2DemoMotion.Dust2Motion'
print('Linked new mesh to new animation',animref,len(data))
