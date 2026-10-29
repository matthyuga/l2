import pathlib,json,collections,urllib.parse,math
from PIL import Image,ImageDraw,ImageFont
from publish import CAT,OUT,BATCH

entries=json.loads((OUT/'catalog-entries.json').read_text('utf-8'));ready=[m for m in entries if m['status']=='ready'];inv=json.loads((OUT/'inventory.json').read_text('utf-8'))['records']
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',11)
for start in range(0,len(ready),25):
    group=ready[start:start+25];sheet=Image.new('RGB',(1000,math.ceil(len(group)/5)*265),'#17212a');draw=ImageDraw.Draw(sheet)
    for i,m in enumerate(group):
        x=(i%5)*200;y=(i//5)*265
        im=Image.open(CAT/m['thumbnail']).convert('RGB');im.thumbnail((192,210));sheet.paste(im,(x+(200-im.width)//2,y))
        title=m['title']
        for line in range(2):draw.text((x+5,y+213+line*16),title[line*27:(line+1)*27],font=font,fill='#f0c078')
        facts=m['asset_analysis'];draw.text((x+5,y+246),str(facts['bones'])+' huesos / '+str(facts['animations'])+' clips',font=small,fill='#abb9c4')
    sheet.save(OUT/('contacto-'+str(start//25+1)+'.jpg'),quality=88)

categories=collections.Counter(m['category'] for m in ready);reviews=collections.Counter(m['material_review']['status'] for m in ready)
animated=[m for m in ready if m['asset_analysis']['animations']];rigged=[m for m in ready if m['asset_analysis']['bones']]
old=json.loads(pathlib.Path(r'E:\l2-local\backups\external-assets-20261028\gallery.json').read_text('utf-8'))['models'];current={m['key']:m for m in json.loads((CAT/'gallery.json').read_text('utf-8'))['models']}
assert all(current.get(m['key'])==m for m in old),'An original catalog record changed'
text=f'''# Assets externos · Tanda 3

Revisión del 28/10/2026. Carpeta de entrada: `E:\\l2-local\\descarga de assets`.

## Resultado

- {len(ready)} modelos distintos con GLB portátil y miniatura renderizada.
- {len(entries)-len(ready)} recurso pendiente de conversión: Scary Guy, fuente Collada/DAE no admitida por Blender 5.
- 2 descargas de Sketchfab duplicadas agrupadas en la misma ficha.
- Un dirigible Airship02 incorporado desde FBX; sus variantes BLEND/OBJ/STL se conservan como formatos alternativos.
- {len(rigged)} modelos con huesos en la fuente; {len(animated)} modelos con clips de animación exportados, reproducibles en el visor.
- {len(old)} fichas anteriores conservadas sin cambios. Los originales y favoritos del navegador del usuario no se modificaron.

[Abrir esta tanda en el catálogo](http://127.0.0.1:32280/?batch={urllib.parse.quote(BATCH)})

## Categorías

'''
text+='\n'.join(f'- {k}: {v}' for k,v in categories.items())
text+='\n\n## Texturas y límites\n\n'
text+=f'- {reviews["complete"]} vistas con imágenes de textura y sin referencias ausentes detectadas. Esto no garantiza equivalencia de todos los shaders con el programa de origen.\n'
text+=f'- {reviews["pending"]} vistas con referencias de textura pendientes; están señaladas en la ficha.\n'
text+=f'- {reviews["flat_color"]} vistas sin texturas de imagen.\n'
text+='- Demogorgon: vista estática con esqueleto. Exportar sus clips excedió 300 segundos; el original se conserva y la limitación está indicada en la ficha.\n'
text+='- El visor permite explorar estos recursos. Todavía no son paquetes UKX/UTX adaptados a Interlude, ni tienen estadísticas, ID o IA de NPC.\n'
text+='- Algunas fuentes incluyen licencias NC o ND. Cada ficha muestra la licencia declarada por el publicador y su enlace original; la descarga no se presenta como autorización general para cualquier uso.\n'
text+='- Los 9 paquetes nativos restantes de L2 y los recursos auxiliares de cabello/interfaz quedan inventariados aparte, sin mezclarlos con esta tanda externa.\n'
text+='\n## Archivos de revisión\n\n- [Inventario CSV](INVENTARIO.csv): nombres, formatos, triángulos, huesos, clips, texturas, autor y licencia.\n- [Inventario de paquetes](inventory.json): todos los paquetes encontrados y formatos alternativos.\n- [Procedencia de Sketchfab](sources.json): metadatos públicos de 87 descargas, sin URLs de descarga firmadas.\n- [Fichas incorporadas](catalog-entries.json).\n- [Verificación del navegador](browser-verification.json).\n'
text+='\n## Recursos con texturas pendientes\n\n'
text+='\n'.join('- '+m['title']+' — '+', '.join(m['asset_analysis']['missing_images'][:6])+('…' if len(m['asset_analysis']['missing_images'])>6 else '') for m in ready if m['material_review']['status']=='pending')
text+='\n\n## Contactos visuales\n\n'+'\n'.join(f'- [Hoja {i+1}](contacto-{i+1}.jpg)' for i in range(math.ceil(len(ready)/25)))
text+='\n\n## Reproducción y respaldo\n\nScripts locales: inventory.py, unpack_rars.py, metadata.py, convert_blender.py, run_batch.py, publish.py, document.py y verify.cjs. No ejecutar el lote completo para reparar una sola ficha; usar --keys. Respaldo anterior a la publicación: `E:\\l2-local\\backups\\external-assets-20261028`.\n'
(OUT/'REVISION.md').write_text(text,encoding='utf-8')
(OUT/'final-metrics.json').write_text(json.dumps({'ready':len(ready),'pending':len(entries)-len(ready),'rigged':len(rigged),'animated':len(animated),'categories':dict(categories),'textures':dict(reviews),'original_records_unchanged':len(old)},indent=2),encoding='utf-8')
print(json.dumps({'ready':len(ready),'rigged':len(rigged),'animated':len(animated),'textures':dict(reviews),'original_unchanged':len(old)}))
