"""Deterministic vector drawing set; same dimensions and stations as build_resort.py."""
from pathlib import Path
import math,json,html
P=Path(__file__).resolve().parent
C={'bg':'#091a2b','line':'#8ed9ea','soft':'#36556b','text':'#d8eff8','accent':'#e9b974','water':'#125c79'}
def text(x,y,s,size=18,color=None):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color or C["text"]}">{html.escape(str(s))}</text>'
def line(x1,y1,x2,y2,color=None,dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["line"]}" stroke-width="1.4" stroke-dasharray="{dash}"/>'
def rect(x,y,w,h,fill='none',stroke=None):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or C["line"]}"/>'
def ellipse(x,y,rx,ry,fill='none'):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{C["line"]}" stroke-width="1.5"/>'
def poly(pts,fill='none',stroke=None):return f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{fill}" stroke="{stroke or C["line"]}" stroke-width="1.5"/>'
def dim(x1,y1,x2,y2,label):
    dx=x2-x1;dy=y2-y1;L=max(math.hypot(dx,dy),1);nx=-dy/L*6;ny=dx/L*6
    return line(x1,y1,x2,y2,C['accent'])+line(x1-nx,y1-ny,x1+nx,y1+ny,C['accent'])+line(x2-nx,y2-ny,x2+nx,y2+ny,C['accent'])+text((x1+x2)/2+8,(y1+y2)/2-9,label,16,C['accent'])
def base(code,title,subtitle):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000"><rect width="1600" height="1000" fill="{C["bg"]}"/><g font-family="Segoe UI,Arial,sans-serif">'
    for x in range(30,1580,40):s+=line(x,110,x,890,C['soft'])
    for y in range(110,900,40):s+=line(30,y,1570,y,C['soft'])
    s+=rect(30,25,1540,945)+text(55,65,'AURELIA / '+title,28)+text(55,94,subtitle,16)
    s+=rect(30,900,1540,70,C['bg'])+text(50,926,code+'  |  MODELO 3D · REV 01 · 14 OCT 2026',17)+text(50,952,'Metros · cotas de diseño propuestas · referencia parcial · sin integración en L2',15)
    s+=text(1120,928,'+X POPA  /  +Y BABOR  /  +Z ARRIBA',14)+text(1120,951,'SVG vectorial · imprimir A3 horizontal',14)
    return s
def save(code,s):
    (P/(code+'.svg')).write_text(s+'</g></svg>',encoding='utf8')
def xy(x,y,ox=660,oy=470,k=7.5):return ox+x*k,oy-y*k
def rr(x,y,w,d,fill='none',ox=660,oy=470,k=7.5):
    a,b=xy(x-w/2,y+d/2,ox,oy,k);return rect(a,b,w*k,d*k,fill)
def label(x,y,t,k=7.5,ox=660,oy=470,size=14):
    a,b=xy(x,y,ox,oy,k);return text(a,b,t,size)
def scalebar(x,y,k):
    s=''
    for i in range(4):s+=rect(x+i*5*k,y,5*k,8,C['line'] if i%2==0 else C['bg'])
    return s+text(x,y+28,'0',14)+text(x+10*k,y+28,'10',14)+text(x+20*k,y+28,'20 m',14)

s=base('A01','PLANTA GENERAL','Proyección ortográfica geométrica · proa a la izquierda · X=0 en centro del casco')
for rx,ry in [(60,26),(56,24),(51,19)]:s+=ellipse(660,470,rx*7.5,ry*7.5)
s+=line(130,470,1220,470,C['accent'],'8 7')
for side in [-1,1]:
    pts=[xy(x,side*y) for x,y in [(34,18),(48,38),(67,38),(58,17)]];s+=poly(pts)
s+=rr(0,0,38,12,C['water'])
s+=label(-16,3,'PISCINA 38 × 12 m',size=18)
for side in [-1,1]:
    for x in [-24,-12,0,12,24]:
        s+=rr(x,side*12.5,6,4)
        for dx in [-1.4,1.4]:s+=rr(x+dx,side*12.5,1.1,2.5,C['soft'])
    for x in [-34,-29,29,34]:s+=rr(x,side*8,1.1,2.5,C['soft'])
    s+=rr(-37.7,side*6,11.4,3.2,C['water'])
    for step in range(38):
        a,b=xy(-43.4+step*.3,side*6+1.6);c,d=xy(-43.4+step*.3,side*6-1.6);s+=line(a,b,c,d,C['soft'])
for x in [-39,39]:
    for y in [-7,7]:a,b=xy(x,y);s+=ellipse(a,b,8,8,C['soft'])
s+=rr(40,0,12,14,C['water'])+label(35,1,'SALÓN',size=14)
s+=rect(*xy(-54,.5),108*7.5,7.5,C['soft'])
for x in [-48,-36,-24,-12,0,12,24,36,48,60]:
    a,b=xy(x,26);s+=line(a,b-15,a,b+405,C['soft'],'5 6')+text(a-12,b-22,str(x),13)
s+=dim(210,160,1110,160,'CASCO 120 m')+dim(210,815,1177.5,815,'ENVOLVENTE 129 m')
s+=dim(1240,185,1240,755,'76 m')
s+=text(1300,220,'CUBIERTA',19)+text(1300,250,'Z = 18 m',17)+text(1300,287,'Borda: Z 23',17)
for i,t in enumerate(['10 cabañas 6 × 4','20 camas bajo lona','8 tumbonas abiertas','2 accesos a escaleras','Arco: Z máx. 34','Salón: 12 × 14','Vaso: fondo Z 16,5','Agua: Z 17,65']):s+=text(1290,345+i*35,t,15)
s+=scalebar(190,850,7.5);save('A01-planta-general',s)

s=base('A02','PERFILES Y ESTACIONES','Vistas alineadas: lateral y frontal · silueta exterior nominal sin espesor de revestimiento')
K=8;OX=570;OY=530
def side(x,z):return OX+x*K,OY-z*K
upper=[(-60,16),(-59,20),(-56,23),(56,23),(59,20),(60,16)]
lower=[(60,16),(55,10),(43,5),(25,1.5),(1,0),(-1,0),(-25,1.5),(-43,5),(-55,10),(-60,16)]
s+=poly([side(x,z) for x,z in upper+lower])
for z in [5.5,10.5,14.2,18,23]:
    a,b=side(-54,z);c,d=side(54,z);s+=line(a,b,c,d,C['soft'],'5 5')+text(1065,b+5,'Z '+str(z),14)
s+=poly([side(x,z) for x,z in [(44,22),(64,40),(69,40),(61,21)]])
pts=[side(-54+108*i/80,23+11*math.sin(math.pi*i/80)) for i in range(81)]
s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{C["line"]}" stroke-width="7"/>'
s+=rect(*side(-58,16.7),116*K,3.4*K,C['water'])
s+=rect(*side(-19,18),38*K,1.5*K,C['water'])
s+=rect(*side(34,22.3),12*K,4.3*K,C['water'])
for x in [-24,-12,0,12,24]:s+=rect(*side(x-3,21.4),6*K,3.4*K)
s+=rect(*side(29,10.1),6*K,5.4*K)
s+=dim(90,585,1050,585,'120 m casco')+dim(1140,210,1140,530,'40 m')
s+=text(90,625,'PERFIL / +X hacia popa',19)
# Front outline from the same hull stations.
ox,oy,k=1360,700,3
rs=[(1,.5,0),(25,11,1.5),(43,19,5),(55,24,10),(60,26,16),(59,25.5,20),(56,24,23)]
front=[(ox-ry*k,oy-z*k) for rx,ry,z in rs]+[(ox+ry*k,oy-z*k) for rx,ry,z in reversed(rs)]
s+=poly(front)+line(ox-38*k,oy-13.5*k,ox+38*k,oy-13.5*k)
s+=dim(ox-38*k,oy+35,ox+38*k,oy+35,'76 m')+text(1240,785,'FRENTE / mirando +X',16)
s+=text(85,710,'ESTACIONES DE CASCO / semiejes de cada anillo (m)',19)
for i,t in enumerate(['Z 0,0 : X 1 / Y 0,5','Z 1,5 : X 25 / Y 11','Z 5,0 : X 43 / Y 19','Z 10 : X 55 / Y 24','Z 16 : X 60 / Y 26','Z 20 : X 59 / Y 25,5','Z 23 : X 56 / Y 24','Hueco Z 23: X 51 / Y 19']):s+=text(85+(i%4)*275,750+(i//4)*42,t,15)
s+=text(85,862,'48 paños laterales · Z 13,3–16,7 · visera de proa Z 18–22,9 · 3 turbinas visuales',17)
save('A02-perfiles',s)

audit=json.loads((P/'design-audit.json').read_text(encoding='utf8'))
s=base('A03','INTERIORES PROPUESTOS','Cubiertas de alojamiento a Z 10,5 y Z 5,5 · geometría modular editable · partes no visibles en la referencia')
for level,z,rx,ry,oy in [('A',10.5,54,23,310),('B',5.5,42,18,680)]:
    ox,k=600,7
    s+=ellipse(ox,oy,rx*k,ry*k)+rr(0,0,rx*1.65,9,C['soft'],ox,oy,k)
    for i,r in enumerate([r for r in audit['rooms_data'] if r['level']==level],1):
        s+=rr(r['x'],r['y'],10,10,'none',ox,oy,k)
        s+=rr(r['x']+1,r['y'],2,3,C['water'],ox,oy,k)
        s+=label(r['x']-4,r['y']+.5,level+str(i).zfill(2),k,ox,oy,13)
        # Door opening symbol on central corridor.
        a,b=xy(r['x'],math.copysign(5,r['y']),ox,oy,k);s+=line(a-4,b,a+4,b,C['accent'])
    s+=text(150,oy-ry*k-22,f'CUBIERTA {level} / Z {z} m',20)
    s+=rr(31.75,0,7.5,3.2,C['water'],ox,oy,k)+label(28.5,0,'ESC.',k,ox,oy,12)
    s+=dim(ox-rx*k,oy+ry*k+30,ox+rx*k,oy+ry*k+30,f'{rx*2} × {ry*2} m')
for i,t in enumerate(['DISTRIBUCIÓN DE ESTUDIO','Pasillo central: 9 m','Módulo: 10 × 10 m','Altura de tabiques: 3,3 m','Puertas: 1,2 × 2,7 m','Cama: 2 × 3 m','Armario: 1,2 × 2 m','Puente: X -51 a -35','Puente: Z 14,2 m',f"Total: {audit['rooms']} camarotes",'Conexiones entre niveles:','ver cortes y memoria.','Escaleras como geometría;','sin prueba de navegación.']):s+=text(1120,190+i*43,t,17 if i else 20)
save('A03-interiores',s)

s=base('A04','CORTES Y DETALLES','Secciones nominales · geometría para arte 3D · alturas y módulos de la maqueta')
ox,oy,k=480,520,11
rs=[(.5,0),(11,1.5),(19,5),(24,10),(26,16),(25.5,20),(24,23),(19,23),(19,18)]
s+=poly([(ox-y*k,oy-z*k) for y,z in rs]+[(ox+y*k,oy-z*k) for y,z in reversed(rs)])
for z,w in [(5.5,18),(10.5,23)]:s+=line(ox-w*k,oy-z*k,ox+w*k,oy-z*k)+text(ox+w*k+15,oy-z*k+4,'Z '+str(z),16)
s+=line(ox-19*k,oy-18*k,ox-6*k,oy-18*k)+line(ox+6*k,oy-18*k,ox+19*k,oy-18*k)
s+=rect(ox-6*k,oy-18*k,12*k,1.5*k,C['water'])
s+=dim(ox-26*k,570,ox+26*k,570,'52 m')+dim(ox-6*k,oy-18*k-25,ox+6*k,oy-18*k-25,'12 m piscina')
s+=text(190,620,'SECCIÓN TRANSVERSAL / X = 0',21)
s+=text(190,655,'Vaso de piscina: Z 16,5–18 · agua Z 17,65',17)
# Cabana module elevation with dimensions.
xx,yy,kk=1040,490,48
s+=rect(xx,yy-3.2*kk,6*kk,3.2*kk)+rect(xx,yy-3.3*kk,6*kk,.1*kk,C['accent'])
s+=rect(xx+5,yy-3.2*kk,.15*kk,3.2*kk,C['line'])+rect(xx+6*kk-12,yy-3.2*kk,.15*kk,3.2*kk,C['line'])
s+=rect(xx+22,yy-.6*kk,1.1*kk,.6*kk,C['soft'])+rect(xx+190,yy-.6*kk,1.1*kk,.6*kk,C['soft'])
s+=dim(xx,yy+38,xx+6*kk,yy+38,'6 m')+dim(xx+6*kk+35,yy-3.2*kk,xx+6*kk+35,yy,'3,2 m')
s+=text(1020,590,'MÓDULO CABAÑA / fondo 4 m',20)
for i,t in enumerate(['Propulsión: 2 conductos Ø 5,4 × 6 m + popa Ø 7,4 × 8 m','Arco: x = -54…54; z = 23 + 11 sen(πt); tubos Ø 0,96 m','Aletas horizontales: Z 13,5 m; espesor 0,65 m; puntas Y ±38','Aleta dorsal: vértices (X,Z) = (44,22), (64,40), (69,40), (61,21)','Casco: 160 segmentos por anillo; revestimiento visual 0,35 m','Materiales: perla / cristal azul opaco / tarima / agua / lino / titanio']):s+=text(150,710+i*27,t,17)
save('A04-cortes-detalles',s)

pages=[]
for f in sorted(P.glob('A0*.svg')):
    pages.append('<section class="sheet">'+f.read_text(encoding='utf8')+'</section>')
photos=''.join(f'<figure><img src="{n}.png"><figcaption>{t}</figcaption></figure>' for n,t in [('perspectiva','Perspectiva general'),('terraza','Terraza y piscina'),('superior','Ortográfica superior'),('lateral','Ortográfica lateral'),('frontal','Ortográfica frontal'),('popa','Ortográfica de popa'),('corte-3d','Sección 3D por el plano central')])
doc='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Aurelia — planos de modelado 3D</title><style>
*{box-sizing:border-box}body{margin:0;background:#071422;color:#d8eff8;font:17px/1.55 system-ui}main{max-width:1500px;margin:auto;padding:35px}h1{font-size:44px;margin:0}p{max-width:1000px}a{color:#8ed9ea}.tag{color:#e9b974}nav{display:flex;gap:20px;flex-wrap:wrap;margin:25px 0}.sheet{margin:30px 0}.sheet svg{width:100%;height:auto;border:1px solid #36556b}.renders{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0;background:#102437}figure:first-child{grid-column:1/-1}img{display:block;width:100%;height:auto}figcaption{padding:12px}table{border-collapse:collapse}td,th{padding:10px 22px;border:1px solid #36556b;text-align:left}@media print{@page{size:A3 landscape;margin:7mm}body{background:white}main{padding:0}.intro,.renders,.notes{display:none}.sheet{margin:0;break-after:page;page-break-after:always}.sheet:last-child{break-after:auto}.sheet svg{width:100%;max-height:275mm;border:0;print-color-adjust:exact}}
</style><main><div class="intro"><span class="tag">DISEÑO PARA MODELADO 3D / REVISIÓN 01</span><h1>Aurelia</h1><p>Aeronave resort inspirada en la imagen aportada. Casco oval, piscina abierta, arco central y propulsores carenados. Las partes no visibles y las medidas son propuestas de diseño. Paquete editable para revisar antes de la adaptación a L2.</p><nav><a href="Aurelia-v1.blend">Blender editable</a><a href="Aurelia-v1.glb">Modelo GLB</a><a href="README.md">Memoria y pendientes</a><a href="#planos">Planos vectoriales</a></nav><p>Para imprimir: Ctrl+P → A3 horizontal → activar gráficos de fondo. Se imprimen las cuatro láminas. Las vistas renderizadas usan la misma malla que el modelo editable.</p></div><div class="renders">'''+photos+'</div><div id="planos">'+''.join(pages)+'''</div><div class="notes"><p>Revisión visual pendiente del usuario. El detalle exterior y los módulos están modelados; baños, cocinas, cableado, UV finales, colisiones y materiales de juego no están resueltos. Los planos no son de fabricación.</p></div></main></html>'''
(P/'PLANOS-AURELIA.html').write_text(doc,encoding='utf8')
print('4 SVG sheets and HTML dossier created.')
