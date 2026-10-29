"""Extract the existing sprite art; preserve the source and do not redraw characters."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from collections import deque
S=Path(__file__).resolve().parent;R=S.parents[1]
source=R/'descarga de assets/maggie-fess-2xj1f66khj0.jpg'
out=S/'cutouts';out.mkdir(parents=True,exist_ok=True)
im=Image.open(source).convert('RGB');assert im.size==(1280,609)
specs=[
 ('tesoro',(6,8,214,180)),('ataco',(216,0,423,173)),('duelo',(430,9,632,188)),
 ('pergamino',(638,7,824,188)),('curame',(825,10,1057,190)),('escondite',(1062,0,1278,205)),
 ('elfa',(8,189,176,401)),('abrazo',(175,172,352,403)),('paladin',(351,187,507,406)),
 ('gato',(507,216,699,402)),('magia',(696,211,908,401)),('asesino',(909,209,1068,396)),
 ('cocina',(1067,208,1278,402)),('orco',(3,405,210,592)),('arbol',(212,411,385,605)),
 ('unicornio',(384,407,598,602)),('amor',(600,405,815,605)),('castillo',(818,400,1064,605)),
 ('furia',(1067,394,1279,607))]
records=[]
for i,(name,box) in enumerate(specs):
    cut=im.crop(box);w,h=cut.size
    # Only remove near-white pixels connected to the exterior. Enclosed whites,
    # speech balloons, eyes, armor highlights and the character colors survive.
    mask=Image.new('L',cut.size)
    mask.putdata([255 if min(rgb)>=242 and max(rgb)-min(rgb)<=14 else 0 for rgb in cut.getdata()])
    seeds=[(x,0) for x in range(w)]+[(x,h-1) for x in range(w)]+[(0,y) for y in range(h)]+[(w-1,y) for y in range(h)]
    for xy in seeds:
        if mask.getpixel(xy)==255:ImageDraw.floodfill(mask,xy,127,thresh=0)
    outside=mask.point(lambda a:255 if a==127 else 0)
    alpha=outside.point(lambda a:255-a)
    # Remove small pieces of neighboring drawings clipped by a crop edge.
    # Complete detached details and speech bubbles inside each box are retained.
    seen=bytearray(w*h);ap=alpha.load()
    for sy in range(h):
        for sx in range(w):
            if seen[sy*w+sx] or not ap[sx,sy]:continue
            q=deque([(sx,sy)]);seen[sy*w+sx]=1;component=[];edge=False
            while q:
                x,y=q.popleft();component.append((x,y));edge|=x==0 or y==0 or x==w-1 or y==h-1
                for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0<=nx<w and 0<=ny<h and not seen[ny*w+nx] and ap[nx,ny]:seen[ny*w+nx]=1;q.append((nx,ny))
            if edge and len(component)<=600:
                for xy in component:ap[xy]=0
    cut=cut.convert('RGBA');cut.putalpha(alpha)
    bounds=cut.getbbox();assert bounds
    cut=cut.crop(bounds)
    path=out/f'{i+1:02}-{name}.png';cut.save(path)
    assert cut.getchannel('A').getextrema()==(0,255)
    records.append({'number':i+1,'name':name,'source_box':box,'trim_box':bounds,'file':str(path),'size':cut.size})
(S/'cutouts.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'count':19,'stickers':records},indent=2))
preview=Image.new('RGB',(1200,880),(25,32,45));d=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,record in enumerate(records):
    x=(i%5)*240;y=(i//5)*220
    for yy in range(y,y+192,16):
        for xx in range(x,x+240,16):d.rectangle((xx,yy,xx+15,yy+15),fill=(43,51,65) if ((xx-x)//16+(yy-y)//16)%2 else (34,42,55))
    cut=Image.open(record['file']);cut.thumbnail((218,184),Image.Resampling.LANCZOS)
    preview.paste(cut,(x+(240-cut.width)//2,y+(192-cut.height)//2),cut)
    d.text((x+120,y+207),f"{i+1:02} {record['name']}",font=font,anchor='mm',fill=(244,222,173))
preview.save(S/'contact-sheet.png')
print('EXTRACTED: 19 original stickers with transparent exteriors; source unchanged.')
