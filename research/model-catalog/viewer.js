import * as THREE from 'three';
import {GLTFLoader} from './vendor/addons/loaders/GLTFLoader.js';
import {OrbitControls} from './vendor/addons/controls/OrbitControls.js?v=20261023-wheel';
export function preparePlaybackClip(source){
 const clip=source.clone(),starts=clip.tracks.filter(track=>track.times.length).map(track=>track.times[0]);
 const start=starts.length?Math.min(...starts):0;if(Number.isFinite(start)&&start!==0)for(const track of clip.tracks)track.shift(-start);
 clip.resetDuration();return clip;
}
export async function createViewer(container,url,viewBounds=null,terrainVisible=true){
 const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(container.clientWidth,container.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;container.append(renderer.domElement);
 const scene=new THREE.Scene();scene.background=new THREE.Color('#596471');
 const lights=[];const ambient=new THREE.HemisphereLight(0xffffff,0x63718b,2.2);scene.add(ambient);lights.push([ambient,2.2]);
 for(const [position,intensity] of [[[3,4,5],2.4],[[-4,1,1],1.2],[[0,3,-4],1.8]]){const l=new THREE.DirectionalLight(0xffffff,intensity);l.position.set(...position);scene.add(l);lights.push([l,intensity]);}
 function setLighting(mode){const strength=mode==='night'?.12:1;for(const [light,intensity] of lights)light.intensity=intensity*strength;scene.background.set(mode==='night'?'#17212a':'#596471');}
 const camera=new THREE.PerspectiveCamera(35,container.clientWidth/container.clientHeight,.01,10000);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
 let disposed=false,frame=0,object=null,mixer=null,animationPanel=null;
 const clock=new THREE.Clock();
 function cleanup(){disposed=true;cancelAnimationFrame(frame);mixer?.stopAllAction();if(mixer&&object)mixer.uncacheRoot(object);animationPanel?.remove();controls.dispose();resize.disconnect();scene.traverse(o=>{if(o.geometry)o.geometry.dispose();for(const mat of o.material?Array.isArray(o.material)?o.material:[o.material]:[]){for(const value of Object.values(mat))if(value?.isTexture)value.dispose();mat.dispose();}});renderer.dispose();renderer.domElement.remove();}
 const resize=new ResizeObserver(()=>{if(!container.clientWidth||!container.clientHeight)return;camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();renderer.setSize(container.clientWidth,container.clientHeight);});resize.observe(container);
 try{const gltf=await new GLTFLoader().loadAsync(url);object=gltf.scene;scene.add(object);function setTerrainVisible(visible){object.traverse(o=>{if(o.name.includes('NativeTerrain'))o.visible=visible;});}setTerrainVisible(terrainVisible);object.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(object);
  if(Array.isArray(viewBounds)&&viewBounds.length===2&&viewBounds.every(v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite))&&viewBounds[0].every((v,i)=>v<=viewBounds[1][i]))bounds.set(new THREE.Vector3(...viewBounds[0]),new THREE.Vector3(...viewBounds[1]));
  const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());
  const radius=Math.max(size.length()/2,.01),distance=radius/Math.sin(THREE.MathUtils.degToRad(17.5))*1.15;camera.position.copy(center).add(new THREE.Vector3(1,.6,2.8).normalize().multiplyScalar(distance));camera.near=Math.max(radius/1000,.00001);camera.far=distance*30;camera.updateProjectionMatrix();controls.target.copy(center);controls.minDistance=radius*.15;controls.maxDistance=distance*5;controls.update();
  const playbackClips=gltf.animations.map(preparePlaybackClip);
  if(playbackClips.length){
   mixer=new THREE.AnimationMixer(object);animationPanel=document.createElement('div');animationPanel.className='modelAnimationControls';
   const select=document.createElement('select');select.setAttribute('aria-label','Animación del modelo');
   const base=document.createElement('option');base.value='';base.textContent='Pose base';select.append(base);
   gltf.animations.forEach((clip,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=clip.name||'Animación '+(i+1);select.append(option);});
   const pause=document.createElement('button');pause.type='button';pause.textContent='Pausar';pause.disabled=true;
   select.onchange=()=>{mixer.stopAllAction();mixer.timeScale=1;pause.textContent='Pausar';pause.disabled=select.value==='';if(select.value!=='')mixer.clipAction(playbackClips[Number(select.value)]).reset().play();};
   pause.onclick=()=>{mixer.timeScale=mixer.timeScale?0:1;pause.textContent=mixer.timeScale?'Pausar':'Reanudar';};
   animationPanel.append(select,pause);container.append(animationPanel);
  }
  function animate(){if(disposed)return;const delta=Math.min(clock.getDelta(),.1);mixer?.update(delta);controls.update();renderer.render(scene,camera);frame=requestAnimationFrame(animate);}animate();return{dispose:cleanup,setLighting,setTerrainVisible,animationCount:gltf.animations.length};
 }catch(e){cleanup();throw e;}
}
