from pathlib import Path
import json,re,hashlib,math
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
import pymupdf
from content import PAGES,SOURCES,CATEGORIES

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
OUT=PROJECT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
QA=PROJECT/'tmp/pdfs/narrative-powers';QA.mkdir(parents=True,exist_ok=True)
DEST=OUT/'L2-fuerzas-poderes-y-conflictos.pdf'
SOURCES.append(('R','Bitácoras y revisión de assets del proyecto','E:/l2-local/research/narrative-asset-review-20261026/REVISION.md','También identidad/prólogo y cobertura, 26/10/2026.'))
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
W,H=A4;M=42;CW=W-2*M
INK=colors.HexColor('#203047');MUTED=colors.HexColor('#596B80')
P={k:colors.HexColor(v) for k,v in dict(gold='#A67612',violet='#7045A0',bronze='#88653D',blue='#3264A3',teal='#19787C',red='#B34B43',green='#3F7A52',neutral='#626C7B').items()}
def pale(col):return colors.Color(.90+.10*col.red,.90+.10*col.green,.90+.10*col.blue)
ST={
 'body':ParagraphStyle('body',fontName='Body',fontSize=10.3,leading=14.5,textColor=INK),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.5,leading=11.5,textColor=MUTED),
 'card':ParagraphStyle('card',fontName='Body',fontSize=10.2,leading=14,textColor=INK),
 'head':ParagraphStyle('head',fontName='Bold',fontSize=10.4,leading=14,textColor=INK),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=9.2,leading=12.5,textColor=INK),
 'cellhead':ParagraphStyle('cellhead',fontName='Bold',fontSize=9,leading=12,textColor=INK),
}
c=canvas.Canvas(str(DEST),pagesize=A4)
c.setTitle('Lineage II - Fuerzas, poderes y conflictos')
c.setAuthor('Proyecto L2 - Kevin')
c.setSubject('Mapa conceptual del lore: de los poderes principales a los conflictos regionales. Base Interlude.')
page_no=0;layout=[]

def text(x,y,s,size=10,font='Body',color=INK):
 c.setFont(font,size);c.setFillColor(color);c.drawString(x,y,s)

def para(s,y,x=M,width=CW,style='body',raw=False):
 obj=Paragraph(s if raw else escape(s),ST[style]);_,h=obj.wrap(width,H)
 obj.drawOn(c,x,y-h);return y-h

def begin(title,sub='',cat='teal'):
 global page_no
 page_no+=1;c.bookmarkPage('p'+str(page_no));c.addOutlineEntry(title,'p'+str(page_no),0)
 c.setFillColor(P[cat]);c.rect(0,H-8,W,8,fill=1,stroke=0)
 text(M,H-32,'LINEAGE II  /  PODERES Y CONFLICTOS',8,'Bold',MUTED)
 title_style=ParagraphStyle('title',fontName='Bold',fontSize=24,leading=28,textColor=INK)
 p=Paragraph(escape(title),title_style);_,h=p.wrap(CW,100);p.drawOn(c,M,H-51-h)
 y=H-51-h-11
 if sub:y=para(sub,y,style='small')-16
 return y

def finish(y):
 assert y>=49,f'Page {page_no} overflow: {y}'
 c.setStrokeColor(colors.HexColor('#DCE3EB'));c.line(M,37,W-M,37)
 text(M,23,'27/10/2026 · Base Interlude · Colores editoriales, no alineamientos oficiales',7.4,color=MUTED)
 c.setFont('Bold',8);c.drawRightString(W-M,23,str(page_no))
 layout.append({'page':page_no,'bottom':round(y,1)})
 c.showPage()

def card(title,body,refs,cat,y):
 head=Paragraph(escape(title),ST['head']);_,hh=head.wrap(CW-30,H)
 p=Paragraph(escape(body),ST['card']);_,ph=p.wrap(CW-30,H)
 rh=13 if refs else 0
 height=hh+ph+rh+25
 c.setFillColor(pale(P[cat]));c.roundRect(M,y-height,CW,height,5,fill=1,stroke=0)
 c.setFillColor(P[cat]);c.rect(M,y-height,4,height,fill=1,stroke=0)
 head.drawOn(c,M+15,y-11-hh);p.drawOn(c,M+15,y-17-hh-ph)
 if refs:text(M+15,y-height+9,'Fuentes ['+refs+']',8,color=MUTED)
 return y-height-12

def gridtable(headers,rows,y,widths=None):
 widths=widths or [CW*.23,CW*.38,CW*.39]
 vals=[[Paragraph(escape(x),ST['cellhead']) for x in headers]]+[[Paragraph(escape(x),ST['cell']) for x in row] for row in rows]
 t=Table(vals,colWidths=widths)
 cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E6EEF5')),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#CCD6E2'))]
 for i in range(1,len(vals)):cmds.append(('BACKGROUND',(0,i),(0,i),pale(P['teal'])))
 t.setStyle(TableStyle(cmds));_,h=t.wrap(CW,H);t.drawOn(c,M,y-h)
 return y-h-17

def box(x,y,w,h,title,detail,cat):
 c.setFillColor(pale(P[cat]));c.setStrokeColor(P[cat]);c.setLineWidth(.7);c.roundRect(x,y,w,h,5,fill=1,stroke=1)
 para(title,y+h-10,x+10,w-20,'head')
 if detail:para(detail,y+h-28,x+10,w-20,'small')

def line(x1,y1,x2,y2,label='',dashed=False):
 c.setStrokeColor(MUTED);c.setLineWidth(.8);c.setDash(3,3) if dashed else c.setDash()
 c.line(x1,y1,x2,y2);c.setDash()
 if label:
  angle=math.atan2(y2-y1,x2-x1)
  # Label on an opaque neutral backing prevents crossing line text.
  mx=(x1+x2)/2;my=(y1+y2)/2;tw=pdfmetrics.stringWidth(label,'Body',8)
  c.setFillColor(colors.white);c.rect(mx-tw/2-3,my-3,tw+6,12,fill=1,stroke=0)
  text(mx-tw/2,my,label,8,color=MUTED)

def diagram(kind,y):
 if kind=='scales':
  bands=[('01','ORIGEN Y LÍMITES DEL MUNDO','Einhasad, Gran Kain, Shilen y la familia divina','gold'),('02','PODERES QUE ATRAVIESAN ERAS','Gigantes, dragones, legado imperial y sellos','bronze'),('03','QUIÉN GOBIERNA Y QUIÉN LEGITIMA','Aden, Elmore, Gracia, nobles y cabales','blue'),('04','QUIÉN SABE, INTERPRETA O HACE PACTOS','Templos, Ivory Tower, Hardin, Beleth y cultos','teal'),('05','QUIÉN CONTROLA UN TERRITORIO','Hallate, Ketra/Varka, guardianes y colonias','red'),('06','QUIÉN VIVE LAS CONSECUENCIAS','Clanes, soldados, familias y el personaje jugador','green')]
  for num,title,detail,cat in bands:
   c.setFillColor(pale(P[cat]));c.rect(M,y-53,CW,53,fill=1,stroke=0)
   text(M+12,y-31,num,18,'Bold',P[cat]);text(M+49,y-20,title,9.2,'Bold');text(M+49,y-38,detail,9)
   y-=62
  return y-3
 if kind=='family':
  top=y-58
  box(M+35,top,170,55,'EINHASAD','Potencia originaria','gold');box(W-M-205,top,170,55,'GRAN KAIN','Potencia originaria','neutral')
  mid=top-34
  line(M+120,top,M+120,mid);line(W-M-120,top,W-M-120,mid);line(M+120,mid,W-M-120,mid)
  bottom=mid-100;bw=(CW-24)/5
  for i,(name,dom,cat) in enumerate([('SHILEN','Agua; luego muerte','violet'),('PAAGRIO','Fuego','red'),('MAPHR','Tierra','bronze'),('SAYHA','Viento','teal'),('EVA','Arte; luego agua','blue')]):
   x=M+i*(bw+6);line(W/2,mid,x+bw/2,bottom+60)
   box(x,bottom,bw,60,name,dom,cat)
  text(M,bottom-20,'Esquema de descendencia y funciones según el relato mítico [01,03,04].',8,color=MUTED)
  return bottom-41
 if kind=='seals':
  # Two levels of supernatural association, separated from mortal politics.
  top=y-60
  box(M,top,213,58,'EINHASAD','Poder creador','gold');box(W-M-213,top,213,58,'SHILEN','Muerte e inframundo','violet')
  sec=top-105
  box(M,sec,213,66,'ANAKIM / NEPHILIM','Agente y fuerzas de luz [19]','gold');box(W-M-213,sec,213,66,'LILITH / LILIM','Liderazgo y fuerzas vinculadas [19]','violet')
  line(M+106,top,M+106,sec+66,'vínculo sobrenatural');line(W-M-106,top,W-M-106,sec+66,'vínculo sobrenatural')
  line(M+213,sec+33,W-M-213,sec+33,'oposición')
  center=sec-120
  box(M+134,center,243,67,'SELLOS / PODER ENTERRADO','Herencia y objeto de disputa [17,18]','bronze')
  line(M+106,sec,M+188,center+67,'encierro');line(W-M-106,sec,W-M-188,center+67,'encierro')
  third=center-108
  box(M,third,213,62,'LORDS OF DAWN','Cabala política [18]','blue');box(W-M-213,third,213,62,'ARMY OF DUSK','Cabala política [18]','blue')
  line(M+106,third+62,M+188,center,'disputa');line(W-M-106,third+62,W-M-188,center,'disputa')
  last=third-77
  box(M+90,last,CW-180,46,'SHUNAIMAN / BAIUM','Control heredado y después perdido [17]','bronze')
  return last-20
 if kind=='conflicts':
  return gridtable(['Escala','Conflicto','Casos / pregunta'],[
   ['MUNDIAL','Autoridad divina / autonomía','Gigantes y dioses [05,06]. ¿Quién puede crear vida?'],
   ['MUNDIAL','Pérdida / venganza','Shilen [03]. ¿Cuándo una reparación se vuelve devastación?'],
   ['IMPERIAL','Poder / mortalidad','Baium y Frintezza [13,25]. ¿Qué se sacrifica por durar?'],
   ['POLÍTICA','Herencia / participación','Sellos, Dawn y Dusk [17,18]. ¿Quién decide su uso?'],
   ['POLÍTICA','Unidad / autonomía','Reinos y señoríos [14-16]. ¿Protección o subordinación?'],
   ['INSTITUCIONAL','Conocimiento / responsabilidad','Ivory Tower y Beleth [11]. ¿Quién paga el experimento?'],
   ['REGIONAL','Fe / obediencia','Rune y el valle [23,L2]. ¿Qué voluntad tiene el guardián?'],
   ['REGIONAL','Territorio / supervivencia','Ketra, Varka y colonias [22-24]. ¿Se puede negociar?'],
   ['PERSONAL','Lealtad / proyecto propio','Biografías [26]. ¿Qué haces cuando tu institución falla?'],
  ],y,[CW*.17,CW*.31,CW*.52])
 if kind=='timeline':
  eras=[('MITO DE ORIGEN','Formación del mundo y dioses; creación de pueblos. [01,02]','gold'),('GUERRAS DIVINAS','Caída de Shilen, retirada de sus fuerzas, cambio de Eva. [03,04]','violet'),('REBELIÓN Y CAÍDA GIGANTE','Desafío a los dioses, catástrofe y supervivientes. [05,06]','bronze'),('HEGEMONÍAS MORTALES','Alianzas, aprendizaje mágico y dominio humano. [07,08]','green'),('ELMOREDEN Y SU LEGADO','Shunaiman, reforma religiosa, Baium y decadencia. [09,13]','bronze'),('REINOS Y COMPETENCIA','Elmore, unificación de Aden/Gracia y luchas por sellos. [14-18]','blue')]
  for i,(title,desc,cat) in enumerate(eras):
   c.setFillColor(P[cat]);c.circle(M+8,y-18,5,fill=1,stroke=0)
   if i<5:line(M+8,y-26,M+8,y-71)
   text(M+25,y-13,title,10,'Bold');para(desc,y-24,M+25,CW-25,'body');y-=78
  return y
 return y

# Cover: a concise reading map, not a generic title-only sheet.
y=begin('Fuerzas, poderes\ny conflictos de L2'.replace('\n',' '),'Una guía para comprender el tablero y preparar una reinterpretación','violet')
y=para('No todo poder es un reino. No todo conflicto necesita el mismo enemigo.',y,style='head')-21
y=para('Este documento ordena las fuerzas desde las que alteran el mundo hasta las que deciden la vida de una región. Resume objetivos, recursos, rivalidades y límites de lo que sabemos. Las preguntas de adaptación están separadas del material histórico.',y)-23
text(M,y,'CÓDIGO VISUAL',10,'Bold');y-=23
for i,(cat,code,label) in enumerate(CATEGORIES):
 col=i%2;row=i//2;x=M+col*CW/2;yy=y-row*31
 c.setFillColor(P[cat]);c.roundRect(x,yy-6,22,21,3,fill=1,stroke=0);text(x+7,yy,code,10,'Bold',colors.white);text(x+31,yy,label,9.4)
y-=4*31+8
y=para('Los colores indican temas para orientarse. No son uniformes oficiales ni significan bien, mal, alianza o subordinación.',y,style='small')-22
text(M,y,'RECORRIDOS DE LECTURA',10,'Bold');y-=24
targets=[('Para comprender el tablero',2),('Para entender sellos y cabales',7),('Para distinguir reinos y religiones',9),('Para criaturas y conflictos regionales',12),('Para reinterpretar y tomar decisiones',20)]
for label,target in targets:
 text(M,y,label,10);c.setFont('Bold',10);c.drawRightString(W-M,y,'p. '+str(target));c.linkRect('',f'p{target}',(M,y-4,W-M,y+12),relative=0,thickness=0);y-=25
y-=14
y=para('Base: mitos y relatos antiguos, C3-C5 y diálogos del datapack local. Las fuentes posteriores se identifican como tales. Consulta y edición: 27 de octubre de 2026.',y,style='small')
finish(y)

for page in PAGES:
 category='teal'
 if page['blocks']:category=page['blocks'][0][3]
 y=begin(page['title'],page['sub'],category)
 if page.get('kind'):y=diagram(page['kind'],y)
 if page.get('table'):y=gridtable(*page['table'],y)
 for block in page['blocks']:y=card(*block,y)
 finish(y)

# Three short, readable source sheets with direct links and local evidence.
for start in range(0,len(SOURCES),12):
 y=begin('Fuentes y grado de certeza',f'Referencias {start+1}-{min(start+12,len(SOURCES))} de {len(SOURCES)} · números citados en cada ficha')
 if start==0:
  y=para('Los mitos se leen como relatos, las fichas de criaturas como descripciones y los diálogos como testimonios. Las relaciones no documentadas se dejan abiertas. No se reprodujeron textos extensos de las fuentes.',y,style='small')-15
 for code,title,url,note in SOURCES[start:start+12]:
  head=f'<b>[{escape(code)}] {escape(title)}</b>'
  y=para(head,y,style='body',raw=True)-3
  if url.startswith('http'):
   link=f'<a href="{escape(url)}" color="#3264A3">{escape(url)}</a>'
   y=para(link,y,style='small',raw=True)-2
  else:y=para(url,y,style='small')-2
  y=para(note,y,style='small')-9
 finish(y)
c.save()

# Readable source and content snapshots for later maintenance.
snap={'fecha':'2026-10-27','enfoque':'Interlude; capas posteriores señaladas','colores':[(k,code,label) for k,code,label in CATEGORIES],'sources':SOURCES,'pages':PAGES,'pdf':str(DEST),'layout':layout}
local=[]
for code,title,url,note in SOURCES:
 if not url.startswith('http'):
  path=Path(url)
  if path.exists():local.append({'id':code,'path':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
snap['local_evidence']=local
(ROOT/'investigacion.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding='utf-8')
md='# Fuerzas, poderes y conflictos de L2\n\n27/10/2026. Síntesis con fuentes y propuestas diferenciadas.\n'
for page in PAGES:
 md+='\n## '+page['title']+'\n\n'+page['sub']+'\n'
 if page.get('table'):
  headers,rows=page['table'];md+='\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
  for row in rows:md+='| '+' | '.join(row)+' |\n'
 for title,body,refs,cat in page['blocks']:md+='\n### '+title+'\n\n'+body+(' Fuentes ['+refs+'].' if refs else '')+'\n'
md+='\n## Fuentes\n'
for code,title,url,note in SOURCES:md+='\n- ['+code+'] '+title+': '+url+' - '+note
(ROOT/'FUERZAS-Y-CONFLICTOS.md').write_text(md,encoding='utf-8')
doc=pymupdf.open(DEST)
for i,page in enumerate(doc):
 assert '\ufffd' not in page.get_text()
 page.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(QA/f'page-{i+1:02d}.png')
print(json.dumps({'pdf':str(DEST),'pages':len(doc),'sources':len(SOURCES),'minimum_bottom_margin':min(x['bottom'] for x in layout),'qa':str(QA)},ensure_ascii=False))
