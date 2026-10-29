from pathlib import Path
import json,struct,collections
from decode_catalog import Reader
base=Path(__file__).resolve().parent
names=(base/'raw/names.txt').read_text().splitlines()
def texture(p):
    r=Reader(p);properties={}
    while True:
        name=names[r.compact()]
        if name=='None':break
        info=r.read('B');kind=info&15;code=(info>>4)&7
        if kind==10:r.compact()
        length=[1,2,4,12,16,None,None,None][code]
        if length is None:length=r.read({5:'B',6:'H',7:'I'}[code])
        if info&128 and kind!=3:r.compact()
        data=r.data[r.pos:r.pos+length];r.pos+=length
        properties[name]=data.hex()
    unknown=r.read('I');mips=r.compact();lazy=r.read('I');size=r.compact();pixels=r.data[r.pos:r.pos+size];r.pos+=size
    width,height,ubits,vbits=r.read('IIBB')
    assert unknown==0 and mips==1 and width==128 and height==128 and size==16384 and r.pos==len(r.data),(p.name,properties,r.pos,len(r.data),unknown,mips,width,height)
    return pixels
def extract():
    tiles=[]
    for p in sorted((base/'raw').glob('*_*.raw')):
        x,y=map(int,p.stem.split('_'));pixels=texture(p)
        tiles.append(dict(x=x,y=y,colors=sorted(set(pixels)),pixels=pixels))
    out=bytearray(b'NXZONE5\0')+struct.pack('<I',len(tiles))
    for t in tiles:out+=struct.pack('<ii',t['x'],t['y'])+t['pixels']
    (base/'zone-masks.bin').write_bytes(out)
    (base/'mask-inventory.json').write_text(json.dumps([{k:v for k,v in t.items() if k!='pixels'} for t in tiles],indent=2))
    print('Extracted',len(tiles),'original P8 masks,128x128; bytes',len(out))
    return tiles
if __name__=='__main__':extract()
