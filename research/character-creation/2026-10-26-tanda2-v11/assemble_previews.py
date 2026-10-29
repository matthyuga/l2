from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
D=Path(__file__).resolve().parent;items=json.loads((D/'assets-manifest.json').read_text())['items'];out=Image.new('RGB',(1200,7*385+95),(25,28,35));draw=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
draw.text((12,8),'Vista previa de los modelos fuera del juego',font=small,fill=(190,200,215))
for i,title in enumerate(['A · Original','B · Castaño','C · Rubio','D · Plateado']):draw.text((i*300+10,42),title,font=font,fill='white')
names={'MElf':'Elfo claro','MDarkElf':'Elfo oscuro','FOrc':'Orca guerrera','MOrc':'Orco guerrero','MShaman':'Orco místico','FDwarf':'Enana'}
for y,item in enumerate(items):
 for color in range(4):
  im=Image.open(D/'color-previews'/(item['model']+'-'+item['letter']+'-'+str(color)+'.png')).convert('RGB');out.paste(im,(color*300,95+y*385))
 draw.text((12,95+y*385+342),names[item['model']]+' · '+item['letter'],font=font,fill='white')
out.save(D/'tonos-A-D.jpg',quality=94)
