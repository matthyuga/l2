from pathlib import Path
from xml.sax.saxutils import escape
import re,json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader,PdfWriter
import pymupdf

root=Path(__file__).resolve().parent
project=root.parent.parent
out=project/'output/pdf';out.mkdir(parents=True,exist_ok=True)
qa=project/'tmp/pdfs/narrative-dossier';qa.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('DossierArial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('DossierArialBold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFontFamily('DossierArial',normal='DossierArial',bold='DossierArialBold',italic='DossierArial',boldItalic='DossierArialBold')
styles=getSampleStyleSheet()
for key in ['BodyText','Normal','Heading1','Heading2','Heading3','Title']:
 styles[key].fontName='DossierArialBold' if key.startswith('Heading') or key=='Title' else 'DossierArial'
 styles[key].textColor=colors.HexColor('#233348')
styles['BodyText'].fontSize=10;styles['BodyText'].leading=14;styles['BodyText'].spaceAfter=8
styles['BodyText'].splitLongWords=True
styles['Heading1'].fontSize=21;styles['Heading1'].leading=25;styles['Heading1'].spaceAfter=16
styles['Heading2'].fontSize=14;styles['Heading2'].leading=18;styles['Heading2'].spaceBefore=15;styles['Heading2'].spaceAfter=7
styles['Heading3'].fontSize=11;styles['Heading3'].leading=15;styles['Heading3'].spaceBefore=11
styles['Title'].fontSize=29;styles['Title'].leading=35
styles.add(ParagraphStyle(name='SmallD',parent=styles['BodyText'],fontSize=8,leading=11))
styles.add(ParagraphStyle(name='CellD',parent=styles['BodyText'],fontSize=8,leading=10,spaceAfter=0))
styles.add(ParagraphStyle(name='BulletD',parent=styles['BodyText'],leftIndent=12,firstLineIndent=-8))

def plain(s):
 return s.replace('inequÃ­voca','inequívoca').replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u2212','-')

def rich(s):
 s=plain(s)
 links=[]
 def lnk(m):
  label,url=m.groups();n=len(links)
  if url.startswith(('https://','http://')):
   links.append('<a href="'+escape(url,{'"':'&quot;'})+'" color="#285E94">'+escape(label)+'</a>')
  else:links.append(escape(label)+' <font color="#65758A">('+escape(url)+')</font>')
  return f'ZZLINKTOKEN{n}ZZ'
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lnk,s)
 def bare(m):
  url=m.group(0);n=len(links)
  links.append('<a href="'+escape(url,{'"':'&quot;'})+'" color="#285E94">'+escape(url)+'</a>')
  return f'ZZLINKTOKEN{n}ZZ'
 s=re.sub(r'https?://[^\s<>`]+',bare,s)
 s=escape(s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'`([^`]+)`',r'<font color="#53657A">\1</font>',s)
 for i,item in enumerate(links):s=s.replace(f'ZZLINKTOKEN{i}ZZ',item)
 return s

class Doc(BaseDocTemplate):
 def __init__(self,path):
  super().__init__(str(path),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=52,bottomMargin=47,title='L2 - Atlas y dossier de investigación narrativa',author='Proyecto L2 - Kevin')
  self.addPageTemplates(PageTemplate(id='main',frames=Frame(46,47,A4[0]-92,A4[1]-99,id='normal'),onPage=self.decorate))
  self.headings=[]
 def decorate(self,c,doc):
  c.saveState();c.setFillColor(colors.HexColor('#66758A'));c.setFont('DossierArial',8)
  c.drawString(46,A4[1]-29,'L2 / DOSSIER NARRATIVO / 26.10.2026')
  c.drawString(46,26,'Historia documentada, hipótesis y propuestas diferenciadas')
  c.drawRightString(A4[0]-46,26,str(doc.page));c.restoreState()
 def beforeDocument(self):self.headings=[]
 def afterFlowable(self,f):
  if getattr(f,'_chapter',None):
   title,key=f._chapter;self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,0)
   self.notify('TOCEntry',(0,title,self.page,key));self.headings.append((title,self.page))

story=[]
def p(text,style='BodyText'):story.append(Paragraph(rich(text),styles[style]))
def chapter(title):
 story.append(PageBreak());h=Paragraph(escape(title),styles['Heading1']);h._chapter=(title,'chapter-'+str(len(story)));story.append(h)

def table(lines):
 cells=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
 cells=[r for r in cells if not all(re.fullmatch(r'[:\- ]+',x or '-') for x in r)]
 cols=max(map(len,cells));cells=[r+['']*(cols-len(r)) for r in cells]
 vals=[[Paragraph(rich(x),styles['CellD']) for x in row] for row in cells]
 if cols==7:widths=[26,122,43,47,48,43,A4[0]-92-329]
 elif cols==3:widths=[90,180,A4[0]-92-270]
 else:widths=[(A4[0]-92)/cols]*cols
 t=Table(vals,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EFF6')),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#A5B5C8')),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#DFE5EC')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 story.append(t);story.append(Spacer(1,10))

def markdown(path,skip_title=True):
 text=path.read_text(encoding='utf-8-sig');lines=text.splitlines();para=[];tab=[];fenced=False
 def flush():
  if para:p(' '.join(para));para.clear()
 def flusht():
  if tab:table(tab);tab.clear()
 for line in lines:
  line=line.strip()
  if line.startswith('```'):flush();flusht();fenced=not fenced;continue
  if line.startswith('|'):flush();tab.append(line);continue
  flusht()
  if not line:flush();continue
  m=re.match(r'^(#{1,5})\s+(.*)',line)
  if m:
   flush();level,title=m.groups()
   if len(level)==1 and skip_title:continue
   p(title,'Heading2' if len(level)<=2 else 'Heading3');continue
  if re.match(r'^[-*]\s+',line):flush();p('- '+line[2:],'BulletD');continue
  if re.match(r'^\d+\.\s+',line):flush();p(line,'BulletD');continue
  if line.startswith('>'):flush();p(line.lstrip('> '));continue
  para.append(line)
 flush();flusht()

story.append(Spacer(1,55));p('ATLAS Y DOSSIER\nDE INVESTIGACIÓN NARRATIVA'.replace('\n','<br/>'),'Title')
# Title uses literal XML break instead of escaped user content.
story[-1]=Paragraph('ATLAS Y DOSSIER<br/>DE INVESTIGACIÓN<br/>NARRATIVA',styles['Title'])
story.append(Spacer(1,18));p('Lineage II - base Interlude','Heading2')
p('Historia regional, protagonistas, criaturas, conflictos y preguntas para desarrollar el servidor.')
p('Edición de trabajo - 26 de octubre de 2026')
story.append(Spacer(1,24))
p('Esta edición reúne las investigaciones y bitácoras de la sesión, añade una revisión de zonas poco documentadas e incluye al final los cuatro mapas por tema y la grilla de 32 fichas. Las fuentes web se pueden abrir desde los enlaces del texto.')
p('Conserva las alternativas y contradicciones. Las propuestas de Kevin y del asistente no se convierten en hechos oficiales ni en funciones implementadas por figurar en este documento.')
p('Lectura sugerida: método y ampliación; región que interese; personajes/assets; reglas narrativas y propuestas. Usar el índice y los marcadores laterales del lector PDF.','SmallD')
story.append(PageBreak());p('Índice de lectura','Heading1')
toc=TableOfContents();toc.levelStyles=[ParagraphStyle(name='TOCD',fontName='DossierArial',fontSize=10,leading=15,leftIndent=0,firstLineIndent=0,spaceBefore=7,textColor=colors.HexColor('#233348'))];story.append(toc)
chapter('01 / Método, nuevas pistas y preguntas')
markdown(root/'AMPLIACION-DOSSIER-20261026.md')
chapter('02 / Las nueve ciudades y sus protagonistas')
markdown(project/'research/LORE-CIUDADES-INVESTIGACION-20261026.md')
chapter('03 / Rune, el valle y la guerra de la torre')
note=(root/'BITACORA-COBERTURA-20261026.md').read_text(encoding='utf-8')
section=note.split('## Lo conservado en esta ampliación')[1].split('## Grilla de seguimiento')[0]
for block in section.strip().split('\n\n'):p(block)
p('Testimonios locales para contrastar','Heading2')
for relative in ['html/guard/31343-1.htm','scripts/quests/Q00627_HeartInSearchOfPower/31518-01.htm','html/default/30950-1.htm']:
 source=project/'server/game/data'/relative
 text=source.read_text(encoding='utf-8-sig')
 text=re.sub(r'<a\b.*?</a>','',text,flags=re.S|re.I)
 text=re.sub(r'<br\s*/?>','\n',text,flags=re.I);text=re.sub('<[^>]+>','',text)
 p(relative,'Heading3')
 p('Transcripción local en inglés. Acredita el contenido de este datapack, sin asegurar coincidencia absoluta con todas las revisiones retail.','SmallD')
 for line in text.splitlines():
  if line.strip():p(line.strip())
chapter('04 / Personajes, modelos y pueblos de criaturas')
text=(root/'REVISION.md').read_text(encoding='utf-8')
text=text.split('## Ampliaci?n de lore:')[0]
temp=qa/'assets-clean.md';temp.write_text(text,encoding='utf-8');markdown(temp)
for name,title in [('seleccion-personajes.jpg','Selección visual de personajes'),('tribus-y-servidores.jpg','Tribus y servidores: referencias visuales')]:
 path=root/name
 if path.exists():
  story.append(PageBreak());p(title,'Heading2')
  from PIL import Image as PILImage
  with PILImage.open(path) as im:iw,ih=im.size
  scale=min((A4[0]-92)/iw,(A4[1]-160)/ih)
  story.append(Image(str(path),width=iw*scale,height=ih*scale));p('Lámina de revisión local. No acredita presencia en el mundo ni integración de recursos externos.','SmallD')
chapter('05 / Identidad, academia y prólogo')
markdown(project/'BITACORA-IDENTIDAD-ACADEMIA-Y-PROLOGO-20261026.md')
chapter('06 / Creación modular y competencias de aventura')
markdown(project/'BITACORA-CREACION-Y-ROLES-EXPLORACION-20261025.md')
chapter('07 / Propuesta de campaña y recuperación regional')
markdown(project/'PROPUESTA-LORE-L2-ULTIMO-BASTION-20261023.md')
chapter('08 / Festival, rescates y vínculos con animales')
markdown(project/'BITACORA-IDEAS-FESTIVAL-Y-RESCATE-20261021.md')
chapter('09 / Agenda por lugar y documentos de consulta')
data=json.loads((root/'cobertura-narrativa.json').read_text(encoding='utf-8'))
for i,r in enumerate(data['lugares'],1):
 start=len(story)
 p(f'{i:02d}. {r["lugar"]} / {r["region"]}','Heading3')
 p('**Base:** '+r['material'])
 p('**Próxima investigación:** '+r['falta'])
 p('Documentos: '+(', '.join(data['fuentes'][s] for s in r['fuentes']) or 'Conversación; dossier específico pendiente.'),'SmallD')
 block=story[start:];del story[start:];story.append(KeepTogether(block))
p('Registro de fuentes y límites','Heading2')
p('Los capítulos 2 y 4 a 8 se consolidaron a partir de documentos del proyecto. Sus fuentes externas y atribuciones se conservan en el texto. El capítulo 1 reconsulta las páginas S01 a S04; S05 fue verificada en la investigación previa de la torre. Los tres testimonios del capítulo 3 se leyeron nuevamente del datapack local.')
p('Los enlaces al visor requieren el servicio local. Los archivos mencionados son rutas del proyecto, no recursos publicados. Las tablas y mapas finales conservan la instantánea de cobertura anterior a los nuevos hallazgos del capítulo 1.')
p('Anexo cartográfico','Heading2')
p('Las seis páginas siguientes conservan el atlas ya revisado, con numeración interna 1 a 6: cuatro mapas A3 (historia, personajes, facciones y trama propia) y dos grillas A4. Los anclajes ilustrativos no permiten medir distancias ni demostrar pasadizos. El número de ficha vincula mapa, grilla y agenda.')

doc=Doc(qa/'dossier-texto.pdf');doc.multiBuild(story)
textreader=PdfReader(qa/'dossier-texto.pdf');basecount=len(textreader.pages)
writer=PdfWriter();writer.append(textreader)
atlas=project/'output/pdf/L2-mapa-cobertura-narrativa.pdf'
writer.append(atlas,import_outline=False)
parent=writer.add_outline_item('10 / Atlas de cobertura y grilla',basecount)
for i,name in enumerate(['Mapa: historia','Mapa: personajes','Mapa: facciones','Mapa: trama propia','Grilla: fichas 1-16','Grilla: fichas 17-32']):writer.add_outline_item(name,basecount+i,parent=parent)
writer.add_metadata({'/Title':'L2 - Atlas y dossier de investigación narrativa','/Author':'Proyecto L2 - Kevin','/Subject':'Lore, personajes, pueblos, propuestas y pendientes; base Interlude'})
dest=out/'L2-atlas-dossier-narrativo-ampliado.pdf'
with dest.open('wb') as f:writer.write(f)
pdf=pymupdf.open(dest)
for i,page in enumerate(pdf):
 assert '\ufffd' not in page.get_text()
 # All pages get a preview, not only a selection.
 page.get_pixmap(matrix=pymupdf.Matrix(.7,.7)).save(qa/f'page-{i+1:03d}.png')
headings=doc.headings+[('10 / Atlas de cobertura y grilla',basecount+1)]
(qa/'qa.json').write_text(json.dumps({'pages':len(pdf),'text_pages':basecount,'chapters':headings,'pdf':str(dest)},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pdf),'text_pages':basecount,'pdf':str(dest),'chapters':headings},ensure_ascii=False))
