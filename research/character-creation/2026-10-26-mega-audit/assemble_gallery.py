from pathlib import Path
import json,html,zipfile
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
rows=json.loads((root/'gallery-manifest.json').read_text(encoding='utf8'))
dest=root/'galeria';dest.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',40)
groups=list(dict.fromkeys(r['group'] for r in rows))
sheets=[];body=[]
for group in groups:
 selected=[r for r in rows if r['group']==group];title=selected[0]['title']
 im=Image.new('RGB',(2400,1800),(29,31,36));draw=ImageDraw.Draw(im)
 draw.text((24,18),title+' - paquete MEGA',font=big,fill='white')
 draw.text((24,72),'Modelos reales fuera del juego, con texturas disponibles. No es una prueba de integración.',font=small,fill=(200,205,214))
 for gender,ybase in [('M',120),('F',940)]:
  draw.text((24,ybase),'Masculino' if gender=='M' else 'Femenino',font=font,fill=(245,200,110))
  for i,r in enumerate(x for x in selected if x['sex']==gender):
   x=(i%4)*600;y=ybase+45+(i//4)*380
   for v,f in enumerate(r['files']):
    picture=Image.open(f).convert('RGB');im.paste(picture,(x+v*300,y))
   draw.text((x+16,y+340),r['style']+'   Frente / espalda',font=small,fill='white')
 output=dest/(group+'.jpg');im.save(output,quality=93);sheets.append(output)
 body.append('<h2>'+html.escape(title)+'</h2><a href="'+output.name+'"><img class="sheet" src="'+output.name+'"></a>')
 body.append('<details><summary>Ver cada peinado a tamaño completo</summary><div class="grid">')
 for r in selected:
  label=('Masculino' if r['sex']=='M' else 'Femenino')+' '+r['style']
  body.append('<figure><figcaption>'+label+'</figcaption>'+''.join('<a href="../gallery-renders/'+Path(f).name+'"><img src="../gallery-renders/'+Path(f).name+'"></a>' for f in r['files'])+'</figure>')
 body.append('</div></details>')
page='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Peinados MEGA</title><style>body{background:#1d1f24;color:#eee;font:18px Arial;max-width:1450px;margin:auto;padding:24px}a{color:#f4ca84}.sheet{width:100%;border-radius:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:12px}figure{margin:0;background:#262932;padding:10px}figure img{width:49%}summary{cursor:pointer;padding:20px}h2{margin-top:48px}</style><h1>Peinados del paquete MEGA</h1><p>84 opciones del creador, con frente y espalda. Son vistas de los modelos extraídos; no capturas del juego. Texturas disponibles del donante y del cliente nativo. No todas las opciones representan diseños nuevos. No se instaló el paquete.</p>'''+''.join(body)+'</html>'
(dest/'index.html').write_text(page,encoding='utf8')
with zipfile.ZipFile(root/'Galeria-peinados-MEGA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in [*dest.glob('*'),*(root/'gallery-renders').glob('*.png')]:z.write(f,f.relative_to(root))
assert len(rows)==84,len(rows)
assert sum(len(r['files']) for r in rows)==168
print('Galería:',len(rows),'opciones,',len(sheets),'láminas, 168 vistas.')
