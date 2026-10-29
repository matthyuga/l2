from pathlib import Path
from xml.sax.saxutils import escape
import json,hashlib,math
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
import pymupdf
from catalog import GROUPS

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent.parent
OUT=PROJECT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
QA=PROJECT/'tmp/pdfs/power-catalog';QA.mkdir(parents=True,exist_ok=True)
for name,font in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/font)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
W,H=A4;M=40;CW=W-2*M
INK=colors.HexColor('#253349');MUTED=colors.HexColor('#5D6C80')
PAL={k:colors.HexColor(v) for k,v in dict(gold='#A67612',violet='#7045A0',bronze='#88653D',blue='#3264A3',teal='#19787C',red='#B34B43',green='#3F7A52').items()}
def light(col):return colors.Color(.92+.08*col.red,.92+.08*col.green,.92+.08*col.blue)
ST={key:ParagraphStyle(key,fontName=font,fontSize=size,leading=leading,textColor=INK,spaceAfter=0) for key,font,size,leading in [('body','Body',10.3,14.5),('small','Body',8.5,11.5),('name','Body',9.3,12),('cell','Body',8,10.5),('head','Bold',8.5,11)]}
path=OUT/'L2-catalogo-indices-de-poder.pdf';c=canvas.Canvas(str(path),pagesize=A4)
c.setTitle('L2 - Catálogo de índices de poder propuestos');c.setAuthor('Proyecto L2 - Kevin')
num=0;layout=[]
allrows=[]
for group,cat,note,rows in GROUPS:
 for name,normal,role,ref,origin in rows:
  reduced=normal/2;maximum=normal*17/8
  allrows.append(dict(nombre=name,grupo=group,color=cat,reducido=reduced,normal=normal,maximo_hipotetico=maximum,recordatorio=role,referencia=ref,origen=origin))
assert len({r['nombre'] for r in allrows})==len(allrows)
lookup={r['nombre']:r for r in allrows}
def fmt(n):
 if int(n)==n:return f'{int(n):,}'.replace(',','.')
 return f'{int(n):,}'.replace(',','.')+','+str(n).split('.')[1]
def tx(x,y,s,size=10,bold=False,col=INK):c.setFillColor(col);c.setFont('Bold' if bold else 'Body',size);c.drawString(x,y,s)
def p(s,y,style='body',x=M,width=CW,raw=False):
 o=Paragraph(s if raw else escape(s),ST[style]);_,h=o.wrap(width,H);o.drawOn(c,x,y-h);return y-h
def begin(title,sub,cat='teal'):
 global num
 num+=1;c.bookmarkPage('page'+str(num));c.addOutlineEntry(title,'page'+str(num),0)
 c.setFillColor(PAL[cat]);c.rect(0,H-8,W,8,fill=1,stroke=0)
 tx(M,H-32,'LINEAGE II / CATÁLOGO NUMÉRICO DE PERSONAJES',8,True,MUTED)
 style=ParagraphStyle('title',fontName='Bold',fontSize=23,leading=27,textColor=INK)
 obj=Paragraph(escape(title),style);_,h=obj.wrap(CW,H);obj.drawOn(c,M,H-51-h)
 return p(sub,H-62-h,'small')-19
def end(y):
 assert y>48,(num,y)
 c.setStrokeColor(colors.HexColor('#DDE4EB'));c.line(M,38,W-M,38)
 tx(M,23,'27/10/2026 · Todos los IP son propuestas inventadas; no estadísticas oficiales.',7.5,col=MUTED)
 c.setFont('Bold',8);c.drawRightString(W-M,23,str(num));layout.append({'pagina':num,'fondo':y});c.showPage()
def table(headers,rows,widths,y,cat='teal',normalcol=None):
 t=Table([[Paragraph(escape(x),ST['head']) for x in headers]]+rows,colWidths=widths)
 commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,-1),'Body'),('FONTSIZE',(0,0),(-1,-1),8.4),('BACKGROUND',(0,0),(-1,0),light(PAL[cat])),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#D5DEE8')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]
 if normalcol is not None:commands += [('BACKGROUND',(normalcol,1),(normalcol,-1),light(PAL[cat])),('FONTNAME',(normalcol,1),(normalcol,-1),'Bold')]
 t.setStyle(TableStyle(commands));_,h=t.wrap(CW,H);t.drawOn(c,M,y-h);return y-h-15

y=begin(f'{len(allrows)} personajes, una escala','Índices de Poder (IP) para comparar, recordar y después ajustar')
y=p('Este catálogo convierte nuestra escala numérica en una ayuda de memoria. Reúne los personajes de las guías y algunos nombres presentes en sus fuentes enlazadas. Cada fila incluye un recordatorio de identidad y una referencia para volver al contexto.',y)-17
y=p('Las identidades proceden de las guías; todos los números y sus comparaciones son decisiones creativas. No se calcularon a partir de HP, nivel, estadísticas o duelos oficiales.',y)-20
y=p('Tu ejemplo como patrón de lectura',y,raw=False)-11
example=[[Paragraph('Estado hipotético',ST['name']),'200.000','400.000','850.000']]
y=table(['Ejemplo','Reducido','Normal','Máximo'],example,[190,(CW-190)/3,(CW-190)/3,(CW-190)/3],y,normalcol=2)
y=p('Reducido = 0,5 × normal. Máximo hipotético = 2,125 × normal. Aquí son columnas matemáticas de referencia: no afirman que cada personaje tenga un ritual incompleto, una transformación o un estado de furia. Podemos cambiarlas individualmente después.',y,'small')-18
y=p('Cómo leer las cifras',y)-9
for s in ['La columna NORMAL es la principal para memorizar. El número mide poder personal propuesto, no todo un reino, legión o encuentro de raid.','ANCLA indica una cifra ya propuesta en el chat. NUEVO indica una ubicación añadida en esta edición; ambas son inventadas.','Entre nobles, docentes y figuras poco descritas, la cifra solo reserva un lugar revisable. Poder político y conocimiento no se transforman automáticamente en daño.']:
 y=p('- '+s,y)-10
y=p('Unidades y referencias',y)-8
y=p('1 k = 1.000 IP; 1 M = 1.000.000 IP. En las tablas se escriben las cifras completas con puntos de millares. F = guía de fuerzas de 24 páginas; D = dossier ampliado de 45 páginas. “ref.26” remite a las biografías oficiales enlazadas en F.',y,'small')-15
y=p('Navegación: nueve grupos por tema, ranking general y ejemplos de comparación. El lector PDF dispone de marcadores por página.',y,'small')
end(y)

for group,cat,note,rows in GROUPS:
 y=begin(group,note,cat)
 vals=[]
 for name,normal,role,ref,origin in rows:
  r=lookup[name]
  desc='<b>'+escape(name)+'</b><br/><font size="8" color="#5D6C80">'+escape(role)+'</font>'
  vals.append([Paragraph(desc,ST['name']),fmt(r['reducido']),fmt(normal),fmt(r['maximo_hipotetico']),Paragraph(escape(ref)+'<br/>'+origin.upper(),ST['cell'])])
 widths=[CW-3*70-75,70,70,70,75]
 y=table(['Personaje / recordatorio','Reducido','NORMAL','Máximo hipotético','Guía / cifra'],vals,widths,y,cat,normalcol=2)
 y=p('Comparación de diseño: el orden de estas filas no acredita quién ganaría un duelo en el lore. Las condiciones personales, rituales y apoyos se definirán al desarrollar cada encuentro.',y,'small')
 end(y)

ranking=sorted(allrows,key=lambda r:(-r['normal'],r['nombre']))
for offset in range(0,len(ranking),18):
 chunk=ranking[offset:offset+18]
 y=begin('Ranking general',f'Poder normal propuesto · puestos {offset+1}-{offset+len(chunk)} de {len(ranking)}','blue')
 vals=[]
 for pos,r in enumerate(chunk,offset+1):
  vals.append([str(pos),Paragraph(escape(r['nombre']),ST['name']),fmt(r['normal']),Paragraph(escape(r['grupo']),ST['cell'])])
 y=table(['Puesto','Personaje','IP normal','Grupo'],vals,[34,CW-34-100-135,100,135],y,'blue',normalcol=2)
 y=p('Misma cifra = misma referencia inicial; no igualdad demostrada de capacidades. Un puesto refleja únicamente esta propuesta editorial.',y,'small')
 end(y)

y=begin('Comparaciones para recordar','Los resultados comparan nuestra escala; no son hazañas acreditadas','violet')
pairs=[('Hardin / Einhovant','Death Lord Hallate'),('Beleth','Hardin / Einhovant'),('Baium transformado','Beleth'),('Anakim','Baium transformado'),('Antharas','Baium transformado'),('Shilen','Valakas'),('Gran Kain','Shilen'),('Gustin','Raoul')]
vals=[]
for a,b in pairs:
 ratio=lookup[a]['normal']/lookup[b]['normal']
 vals.append([Paragraph(escape(a)+'<br/>'+fmt(lookup[a]['normal']),ST['name']),Paragraph(escape(b)+'<br/>'+fmt(lookup[b]['normal']),ST['name']),f'{ratio:.2f}'.replace('.',',')+' ×'])
y=table(['A','B','IP de A / IP de B'],vals,[CW*.40,CW*.40,CW*.20],y,'violet')
y=p('Por ejemplo: Raoul queda por debajo de Gustin en poder personal propuesto, aunque su capacidad de organizar un reino pueda ser muchísimo mayor. Así el catálogo separa combate, autoridad y función narrativa.',y)-13
y=p('Revisión posterior sugerida: escoger un solo grupo, revisar qué versión de cada personaje queremos usar y ajustar sus cifras juntas. No mover un número aislado sin mirar sus vecinos.',y,'small')
end(y)

y=begin('Fuentes, versiones y pendientes','Las cifras son nuevas; el contexto se rastrea hasta las guías','teal')
for title,body in [
 ('F / Fuerzas, poderes y conflictos','L2-fuerzas-poderes-y-conflictos.pdf, 24 páginas. Resume deidades, legado imperial, sellos, instituciones, criaturas y conflictos. Páginas y fuente 26 orientan las referencias del catálogo.'),
 ('D / Atlas y dossier ampliado','L2-atlas-dossier-narrativo-ampliado.pdf, 45 páginas. Ciudades, nombres completos, revisión de modelos, prólogo y propuestas. Para nobleza y maestros se usaron especialmente sus páginas 6-15.'),
 ('Personajes añadidos desde las fuentes enlazadas','Kain, Erica, Devianne, Rukal, Teon, Shikken, Seresin, Orim y Lionel Hunter se recuerdan mediante las biografías enlazadas por la guía. No se afirma que cada uno tuviera allí una ficha extensa.'),
 ('Alias y estados','Hardin/Einhovant figura una vez. Cedric y Sedrick se mantienen separados. Baium se evalúa transformado. Shilen se evalúa como potencial plenamente manifestado. Freya queda como referencia externa cuya versión narrativa está pendiente.'),
 ('Los casos más tentativos','Triol, Halisha, Solina, los demás dioses y numerosos gobernantes reciben ahora números de diseño sin medición canónica comparable. Eso permite recordarlos y discutir su lugar, no convierte esa ubicación en evidencia del lore.'),
 ('Lo que no se ha hecho','No se calculó un IP oficial, no se modificaron estadísticas ni se implementaron formas de combate. Tampoco se sumaron automáticamente ejércitos, guardianes, máquinas o el poder completo de los sellos a su propietario.'),
]:
 y=p(title,y,'body')-5;y=p(body,y,'small')-15
url='https://legacy-lineage2.com/background/leading_role.html'
y=p('<a href="'+url+'" color="#3264A3">Biografías oficiales históricas: abrir fuente</a>',y,'small',raw=True)-12
y=p('Los PDF anteriores se conservan sin cambios. La futura calibración puede conservar estos números, sustituirlos por intervalos o dar a cada individuo sus propios estados reducido/normal/máximo.',y,'small')
end(y)
c.save()

inputs=[]
for filename in ['L2-fuerzas-poderes-y-conflictos.pdf','L2-atlas-dossier-narrativo-ampliado.pdf']:
 source=OUT/filename;inputs.append({'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':len(pymupdf.open(source))})
meta={'fecha':'2026-10-27','tipo':'escala creativa, no datos oficiales','factores':{'reducido':.5,'normal':1,'maximo_hipotetico':2.125},'personajes':allrows,'inputs':inputs,'pdf':str(path),'paginas':num,'layout':layout}
(ROOT/'catalogo.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
md='# Catálogo de índices de poder propuestos\n\nTodos los números son inventados. Reducido y máximo son referencias derivadas, no estados confirmados.\n\n| Personaje | Grupo | Reducido | Normal | Máximo hipotético | Referencia |\n|---|---|---:|---:|---:|---|\n'
for r in ranking:md+='| '+' | '.join([r['nombre'],r['grupo'],fmt(r['reducido']),fmt(r['normal']),fmt(r['maximo_hipotetico']),r['referencia']])+' |\n'
(ROOT/'CATALOGO-IP.md').write_text(md,encoding='utf-8')
doc=pymupdf.open(path)
for i,page in enumerate(doc):
 assert '\ufffd' not in page.get_text()
 page.get_pixmap(matrix=pymupdf.Matrix(.95,.95)).save(QA/f'page-{i+1:02d}.png')
print(json.dumps({'pdf':str(path),'pages':len(doc),'characters':len(allrows),'minimum_bottom':min(x['fondo'] for x in layout),'qa':str(QA)},ensure_ascii=False))
