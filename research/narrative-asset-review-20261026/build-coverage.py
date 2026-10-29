import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'ciudades': '../LORE-CIUDADES-INVESTIGACION-20261026.md',
    'assets': 'REVISION.md',
    'rune': 'RUNE-VALLEY-TOWER.md',
    'adaptacion': '../../PROPUESTA-LORE-L2-ULTIMO-BASTION-20261023.md',
    'prologo': '../../BITACORA-IDENTIDAD-ACADEMIA-Y-PROLOGO-20261026.md',
    'festival': '../../BITACORA-IDEAS-FESTIVAL-Y-RESCATE-20261021.md',
    'pagan': '../pagan-access-analysis-20261024.md',
}
# Estados describen el material localizado, no el grado de implementación.
# Historia / personajes / pueblos y facciones / trama propia.
raw = [
('Talking Island','Isla','DDPI','Escuelas de Cedric y Einhovant; Roien, Gallint, Collin; pasado élfico.','Verificar cronología y elegir un conflicto local.',['ciudades','assets','adaptacion']),
('Gludin','Gludio','DDPI','Asentamiento humano, guerra de Gracia y reconstrucción; Alvah y Bezique.','Desarrollar habitantes, responsables y arco del puerto.',['ciudades','adaptacion']),
('Gludio','Gludio','DDPI','Orden real, Waldner y Vasper; comienzo en muelle aéreo propuesto.','Identidad del capitán, fecha de guerra y misiones de inicio.',['ciudades','assets','prologo','adaptacion']),
('Ruinas de Gludio','Gludio','---I','Plaga, contención y rescate propuestos en la adaptación.','Investigar Ruins of Agony y Ruins of Despair por separado.',['adaptacion']),
('Dion','Dion','DDPI','Ashton, tributos, rebelión y consecuencias; versiones contradictorias registradas.','Resolver continuidad elegida y personajes del presente.',['ciudades','assets','adaptacion']),
('Execution Grounds','Dion','PPP-','Represión y muertos vinculados a Dion.','Ficha propia de víctimas, criaturas y misiones.',['ciudades']),
('Floran','Dion','---I','Propuesta de hambre, cosechas y mecanismo de producción.','Investigar su historia y comunidad antes de fijar trama.',['adaptacion']),
('Giran','Giran','DDPI','Esthus, Lionna, Sieghardt; asedio y comercio. Refugio protegido en la propuesta.','Definir protección, refugiados y relaciones con otras regiones.',['ciudades','assets','adaptacion']),
('Hardin’s Academy','Giran','PDPI','Hardin y discípulos con recursos visuales; academia como idea narrativa.','No se decidió ubicar la academia de la historia en este lugar.',['ciudades','assets','prologo']),
('Oren','Oren','DDPI','Frontera, guerra, Vanik e instituciones mágicas.','Separar historia urbana, instituciones y conflicto propio.',['ciudades','assets','adaptacion']),
('Ivory Tower','Oren','PPP-','Mencionada como institución influyente; no tiene dossier específico.','Investigar dirigentes, órdenes e historia interna.',['ciudades']),
('Aden','Aden','DDPI','Raoul, sucesión, Amadeo y arquitectura; recuperación y festival propuestos.','Definir gobierno posterior y relación del festival con recuperación.',['ciudades','assets','adaptacion','festival']),
('Tower of Insolence','Aden','DDDI','Baium, castigo, Hallate, Kernon, Golconda, Platinum y ángeles.','Historia individual de habitantes y posibles encuentros religiosos.',['rune','assets']),
('Goddard','Goddard','DDPI','Antecedente orco, reclamos Ketra y tensiones regionales.','Distinguir memoria de cada bando y concretar arco regional.',['ciudades','assets','adaptacion']),
('Ketra Orc Outpost','Goddard','PDD-','Kadun, Brakki, Wahkan y Asefa; sociedad, alianza y reivindicación.','Investigar historia interna y voces distintas de la tribu.',['ciudades','assets']),
('Varka Silenos Outpost','Goddard','PPD-','Sociedad organizada, diplomacia y roles visuales revisados.','Nombres y biografías de líderes; motivos propios de la guerra.',['assets']),
('Imperial Tomb','Goddard','----','Conversación sobre acceso físico y teletransporte, sin dossier narrativo.','Historia, ocupantes y relación con el imperio; ruta queda pendiente.',[]),
('Rune','Rune','PPP I'.replace(' ',''),'Contexto religioso y zonas vecinas; control religioso propuesto.','Dossier de ciudad, casas nobles, gobierno y conflictos actuales.',['rune','pagan','adaptacion']),
('Pagan Temple','Rune','PPP-','Análisis de acceso y contexto de culto a Triol.','Historia del culto, jerarquía, personajes y autonomía de servidores.',['pagan','rune']),
('Swamp of Screams / Stakato Nest','Rune','PPP-','Colonia, reina y élite; identificación probable de «skalators».','Confirmar criatura vista; investigar reina y organización en detalle.',['rune','assets']),
('Valley of Saints','Rune','P P D I'.replace(' ',''),'Kel Mahum/Splendor, cuentas de obediencia y Barakiel candidato.','Identificar ángeles vistos y estudiar origen de cada guardián.',['rune']),
('Monastery of Silence','Rune','PPP-','Institución de Einhasad, conexión con valle y oposición al templo.','Investigar orden, Solina, dirigentes y criaturas individualmente.',['rune']),
('Schuttgart','Schuttgart','DDPI','Fortificación orca, ferrocarril, Sky Wagon y entorno industrial.','Fichas de técnicos, población y aislamiento propuesto.',['ciudades','adaptacion']),
('Pavel Ruins','Schuttgart','PPP-','Pavel y Dr. Chaos mencionados en investigación regional.','Historia y objetivos propios de máquinas y ocupantes.',['ciudades']),
('Frozen Labyrinth / Ice Queen','Schuttgart','-P--','Recurso externo de Freya revisado; no equivale a estudiar su historia.','Dossier completo y comprobación de cronología aplicable.',['assets']),
('Innadril / Heine','Innadril','---I','Canales, agua y rutas propuestos como conflicto.','Investigar ciudad, castillo, habitantes e historia oficial.',['adaptacion']),
('Alligator Island / Crokian','Innadril','P-P-','Guardia: Crokian armados que consideran sagrados a los caimanes.','Distinguir su pueblo de la fauna; estudiar líderes y creencias.',['assets']),
('Elven Village','Tierras iniciales','----','Sin dossier específico localizado en esta revisión.','Historia, casas, NPC y vínculos con otras regiones.',[]),
('Dark Elven Village','Tierras iniciales','----','Sin dossier específico localizado en esta revisión.','Historia, órdenes, NPC y relaciones religiosas.',[]),
('Orc Village / Immortal Plateau','Tierras iniciales','PPP-','Kakai, tribus originales y ruptura Ragna mencionados.','Estudiar cada tribu y personajes; separar prejuicios de hechos.',['ciudades','assets']),
('Dwarven Village','Tierras iniciales','P---','Antecedentes de transporte y rey enano mencionados indirectamente.','Historia propia, gremios, personajes y conflictos.',['ciudades']),
('Tribus de hombres lagarto','Varias regiones','-PP-','Modelos y nombres Langk, Maille, Delu, Tasaba, Virud; sin biografías completas.','Ubicar y estudiar cada tribu por separado; no unificar culturas.',['assets']),
]
labels = {'D':'Recopilado','P':'Parcial','I':'Idea propuesta','-':'Pendiente'}
rows = [dict(lugar=a,region=b,estados=list(c),material=d,falta=e,fuentes=f) for a,b,c,d,e,f in raw]
assert all(len(r['estados']) == 4 and set(r['estados']) <= set(labels) for r in rows)
assert all((ROOT / v).exists() for v in SOURCES.values())
(ROOT/'cobertura-narrativa.json').write_text(json.dumps({'fecha':'2026-10-26','columnas':['Historia','Personajes','Facciones','Trama propia'],'leyenda':labels,'fuentes':SOURCES,'lugares':rows},ensure_ascii=False,indent=2),encoding='utf-8')

intro = '''# Cobertura narrativa del mundo L2

Actualizado: 26/10/2026. Base Interlude. Inventario de documentos localizados en esta revisión; no es un inventario exhaustivo de todas las zonas del juego.

**D / verde: recopilado** — hay investigación dedicada o material concreto del tema; no significa investigación exhaustiva ni canon definitivo.
**P / ámbar: parcial** — referencias, identificación o contexto limitado; falta un dossier propio.
**I / azul: idea propuesta** — diseño conversado, sin trama cerrada ni implementación.
**— / gris: pendiente** — no se localizó una recopilación específica en los documentos revisados. No significa que el juego carezca de historia.

Cada lugar se evalúa por historia, personajes, pueblos/facciones y trama propia del servidor. Revisar un modelo no acredita su biografía; tener lore no significa tener misiones escritas. Las propuestas de El Último Bastión siguen siendo alternativas; no se adoptan como canon por aparecer aquí.

La grilla es de cobertura documental, no geográfica: no representa distancias, coordenadas ni rutas. Imperial Tomb se registra por la conversación sobre acceso, con historia pendiente. Las tierras iniciales se incluyen para hacer visibles huecos. No se modificó el juego.

## Grilla

| Lugar | Región | Historia | Personajes | Facciones | Trama propia | Próximo pendiente |
|---|---|---|---|---|---|---|
'''
md = intro
for r in rows:
    md += '| '+' | '.join([r['lugar'],r['region'],*[labels[s] for s in r['estados']],r['falta']])+' |\n'
md += '\n## Fichas y fuentes\n'
for r in rows:
    md += '\n### '+r['lugar']+'\n\n'+r['material']+'\n\n'
    md += 'Fuentes: '+(', '.join('['+s+']('+SOURCES[s]+')' for s in r['fuentes']) or 'Conversación de esta sesión; investigación narrativa pendiente.')+'\n'
md += '\n## Temas transversales conservados\n\nIdentidad y pasado, prólogo opcional, vínculos personales sin líneas históricas paralelas, academia e incidentes, competencias de exploración, modularidad de creación y puntos de stats. Ver las bitácoras de identidad/prólogo y creación/roles; sin asignar estos sistemas automáticamente a cada región.\n'
(ROOT/'COBERTURA-NARRATIVA.md').write_text(md,encoding='utf-8')

header = '''<div id="l2-coverage">
<h2>Cobertura narrativa · Lineage II</h2>
<div class="text-small text-muted">26 oct 2026 · 32 lugares y grupos · documentación recopilada</div>
<div class="card" id="l2-detail" aria-live="polite"></div>
<div class="table-responsive"><table class="table table-sm"><thead><tr><th>Lugar</th><th>Historia</th><th>Personajes</th><th>Facciones</th><th>Trama propia</th></tr></thead><tbody>'''
body=''
for i,r in enumerate(rows):
    body+='<tr><th scope="row"><button class="btn btn-ghost" type="button" data-place="'+str(i)+'">'+escape(r['lugar'])+'</button></th>'
    for s in r['estados']:
        body+='<td><span class="mark state-'+('none' if s=='-' else s)+'">'+('—' if s=='-' else s)+'</span></td>'
    body+='</tr>\n'
tail='''</tbody></table></div>
<div class="viz-row text-small"><span><span class="mark state-D">D</span> Recopilado</span><span><span class="mark state-P">P</span> Parcial</span><span><span class="mark state-I">I</span> Idea propuesta</span><span><span class="mark state-none">—</span> Pendiente</span></div>
</div>
<style>
#l2-coverage .mark { display:inline-block; text-align:center; min-width:1.8em; color:var(--foreground); padding:0.1em 0.25em; }
#l2-coverage .state-D { background:color-mix(in srgb,var(--green) 24%,transparent); }
#l2-coverage .state-P { background:color-mix(in srgb,var(--orange) 24%,transparent); }
#l2-coverage .state-I { background:color-mix(in srgb,var(--blue) 24%,transparent); }
#l2-coverage .state-none { background:var(--muted); }
#l2-coverage th { font-weight:500; }
#l2-coverage #l2-detail { margin:1em 0; }
</style>
<script>
(() => {
const root=document.getElementById('l2-coverage');
const rows=__ROWS__;
const detail=root.querySelector('#l2-detail');
function show(index,save=false){
 if(!Number.isInteger(index)||!rows[index])index=0;
 const r=rows[index];
 detail.textContent=r.lugar+' · '+r.region+' — '+r.material+' Pendiente: '+r.falta;
 root.querySelectorAll('[data-place]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.place)===index)));
 if(save&&window.openai?.setWidgetState)window.openai.setWidgetState({modelContent:{lugar:r.lugar},privateContent:{index}}).catch(()=>{});
}
root.querySelectorAll('[data-place]').forEach(b=>b.addEventListener('click',()=>show(Number(b.dataset.place),true)));
show(window.openai?.widgetState?.privateContent?.index??0);
window.addEventListener('openai:set_globals',e=>{const s=e.detail?.globals?.widgetState;if(s)show(s.privateContent?.index??0);});
})();
</script>
'''.replace('__ROWS__',json.dumps(rows,ensure_ascii=False))
(ROOT/'cobertura-narrativa.html').write_text(header+body+tail,encoding='utf-8')
print('Generados: JSON, bitácora Markdown y grilla visual; '+str(len(rows))+' filas.')
