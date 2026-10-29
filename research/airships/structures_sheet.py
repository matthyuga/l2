from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'model-catalog'
items=[('glacia_destruction_tower','Torre de Destrucción'),('glacia_destruction_deadtower','Torre en ruinas'),('glacia_destruction_flymini','Pieza aérea de Destrucción'),('immortal_landmark_top','Cima de Infinity'),('immortal_landmark_head','Cabeza de Infinity'),('matrix_out','Estructura orgánica'),('g_field_kserthgateway','Arco de Gracia'),('g_field_astone01','Rocas de Gracia'),('e_f_tower_01','Torre ornamental'),('e_f_bridge_01','Puente ornamental')]
sheet=Image.new('RGB',(1500,720),'#18222b');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,(name,label) in enumerate(items):
 im=Image.open(root/'thumbs'/('airship_'+name+'.png'));im.thumbnail((290,318))
 x=(i%5)*300;y=(i//5)*360;sheet.paste(im,(x+(300-im.width)//2,y))
 draw.text((x+10,y+325),label,font=font,fill='#e8dcc3')
sheet.save(Path(__file__).resolve().parent/'otras-estructuras.jpg')
