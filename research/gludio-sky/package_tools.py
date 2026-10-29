"""Small append-only UE2 package editor. Existing native payload offsets stay valid.

Property/package layout follows the local read_map reader and acmi L2io/L2unreal.
Only staged files are written by this module.
"""
import sys, struct, pathlib, uuid
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/airships'))
from read_map import Package, Reader

def ci(v):
    neg=v<0;v=abs(v);out=bytearray([(v&63)|(128 if neg else 0)|(64 if v>63 else 0)]);v>>=6
    while v:out.append((v&127)|(128 if v>127 else 0));v>>=7
    return bytes(out)

class Edit(Package):
    def __init__(self,path):
        super().__init__(path);self.data=bytearray(self.b)
        r=Reader(self.b,struct.unpack_from('<i',self.b,16)[0]);self.nameflags=[]
        for _ in self.names:
            n=r.compact();r.read(abs(n)*(2 if n<0 else 1));self.nameflags.append(r.num('I'))
        self.pending={}
    def name(self,s):
        if s not in self.names:self.names.append(s);self.nameflags.append(0x00070010)
        return self.names.index(s)
    def imp(self,full,cl='Engine.StaticMesh'):
        for i,e in enumerate(self.imports):
            if self.ref(-i-1)==full:return -i-1
        parts=full.rsplit('.',1);outer=self.imp(parts[0],'Core.Package') if len(parts)>1 else 0
        cp,kind=cl.split('.');n=parts[-1]
        for s in (cp,kind,n):self.name(s)
        self.imports.append(dict(name=n,outer=outer,cl=kind,cp=cp));return -len(self.imports)
    def add(self,name,cl,raw,flags=0x02070001):
        assert not any(e['name']==name for e in self.exports),name
        self.name(name);ref=self.imp(cl,'Core.Class')
        self.exports.append(dict(name=name,outer=0,cl=ref,su=0,size=len(raw),offset=0,flags=flags));self.pending[len(self.exports)-1]=raw
        return len(self.exports)
    def replace(self,e,raw):self.pending[self.exports.index(e)]=raw
    def prop(self,name,ty,raw=b'',st=None,index=None):
        n=len(raw);code={1:0,2:1,4:2,12:3,16:4}.get(n,5 if n<256 else 6 if n<65536 else 7)
        out=ci(self.name(name))+bytes([ty|(code<<4)|(128 if index is not None else 0)])
        if ty==10:out+=ci(self.name(st))
        if code>=5:out+=struct.pack('<'+{5:'B',6:'H',7:'i'}[code],n)
        if index is not None:assert index<128;out+=bytes([index])
        return out+raw
    def boolean(self,name,val):return ci(self.name(name))+bytes([0x53|(0x80 if val else 0),0])
    def obj(self,name,ref,index=None):return self.prop(name,5,ci(ref),index=index)
    def vector(self,name,v):return self.prop(name,10,struct.pack('<3f',*v),'Vector')
    def integer(self,name,v):return self.prop(name,2,struct.pack('<i',v))
    def float(self,name,v):return self.prop(name,4,struct.pack('<f',v))
    def nametag(self,name,v):return self.prop(name,6,ci(self.name(v)))
    def end(self):return ci(self.name('None'))
    def save(self,path,license=None):
        # Copy superclass refs from the original table; Package reader does not retain them.
        r=Reader(self.b,struct.unpack_from('<i',self.b,24)[0])
        for e in self.exports[:struct.unpack_from('<i',self.b,20)[0]]:
            r.compact();e['su']=r.compact();r.read(4);r.compact();r.read(4);sz=r.compact()
            if sz:r.compact()
        for idx,raw in self.pending.items():
            e=self.exports[idx];off=len(self.data)
            if callable(raw):raw=raw(off)
            e['offset']=off;e['size']=len(raw);self.data+=raw
        no=len(self.data)
        for name,flags in zip(self.names,self.nameflags):
            b=name.encode('latin1')+b'\0';self.data+=ci(len(b))+b+struct.pack('<I',flags)
        io=len(self.data)
        for e in self.imports:self.data+=ci(self.name(e['cp']))+ci(self.name(e['cl']))+struct.pack('<i',e['outer'])+ci(self.name(e['name']))
        eo=len(self.data)
        for e in self.exports:
            self.data+=ci(e['cl'])+ci(e.get('su',0))+struct.pack('<i',e['outer'])+ci(self.name(e['name']))+struct.pack('<I',e['flags'])+ci(e['size'])
            if e['size']:self.data+=ci(e['offset'])
        struct.pack_into('<6i',self.data,12,len(self.names),no,len(self.exports),eo,len(self.imports),io)
        if license is not None:struct.pack_into('<H',self.data,6,license)
        # The original map's GUID is preserved; new standalone packages get their own in caller.
        path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(self.data)
        return path

def tags(pkg,e):
    """Raw tagged properties, retaining their native encodings and order."""
    r=Reader(pkg.b,e['offset']);out=[]
    assert not e['flags']&0x02000000 or pkg.ref(e['cl']).startswith('Engine.'),'unsupported execution frame'
    # Actors in our maps carry RF_HasStack but serialize no execution frame; read_map
    # consumes that frame when present. Mirror its exact header handling.
    if e['flags']&0x02000000:
        node=r.compact();r.compact();r.read(8);r.read(4)
        if node:r.compact()
    prefix=pkg.b[e['offset']:r.p]
    while True:
        start=r.p;n=pkg.names[r.compact()]
        if n=='None':return prefix,out,r.p
        info=r.num('B');ty=info&15
        if ty==10:r.compact()
        code=(info>>4)&7;size=[1,2,4,12,16,None,None,None][code]
        if size is None:size=r.num({5:'B',6:'H',7:'i'}[code])
        if ty!=3 and info&128:
            idx=r.num('B')
            if idx&128:r.read(2 if idx&64 else 1)
        if ty!=3:r.read(size)
        out.append((n,pkg.b[start:r.p]))

def change_props(pkg,e,changes):
    prefix,items,end=tags(pkg,e);seen=set();out=bytearray(prefix)
    for name,raw in items:
        if name in changes:
            if name not in seen:out+=changes[name]
            seen.add(name)
        else:out+=raw
    for name,raw in changes.items():
        if name not in seen:out+=raw
    return bytes(out)+pkg.end()+pkg.b[end:e['offset']+e['size']]

def mesh_offsets(pkg,e):
    """Offsets of the three native lazy arrays; L2unreal StaticMesh serialization."""
    pkg.props(e);r=Reader(pkg.b,pkg.last_props_end);r.read(41)
    n=r.compact();r.read(n*14+25)
    n=r.compact();r.read(n*24+4)
    for _ in range(2):n=r.compact();r.read(n*4+4)
    for _ in range(r.compact()):n=r.compact();r.read(n*8+8)
    for _ in range(2):n=r.compact();r.read(n*2+4)
    r.compact();a=r.p;r.p=r.num('i');b=r.p;r.p=r.num('i')
    r.read(4);r.compact();r.compact();r.read(20+12+4)
    u01=r.p
    if pkg.license>=37:r.read(4)
    c=r.p
    for x in (a,b,c):assert e['offset']<=x<e['offset']+e['size'],(e['name'],x,e)
    return [a-e['offset'],b-e['offset'],c-e['offset']],u01-e['offset']
