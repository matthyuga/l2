import sys,struct,json
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native');from inspect_package import Package,Reader
from write_l2_animation import ci,chunks
P=struct.pack;p=Package(r'E:\l2-local\research\amber-l2\tools\l2editor\L2Editor\HGRifleV5.u');names=list(p.names);imports=list(p.imports)
def nr(n):
 if n not in names:names.append(n)
 return names.index(n)
c=chunks(R/'RifleNPCV5.psk')['REFSKELT'];expected=[c[2][i*120:i*120+64].split(b'\0')[0].decode() for i in range(c[1])]
entries=[{'mesh':'RifleMesh','package':'HGRifleMotionV5'}]+[{'mesh':'CycleMesh','package':'HGRifleCycleV5'}];data=bytearray(p.d);changes=[]
for entry in entries:
 imports.append(dict(cls_pkg=nr('Core'),cls=nr('Package'),outer=0,name=nr(entry['package'])));pkgref=-len(imports)
 imports.append(dict(cls_pkg=nr('Engine'),cls=nr('MeshAnimation'),outer=pkgref,name=nr('Dust2Motion')));animref=-len(imports)
 e=next(x for x in p.exports if p.names[x['name']]==entry['mesh']);raw=p.d[e['offset']:e['offset']+e['size']];matches=[]
 for pos in range(len(raw)-2):
  try:
   rd=Reader(raw,pos)
   if rd.ci()!=len(expected):continue
   for n in expected:
    if p.names[rd.ci()]!=n:raise ValueError()
    rd.p+=56
   if rd.ci()==0:matches.append(rd.p-1)
  except(IndexError,ValueError,struct.error):pass
 assert len(matches)==1,matches;pos=matches[0];v=ci(animref);assert len(v)==1;data[e['offset']+pos]=v[0];changes.append({'mesh':entry['mesh'],'animation':entry['package'],'byte_offset':e['offset']+pos})
nameoff=len(data);rd=Reader(p.d,struct.unpack_from('<I',p.d,16)[0]);start=rd.p
for n in p.names:rd.string();rd.u()
data+=p.d[start:rd.p]
for n in names[len(p.names):]:b=n.encode()+b'\0';data+=ci(len(b))+b+P('<I',0x70010)
importoff=len(data)
for x in imports:data+=ci(x['cls_pkg'])+ci(x['cls'])+P('<i',x['outer'])+ci(x['name'])
exportoff=len(data)
for x in p.exports:data+=ci(x['cls'])+ci(x['super'])+P('<i',x['outer'])+ci(x['name'])+P('<I',x['flags'])+ci(x['size'])+(ci(x['offset']) if x['size'] else b'')
struct.pack_into('<6I',data,12,len(names),nameoff,len(p.exports),exportoff,len(imports),importoff);out=R/'HGRifleV5.ukx';out.write_bytes(data)
q=Package(out)
for a,b in zip(p.exports,q.exports):
 assert a==b;u=p.d[a['offset']:a['offset']+a['size']];v=q.d[b['offset']:b['offset']+b['size']];assert sum(x!=y for x,y in zip(u,v))==(1 if p.names[a['name']] in [e['mesh'] for e in entries] else 0)
(R/'link-validation.json').write_text(json.dumps({'changes':changes,'all_export_offsets_and_sizes_preserved':True,'only_one_byte_per_mesh_changed':True},indent=2));print('LINK2MESH_PASS')

