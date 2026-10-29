"""Read/append Interlude records while preserving every existing record byte."""
import struct, pathlib, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMAS=ROOT/'tools/L2ClientDat/dist/data/structure/dats'
def compact(v):
    neg=v<0;v=abs(v);out=bytearray([(v&63)|(128 if neg else 0)|(64 if v>>6 else 0)]);v>>=6
    while v: out.append((v&127)|(128 if v>>7 else 0));v>>=7
    return out
class Catalog:
    def __init__(self,path,schema,pattern):
        self.data=pathlib.Path(path).read_bytes();self.offset=0
        self.schema=next(n for n in ET.parse(SCHEMAS/schema).getroot().findall('file') if n.get('pattern')==pattern).find('for')
        self.count=self.read('UINT');self.rows=[]
        for _ in range(self.count):
            start=self.offset;r=self.parse(self.schema,{});r['_start']=start;r['_end']=self.offset;self.rows.append(r)
        self.end=self.offset
    def read(self,kind):
        if kind in ('UINT','FLOAT','RGBA'): v=struct.unpack_from('<f' if kind=='FLOAT' else '<I',self.data,self.offset)[0];self.offset+=4;return v
        if kind in ('CNTR','ASCF'):
            b=self.data[self.offset];self.offset+=1;v=b&63;neg=b&128;more=b&64;shift=6
            while more:
                b=self.data[self.offset];self.offset+=1;v|=(b&127)<<shift;more=b&128;shift+=7
            v=-v if neg else v
            if kind=='CNTR':return v
            n=abs(v)*(2 if v<0 else 1);raw=self.data[self.offset:self.offset+n];self.offset+=n
            return raw.decode('utf-16-le' if v<0 else 'cp1252').rstrip('\0') if v else ''
        if kind=='UNICODE':
            n=self.read('UINT');raw=self.data[self.offset:self.offset+n];self.offset+=n;return raw.decode('utf-16-le')
        raise ValueError(kind)
    def parse(self,nodes,vars):
        out={}
        for node in nodes:
            name=node.get('name')
            if node.tag=='node':out[name]=self.read(node.get('reader'));vars[name]=out[name]
            else:out[name+'_items']=[self.parse(node,dict(vars)) for _ in range(vars[node.get('size').lstrip('#')])]
        return out
    def encode(self,record,nodes=None):
        out=bytearray()
        for node in (self.schema if nodes is None else nodes):
            name=node.get('name')
            if node.tag!='node':
                for item in record[name+'_items']:out+=self.encode(item,node)
                continue
            kind=node.get('reader');v=record[name]
            if kind in ('UINT','FLOAT','RGBA'):out+=struct.pack('<f' if kind=='FLOAT' else '<I',v)
            elif kind=='CNTR':out+=compact(v)
            elif kind=='UNICODE':raw=v.encode('utf-16-le');out+=struct.pack('<I',len(raw))+raw
            elif kind=='ASCF':out+=compact(-(len(v)+1))+v.encode('utf-16-le')+b'\0\0' if v else compact(0)
            else:raise ValueError(kind)
        return out
    def append(self,rows,path):
        output=struct.pack('<I',self.count+len(rows))+self.data[4:self.end]+b''.join(self.encode(r) for r in rows)+self.data[self.end:]
        pathlib.Path(path).write_bytes(output)
        assert output[4:self.end]==self.data[4:self.end]
        return len(output)
if __name__=='__main__':
    import json
    backup=ROOT.parents[1]/'backups/amber-contract-2026-10-09'
    for file,schema,pattern in [('skillgrp.raw','skillgrp.xml','ScionsOfDestiny'),('skillname.raw','skillname.xml','ScionsOfDestiny'),('npcgrp.raw','npcgrp.xml','Interlude')]:
        cat=Catalog(backup/file,schema,pattern);print(file,cat.count,cat.end,len(cat.data))
        if file=='skillgrp.raw':
            for row in cat.rows:
                if row['skill_id'] in (19,24,343,1442,1420,1423,1333,1223,1059) and row['skill_level']==1:print(json.dumps(row))
