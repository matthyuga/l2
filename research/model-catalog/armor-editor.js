import * as THREE from 'three';
import {GLTFLoader} from './vendor/addons/loaders/GLTFLoader.js';
import {OrbitControls} from './vendor/addons/controls/OrbitControls.js?v=20261023-wheel';
import {TransformControls} from './vendor/addons/controls/TransformControls.js';
import {GLTFExporter} from './vendor/addons/exporters/GLTFExporter.js';

const $=id=>document.getElementById(id),storeKey='l2-armor-draft-v1';
const scene=new THREE.Scene();scene.background=new THREE.Color('#293643');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
$('viewport').append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(35,1,.0001,20);camera.position.set(.42,.29,.72);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.target.set(0,.16,0);orbit.minDistance=.06;orbit.maxDistance=2;
const transform=new TransformControls(camera,renderer.domElement);transform.setSize(.8);scene.add(transform);
transform.addEventListener('dragging-changed',e=>{orbit.enabled=!e.value;});
scene.add(new THREE.HemisphereLight(0xf3f6ff,0x5e7086,2));
for(const [p,intensity] of [[[1,2,3],2.3],[[-2,1,1],1.3],[[0,2,-3],1.8]]){const l=new THREE.DirectionalLight(0xffffff,intensity);l.position.set(...p);scene.add(l);}
const grid=new THREE.GridHelper(.8,16,0x6c8292,0x425668);grid.position.y=-.003;scene.add(grid);
const assembly=new THREE.Group();assembly.name='Armadura de Lucien';scene.add(assembly);
let baseObject=null,baseToken=0,loadedBase='fitting',manifest=null,selected=null,category='Cascos',busy=false,restoring=false,items=[],undoStack=[],redoStack=[];
const loader=new GLTFLoader(),assetCache=new Map();
function status(message){$('status').textContent=message;}
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function resize(){const w=$('viewport').clientWidth,h=$('viewport').clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe($('viewport'));resize();
renderer.setAnimationLoop(()=>{orbit.update();renderer.render(scene,camera);});

async function asset(url){
 if(!assetCache.has(url))assetCache.set(url,loader.loadAsync(url).then(g=>g.scene).catch(e=>{assetCache.delete(url);throw e;}));
 const original=await assetCache.get(url),copy=original.clone(true);
 copy.traverse(o=>{if(o.isMesh){o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();}});
 return copy;
}
function disposeCopy(object){object.traverse(o=>{for(const m of o.material?Array.isArray(o.material)?o.material:[o.material]:[])m.dispose();});}
function snapshot(){return {version:1,kind:'l2-armor-project',name:$('projectName').value,base:$('base').value,items:items.map(i=>({id:i.id,partId:i.part.id,name:i.name,position:i.object.position.toArray(),rotation:[i.object.rotation.x,i.object.rotation.y,i.object.rotation.z],scale:i.object.scale.toArray(),visible:i.object.visible,tint:i.tint}))};}
function persist(){if(restoring)return;try{localStorage.setItem(storeKey,JSON.stringify(snapshot()));}catch{status('No se pudo guardar el borrador. Guardá el proyecto como JSON.');}}
function history(){if(restoring)return;undoStack.push(snapshot());if(undoStack.length>50)undoStack.shift();redoStack=[];historyButtons();}
function historyButtons(){$('undo').disabled=!undoStack.length||busy;$('redo').disabled=!redoStack.length||busy;}
async function operation(work){if(busy)return;busy=true;historyButtons();try{await work();}catch(e){console.error(e);status('No se pudo completar: '+e.message);}finally{busy=false;historyButtons();}}
function tintItem(i,color){i.tint=color;i.object.traverse(o=>{for(const m of o.material?Array.isArray(o.material)?o.material:[o.material]:[]){if(!m.color)continue;if(!m.userData.originalColor)m.userData.originalColor=m.color.toArray();m.color.fromArray(m.userData.originalColor).multiply(new THREE.Color(color));}});}
function select(i){selected=i;transform.detach();if(i?.object.visible)transform.attach(i.object);$('properties').hidden=!i;renderAssembly();syncFields();}
function syncFields(){if(!selected)return;const i=selected;$('selectedName').textContent=i.name;$('itemName').value=i.name;$('tint').value=i.tint;
 for(const [field,values] of [['position',i.object.position.toArray().map(x=>x*100)],['rotation',[i.object.rotation.x,i.object.rotation.y,i.object.rotation.z].map(THREE.MathUtils.radToDeg)],['scale',i.object.scale.toArray().map(x=>x*100)]])for(let k=0;k<3;k++)$(field+k).value=Number(values[k].toFixed(field==='position'?3:2));
 $('pieceSource').textContent=i.part.source+(i.part.provisional?' · Corte inicial: puede conservar restos del cuerpo y necesita limpieza.':' · Pieza separada para ajuste.');
}
function renderAssembly(){
 applyBaseFit();
 $('assembly').replaceChildren();$('pieceCount').textContent=items.length+' piezas';$('emptyAssembly').hidden=!!items.length;
 for(const i of items){const row=el('div',undefined,'assemblyRow'+(i===selected?' selected':''));row.dataset.itemId=i.id;
  const visible=el('button',i.object.visible?'◉':'○');visible.title=i.object.visible?'Ocultar pieza':'Mostrar pieza';visible.setAttribute('aria-label',visible.title+' '+i.name);
  visible.onclick=()=>{if(busy)return;history();i.object.visible=!i.object.visible;select(selected);persist();};
  const button=el('button',i.name);button.title=i.name;button.onclick=()=>select(i);row.append(visible,button);$('assembly').append(row);
 }
}
async function createItem(part,record={}){
 const content=await asset(part.url),object=new THREE.Group();object.name=record.name||part.name;object.add(content);
 const i={id:record.id||crypto.randomUUID(),part,name:record.name||part.name,object,tint:'#ffffff'};object.userData.itemId=i.id;
 object.position.fromArray(record.position||part.position);object.rotation.set(...(record.rotation||part.rotation));object.scale.fromArray(record.scale||part.scale);object.visible=record.visible!==false;
 assembly.add(object);items.push(i);tintItem(i,record.tint||'#ffffff');return i;
}
async function add(part){await operation(async()=>{const i=await createItem(part);const after=items.pop();history();items.push(after);select(i);persist();status('Añadida: '+part.name+(part.provisional?' · corte inicial para ajustar.':''));});}
function renderLibrary(){
 $('parts').replaceChildren();const q=$('partSearch').value.toLocaleLowerCase();const source=$('source').value;
 const list=manifest.parts.filter(p=>(!category||p.category===category)&&(!source||(source==='donor'?p.provisional:source==='ref5'?p.id.startsWith('ref5-'):source==='adapted'?p.id.startsWith('fitv1-'):p.id.startsWith('v2-')))&&(!q||(p.name+' '+p.category).toLocaleLowerCase().includes(q)));
 $('libraryCount').textContent=list.length+' piezas en esta selección';
 for(const part of list){const card=el('article',undefined,'part'+(part.provisional?' provisional':''));card.dataset.partId=part.id;
  if(part.thumbnail){const image=el('img');image.src=part.thumbnail;image.alt=part.name;image.loading='lazy';card.append(image);}
  card.append(el('strong',part.name),el('small',part.source+' · '+part.triangles.toLocaleString('es')+' triángulos'));
  const button=el('button','+ Añadir al modelo');button.onclick=()=>add(part);card.append(button);$('parts').append(card);
 }
 if(!list.length)$('parts').append(el('p','No hay piezas con estos filtros.','hint'));
}
function mode(value){transform.setMode(value);document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===value)));}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>mode(b.dataset.mode));
$('space').onchange=()=>transform.setSpace($('space').value);
for(const [kind,label,step] of [['position','positionFields',.1],['rotation','rotationFields',1],['scale','scaleFields',1]])for(let k=0;k<3;k++){
 const l=el('label',['X','Y','Z'][k]),input=el('input');input.id=kind+k;input.type='number';input.step=String(step);input.setAttribute('aria-label',kind+' '+['X','Y','Z'][k]);l.append(input);$(label).append(l);
 input.onchange=()=>{if(!selected||busy)return;const value=Number(input.value);if(!Number.isFinite(value)||input.value.trim()===''){syncFields();return;}
  if(kind==='scale'&&(Math.abs(value)<1||Math.abs(value)>1000)){status('Usá un tamaño entre 1% y 1000% en valor absoluto.');syncFields();return;}
  history();const o=selected.object;
  if(kind==='position')o.position.setComponent(k,THREE.MathUtils.clamp(value,-100,100)/100);
  if(kind==='rotation')o.rotation[['x','y','z'][k]]=THREE.MathUtils.degToRad(value);
  if(kind==='scale'){
   const v=value/100;if($('uniform').checked){const ratio=v/o.scale.getComponent(k);o.scale.multiplyScalar(ratio);}else o.scale.setComponent(k,v);
  }
  syncFields();persist();
 };
}
transform.addEventListener('mouseDown',()=>history());
transform.addEventListener('objectChange',()=>{syncFields();});
transform.addEventListener('mouseUp',()=>{if(selected){for(const a of ['x','y','z'])if(Math.abs(selected.object.scale[a])<.01)selected.object.scale[a]=.01;syncFields();persist();}});
const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();let pointerStart=null;
renderer.domElement.addEventListener('pointerdown',e=>{pointerStart={x:e.clientX,y:e.clientY};});
renderer.domElement.addEventListener('pointerup',e=>{
 if(!pointerStart||Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5||transform.axis||busy)return;
 const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(pointer,camera);
 for(const hit of raycaster.intersectObjects(assembly.children,true)){let o=hit.object;if(!o.visible)continue;while(o&&!o.userData.itemId)o=o.parent;const i=items.find(i=>i.id===o?.userData.itemId);if(i?.object.visible){select(i);return;}}
});
$('itemName').onchange=()=>{if(!selected||busy)return;history();selected.name=$('itemName').value.trim()||selected.part.name;selected.object.name=selected.name;renderAssembly();syncFields();persist();};
$('tint').onchange=()=>{if(!selected||busy)return;history();tintItem(selected,$('tint').value);persist();};
$('mirror').onclick=()=>{if(!selected||busy)return;history();selected.object.position.x*=-1;selected.object.scale.x*=-1;selected.object.rotation.y*=-1;selected.object.rotation.z*=-1;syncFields();persist();};
$('resetPiece').onclick=()=>{if(!selected||busy)return;history();const {object,part}=selected;object.position.fromArray(part.position);object.rotation.set(...part.rotation);object.scale.fromArray(part.scale);tintItem(selected,'#ffffff');syncFields();persist();};
$('duplicate').onclick=()=>{if(!selected)return;const original=selected,record=snapshot().items.find(i=>i.id===original.id);delete record.id;record.name+=' · copia';operation(async()=>{const i=await createItem(original.part,record);items.pop();history();items.push(i);select(i);persist();});};
function removeSelected(){if(!selected||busy)return;history();const i=selected;select(null);assembly.remove(i.object);disposeCopy(i.object);items=items.filter(x=>x!==i);renderAssembly();persist();}
$('delete').onclick=removeSelected;
function ghostBase(){baseObject?.traverse(o=>{for(const m of o.material?Array.isArray(o.material)?o.material:[o.material]:[]){m.transparent=$('ghost').checked;m.opacity=$('ghost').checked?.25:1;m.depthWrite=!$('ghost').checked;}});}
function applyBaseFit(){const helmet=items.some(i=>i.object.visible&&i.part.category==='Cascos');baseObject?.traverse(o=>{if(o.userData.helmet_hide)o.visible=!helmet;});}
$('ghost').onchange=ghostBase;
async function loadBase(value){const token=++baseToken;const data=value==='turnaround-r4'?manifest.turnaround_r4_base:value==='turnaround-r3'?manifest.turnaround_r3_base:value==='turnaround-r2'?manifest.turnaround_r2_base:value==='turnaround'?manifest.turnaround_base:value==='female'?manifest.female_base:value==='fitted'?manifest.fitted_base:value==='fitting'?manifest.fitting_base:{url:'exports/LineageMonsters3/SkeletalMesh/king_of_cat_m00.gltf',position:[0,0,0]};if(!data)throw Error('Base no disponible.');
 const object=await asset(data.url);if(token!==baseToken){disposeCopy(object);return;}
 object.position.fromArray(data.position);object.name='Lucien base';if(baseObject){scene.remove(baseObject);disposeCopy(baseObject);}baseObject=object;loadedBase=value;scene.add(object);ghostBase();applyBaseFit();
}
$('base').onchange=()=>operation(async()=>{const previous=snapshot();previous.base=loadedBase;undoStack.push(previous);redoStack=[];try{await loadBase($('base').value);}catch(e){$('base').value=loadedBase;throw e;}persist();});
function view(direction='iso'){
 const visible=items.filter(i=>i.object.visible).map(i=>i.object);const bounds=new THREE.Box3();if(baseObject)bounds.setFromObject(baseObject);for(const o of visible)bounds.expandByObject(o);
 if(bounds.isEmpty())return;const center=bounds.getCenter(new THREE.Vector3()),radius=Math.max(bounds.getSize(new THREE.Vector3()).length()/2,.15);
 const vectors={front:[0,.08,1],back:[0,.08,-1],side:[1,.08,0],iso:[.6,.28,1]};const d=new THREE.Vector3(...vectors[direction]);orbit.target.copy(center);camera.position.copy(center).add(d.normalize().multiplyScalar(radius/Math.sin(THREE.MathUtils.degToRad(17.5))*1.1));orbit.update();
}
$('frame').onclick=()=>view();document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
function validateProject(data){
 if(!data||data.kind!=='l2-armor-project'||data.version!==1||!Array.isArray(data.items)||data.items.length>150||!['fitting','original','fitted','female','turnaround','turnaround-r2','turnaround-r3','turnaround-r4'].includes(data.base))throw Error('No es un proyecto válido de este taller.');
 const ids=new Set();for(const i of data.items){if(!manifest.parts.some(p=>p.id===i.partId))throw Error('El proyecto usa una pieza que no está en esta biblioteca.');
  for(const key of ['position','rotation','scale'])if(!Array.isArray(i[key])||i[key].length!==3||!i[key].every(v=>Number.isFinite(v)&&Math.abs(v)<1000))throw Error('Transformación no válida.');
  if(i.scale.some(v=>Math.abs(v)<.01||Math.abs(v)>10))throw Error('Tamaño de pieza fuera de rango.');
  if(typeof i.id!=='string'||ids.has(i.id)||typeof i.name!=='string'||i.name.length>150||!/^#[0-9a-f]{6}$/i.test(i.tint))throw Error('Datos de pieza no válidos.');ids.add(i.id);
 }return data;
}
async function restore(data){
 validateProject(data);restoring=true;const staged=[];
 try{
  // Load everything before replacing the current project, so a failed file preserves work.
  for(const record of data.items){const part=manifest.parts.find(p=>p.id===record.partId);await asset(part.url);}
  await loadBase(data.base);
  select(null);for(const i of items){assembly.remove(i.object);disposeCopy(i.object);}items=[];
  $('base').value=data.base;$('projectName').value=String(data.name||'Armadura de Lucien').slice(0,100);
  for(const record of data.items)staged.push(await createItem(manifest.parts.find(p=>p.id===record.partId),record));
  select(staged.at(-1)||null);renderAssembly();
 }finally{restoring=false;}persist();
}
async function undo(redo=false){if(busy)return;const source=redo?redoStack:undoStack,target=redo?undoStack:redoStack;if(!source.length)return;
 await operation(async()=>{const data=source.at(-1),current=snapshot();await restore(data);source.pop();target.push(current);status(redo?'Cambio rehecho.':'Cambio deshecho.');});}
$('undo').onclick=()=>undo();$('redo').onclick=()=>undo(true);
$('clear').onclick=()=>{if(busy||!items.length)return;if(!confirm('¿Vaciar este montaje? Podés recuperarlo con Deshacer.'))return;history();select(null);for(const i of items){assembly.remove(i.object);disposeCopy(i.object);}items=[];renderAssembly();persist();};
$('preset').onclick=()=>operation(async()=>{if(items.length&&!confirm('¿Reemplazar el montaje por el conjunto V2? Podés deshacerlo.'))return;const data=snapshot();data.base='fitting';data.items=manifest.parts.filter(p=>p.id.startsWith('v2-')).map(p=>({id:crypto.randomUUID(),partId:p.id,name:p.name,position:p.position,rotation:p.rotation,scale:p.scale,visible:true,tint:'#ffffff'}));history();await restore(data);view();status('Conjunto V2 listo. Seleccioná una pieza para ajustarla.');});
function download(blob,name){const url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function filename(){return ($('projectName').value||'armadura-lucien').replace(/[^a-z0-9áéíóúñ_-]+/gi,'-').slice(0,80);}
$('saveProject').onclick=()=>{persist();download(new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'}),filename()+'.json');status('Proyecto JSON guardado.');};
$('projectName').onchange=persist;$('openProject').onclick=()=>$('projectFile').click();
$('projectFile').onchange=async()=>{const file=$('projectFile').files[0];$('projectFile').value='';if(!file)return;if(file.size>2e6){status('El JSON es demasiado grande.');return;}
 await operation(async()=>{const data=validateProject(JSON.parse(await file.text()));history();await restore(data);view();status('Proyecto cargado.');});};
// Bake the displayed rest pose into a portable static montage, excluding gizmos and lights.
async function exportModel(){const result=new THREE.Scene();result.name=$('projectName').value;scene.updateMatrixWorld(true);
 const objects=[baseObject,...items.filter(i=>i.object.visible).map(i=>i.object)].filter(Boolean);
 for(const object of objects)object.traverse(o=>{if(!o.isMesh)return;for(let p=o;p;p=p.parent)if(!p.visible)return;const g=o.geometry.clone();
  if(o.isSkinnedMesh){const p=g.attributes.position,v=new THREE.Vector3();for(let k=0;k<p.count;k++){v.fromBufferAttribute(p,k);o.applyBoneTransform(k,v);p.setXYZ(k,v.x,v.y,v.z);}g.deleteAttribute('skinIndex');g.deleteAttribute('skinWeight');g.computeVertexNormals();}
  const mats=(Array.isArray(o.material)?o.material:[o.material]).map(m=>{const c=m.clone();c.opacity=1;c.transparent=false;return c;});const mesh=new THREE.Mesh(g,Array.isArray(o.material)?mats:mats[0]);mesh.name=o.name;mesh.applyMatrix4(o.matrixWorld);result.add(mesh);
 });
 try{const bytes=await new GLTFExporter().parseAsync(result,{binary:true,onlyVisible:true});return bytes;}finally{result.traverse(o=>{o.geometry?.dispose();for(const m of o.material?Array.isArray(o.material)?o.material:[o.material]:[])m.dispose();});}
}
$('exportGlb').onclick=()=>operation(async()=>{status('Preparando el GLB del montaje…');const bytes=await exportModel();download(new Blob([bytes],{type:'model/gltf-binary'}),filename()+'.glb');status('GLB estático exportado. El proyecto JSON conserva los ajustes editables.');});
window.addEventListener('keydown',e=>{if(e.target.matches('input,select,textarea')||e.ctrlKey||e.metaKey||e.altKey)return;if(e.key.toLowerCase()==='w')mode('translate');if(e.key.toLowerCase()==='e')mode('rotate');if(e.key.toLowerCase()==='r')mode('scale');if(e.key==='Delete')removeSelected();});
$('source').onchange=renderLibrary;$('partSearch').oninput=renderLibrary;
try{
 const response=await fetch('armor-parts.json?v=7-ear-housings');if(!response.ok)throw Error('Biblioteca no disponible');manifest=await response.json();
 if(manifest.fitted_base){const option=el('option','Lucien · base limpia del montaje ajustado');option.value='fitted';$('base').append(option);}
 if(manifest.female_base){const option=el('option','Lucien · variante femenina');option.value='female';$('base').append(option);}
 if(manifest.turnaround_r4_base){const option=el('option','Lucien ? cabeza original / casco hueco');option.value='turnaround-r4';$('base').append(option);}
 if(manifest.turnaround_r3_base){const option=el('option','Lucien ? cabeza original');option.value='turnaround-r3';$('base').append(option);}
 if(manifest.turnaround_r2_base){const option=el('option','Lucien ? cabeza reparada');option.value='turnaround-r2';$('base').append(option);}
 if(manifest.turnaround_base){const option=el('option','Lucien · encaje de las cinco vistas');option.value='turnaround';$('base').append(option);}
 const adapted=el('option','Tu montaje · piezas ajustadas');adapted.value='adapted';$('source').append(adapted);
 const ref=el('option','Armadura · cinco vistas');ref.value='ref5';$('source').append(ref);
 for(const name of ['Todas',...manifest.categories]){const b=el('button',name);b.dataset.category=name;b.setAttribute('aria-pressed',String(name===category));b.onclick=()=>{category=name==='Todas'?'':name;document.querySelectorAll('#categories button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));renderLibrary();};$('categories').append(b);}
 renderLibrary();await loadBase('fitting');const saved=localStorage.getItem(storeKey),requested=new URLSearchParams(location.search).get('project');
 if(['lucien-v1-ajustada','lucien-femenina','lucien-cinco-vistas','lucien-cinco-vistas-r2','lucien-cinco-vistas-r3','lucien-cinco-vistas-r4'].includes(requested)){const response=await fetch('projects/'+requested+'.json?v=7');if(!response.ok)throw Error('Montaje no disponible.');await restore(await response.json());status(requested==='lucien-cinco-vistas-r4'?'Casco con alojamientos curvos y huecos para las orejas. Cabeza original conservada.':requested==='lucien-cinco-vistas-r3'?'Cabeza original de Lucien restaurada. Protecciones del casco basadas en sus orejas originales.':requested==='lucien-cinco-vistas-r2'?'Casco felino con orejas y penacho esculpido de Armor Cat. Cabeza reparada bajo el casco.':requested==='lucien-cinco-vistas'?'Estudio de la armadura de cinco vistas. Diez grupos separados para seguir ajustando.':requested==='lucien-femenina'?'Variante femenina lista. Al ocultar el casco se muestran el flequillo y las orejas.':'Tu montaje ajustado está listo. El JSON original se conserva en la carpeta de assets.');}
 else if(saved){try{await restore(JSON.parse(saved));status('Borrador recuperado.');}catch(e){console.error(e);status('No se pudo recuperar el borrador. Podés abrir un JSON guardado.');}}
 else status('Lucien está listo. Elegí una pieza para empezar.');
 view();$('loading').hidden=true;document.body.dataset.ready='true';
}catch(e){console.error(e);$('loading').textContent='No se pudo preparar el taller: '+e.message;status(e.message);}

// Small public API for project interoperability and repeatable browser validation.
window.armorEditor={getProject:snapshot,loadProject:data=>operation(()=>restore(validateProject(data))),exportModel,ready:()=>!!manifest&&!!baseObject};
