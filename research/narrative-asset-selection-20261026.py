from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
base=Path('E:/l2-local/research/model-catalog');out=Path('E:/l2-local/research/narrative-asset-review-20261026');out.mkdir(exist_ok=True)
j=json.loads((base/'gallery.json').read_text(encoding='utf8'));by={m['key']:m for m in j['models']}
sel=[('m0435','Hardin - original'),('b2_ee0a0d63628ef8d346','Hardin - pack externo'),('b2_7df2a6e630e45ac11e','Sieghardt - pack externo'),('b2_f80313fd71a710d847','Gustin - pack externo'),('m0439','Noble: Amadeo / Waldner / Ashton / Esthus'),('m0453','Guardia real: Collin / Klaus / Aron / Sedrick'),('m0421','Roien - maestro de guerreros'),('m0527','Kakai - patriarca orco'),('m0289','Kadun Zu Ketra - jefe orco'),('m0291','Brakki - jefe Ketra'),('m0103','Wahkan - guerrero Ketra'),('m0105','Asefa - chaman Ketra'),('m0436','Discipula de Hardin'),('m0437','Discipulo de Hardin'),('b2_33def732561a73a814','Baium NPC - pack externo'),('b2_4bb20cd4e101605d76','Freya de pie - pack externo')]
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
s=Image.new('RGB',(1280,1520),'#202530');d=ImageDraw.Draw(s)
records=[]
for k,(key,label) in enumerate(sel):
 m=by[key];x=k%4*320;y=k//4*380;p=base/m['thumbnail']
 with Image.open(p) as im:
  im=im.convert('RGBA');im.thumbnail((310,320));s.paste(im,(x+(320-im.width)//2,y),im)
 d.text((x+6,y+322),f'{k+1:02} '+label[:37],font=f,fill='white')
 d.text((x+6,y+345),key,font=sm,fill='#c6b78e')
 d.text((x+6,y+363),'Externo: no integrado' if m.get('external_source') else 'Base: malla compartida' if len(m.get('npcs',[]))>1 else 'Base: referencia NPC',font=sm,fill='#9faec0')
 records.append(dict(number=k+1,label=label,model=m))
s.save(out/'seleccion-personajes.jpg',quality=94)
(out/'seleccion.json').write_text(json.dumps(dict(source=str(base/'gallery.json'),catalog_entries=len(j['models']),selection=records),ensure_ascii=False,indent=2),encoding='utf8')
print('Catalogo',len(j['models']),'seleccion',len(records))
