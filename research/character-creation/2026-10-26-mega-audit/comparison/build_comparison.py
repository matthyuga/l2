from pathlib import Path
import json,html,os,zipfile
from PIL import Image,ImageDraw,ImageFont
work=Path(__file__).resolve().parent;root=work.parent
current=json.loads((work/'current-manifest.json').read_text(encoding='utf8'))
candidate=json.loads((root/'gallery-manifest.json').read_text(encoding='utf8'))
v9=root.parent/'2026-10-26-tanda2-v9'
installed={}
if (v9/'installation.json').exists() and json.loads((v9/'installation.json').read_text())['live_installed']:
 installed={(x['model'],x['source_style']):x['letter'] for x in json.loads((v9/'assets-manifest.json').read_text())['items']}
for r in candidate:
 r['batch']='tanda2';r['installed_style']=installed.get((r['sex']+r['group'],r['style']))
rows=current+candidate
for r in rows:
 r['images']=[Path(os.path.relpath(f,work)).as_posix() for f in r['files']]
 assert all(Path(f).is_file() for f in r['files'])
groups=list(dict.fromkeys(r['group'] for r in current))
names={r['group']:r['title'] for r in rows}
template='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Original · Tanda 1 · Tanda 2</title>
<style>*{box-sizing:border-box}body{margin:0;background:#12151b;color:#e8edf5;font:16px system-ui,sans-serif}main{max-width:1650px;margin:auto;padding:24px}h1{font-size:30px;margin:0 0 12px}p{line-height:1.6;color:#bec9d8}a{color:#91c8ff}.toolbar{position:sticky;top:0;z-index:3;background:#12151bf2;border-bottom:1px solid #354052;padding:14px 0;display:flex;gap:14px;align-items:center;flex-wrap:wrap}select,button{font:inherit;background:#232b38;color:#fff;border:1px solid #536277;padding:10px;border-radius:8px}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:24px}.batch{background:#1b212c;border:1px solid #354052;border-radius:12px;overflow:hidden}.heading{padding:18px;position:sticky;top:73px;background:#1b212cf5;z-index:2;border-top:5px solid var(--accent)}h2{font-size:22px;margin:0 0 5px}.status{font-size:13px;color:var(--accent)}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;padding:12px}.card{background:#242c39;border-radius:8px;padding:10px;min-width:0}.card strong{display:block;padding-bottom:8px}.views{display:flex}.views a{width:50%}.views img{width:100%;display:block;cursor:zoom-in}.view-labels{display:flex;justify-content:space-around;font-size:12px;color:#b9c3d1}.note{font-size:13px;margin:0;padding:0 18px 12px}dialog{background:#151a23;color:white;border:1px solid #4b5d76;border-radius:12px;max-width:95vw;padding:16px}dialog::backdrop{background:#000b}dialog img{height:min(75vh,680px);max-width:85vw;object-fit:contain;image-rendering:auto}dialog p{margin:4px 0}#stats{font-size:13px;color:#9fb0c8}@media(max-width:850px){.columns{grid-template-columns:1fr}.heading{position:static}.cards{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}h1{font-size:25px}}</style>
<main><h1>Original · Tanda 1 · Tanda 2</h1>
<p><b>Original + tanda 1 = selección actual del servidor.</b> La tanda 2 es el paquete MEGA y todavía no está instalada. Estas imágenes son renders de recursos reales, fuera del juego; pueden variar la luz, el color y la transparencia respecto al cliente. Se muestra un color por diseño.</p>
<div class="toolbar"><label>Modelo <select id="model"></select></label><label>Sexo <select id="sex"><option value="M">Masculino</option><option value="F">Femenino</option></select></label><a id="sheet" href="#">Abrir lámina de los tres grupos</a><span id="stats"></span></div>
<div id="columns" class="columns"></div><p>Las letras de tanda 2 indican la opción que reemplaza en su cliente de origen; no son letras nuevas asignadas en nuestro servidor. Una imagen parecida no demuestra por sí sola que dos recursos sean idénticos. No se modificó el cliente ni el servidor para crear esta galería.</p>
<p><a href="../galeria/index.html">Galería anterior de MEGA</a> · <a href="Comparacion-original-tanda1-tanda2.zip">Descargar las 14 láminas</a></p></main>
<dialog id="zoom"><button id="close">Cerrar</button><p id="caption"></p><img id="large"></dialog>
<script>const DATA=__DATA__,GROUPS=__GROUPS__,NAMES=__NAMES__;
const model=document.querySelector('#model'),sex=document.querySelector('#sex');model.innerHTML=GROUPS.map(g=>`<option value="${g}">${NAMES[g]}</option>`).join('');
const batches=[['original','Original','#91b9e8','Instalado · opciones originales'],['tanda1','Tanda 1','#7edba4','Instalada · dos extras añadidos'],['tanda2','Tanda 2 · MEGA','#efc27d','Sin instalar · candidatos para comparar']];
function show(){let selected=DATA.filter(r=>r.group===model.value&&r.sex===sex.value);document.querySelector('#columns').innerHTML=batches.map(([id,title,color,status])=>{let list=selected.filter(r=>r.batch===id);return `<section class="batch" style="--accent:${color}"><div class="heading"><h2>${title}</h2><span class="status">${status}</span></div><p class="note">${list.length} opciones</p><div class="cards">${list.map(r=>`<article class="card"><strong>${id==='tanda2'?'Origen ': 'Type '}${r.style}${r.installed_style?' ? instalado como '+r.installed_style:''}</strong><div class="views">${r.images.map((src,i)=>`<a href="${src}" data-caption="${NAMES[r.group]} · ${r.sex==='M'?'masculino':'femenino'} · ${title} ${r.style} · ${i?'espalda':'frente'}"><img loading="lazy" src="${src}" alt="${title} ${r.style} ${i?'espalda':'frente'}"></a>`).join('')}</div><div class="view-labels"><span>Frente</span><span>Espalda</span></div></article>`).join('')}</div></section>`}).join('');document.querySelector('#sheet').href=`sheets/${model.value}-${sex.value}.jpg`;document.querySelector('#stats').textContent=`${selected.filter(r=>r.batch!=='tanda2'||r.installed_style).length} actuales + ${selected.filter(r=>r.batch==='tanda2'&&!r.installed_style).length} candidatos sin instalar`;}
model.onchange=sex.onchange=show;show();document.querySelector('#columns').addEventListener('click',e=>{const a=e.target.closest('a[data-caption]');if(!a)return;e.preventDefault();document.querySelector('#large').src=a.href;document.querySelector('#caption').textContent=a.dataset.caption;document.querySelector('#zoom').showModal()});document.querySelector('#close').onclick=()=>document.querySelector('#zoom').close();</script></html>'''
page=template.replace('__DATA__',json.dumps(rows,ensure_ascii=False)).replace('__GROUPS__',json.dumps(groups)).replace('__NAMES__',json.dumps(names,ensure_ascii=False))
(work/'index.html').write_text(page,encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',37)
sheets=work/'sheets';sheets.mkdir(exist_ok=True)
for group in groups:
 for gender in ['M','F']:
  im=Image.new('RGB',(2240,1450),(23,27,34));draw=ImageDraw.Draw(im)
  draw.text((22,15),names[group]+' · '+('Masculino' if gender=='M' else 'Femenino'),font=big,fill='white')
  draw.text((22,65),'Recursos reales · vista previa fuera del juego · un color por diseño',font=small,fill=(185,198,215))
  for j,(batch,title,status,color) in enumerate([('original','ORIGINAL','Instalado',(145,185,232)),('tanda1','TANDA 1','Instalada · extras',(126,219,164)),('tanda2','TANDA 2 · MEGA','Sin instalar · letras del cliente de origen',(239,194,125))]):
   y=115+j*440;draw.text((22,y),title+' — '+status,font=font,fill=color)
   for i,r in enumerate(x for x in rows if x['group']==group and x['sex']==gender and x['batch']==batch):
    x=i*320
    for v,f in enumerate(r['files']):
     image=Image.open(f).convert('RGB');image.thumbnail((160,182));im.paste(image,(x+v*160,y+48))
    draw.text((x+16,y+245),('Origen ' if batch=='tanda2' else 'Type ')+r['style']+(' > '+r['installed_style'] if r.get('installed_style') else ''),font=font,fill='white')
    draw.text((x+12,y+287),'Frente / espalda',font=small,fill=(180,193,210))
  im.save(sheets/(group+'-'+gender+'.jpg'),quality=95)
with zipfile.ZipFile(work/'Comparacion-original-tanda1-tanda2.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sheets.glob('*.jpg'):z.write(f,f.name)
assert len(current)==112 and len(candidate)==84,(len(current),len(candidate))
assert len(list(sheets.glob('*.jpg')))==14
(work/'comparison-data.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
old=root/'galeria/index.html';text=old.read_text(encoding='utf8')
if 'Comparar con Original' not in text:text=text.replace('<h1>Peinados del paquete MEGA</h1>','<h1>Peinados del paquete MEGA</h1><p><a href="../comparison/index.html"><b>Comparar con Original + Tanda 1 instalados</b></a></p>');old.write_text(text,encoding='utf8')
print('PASS: 84 originales + 28 tanda 1 + 84 tanda 2; 392 vistas; 14 láminas. No se cambió el cliente.')
