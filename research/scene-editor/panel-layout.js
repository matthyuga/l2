// Compact scene controls. Existing panel nodes and their listeners are retained.
import {icon,iconButton,initSidebarResize} from './sidebar-ui.js';
export function initPanelLayout({studio,showTab,rendererElement}) {
  if (!studio || typeof showTab !== 'function') throw new Error('El panel necesita studio y showTab.');
  if (studio.panelLayout) return studio.panelLayout;
  const main=studio.parentElement;
  const viewport=rendererElement?.parentElement || document.getElementById('viewport');
  initViewportWindow(viewport);
  const tabs=studio.querySelector('.tabs');
  const tools=studio.querySelector('.tools');
  const actions=studio.querySelector('.view-actions');
  const panels=[...studio.querySelectorAll('[role="tabpanel"]')];
  const paths={
    library:'<path d="M12 4v16M4 12h16"/>',
    scene:'<path d="M5 5h14v4H5zM5 15h14v4H5zM8 9v6M16 9v6"/>',
    view:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    terrain:'<path d="m2 18 6-10 5 6 3-5 6 9H2Z"/>',
    material:'<path d="m12 2 9 5v10l-9 5-9-5V7l9-5Z M3 7l9 5 9-5 M12 12v10"/>',
    transform:'<path d="M12 3v18M3 12h18m-9-9-3 3m3-3 3 3M3 12l3-3m-3 3 3 3"/>',
    translate:'<path d="M12 2v20M2 12h20M8 6l4-4 4 4M8 18l4 4 4-4M6 8l-4 4 4 4M18 8l4 4-4 4"/>',
    rotate:'<path d="M20 8a8 8 0 1 0 0 8M20 3v5h-5"/>',
    scale:'<path d="M4 14v6h6M14 4h6v6M4 20l7-7M20 4l-7 7"/>'
  };
  const svg=name=>`<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${paths[name]}</svg>`;
  const labels={library:'Añadir',scene:'Detalles',transform:'Posición',material:'Material',view:'Vista',terrain:'Terreno'};
  studio.classList.add('compact-studio');main.classList.add('compact-layout');
  studio.querySelector('.studio-title')?.remove();
  const rail=document.createElement('nav');rail.className='studio-rail';rail.setAttribute('aria-label','Secciones del editor');
  tabs.classList.add('studio-icon-tabs');rail.append(tabs);
  const content=document.createElement('div');content.className='studio-content';content.id='studio-panel-content';
  const heading=document.createElement('div');heading.className='compact-heading';heading.textContent='Añadir';
  content.append(heading);
  if(tools)content.append(tools);if(actions)content.append(actions);
  content.append(...panels);studio.append(rail,content);
  const toggle=document.createElement('label');toggle.className='studio-panel-toggle';
  const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=true;checkbox.id='show-studio-panel';checkbox.setAttribute('aria-controls',content.id);
  toggle.append(checkbox,document.createTextNode('Mostrar panel'));viewport.append(toggle);
  let expanded=true;
  function setExpanded(value){
    expanded=!!value;checkbox.checked=expanded;content.hidden=!expanded;
    main.classList.toggle('panel-collapsed',!expanded);
    for(const b of tabs.querySelectorAll('[data-tab]'))b.setAttribute('aria-expanded',String(expanded&&b.getAttribute('aria-selected')==='true'));
  }
  function sync(){
    const active=tabs.querySelector('[aria-selected="true"]');
    heading.textContent=labels[active?.dataset.tab]||'Escena';
    for(const b of tabs.querySelectorAll('[data-tab]'))b.setAttribute('aria-expanded',String(expanded&&b===active));
  }
  checkbox.onchange=()=>setExpanded(checkbox.checked);
  const buttons=[...tabs.querySelectorAll('[data-tab]')];
  for(const button of buttons){
    const id=button.dataset.tab;button.innerHTML=svg(id)+`<span>${labels[id]}</span>`;
    button.title=labels[id];button.setAttribute('aria-label',labels[id]);
    button.onclick=()=>{showTab(id);setExpanded(true);sync();};
    button.addEventListener('keydown',event=>{
      let index=buttons.indexOf(button);
      if(event.key==='ArrowDown'||event.key==='ArrowRight')index=(index+1)%buttons.length;
      else if(event.key==='ArrowUp'||event.key==='ArrowLeft')index=(index+buttons.length-1)%buttons.length;
      else if(event.key==='Home')index=0;else if(event.key==='End')index=buttons.length-1;else return;
      event.preventDefault();buttons[index].focus();buttons[index].click();
    });
  }
  tabs.setAttribute('aria-orientation','vertical');
  for(const button of tools?.querySelectorAll('[data-mode]')||[]){
    const label={translate:'Mover (W)',rotate:'Rotar (E)',scale:'Escalar (R)'}[button.dataset.mode];
    button.innerHTML=svg(button.dataset.mode);button.title=label;button.setAttribute('aria-label',label);
  }
  for(const [id,name,label] of [['frame','frame','Encuadrar selección'],['home','home','Ver toda la escena'],['duplicate','duplicate','Duplicar objeto o grupo'],['remove','remove','Quitar objeto o grupo'],['reset-transform','reset','Restaurar transformación']])iconButton(document.getElementById(id),name,label);
  document.getElementById('duplicate')?.closest('.actions')?.append(document.getElementById('reset-transform'));
  const snap=document.getElementById('snap');if(snap){const label=snap.closest('label');label.replaceChildren(snap);const mark=document.createElement('span');mark.innerHTML=icon('snap');label.append(mark);label.title='Ajustar movimientos, giros y escala a la cuadrícula';snap.setAttribute('aria-label','Ajuste a la cuadrícula');}
  const observer=new MutationObserver(sync);observer.observe(tabs,{subtree:true,attributes:true,attributeFilter:['aria-selected']});
  sync();setExpanded(true);
  initSidebarResize({studio,main,isExpanded:()=>expanded});
  studio.panelLayout={setExpanded,get expanded(){return expanded;},destroy(){observer.disconnect();}};
  return studio.panelLayout;
}

function initViewportWindow(viewport){
  const bar=document.createElement('div');bar.className='viewport-window-bar';
  bar.innerHTML='<strong>Visor del mapa</strong><button type="button" id="viewport-float">Ventana flotante</button><button type="button" id="viewport-maximize">Ampliar</button><button type="button" id="viewport-fullscreen">Pantalla completa</button><button type="button" id="viewport-dock" hidden>Acoplar</button>';
  viewport.prepend(bar);
  const float=bar.querySelector('#viewport-float'),max=bar.querySelector('#viewport-maximize'),full=bar.querySelector('#viewport-fullscreen'),dock=bar.querySelector('#viewport-dock');
  let mode='docked',previous='docked',floatingSize={width:'',height:''};
  function setMode(next){
    if(mode==='floating')floatingSize={width:viewport.style.width,height:viewport.style.height};
    viewport.style.width=next==='floating'?floatingSize.width:'';
    viewport.style.height=next==='floating'?floatingSize.height:'';
    mode=next;viewport.dataset.windowMode=mode;
    viewport.classList.toggle('viewport-floating',mode==='floating');
    viewport.classList.toggle('viewport-maximized',mode==='maximized');
    float.hidden=mode==='floating';dock.hidden=mode==='docked';
    max.textContent=mode==='maximized'?'Restaurar':'Ampliar';
    max.setAttribute('aria-pressed',String(mode==='maximized'));
  }
  float.onclick=()=>setMode('floating');
  dock.onclick=async()=>{if(document.fullscreenElement===viewport)await document.exitFullscreen();setMode('docked');};
  max.onclick=()=>{if(mode==='maximized')setMode(previous);else{previous=mode;setMode('maximized');}};
  full.onclick=async()=>{try{if(document.fullscreenElement===viewport)await document.exitFullscreen();else await viewport.requestFullscreen();}catch{previous=mode;setMode('maximized');}};
  document.addEventListener('fullscreenchange',()=>{full.textContent=document.fullscreenElement===viewport?'Salir de pantalla completa':'Pantalla completa';});
  bar.addEventListener('dblclick',event=>{if(!event.target.closest('button'))max.click();});
  let drag=null;
  bar.addEventListener('pointerdown',event=>{
    if(mode!=='floating'||event.button!==0||event.target.closest('button')||document.fullscreenElement)return;
    const rect=viewport.getBoundingClientRect();drag={x:event.clientX,y:event.clientY,left:rect.left,top:rect.top};
    bar.setPointerCapture(event.pointerId);event.preventDefault();
  });
  bar.addEventListener('pointermove',event=>{if(!drag)return;
    viewport.style.setProperty('--view-x',Math.max(0,Math.min(innerWidth-viewport.offsetWidth,drag.left+event.clientX-drag.x))+'px');
    viewport.style.setProperty('--view-y',Math.max(0,Math.min(innerHeight-34,drag.top+event.clientY-drag.y))+'px');
  });
  bar.addEventListener('pointerup',()=>drag=null);bar.addEventListener('lostpointercapture',()=>drag=null);
  window.addEventListener('resize',()=>{if(mode==='floating'){const rect=viewport.getBoundingClientRect();viewport.style.setProperty('--view-x',Math.max(0,Math.min(rect.left,innerWidth-viewport.offsetWidth))+'px');viewport.style.setProperty('--view-y',Math.max(0,Math.min(rect.top,innerHeight-34))+'px');}});
  setMode('docked');
}
