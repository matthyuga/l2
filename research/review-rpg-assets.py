from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib
from collections import Counter
root=Path('C:/Users/KEVIN/Desktop/dise\u00f1o paneles rpg')
out=Path('E:/l2-local/research/rpg-interface-review-20261024');out.mkdir(exist_ok=True)
exts={'.jpg','.jpeg','.png','.webp','.gif','.jfif','.ico'}
files=sorted([p for p in root.rglob('*') if p.suffix.lower() in exts],key=lambda p:(p.parent!=root,str(p.relative_to(root)).lower()))
rows=[]; errors=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
for i,p in enumerate(files,1):
 try:
  with Image.open(p) as im:
   rows.append(dict(id=i,path=str(p),relative=str(p.relative_to(root)),width=im.width,height=im.height,mode=im.mode,alpha='A' in im.getbands(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 except Exception as e:errors.append(dict(path=str(p),error=str(e)))
for start in range(0,len(rows),96):
 sheet=Image.new('RGB',(1600,1680),'#252932');draw=ImageDraw.Draw(sheet)
 for k,r in enumerate(rows[start:start+96]):
  x=k%8*200;y=k//8*140
  with Image.open(r['path']) as im:
   im=ImageOps.exif_transpose(im).convert('RGBA');im.thumbnail((192,109))
   sheet.paste(im,(x+(200-im.width)//2,y),im)
  label=f"{r['id']:04} {r['relative']}";draw.text((x+3,y+110),label[:27],font=font,fill='white');draw.text((x+3,y+125),f"{r['width']}x{r['height']}",font=font,fill='#aab9cd')
 sheet.save(out/f'contact-{start//96+1:02}.jpg',quality=86)
(out/'inventory.json').write_text(json.dumps(dict(root=str(root),images=rows,errors=errors),ensure_ascii=False,indent=2),encoding='utf8')
counts=Counter(r['sha256'] for r in rows)
print(json.dumps(dict(images=len(rows),unique=len(counts),duplicate_copies=sum(v-1 for v in counts.values()),errors=errors,sheets=(len(rows)+95)//96,output=str(out))))
