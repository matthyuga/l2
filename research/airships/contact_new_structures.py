from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;CAT=D.parent/'model-catalog'
items=[('airship_scene_gludio','Gludio: muelle aéreo'),('airship_scene_keucereus','Keucereus: base y muelles'),('airship_scene_aerial','Gracia: zona aérea 13_25'),('airship_scene_superion','Superion: fortaleza ensamblada'),('airship_assembled_gracia','Gracia: nave ensamblada'),('superion_superion_s_superion_20_landmark_01_vc1','Superion: estructura exterior')]
out=Image.new('RGB',(960,740),'#18212b');draw=ImageDraw.Draw(out)
for i,(key,label) in enumerate(items):
 im=Image.open(CAT/'thumbs'/(key+'.png')).convert('RGB');im.thumbnail((310,330));x=i%3*320;y=i//3*370
 out.paste(im,(x+(320-im.width)//2,y));draw.text((x+8,y+340),label,fill='white')
out.save(D/'new-structures-contact.jpg')
