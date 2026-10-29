import pathlib,struct,json
class Reader:
 def __init__(self,d,p=0):self.d=d;self.p=p
 def u(self):v=struct.unpack_from('<I',self.d,self.p)[0];self.p+=4;return v
 def i(self):v=struct.unpack_from('<i',self.d,self.p)[0];self.p+=4;return v
 def ci(self):
  b=self.d[self.p];self.p+=1;neg=b&128;v=b&63;more=b&64;s=6
  while more:
   b=self.d[self.p];self.p+=1;v|=(b&127)<<s;s+=7;more=b&128
  return -v if neg else v
 def string(self):
  n=self.ci();v=self.d[self.p:self.p+(n if n>=0 else -n*2)];self.p+=len(v);return v.rstrip(b'\0').decode('latin1') if n>=0 else v.decode('utf-16-le').rstrip('\0')
class Package:
 def __init__(self,path):
  self.path=pathlib.Path(path);d=self.path.read_bytes()
  if d[:8]=='Line'.encode('utf-16-le'):d=bytes(v^0xac for v in d[28:])
  self.d=d; magic,self.ver,self.lic,flags,nc,no,ec,eo,ic,io=struct.unpack_from('<IHH7I',d);assert magic==0x9e2a83c1
  r=Reader(d,no);self.names=[]
  for _ in range(nc):self.names.append(r.string());r.u()
  r=Reader(d,io);self.imports=[]
  for _ in range(ic):self.imports.append(dict(cls_pkg=r.ci(),cls=r.ci(),outer=r.i(),name=r.ci()))
  r=Reader(d,eo);self.exports=[]
  for _ in range(ec):
   v=dict(cls=r.ci(),super=r.ci(),outer=r.i(),name=r.ci(),flags=r.u(),size=r.ci());v['offset']=r.ci() if v['size'] else 0;self.exports.append(v)
 def obj(self,ref):
  if not ref:return 'None'
  v=self.exports[ref-1] if ref>0 else self.imports[-ref-1]
  name=self.names[v['name']];return (self.obj(v['outer'])+'.' if v['outer'] else '')+name
if __name__=='__main__':
 import sys
 p=Package(sys.argv[1]);term=sys.argv[2] if len(sys.argv)>2 else ''
 for i,v in enumerate(p.exports):
  n=p.obj(i+1);c=p.obj(v['cls'])
  if term.lower() in (n+' '+c).lower():print(i+1,n,c,'super='+p.obj(v['super']),v['size'],v['offset'])
