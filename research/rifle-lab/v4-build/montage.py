from PIL import Image,ImageDraw
from pathlib import Path
R=Path(__file__).parent;keys=['peace_idle','combat_idle','walk','run','aim','fire'];im=Image.new('RGB',(1500,1260),(35,35,35));d=ImageDraw.Draw(im)
for i,k in enumerate(keys):
 x=(i%3)*500;y=(i//3)*630;im.paste(Image.open(R/(k+'.png')),(x,y+30));d.text((x+10,y+8),k,fill='white')
im.save(R/'six-states.png')
