import {createViewer} from './viewer.js';
const $=id=>document.getElementById(id);let actual,candidate,native,choices,variants;
function light(){for(const view of [actual,candidate,native])view?.setLighting($('light').value);}
async function updateCandidate(){candidate?.dispose();candidate=null;try{candidate=await createViewer($('candidate'),variants.variants[$('variant').value]);light();}catch(e){$('status').textContent='No se pudo abrir la prueba de material.';console.error(e);}}
async function updateNative(){native?.dispose();native=null;const model=choices.find(m=>m.key===$('reference').value);$('referenceName').textContent=model.title+' · '+model.mesh;try{native=await createViewer($('native'),model.gltf);light();}catch(e){$('status').textContent='No se pudo abrir el modelo de referencia.';console.error(e);}}
try{const [gallery,data]=await Promise.all([fetch('/api/catalog').then(r=>r.json()),fetch('amber-comparison/variants.json').then(r=>r.json())]);variants=data;
 choices=gallery.models.filter(m=>m.status==='ready'&&m.npc_count>0&&m.category==='NPC').sort((a,b)=>a.title.localeCompare(b.title,'es'));
 for(const m of choices){const o=document.createElement('option');o.value=m.key;o.textContent=m.title+' · '+m.mesh.split('.')[1];$('reference').append(o);}$('reference').value='m0472';
 const params=new URLSearchParams(location.search);if(params.get('light')==='night')$('light').value='night';if(params.get('variant')&&variants.variants[params.get('variant')])$('variant').value=params.get('variant');
 await Promise.all([(async()=>{actual=await createViewer($('actual'),variants.current);})(),updateCandidate(),updateNative()]);light();$('status').textContent='Modelos cargados. Cambiá la iluminación para comparar sus respuestas.';
 $('light').onchange=light;$('variant').onchange=updateCandidate;$('reference').onchange=updateNative;
}catch(e){$('status').textContent='No se pudo cargar la comparación. Abrí GALERIA-MODELOS-L2.cmd.';console.error(e);}
addEventListener('pagehide',()=>{actual?.dispose();candidate?.dispose();native?.dispose();});
