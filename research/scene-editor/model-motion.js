// Optional preview playback for imported glTF clips. It never changes a saved project.
export function createModelMotion({THREE,viewport,getSelected}){
 const models=new WeakMap();let active=null;
 const panel=document.createElement('div');panel.id='model-motion';panel.hidden=true;
 panel.style.cssText='position:absolute;bottom:64px;left:18px;z-index:12;display:flex;gap:7px;align-items:center;padding:8px;background:rgba(10,14,18,.86);border:1px solid #51462c;border-radius:6px;max-width:calc(100% - 36px)';
 const caption=document.createElement('span');caption.textContent='Animación';caption.style.fontSize='11px';
 const select=document.createElement('select');select.id='model-motion-clip';select.setAttribute('aria-label','Animación del modelo');select.style.maxWidth='190px';
 const play=document.createElement('button');play.id='model-motion-play';play.textContent='▶';play.title='Reproducir animación';play.setAttribute('aria-label','Reproducir animación');
 const reset=document.createElement('button');reset.textContent='↶';reset.title='Volver al primer fotograma';reset.setAttribute('aria-label','Reiniciar animación');
 const names={Walk:'Caminar',run:'Correr',atkwait:'Reposo de combate',deathwait:'Caído',Social01:'Gesto',atk01:'Ataque',death:'Morir',spatk02:'Ataque especial 2',spatk01:'Ataque especial 1',Animation:'Caminar con dos ocupantes'};
 panel.append(caption,select,play,reset);viewport.append(panel);
 function choose(record,index){record.mixer.stopAllAction();record.index=index;record.action=record.mixer.clipAction(record.clips[index]);if(record.clips[index].name==='Derrumbe físico de Dion'){record.action.setLoop(THREE.LoopOnce,1);record.action.clampWhenFinished=true;}record.action.reset().play();record.mixer.setTime(0);}
 function current(){let object=getSelected()?.object;while(object){if(models.has(object))return models.get(object);object=object.parent;}return null;}
 select.onchange=()=>{if(active)choose(active,Number(select.value));};
 play.onclick=()=>{if(active){if(active.action.paused&&active.action.clampWhenFinished)choose(active,active.index);active.playing=!active.playing;}};reset.onclick=()=>{if(active){active.playing=false;choose(active,active.index);}};
 return {
  register(object,clips){if(!clips?.length)return;const record={object,clips,mixer:new THREE.AnimationMixer(object),index:0,playing:false};models.set(object,record);choose(record,Math.max(0,clips.findIndex(c=>c.name==='Walk')));},
  update(delta,entries){for(const e of entries){const record=models.get(e.object);if(record?.playing)record.mixer.update(delta);}const next=current();if(next!==active){active=next;select.replaceChildren();if(active)active.clips.forEach((clip,i)=>{const option=document.createElement('option');option.value=i;option.textContent=names[clip.name]||clip.name;select.append(option);});}panel.hidden=!active;panel.style.display=active?'flex':'none';if(active){select.value=active.index;play.textContent=active.playing?'Ⅱ':'▶';play.setAttribute('aria-label',active.playing?'Pausar animación':'Reproducir animación');}},
  state(){return active?{clip:active.clips[active.index].name,time:active.mixer.time,playing:active.playing,clips:active.clips.map(c=>c.name)}:null;}
 };
}
