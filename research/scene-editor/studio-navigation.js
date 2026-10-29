import * as THREE from 'three';

export function validCameraView(v){return !!v&&[v.position,v.target].every(a=>Array.isArray(a)&&a.length===3&&a.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<1e7))&&Number.isFinite(v.fov)&&v.fov>=5&&v.fov<=150&&v.position.some((n,i)=>Math.abs(n-v.target[i])>1e-6);}

// Own implementation of the mouse branches observed in Studio.CameraControl.
// Shift/Ctrl sensitivity follows the installed KKUS configuration; no target code is reused.
export function createStudioNavigation({camera,orbit,element,canStart=()=>true,onChange=()=>{}}){
 orbit.enableDamping=false;orbit.enableRotate=false;orbit.enablePan=false;orbit.enableZoom=false;
 orbit.mouseButtons={LEFT:-1,MIDDLE:-1,RIGHT:-1};
 let drag=null;
 const speed=e=>e.ctrlKey ? 0.6 : (e.shiftKey ? 4 : 1);
 function capture(){return {position:camera.position.toArray(),target:orbit.target.toArray(),fov:camera.fov};}
 function apply(v){if(!validCameraView(v))throw new Error('Vista de cámara inválida.');drag=null;camera.position.fromArray(v.position);orbit.target.fromArray(v.target);camera.fov=v.fov;camera.updateProjectionMatrix();orbit.update();}
 function focus(point){const delta=point.clone().sub(orbit.target);camera.position.add(delta);orbit.target.copy(point);orbit.update();onChange();}
 function down(e){if(e.pointerType==='touch'||!canStart(e))return;drag={id:e.pointerId,x:e.clientX,y:e.clientY};element.setPointerCapture(e.pointerId);}
 function move(e){if(!drag||e.pointerId!==drag.id||!e.buttons||!orbit.enabled)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.x=e.clientX;drag.y=e.clientY;if(!dx&&!dy)return;
  const offset=camera.position.clone().sub(orbit.target),distance=Math.max(.05,offset.length()),unit=distance*.002*speed(e);
  const right=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion),up=new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion),back=offset.clone().normalize();
  if((e.buttons&3)===3){const delta=right.multiplyScalar(dx*unit).add(back.multiplyScalar(-dy*unit));camera.position.add(delta);orbit.target.add(delta);}
  else if(e.buttons&1){const s=new THREE.Spherical().setFromVector3(offset);s.theta-=dx*.006*speed(e);s.phi=THREE.MathUtils.clamp(s.phi-dy*.006*speed(e),.015,Math.PI-.015);camera.position.copy(orbit.target).add(new THREE.Vector3().setFromSpherical(s));}
  else if(e.buttons&2){const lift=-dy*unit;orbit.target.y+=lift;camera.position.copy(orbit.target).add(back.multiplyScalar(THREE.MathUtils.clamp(distance+dx*unit,.05,4000)));}
  else if(e.buttons&4){const delta=right.multiplyScalar(dx*unit).add(up.multiplyScalar(-dy*unit));camera.position.add(delta);orbit.target.add(delta);}
  orbit.update();onChange();
 }
 function up(e){if(drag?.id===e.pointerId){if(!e.buttons)drag=null;else{drag.x=e.clientX;drag.y=e.clientY;}}}
 function wheel(e){if(!canStart(e)||!orbit.enabled)return;e.preventDefault();const offset=camera.position.clone().sub(orbit.target),distance=Math.max(.05,offset.length());camera.position.copy(orbit.target).add(offset.normalize().multiplyScalar(THREE.MathUtils.clamp(distance*Math.exp(THREE.MathUtils.clamp(e.deltaY,-300,300)*.0015*speed(e)),.05,4000)));orbit.update();onChange();}
 element.addEventListener('pointerdown',down);element.addEventListener('pointermove',move);element.addEventListener('pointerup',up);element.addEventListener('pointercancel',up);element.addEventListener('wheel',wheel,{passive:false});
 return {capture,apply,focus,cancel:()=>{drag=null;},dispose(){for(const [event,fn] of [['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',up],['wheel',wheel]])element.removeEventListener(event,fn);}};
}
