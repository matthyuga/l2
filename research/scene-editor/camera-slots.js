import {validCameraView} from './studio-navigation.js';

export function createCameraSlots({viewport,capture,apply,onSave=()=>{},onLoad=()=>{}}){
 let slots=Array(10).fill(null),active=-1;
 const dock=document.createElement('nav');dock.className='camera-dock';dock.setAttribute('aria-label','Tomas guardadas');
 function render(){dock.replaceChildren();for(let i=0;i<10;i++){const cell=document.createElement('div');cell.className='camera-slot';const save=document.createElement('button');save.className='camera-save';save.textContent='Save';save.setAttribute('aria-label','Guardar cámara '+(i+1));save.title='Guardar ubicación y ángulo en la toma '+(i+1);save.onclick=()=>{slots[i]=capture();active=i;render();onSave(i+1);};const load=document.createElement('button');load.className='camera-load'+(active===i?' active':'');load.textContent=i+1;load.disabled=!slots[i];load.setAttribute('aria-label','Cargar cámara '+(i+1));load.title=slots[i]?'Recuperar toma '+(i+1):'Toma vacía: usá Save';load.onclick=()=>{if(!slots[i])return;apply(slots[i]);active=i;render();onLoad(i+1);};cell.append(save,load);dock.append(cell);}}
 viewport.append(dock);render();
 return {get(){return structuredClone(slots);},set(value){if(value!==undefined&&(!Array.isArray(value)||value.length!==10||value.some(v=>v!==null&&!validCameraView(v))))throw new Error('Tomas guardadas inválidas.');slots=value?structuredClone(value):Array(10).fill(null);active=-1;render();},element:dock};
}
