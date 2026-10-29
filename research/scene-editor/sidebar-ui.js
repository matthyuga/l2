const paths={
 apply:'<path d="m14 3 7 7-9 9H5v-7l9-9Z M12 5l7 7 M4 20l-1 1"/><path d="m14 17 2 2 5-5"/>',
 browse:'<path d="M3 7V5h7l2 2h9v12H3V7Z"/><circle cx="11" cy="13" r="3"/><path d="m13 15 3 3"/>',
 reset:'<path d="M4 9a8 8 0 1 1 0 7 M4 3v6h6"/>',
 replace:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M6 12h12m-4-4 4 4-4 4"/>',
 layer:'<path d="m12 3 10 6-10 6L2 9l10-6Z M3 14l9 5 9-5 M12 7v4m-2-2h4"/>',
 repeat:'<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M12 3v18M3 12h18"/>',
 opacity:'<path d="M12 2S4 11 4 16a8 8 0 0 0 16 0c0-5-8-14-8-14Z M12 9v13"/>',
 material:'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Z M3 8l9 5 9-5M12 13v9"/>',
 frame:'<path d="M3 9V3h6m6 0h6v6m0 6v6h-6M9 21H3v-6"/><circle cx="12" cy="12" r="3"/>',
 home:'<path d="m3 11 9-8 9 8 M5 10v11h14V10 M9 21v-7h6v7"/>',
 duplicate:'<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V3H3v13h5 M11 14h7m-3-3v7"/>',
 remove:'<path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/>',
 snap:'<path d="M6 3v9a6 6 0 0 0 12 0V3h-4v9a2 2 0 0 1-4 0V3H6Z M6 7h4m4 0h4"/>'
};
export const icon=name=>'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[name]+'</svg>';
export function iconButton(button,name,label){if(!button)return;button.innerHTML=icon(name);button.title=label;button.setAttribute('aria-label',label);button.classList.add('sidebar-icon-action');}

export function compactSurfaceControls(panel){
 const $=id=>document.getElementById(id);
 iconButton($('surface-apply'),'apply','Aplicar textura');iconButton($('surface-reset'),'reset','Restaurar material heredado');iconButton($('surface-browse'),'browse',$('surface-browse').textContent);
 $('surface-apply').classList.add('primary');
 const quick=document.createElement('div');quick.className='surface-quick';$('surface-previews').before(quick);quick.append($('surface-previews'),$('surface-apply'));
 const actions=document.createElement('div');actions.className='surface-icon-actions';quick.after(actions);actions.append($('surface-browse'),$('surface-reset'));
 const mode=$('surface-mode'),modeLabel=mode.closest('label');modeLabel.hidden=true;mode.setAttribute('aria-hidden','true');mode.tabIndex=-1;
 for(const [value,name,label] of [['replace','replace','Reemplazar textura'],['layer','layer','Capa sobre la textura existente']]){const button=document.createElement('button');button.type='button';button.dataset.surfaceMode=value;iconButton(button,name,label);button.onclick=()=>{mode.value=value;mode.dispatchEvent(new Event('change'));};actions.append(button);}
 function compactLabel(input,name,label){const wrap=input.closest('label'),mark=document.createElement('span');mark.className='surface-control-icon';mark.innerHTML=icon(name);mark.title=label;wrap.replaceChildren(mark,input);wrap.classList.add('surface-inline-control');input.setAttribute('aria-label',label);input.title=label;wrap.title=label;return wrap;}
 compactLabel($('surface-slot'),'material','Material de la pieza');compactLabel($('surface-repeat'),'repeat','Repetición de textura');const opacity=compactLabel($('surface-opacity'),'opacity','Opacidad de la capa');const output=document.createElement('output');output.id='surface-opacity-value';opacity.append(output);
 function sync(){for(const b of actions.querySelectorAll('[data-surface-mode]')){const active=b.dataset.surfaceMode===mode.value;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));}$('surface-opacity').disabled=mode.value!=='layer';output.textContent=Math.round(Number($('surface-opacity').value)*100)+' %';}
 mode.addEventListener('change',sync);$('surface-opacity').addEventListener('input',sync);sync();return {sync};
}

export function initSidebarResize({studio,main,isExpanded}){
 const handle=document.createElement('div');handle.id='studio-resizer';handle.className='studio-resizer';handle.tabIndex=0;handle.setAttribute('role','separator');handle.setAttribute('aria-orientation','vertical');handle.setAttribute('aria-label','Ajustar ancho del panel izquierdo');handle.title='Arrastrá ↔ para cambiar el ancho. Doble clic: restaurar ancho.';handle.innerHTML='<span></span>';studio.append(handle);
 const key='l2-scene-editor-panel-width';let requested=null,drag=null;try{const saved=Number(localStorage.getItem(key));if(saved>=210&&saved<=520)requested=saved;}catch{}
 const limits=()=>({min:210,max:Math.max(210,Math.min(520,main.clientWidth-(document.getElementById('scene-workspace')?.getBoundingClientRect().width||285)-260))});
 function apply(value){const {min,max}=limits();if(value===null){main.style.removeProperty('--studio-width');handle.setAttribute('aria-valuenow',String(Math.round(studio.getBoundingClientRect().width)));}else{const width=Math.round(Math.min(max,Math.max(min,value)));main.style.setProperty('--studio-width',width+'px');handle.setAttribute('aria-valuenow',String(width));}handle.setAttribute('aria-valuemin',String(min));handle.setAttribute('aria-valuemax',String(max));}
 function persist(){try{if(requested===null)localStorage.removeItem(key);else localStorage.setItem(key,String(requested));}catch{}}
 function end(cancel=false){if(!drag)return;if(cancel)requested=drag.before;else requested=studio.getBoundingClientRect().width;drag=null;document.body.classList.remove('resizing-sidebar');apply(requested);persist();}
 handle.addEventListener('pointerdown',e=>{if(e.button!==0||!isExpanded())return;e.preventDefault();handle.focus({preventScroll:true});drag={x:e.clientX,width:studio.getBoundingClientRect().width,before:requested};handle.setPointerCapture(e.pointerId);document.body.classList.add('resizing-sidebar');});
 handle.addEventListener('pointermove',e=>{if(!drag)return;apply(drag.width+e.clientX-drag.x);});handle.addEventListener('pointerup',()=>end());handle.addEventListener('pointercancel',()=>end(true));handle.addEventListener('lostpointercapture',()=>end());handle.ondblclick=()=>{requested=null;apply(null);persist();};
 handle.addEventListener('keydown',e=>{if(e.key==='Escape'&&drag){e.preventDefault();e.stopPropagation();end(true);return;}if(!['ArrowLeft','ArrowRight','Home'].includes(e.key))return;e.preventDefault();e.stopPropagation();if(e.key==='Home')requested=null;else{const delta=(e.shiftKey?30:10)*(e.key==='ArrowLeft'?-1:1),{min,max}=limits();requested=Math.min(max,Math.max(min,studio.getBoundingClientRect().width+delta));}apply(requested);persist();});
 window.addEventListener('resize',()=>apply(requested));apply(requested);return {handle,reset(){requested=null;apply(null);persist();}};
}
