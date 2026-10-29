from pathlib import Path
import struct,json
base=Path(__file__).resolve().parent
class Reader:
    def __init__(self,p):self.data=p.read_bytes();self.pos=0
    def read(self,fmt):
        value=struct.unpack_from('<'+fmt,self.data,self.pos);self.pos+=struct.calcsize('<'+fmt);return value[0] if len(value)==1 else value
    def compact(self):
        b=self.read('B');sign=-1 if b&128 else 1;n=b&63;more=b&64;shift=6
        while more:
            b=self.read('B');n|=(b&127)<<shift;more=b&128;shift+=7
        return n*sign
    def string(self):
        n=self.compact()
        if n==0:return ''
        size=abs(n)*(2 if n<0 else 1);s=self.data[self.pos:self.pos+size];self.pos+=size
        return s.decode('utf-16-le' if n<0 else 'cp1252').rstrip('\0')
def decode():
    r=Reader(base/'ZoneName.dec');zones=[]
    for _ in range(r.read('I')):
        zid,color,mx,my,top,bottom=r.read('IIIIff');name=r.string();coords=r.read('iiiiii');scale=r.read('f');tex=r.string()
        zones.append(dict(id=zid,color=color,map_x=mx,map_y=my,top=top,bottom=bottom,name=name,coords=coords,scale=scale,texture=tex))
    assert len(r.data)-r.pos in (0,13), (r.pos,len(r.data))
    print('Zone rows',len(zones),'tail',len(r.data)-r.pos)
    r=Reader(base/'huntingzone.dec');hunting=[]
    for _ in range(r.read('I')):
        hid,kind,level,unknown=r.read('IIII');x,y,z=r.read('fff');desc=r.string();zone=r.read('I');name=r.string()
        hunting.append(dict(id=hid,type=kind,level=level,unknown=unknown,x=x,y=y,z=z,description=desc,zone=zone,name=name))
    assert len(r.data)-r.pos in (0,13), (r.pos,len(r.data))
    print('Hunting rows',len(hunting),'tail',len(r.data)-r.pos)
    for name,rows in [('zones',zones),('hunting',hunting)]:
        (base/(name+'.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
    print('Ketra zones',[v for v in zones if 'Ketra' in v['name']]);print('Ketra hunting',[v for v in hunting if 'Ketra' in v['name']])
if __name__=='__main__':decode()
