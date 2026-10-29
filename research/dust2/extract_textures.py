"""Read-only extraction from the user's installed GoldSrc map and WADs."""
import pathlib,struct,json
from PIL import Image
D=pathlib.Path(__file__).resolve().parent;game=pathlib.Path('D:/juegos/cs1.6');audit=json.loads((D/'bsp-audit.json').read_text());b=(D/'source/de_dust2.bsp').read_bytes();dest=D/'textures';dest.mkdir(exist_ok=True)
wads={}
for folder in [game/'valve',game/'cstrike']:
 for path in folder.glob('*.wad'):
  raw=path.read_bytes()
  if raw[:4]!=b'WAD3':continue
  count,offset=struct.unpack_from('<ii',raw,4)
  for i in range(count):
   start,disk,size,ty,compression,pad,name=struct.unpack_from('<iiiBBH16s',raw,offset+i*32);name=name.split(b'\0')[0].decode('latin1').lower()
   if ty==0x43 and not compression:wads[name]=(raw,start,str(path))
report=[]
for item in audit['textures']:
 name=item['name'];raw,start,source=(b,item['offset'],'de_dust2.bsp') if item['embedded'] else wads.get(name.lower(),(None,0,''))
 if raw is None:report.append(dict(name=name,missing=True));continue
 n,w,h,*mips=struct.unpack_from('<16s6I',raw,start);palette=start+mips[3]+(w//8)*(h//8);colors=struct.unpack_from('<H',raw,palette)[0];assert colors==256,(name,colors)
 pixels=raw[start+mips[0]:start+mips[0]+w*h];pal=raw[palette+2:palette+2+768];assert len(pixels)==w*h and len(pal)==768
 image=Image.frombytes('P',(w,h),pixels);image.putpalette(pal);image=image.convert('RGB');image.save(dest/(name.lower()+'.png'));report.append(dict(name=name,width=w,height=h,source=source,missing=False))
(D/'texture-audit.json').write_text(json.dumps(report,indent=2));print('Textures extracted',sum(not r['missing'] for r in report),'of',len(report));print('Missing',[r['name'] for r in report if r['missing']])
