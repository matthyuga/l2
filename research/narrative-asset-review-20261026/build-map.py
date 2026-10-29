from pathlib import Path
import json, base64, hashlib
from PIL import Image

root=Path(__file__).resolve().parent
data=json.loads((root/'cobertura-narrativa.json').read_text(encoding='utf-8'))
source=Path(r'E:\l2-local\tmp\pdfs\l2-atlas\AdenWorldMapInterlude.png')
# Coordinates are manual anchors on the inspected illustrated map, expressed as
# fractions of its width/height. They are not game coordinates or boundaries.
points=[
 (0,.128,.960),(1,.141,.790),(2,.318,.735),
 (3,.229,.716),(3,.312,.775),
 (4,.410,.778),(5,.500,.770),(6,.403,.815),
 (7,.586,.781),(9,.589,.595),(10,.590,.519),
 (11,.770,.540),(12,.680,.527),(13,.785,.389),
 (14,.773,.350),(15,.682,.402),(16,.879,.341),
 (17,.462,.399),(19,.612,.412),(19,.577,.395),
 (20,.583,.338),(21,.676,.342),(22,.605,.224),
 (23,.615,.256),(24,.714,.274),(25,.671,.919),
 (26,.685,.829),(27,.487,.595),(28,.379,.524),
 (29,.235,.275),(30,.681,.151),
]
im=Image.open(source).convert('RGB')
im.thumbnail((1100,1600))
im.save(root/'mapa-interlude-base.webp',quality=78,method=6)
base64img=base64.b64encode((root/'mapa-interlude-base.webp').read_bytes()).decode()
provenance={'source_url':'https://www.l2satoshi.app/images/AdenWorldMapInterlude.png','local_source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'anchors':'manuales sobre mapa ilustrado; no coordenadas del juego','points':[{'fila':i+1,'x':x,'y':y} for i,x,y in points],'sin_marcador':['Hardin’s Academy: ubicación no verificada en esta lámina','Pagan Temple: interior de Rune, ficha 19 de la grilla','Tribus de hombres lagarto: repartidas en varias regiones']}
(root/'mapa-procedencia.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
html='''<div id="l2-narrative-map">
<h2>Mapa de cobertura narrativa · Interlude</h2>
<div class="viz-controls"><label class="form-label">Capa de recopilación<select class="form-select" id="l2-layer"><option value="0">Historia</option><option value="1">Personajes</option><option value="2">Facciones</option><option value="3">Trama propia del servidor</option></select></label></div>
<div class="viz-row text-small"><span><span class="legend d">D</span> Recopilado</span><span><span class="legend p">P</span> Parcial</span><span><span class="legend i">I</span> Idea propuesta</span><span><span class="legend n">—</span> Pendiente</span></div>
<div class="card" id="l2-map-detail" aria-live="polite"></div>
<div class="map-field" role="group" aria-label="Mapa ilustrado con marcadores numerados de cobertura documental">
<img alt="Mapa de Aden y Elmore en Interlude; ciudades y zonas rotuladas" src="data:image/webp;base64,__IMAGE__" />
__MARKERS__
</div>
<div class="text-small text-muted">Marcadores aproximados sobre lugares rotulados; números de fila de la grilla. Hardin: ubicación pendiente en esta lámina. Pagan Temple: interior de Rune (18). Hombres lagarto: varias regiones.</div>
<div class="text-small"><a href="https://www.l2satoshi.app/images/AdenWorldMapInterlude.png" target="_blank" rel="noreferrer">Mapa base de Interlude · L2Satoshi</a></div>
</div>
<style>
#l2-narrative-map .map-field{position:relative;margin:1em 0;}
#l2-narrative-map .map-field img{display:block;width:100%;height:auto;}
#l2-narrative-map .pin{position:absolute;transform:translate(-50%,-50%);display:flex;align-items:center;justify-content:center;min-width:1.8em;min-height:1.8em;border-radius:50%;text-decoration:none;color:var(--foreground);box-shadow:0 0 0 1px var(--border);}
#l2-narrative-map .legend{display:inline-block;text-align:center;min-width:1.6em;color:var(--foreground);}
#l2-narrative-map .d{background:color-mix(in srgb,var(--green) 44%,var(--background));}
#l2-narrative-map .p{background:color-mix(in srgb,var(--orange) 44%,var(--background));}
#l2-narrative-map .i{background:color-mix(in srgb,var(--blue) 44%,var(--background));}
#l2-narrative-map .n{background:color-mix(in srgb,var(--foreground) 15%,var(--background));}
#l2-narrative-map #l2-map-detail{margin-top:1em;}
@media(pointer:coarse){#l2-narrative-map .pin::after{content:'';position:absolute;min-width:44px;min-height:44px;}}
</style>
<script>
(()=>{
const root=document.getElementById('l2-narrative-map');
const rows=__ROWS__;
const labels=__LABELS__;
const classes={D:'d',P:'p',I:'i','-':'n'};
const layer=root.querySelector('#l2-layer');
const detail=root.querySelector('#l2-map-detail');
let selected=17;
function render(save=false){
const col=Number(layer.value);
root.querySelectorAll('.pin').forEach(pin=>{
 const r=rows[Number(pin.dataset.row)],s=r.estados[col];
 pin.className='pin cursor-interaction '+classes[s];
 pin.setAttribute('aria-label',(Number(pin.dataset.row)+1)+'. '+r.lugar+': '+labels[s]);
});
const r=rows[selected];
detail.textContent=(selected+1)+'. '+r.lugar+' · '+dataColumns[col]+': '+labels[r.estados[col]]+' — '+r.material+' Falta: '+r.falta;
if(save&&window.openai?.setWidgetState)window.openai.setWidgetState({modelContent:{lugar:r.lugar,capa:dataColumns[col]},privateContent:{selected,col}}).catch(()=>{});
}
const dataColumns=['Historia','Personajes','Facciones','Trama propia'];
root.querySelectorAll('.pin').forEach(pin=>pin.addEventListener('click',e=>{e.preventDefault();selected=Number(pin.dataset.row);render(true);}));
layer.addEventListener('change',()=>render(true));
function restore(s){if(Number.isInteger(s?.selected)&&rows[s.selected])selected=s.selected;if(Number.isInteger(s?.col)&&s.col>=0&&s.col<4)layer.value=String(s.col);render();}
restore(window.openai?.widgetState?.privateContent);
window.addEventListener('openai:set_globals',e=>restore(e.detail?.globals?.widgetState?.privateContent));
})();
</script>
'''
markers='\n'.join(f'<a href="#l2-map-detail" class="pin cursor-interaction" data-row="{i}" style="left:{x*100:.2f}%;top:{y*100:.2f}%">{i+1}</a>' for i,x,y in points)
html=html.replace('__IMAGE__',base64img).replace('__MARKERS__',markers).replace('__ROWS__',json.dumps(data['lugares'],ensure_ascii=False)).replace('__LABELS__',json.dumps(data['leyenda'],ensure_ascii=False))
assert len(html.encode())<1000000
(root/'mapa-cobertura-narrativa.html').write_text(html,encoding='utf-8')
print(f'Mapa: {len(points)} marcadores, {len(set(i for i,_,_ in points))} fichas localizadas, {len(html.encode())} bytes.')
