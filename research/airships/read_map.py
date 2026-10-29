"""Read UE2/L2 v111 maps, retaining source StaticMesh actor placements.

Serialization reference: gildor2/UEViewer Unreal/UnObject.cpp and
Unreal/UnrealPackage/UnPackage2.cpp (downloaded alongside this script).
"""
import struct, pathlib, json, collections
ROOT=pathlib.Path(__file__).resolve().parent
class Reader:
 def __init__(self,b,p=0):self.b=b;self.p=p
 def read(self,n):b=self.b[self.p:self.p+n];self.p+=n;assert len(b)==n;return b
 def num(self,f):return struct.unpack('<'+f,self.read(struct.calcsize('<'+f)))[0]
 def compact(self):
  b=self.num('B');v=b&63;negative=b&128;more=b&64;shift=6
  while more:
   b=self.num('B');v|=(b&127)<<shift;shift+=7;more=b&128
   assert shift<=34
  return -v if negative else v
class Package:
 def __init__(self,path):
  self.path=pathlib.Path(path);b=self.path.read_bytes()
  if b[:28].decode('utf-16le',errors='ignore')=='Lineage2Ver111':b=bytes(x^172 for x in b[28:])
  elif b[:28].decode('utf-16le',errors='ignore')=='Lineage2Ver121':
   key=sum(map(ord,self.path.name.lower()))&255
   b=bytes(x^key for x in b[28:])
  self.b=b;r=Reader(b);assert r.num('I')==0x9e2a83c1
  self.version=r.num('H');self.license=r.num('H');self.flags=r.num('I')
  nc,no,ec,eo,ic,io=[r.num('i') for _ in range(6)]
  self.names=[];r.p=no
  for _ in range(nc):
   n=r.compact();s=r.read(abs(n)*(2 if n<0 else 1));r.read(4)
   self.names.append(s.decode('utf-16le' if n<0 else 'latin1').rstrip('\0'))
  self.imports=[];r.p=io
  for _ in range(ic):
   cp=self.names[r.compact()];cl=self.names[r.compact()];outer=r.num('i');name=self.names[r.compact()]
   self.imports.append(dict(name=name,outer=outer,cl=cl,cp=cp))
  self.exports=[];r.p=eo
  for _ in range(ec):
   cl=r.compact();su=r.compact();outer=r.num('i');name=self.names[r.compact()];flags=r.num('I');size=r.compact();offset=r.compact() if size else 0
   self.exports.append(dict(name=name,outer=outer,cl=cl,size=size,offset=offset,flags=flags))
 def ref(self,i):
  if not i:return 'None'
  e=self.exports[i-1] if i>0 else self.imports[-i-1]
  return (self.ref(e['outer'])+'.' if e['outer'] else '')+e['name']
 def props(self,e):
  r=Reader(self.b,e['offset']);props={}
  if e['flags']&0x02000000:
   node=r.compact();r.compact();r.read(8);r.read(4)
   if node:r.compact()
  while True:
   name=self.names[r.compact()]
   if name=='None':break
   info=r.num('B');ty=info&15;st=self.names[r.compact()] if ty==10 else None
   code=(info>>4)&7;size=[1,2,4,12,16,None,None,None][code]
   if size is None:size=r.num({5:'B',6:'H',7:'i'}[code])
   idx=0
   if ty!=3 and info&128:
    b=r.num('B');idx=b
    if b&128:
     if b&64:idx=((b<<24)|(r.num('B')<<16)|(r.num('B')<<8)|r.num('B'))&0x3fffff
     else:idx=((b<<8)|r.num('B'))&0x3fff
   if ty==3:value=bool(info&128)
   else:
    data=r.read(size);v=Reader(data)
    if ty==5:value=self.ref(v.compact())
    elif ty==4:value=v.num('f')
    elif st=='Vector' or ty==11:value=list(struct.unpack('<3f',data))
    elif st=='Rotator' or ty==12:value=list(struct.unpack('<3i',data))
    elif ty==2:value=v.num('i')
    elif ty==6:value=self.names[v.compact()]
    else:value={'type':ty,'struct':st,'size':size,'raw_offset':r.p-size}
   props[name+(f'[{idx}]' if idx else '')]=value
  assert r.p<=e['offset']+e['size'],e['name']
  self.last_props_end=r.p
  return props
 def actors(self):
  out=[]
  for e in self.exports:
   cl=self.ref(e['cl'])
   if 'StaticMeshActor' not in cl:continue
   p=self.props(e)
   if p.get('StaticMesh') and not p.get('bHidden',False):out.append(dict(actor=e['name'],**p))
  return out
if __name__=='__main__':
 for path in (ROOT/'gracia-assets/MAPS').glob('*.unr'):
  p=Package(path);actors=p.actors();dest=ROOT/(path.stem+'-actors.json');dest.write_text(json.dumps(actors,indent=2))
  print(path.name,p.version,p.license,len(actors),collections.Counter(a['StaticMesh'].split('.')[0] for a in actors))
