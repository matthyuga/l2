import * as T from 'three';
import {defaultAtmosphere,validAtmosphere} from './atmosphere-schema.js';
const labels={none:'Sin clima',rain:'Lluvia',storm:'Tormenta',snow:'Nieve',sand:'Tormenta de arena',wind:'Viento y polvo',ash:'Cenizas',mist:'Niebla'};
export function createAtmosphere({scene,camera,orbit,viewPanel,toolbar,commit,message,isBusy}){
 let config=defaultAtmosphere(),catalog=[],request=0,skyTexture=null,particleTexture=null,particles=null,loadedSky=null,elapsed=0,tab='sky',page=0,search='',refreshTimer=null;
 const sky=new T.Mesh(new T.SphereGeometry(1,48,24),new T.MeshBasicMaterial({side:T.BackSide,depthWrite:false,depthTest:false,fog:false,toneMapped:false}));sky.renderOrder=-1000;sky.visible=false;sky.frustumCulled=false;sky.raycast=()=>{};scene.add(sky);
 const lights=scene.children.filter(n=>n.isLight).map(l=>[l,l.intensity]);
 const loader=new T.TextureLoader();
 const panel=document.createElement('section');panel.className='atmosphere-controls';panel.innerHTML='<div class="section-title">Ambiente</div><button id="browse-atmosphere">Explorar cielos, partículas y audio</button><p id="active-sky" class="hint">Cielo: fondo de estudio</p><button id="clear-sky">Quitar cielo</button><label>Clima<select id="atmosphere-weather"></select></label><div id="atmosphere-ranges"></div><button id="reset-atmosphere">Restaurar ambiente de estudio</button><p class="hint">Vista previa del Taller. Guardá el proyecto para conservar el ambiente.</p>';
 viewPanel.prepend(panel);
 const $=id=>panel.querySelector('#'+id),weather=$('atmosphere-weather');for(const [value,title]of Object.entries(labels)){const o=new Option(title,value);weather.add(o);}
 for(const [key,title,min,max,step]of [['rotation','Giro del cielo',0,360,1],['brightness','Luz',.1,3,.1],['density','Cantidad de partículas',.1,2,.1],['wind','Viento',0,3,.1],['fog','Niebla',0,1,.01]]){const label=document.createElement('label');label.textContent=title+' ';const output=document.createElement('output');output.id='atmosphere-'+key+'-value';const input=document.createElement('input');input.type='range';input.id='atmosphere-'+key;Object.assign(input,{min,max,step});label.append(output,input);$('atmosphere-ranges').append(label);input.onchange=()=>change({...config,[key]:Number(input.value)});}
 const button=document.createElement('button');button.id='atmosphere-open';button.textContent='☁ Ambientes';button.title='Ver cielos, clima, partículas y sonidos';toolbar.append(button);
 const dialog=document.createElement('dialog');dialog.id='atmosphere-library';dialog.setAttribute('aria-label','Biblioteca de ambientes');dialog.innerHTML='<div class="atmosphere-heading"><strong>Biblioteca de ambientes</strong><button id="atmosphere-close" aria-label="Cerrar ambientes">✕</button></div><nav class="atmosphere-tabs"><button data-type="sky">Cielos</button><button data-type="particle">Partículas</button><button data-type="audio">Audio</button></nav><div class="atmosphere-search"><input id="atmosphere-search" type="search" placeholder="Buscar recurso o proveedor" aria-label="Buscar ambientes"><button id="atmosphere-refresh">Actualizar descargas</button></div><p id="atmosphere-count" class="hint"></p><div id="atmosphere-assets"></div><div class="atmosphere-pages"><button id="atmosphere-prev">Anterior</button><span id="atmosphere-page"></span><button id="atmosphere-next">Siguiente</button></div><div class="atmosphere-audio" hidden><span id="atmosphere-audio-title"></span><audio id="atmosphere-player" controls preload="none"></audio></div><p id="atmosphere-note" class="hint"></p>';
 document.body.append(dialog);const q=id=>dialog.querySelector('#'+id),player=q('atmosphere-player');player.volume=.35;
 const close=()=>{dialog.close();player.pause();};q('atmosphere-close').onclick=close;dialog.addEventListener('cancel',()=>player.pause());
 async function loadCatalog(){const r=await fetch('/api/atmosphere');if(!r.ok)throw new Error('No se pudo cargar la biblioteca de ambientes.');const data=await r.json();catalog=data.items||[];render();return data;}
 function render(){
  const filtered=catalog.filter(i=>i.type===tab&&(!search||`${i.title} ${i.provider}`.toLowerCase().includes(search))),pages=Math.max(1,Math.ceil(filtered.length/24));page=Math.min(page,pages-1);
  q('atmosphere-count').textContent=filtered.length+' recursos · '+({sky:'Elegí un cielo para verlo en la escena.',particle:'Elegí una textura para probarla con partículas animadas.',audio:'Fragmentos de hasta 12 s de los ZIP de Sonniss terminados.'}[tab]);
  const grid=q('atmosphere-assets');grid.replaceChildren();grid.className=tab==='audio'?'audio-list':'atmosphere-grid';
  for(const item of filtered.slice(page*24,page*24+24)){const card=document.createElement('button');card.className='atmosphere-card';card.dataset.id=item.id;card.title=item.title+' · '+item.provider;
   if(item.thumbnail){const img=document.createElement('img');img.loading='lazy';img.src=item.thumbnail;img.alt='';card.append(img);}
   const title=document.createElement('strong');title.textContent=item.title;const provider=document.createElement('small');provider.textContent=item.provider+(item.frames>1?' · animada':'');card.append(title,provider);
   card.onclick=async()=>{if(isBusy())return;if(item.type==='audio'){q('atmosphere-audio-title').textContent=item.title;dialog.querySelector('.atmosphere-audio').hidden=false;player.src=item.url;try{await player.play();}catch{message('Usá reproducir para escuchar el sonido.');}return;}
    const ok=await change(item.type==='sky'?{...config,sky:item.id}:{...config,particle:item.id,weather:config.weather==='none'?'wind':config.weather});if(ok)close();};grid.append(card);
  }
  q('atmosphere-prev').disabled=page===0;q('atmosphere-next').disabled=page===pages-1;q('atmosphere-page').textContent=(page+1)+' / '+pages;
  q('atmosphere-note').textContent=tab==='sky'?'Cielos descargados en formato panorámico. La luz se ajusta desde Vista → Ambiente.':tab==='particle'?'Se muestran las imágenes originales en un emisor de prueba; el aspecto final depende de su configuración.':'Sonniss sigue descargándose. Actualizar descargas incorpora nuevos sonidos disponibles. Freesound pendiente de inicio de sesión.';
  dialog.querySelectorAll('[data-type]').forEach(b=>b.classList.toggle('active',b.dataset.type===tab));
 }
 async function open(){if(!dialog.open)dialog.show();try{await loadCatalog();}catch(e){q('atmosphere-count').textContent=e.message;}}
 button.onclick=$('browse-atmosphere').onclick=open;
 dialog.querySelectorAll('[data-type]').forEach(b=>b.onclick=()=>{tab=b.dataset.type;page=0;search='';q('atmosphere-search').value='';player.pause();dialog.querySelector('.atmosphere-audio').hidden=true;render();});
 q('atmosphere-search').oninput=e=>{search=e.target.value.toLowerCase();page=0;render();};q('atmosphere-prev').onclick=()=>{page--;render();};q('atmosphere-next').onclick=()=>{page++;render();};
 q('atmosphere-refresh').onclick=async()=>{const b=q('atmosphere-refresh');b.disabled=true;try{const r=await fetch('/api/atmosphere/refresh',{method:'POST'});if(!r.ok)throw new Error('No se pudo actualizar la biblioteca.');q('atmosphere-count').textContent='Preparando vistas previas de las descargas terminadas…';clearInterval(refreshTimer);refreshTimer=setInterval(async()=>{try{const data=await loadCatalog();if(!data.building){clearInterval(refreshTimer);b.disabled=false;message(data.buildError||'Biblioteca de ambientes actualizada.');}}catch(e){clearInterval(refreshTimer);b.disabled=false;message(e.message);}},2000);}catch(e){b.disabled=false;message(e.message);}};
 function sync(){weather.value=config.weather;for(const k of ['rotation','brightness','density','wind','fog']){$('atmosphere-'+k).value=config[k];$('atmosphere-'+k+'-value').value=config[k];}$('active-sky').textContent='Cielo: '+(catalog.find(i=>i.id===config.sky)?.title||'fondo de estudio');}
 function generatedTexture(){const c=document.createElement('canvas');c.width=c.height=64;const ctx=c.getContext('2d');const g=ctx.createRadialGradient(32,32,0,32,32,32);g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;ctx.fillRect(0,0,64,64);return new T.CanvasTexture(c);}
 function rebuild(texture,frames=1){
  if(particles){scene.remove(particles);particles.geometry.dispose();particles.material.dispose();}particleTexture?.dispose();particleTexture=texture;
  const count=Math.round(1800*config.density),pos=new Float32Array(count*3),seed=new Float32Array(count*3);let n=82731;for(let i=0;i<seed.length;i++){n=(Math.imul(n,1664525)+1013904223)>>>0;seed[i]=n/4294967296;}
  const geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(pos,3).setUsage(T.DynamicDrawUsage));
  const color=config.particle?'#ffffff':config.weather==='sand'?'#d5ad6c':config.weather==='ash'?'#aaa6a0':'#cbdfe7';
  const mat=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{map:{value:texture},tint:{value:new T.Color(color)},pointSize:{value:1},opacity:{value:config.weather==='sand'?.16:.6},frame:{value:0},frames:{value:frames},streak:{value:!config.particle&&['rain','storm'].includes(config.weather)?1:0}},vertexShader:'uniform float pointSize;void main(){vec4 p=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*p;gl_PointSize=clamp(pointSize*500./max(.1,-p.z),1.,110.);}',fragmentShader:'uniform sampler2D map;uniform vec3 tint;uniform float opacity,frame,frames,streak;void main(){vec2 uv=gl_PointCoord;if(streak>.5&&abs(uv.x-.5)>.055)discard;vec4 c=texture2D(map,vec2((uv.x+frame)/frames,1.-uv.y));gl_FragColor=vec4(c.rgb*tint,c.a*opacity);if(gl_FragColor.a<.015)discard;}' });
  particles=new T.Points(geo,mat);particles.userData.seeds=seed;particles.frustumCulled=false;particles.raycast=()=>{};scene.add(particles);
 }
 async function apply(value,notify=false){
  const next=value||defaultAtmosphere();if(!validAtmosphere(next,catalog)){message('Ambiente inválido o recurso no disponible.');return false;}
  const token=++request;
  let skyMap=null,particleMap=null;
  try{
   if(next.sky&&next.sky!==loadedSky){const item=catalog.find(i=>i.id===next.sky);skyMap=await loader.loadAsync(item.url);skyMap.colorSpace=T.SRGBColorSpace;}
   if(next.weather!=='none'){const item=catalog.find(i=>i.id===next.particle);particleMap=item?await loader.loadAsync(item.url):generatedTexture();particleMap.colorSpace=T.SRGBColorSpace;}
   if(token!==request){skyMap?.dispose();particleMap?.dispose();return false;}
   config=structuredClone(next);
   if(skyMap||!next.sky){skyTexture?.dispose();skyTexture=skyMap;loadedSky=next.sky;sky.material.map=skyTexture;sky.material.needsUpdate=true;}
   sky.visible=!!config.sky;sky.rotation.y=T.MathUtils.degToRad(config.rotation);sky.material.color.setScalar(config.brightness);
   for(const [light,power]of lights)light.intensity=power*config.brightness;
   const fogColor=config.weather==='sand'?'#b89a71':config.weather==='ash'?'#74716d':'#a9bac5';scene.fog=config.fog?new T.FogExp2(fogColor,config.fog*.002):null;
   scene.background=new T.Color(config.fog&&!config.sky?fogColor:'#000000');
   if(particleMap)rebuild(particleMap,catalog.find(i=>i.id===config.particle)?.frames||1);else if(particles){scene.remove(particles);particles.geometry.dispose();particles.material.dispose();particles=null;particleTexture?.dispose();particleTexture=null;}
   sync();if(notify){commit();message((config.sky?'Cielo aplicado. ':'')+labels[config.weather]+'. Podés ajustar el ambiente en Vista.');}return true;
  }catch(e){skyMap?.dispose();particleMap?.dispose();sync();message('No se pudo cargar el ambiente: '+e.message);return false;}
 }
 async function change(next){if(isBusy()){sync();return false;}return apply(next,true);}
 weather.onchange=()=>change({...config,weather:weather.value,particle:null,fog:({sand:.25,mist:.45,storm:.08}[weather.value]||0)});
 $('clear-sky').onclick=()=>change({...config,sky:null});$('reset-atmosphere').onclick=()=>change(defaultAtmosphere());
 function update(time){elapsed=time;sky.position.copy(camera.position);sky.scale.setScalar(camera.far*.8);
  const flash=config.weather==='storm'&&time%9.7>9.45?Math.pow(Math.max(0,Math.sin((time%9.7-9.45)*80)),6)*1.7:0;
  for(const [light,power]of lights)light.intensity=power*config.brightness*(1+flash);sky.material.color.setScalar(config.brightness*(1+flash));
  if(!particles)return;
  const radius=T.MathUtils.clamp(camera.position.distanceTo(orbit.target)*.7,30,1200),seed=particles.userData.seeds,a=particles.geometry.attributes.position,v=config.weather,fall=['rain','storm'].includes(v)?1:v==='snow'?.14:.05;
  for(let i=0;i<a.count;i++){const x=seed[i*3],y=seed[i*3+1],z=seed[i*3+2],phase=((y-time*fall*.12)%1+1)%1,drift=config.wind*time*.025;a.setXYZ(i,orbit.target.x+((((x+drift)%1)*2)-1)*radius,orbit.target.y+(phase-.25)*radius,orbit.target.z+(z*2-1)*radius+Math.sin(time*.4+i)*radius*.012);}
  a.needsUpdate=true;particles.material.uniforms.pointSize.value=radius*(config.particle ? .09 : ['sand','wind','mist'].includes(v) ? .045 : ['rain','storm'].includes(v) ? .028 : .008);particles.material.uniforms.frame.value=Math.floor(time*12)%particles.material.uniforms.frames.value;
 }
 sync();
 return {ready:loadCatalog().catch(e=>message(e.message)),restore:apply,get:()=>structuredClone(config),update,open,state:()=>({...config,skyLoaded:loadedSky,particles:particles?.geometry.attributes.position.count||0,sample:particles?Array.from(particles.geometry.attributes.position.array.slice(0,3)):[],time:elapsed})};
}
