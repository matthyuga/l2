import pathlib,json,collections,math,csv,hashlib
from PIL import Image,ImageDraw,ImageFont

OUT=pathlib.Path(__file__).resolve().parent;CAT=pathlib.Path(r'E:\l2-local\research\model-catalog')
catalog=json.loads((CAT/'gallery.json').read_text('utf-8'));entries=[m for m in catalog['models'] if m.get('batch','').endswith('Tanda 4')]
ready=[m for m in entries if m['status']=='ready'];animated=[m for m in ready if m['asset_analysis']['animations']];rigged=[m for m in ready if m['asset_analysis']['bones']]
index=json.loads((CAT/'rig-data/index.json').read_text('utf-8'));categories=collections.Counter(m['category'] for m in ready);textures=collections.Counter(m['material_review']['status'] for m in ready)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',11)
for start in range(0,len(ready),25):
    group=ready[start:start+25];sheet=Image.new('RGB',(1000,math.ceil(len(group)/5)*265),'#17212a');draw=ImageDraw.Draw(sheet)
    for i,m in enumerate(group):
        x=i%5*200;y=i//5*265;im=Image.open(CAT/m['thumbnail']).convert('RGB');im.thumbnail((192,210));sheet.paste(im,(x+(200-im.width)//2,y))
        for line in range(2):draw.text((x+5,y+213+line*16),m['title'][line*27:(line+1)*27],font=font,fill='#f0c078')
        f=m['asset_analysis'];draw.text((x+5,y+246),str(f['bones'])+' huesos / '+str(f['animations'])+' clips',font=small,fill='#abb9c4')
    sheet.save(OUT/('contacto-'+str(start//25+1)+'.jpg'),quality=88)
rows=[{'nombre':m['title'],'categoria':m['category'],'estado':m['status'],'triangulos':m['asset_analysis']['triangles'],'huesos':m['asset_analysis']['bones'],'clips':m['asset_analysis']['animations'],'texturas':m['material_review']['status'],'autor':m['source'].get('author',''),'licencia':m['source'].get('license_label',''),'origen':m['source'].get('url',''),'key':m['key']} for m in entries]
with (OUT/'INVENTARIO.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
before=json.loads(pathlib.Path(r'E:\l2-local\backups\external-assets-round4-20261028\gallery.json').read_text('utf-8'));by={m['key']:m for m in catalog['models']}
assert all(by.get(m['key'])==m for m in before['models']),'Earlier catalog record changed'
manifest=json.loads(pathlib.Path(r'E:\l2-local\research\external-assets-20261028\inventory.json').read_text('utf-8'))['records']
source_hashes=[]
for r in manifest:
    if r.get('batch','').endswith('Tanda 4'):
        p=pathlib.Path(r'E:\l2-local\descarga de assets')/r['file'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==r['archive_sha256'];source_hashes.append({'file':r['file'],'sha256':actual})
(OUT/'source-integrity.json').write_text(json.dumps(source_hashes,indent=2),encoding='utf-8')
metrics={'ready':len(ready),'pending':len(entries)-len(ready),'rigged_new':len(rigged),'animated_new':len(animated),'clips_new':sum(m['asset_analysis']['animations'] for m in ready),'technical_index_total':len(index['models']),'categories':dict(categories),'textures':dict(textures),'previous_records_unchanged':len(before['models']),'original_archive_hashes_verified':len(source_hashes)}
(OUT/'summary.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
text=f'''# Assets externos · Tanda 4 — 28/10/2026

Importación incremental de las nuevas descargas de `E:\\l2-local\\descarga de assets`.

[Abrir Tanda 4 en el catálogo](http://127.0.0.1:32280/?batch=Assets%20externos%20%C2%B7%20Tanda%204)

## Resultado

- {len(ready)} modelos con miniatura y vista 3D; {len(entries)-len(ready)} pendientes de esta tanda.
- {len(rigged)} modelos nuevos con esqueleto.
- {len(animated)} modelos nuevos con clips; {metrics['clips_new']} clips exportados en total.
- {len(index['models'])} modelos en el índice técnico acumulado de huesos y animaciones.
- {len(before['models'])} fichas previas conservadas exactamente, incluidas sus referencias técnicas.
- {len(source_hashes)} archivos ZIP originales comprobados por SHA-256 antes y después.

## Categorías

'''
text+='\n'.join('- '+k+': '+str(v) for k,v in categories.items())
text+='\n\n## Animaciones\n\n'
text+='\n'.join('- '+m['title']+': '+str(m['asset_analysis']['animations'])+' clips.' for m in animated)
text+='''

Los nombres de movimientos se conservan tal como aparecen en el archivo; no certifican daño, alcance, IA ni equivalencia con una habilidad de L2. La reproducción desplaza cada clip a cero sobre una copia en memoria, para evitar esperas cuando el original usa tiempos absolutos tardíos. No se modifican los tiempos de los GLB ni los datos almacenados en SQLite.

## Materiales y calidad

'''
text+=f'- {textures["complete"]} vistas con mapas y sin referencias ausentes detectadas; {textures["pending"]} con revisión de materiales pendiente; {textures["flat_color"]} sin mapas de imagen.\n'
text+='- El estado de textura no garantiza equivalencia de todos los shaders con el programa de origen. Las observaciones visuales particulares se incorporan a la ficha.\n'
text+='- Las vistas del catálogo no equivalen a una adaptación UKX/UTX para Interlude.\n'
text+='\n## Observaciones visuales\n\n'
text+='\n'.join('- '+m['title']+': '+m['preview_review']['text'] for m in entries if m.get('preview_review'))+'\n'
text+='\n## Archivos\n\n- [Inventario CSV](INVENTARIO.csv).\n- [Métricas](summary.json).\n- [Integridad de las descargas](source-integrity.json).\n- [Prueba del navegador](browser-verification.json).\n'
text+='\n'.join('- [Contacto visual '+str(i+1)+'](contacto-'+str(i+1)+'.jpg)' for i in range(math.ceil(len(ready)/25)))
text+='\n\nBase técnica acumulada: `E:\\l2-local\\research\\rig-database-20261028\\rig-catalog.sqlite`. Se conservó una revisión SQLite coherente antes de ampliarla. Los originales y los favoritos del navegador real no fueron alterados. Respaldo de catálogo y visor en `E:\\l2-local\\backups\\external-assets-round4-20261028`.\n'
(OUT/'REVISION.md').write_text(text,encoding='utf-8')
print(json.dumps(metrics))
