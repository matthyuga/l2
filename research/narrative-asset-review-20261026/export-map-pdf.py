from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz

root=Path(__file__).resolve().parent
out=Path(r'E:\l2-local\output\pdf');out.mkdir(parents=True,exist_ok=True)
qa=Path(r'E:\l2-local\tmp\pdfs\narrative-coverage');qa.mkdir(parents=True,exist_ok=True)
data=json.loads((root/'cobertura-narrativa.json').read_text(encoding='utf-8'))
geo=json.loads((root/'mapa-procedencia.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Arial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='ArialBold')
palette={'D':'#A7DDBB','P':'#F1C18B','I':'#A9C9EE','-':'#E0E3E8'}
ink=colors.HexColor('#202C3C')
path=out/'L2-mapa-cobertura-narrativa.pdf'
c=canvas.Canvas(str(path),pagesize=A3)
c.setTitle('Lineage II - Mapa de cobertura narrativa')
c.setAuthor('Proyecto L2 - Kevin')

def txt(x,y,text,size=10,bold=False):
 c.setFillColor(ink);c.setFont('ArialBold' if bold else 'Arial',size);c.drawString(x,y,text)

def footer(w,page):
 txt(36,24,'26/10/2026 | Cobertura documental, sin cambios en el juego.',8)
 c.setFont('Arial',8);c.drawRightString(w-36,24,str(page))

def legend(x,y):
 for code,label in [('D','Recopilado'),('P','Parcial'),('I','Idea propuesta'),('-','Pendiente')]:
  c.setFillColor(colors.HexColor(palette[code]));c.roundRect(x,y-4,18,16,3,fill=1,stroke=0)
  txt(x+5,y,code,9,True);txt(x+24,y,label,10);x+=130

for col,title in enumerate(data['columnas']):
 w,h=A3;c.setPageSize(A3)
 txt(36,h-39,'LINEAGE II / COBERTURA NARRATIVA',11,True)
 txt(36,h-69,title,25,True)
 txt(36,h-91,'Los números corresponden a las 32 fichas de la grilla (páginas 5 y 6).',10)
 legend(36,h-116)
 # Preserve the original aspect ratio, with room for notes and legend.
 iw,ih=1812,2620
 mh=h-220;mw=mh*iw/ih;left=(w-mw)/2;bottom=75
 c.drawImage(geo['local_source'],left,bottom,width=mw,height=mh)
 for p in geo['points']:
  row=data['lugares'][p['fila']-1];state=row['estados'][col]
  x=left+mw*p['x'];y=bottom+mh*(1-p['y'])
  c.setFillColor(colors.HexColor(palette[state]));c.setStrokeColor(ink);c.setLineWidth(.45)
  c.circle(x,y,9,fill=1,stroke=1)
  c.setFillColor(ink);c.setFont('ArialBold',8);c.drawCentredString(x,y-2.7,str(p['fila']))
 txt(36,61,'Anclajes aproximados sobre la ilustración; no indican distancias ni áreas exactas.',8)
 txt(36,49,'Sin punto propio: Hardin (9), Pagan Temple bajo Rune (19), tribus de lagartos (32).',8)
 footer(w,col+1);c.showPage()

style=ParagraphStyle('cell',fontName='Arial',fontSize=8,leading=10,textColor=ink)
headstyle=ParagraphStyle('head',parent=style,fontName='ArialBold')
def para(s,bold=False): return Paragraph(escape(s.replace('—','-')),headstyle if bold else style)
for part in range(2):
 w,h=landscape(A4);c.setPageSize((w,h))
 txt(32,h-36,'Grilla de cobertura - '+('fichas 1 a 16' if part==0 else 'fichas 17 a 32'),19,True)
 txt(32,h-55,'D: recopilado | P: parcial | I: idea propuesta | -: pendiente',9)
 txt(32,h-69,'Recopilado no significa exhaustivo. Las ideas propias siguen sin ser canon definitivo.',8)
 table=[[para(s,True) for s in ['Nº','Lugar / región','Historia','Personajes','Facciones','Trama','Próximo pendiente']]]
 for i,row in enumerate(data['lugares'][part*16:(part+1)*16],part*16+1):
  table.append([str(i),para(row['lugar']+' / '+row['region']),*row['estados'],para(row['falta'])])
 widths=[25,171,48,58,53,42,w-64-25-171-48-58-53-42]
 t=Table(table,colWidths=widths,repeatRows=1)
 commands=[('FONTNAME',(0,0),(-1,-1),'Arial'),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(2,1),(5,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E9EEF4')),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#9DAABD'))]
 for ri,row in enumerate(data['lugares'][part*16:(part+1)*16],1):
  for ci,state in enumerate(row['estados'],2):commands.append(('BACKGROUND',(ci,ri),(ci,ri),colors.HexColor(palette[state])))
  commands.append(('LINEBELOW',(0,ri),(-1,ri),.25,colors.HexColor('#DFE4EB')))
 t.setStyle(TableStyle(commands));tw,th=t.wrap(w-64,h-130)
 assert th < h-125,th
 t.drawOn(c,32,h-88-th)
 txt(32,49,'Fuentes: investigación de ciudades, revisión de assets, Rune/valle/torre y bitácoras de propuestas.',8)
 txt(32,37,'Mapa base: www.l2satoshi.app/images/AdenWorldMapInterlude.png',8)
 footer(w,part+5);c.showPage()
c.save()
doc=fitz.open(path)
assert len(doc)==6
for i,page in enumerate(doc):
 assert '\ufffd' not in page.get_text()
 page.get_pixmap(matrix=fitz.Matrix(.85,.85)).save(qa/f'page-{i+1}.png')
print(str(path));print('6 páginas renderizadas para revisión: '+str(qa))
