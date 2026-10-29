import * as THREE from 'three';
// Editor-only overlays live outside the pickable content and never change source materials.
export function createSelectionHighlights(scene){
 const root=new THREE.Group();root.name='Resaltado del editor';scene.add(root);let enabled=true;
 const slots={selected:{key:null,items:[]},hover:{key:null,items:[]}};
 function clear(slot){for(const item of slot.items){item.fill.removeFromParent();item.edges.removeFromParent();item.fill.material.dispose();item.edges.material.dispose();item.edges.geometry.dispose();if(item.owned)item.fill.geometry.dispose();}slot.items=[];slot.key=null;}
 function show(kind,object,materialName=null){if(!enabled)object=null;const slot=slots[kind],key=object?object.uuid+'|'+(materialName||''):null;if(slot.key===key)return;clear(slot);slot.key=key;if(!object)return;
  let meshes=0,triangles=0;object.traverse(mesh=>{if(mesh.isMesh&&!mesh.userData.surfaceOverlay&&!mesh.userData.sceneEffectParticle){meshes++;triangles+=(mesh.geometry.index?.count||mesh.geometry.attributes.position?.count||0)/3;}});
  // Whole city roots can contain thousands of meshes. Outline their bounds;
  // individual pieces retain their detailed highlight when selected directly.
  if(meshes>128||triangles>200000){
   object.updateWorldMatrix(true,true);const bounds=new THREE.Box3().setFromObject(object).applyMatrix4(object.matrixWorld.clone().invert());
   if(bounds.isEmpty())return;const size=bounds.getSize(new THREE.Vector3()),center=bounds.getCenter(new THREE.Vector3());
   const geometry=new THREE.BoxGeometry(size.x,size.y,size.z);geometry.translate(center.x,center.y,center.z);
   const color=kind==='selected'?0xffd16b:0x64dcff,fill=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color,transparent:true,opacity:0,depthWrite:false}));
   const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geometry),new THREE.LineBasicMaterial({color,transparent:true,opacity:.8,depthWrite:false}));
   fill.matrixAutoUpdate=edges.matrixAutoUpdate=false;fill.frustumCulled=edges.frustumCulled=false;edges.renderOrder=1001;root.add(fill,edges);slot.items.push({source:object,fill,edges,owned:true});return;
  }
  object.traverse(mesh=>{if(!mesh.isMesh||mesh.userData.surfaceOverlay||mesh.userData.sceneEffectParticle)return;const source=mesh.geometry,materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];let geometry=source,owned=false;
   if(materialName){const groups=source.groups.length?source.groups:[{start:0,count:source.index?.count||source.attributes.position.count,materialIndex:0}],indices=[];for(const g of groups)if((materials[g.materialIndex||0]?.name||'Material sin nombre')===materialName)for(let i=g.start;i<g.start+g.count;i++)indices.push(source.index?source.index.getX(i):i);if(!indices.length)return;geometry=source.clone();geometry.setIndex(indices);geometry.clearGroups();owned=true;}
   const color=kind==='selected'?0xffd16b:0x64dcff,fill=mesh.isSkinnedMesh?new THREE.SkinnedMesh(geometry):new THREE.Mesh(geometry);if(mesh.isSkinnedMesh){fill.skeleton=mesh.skeleton;fill.bindMode=mesh.bindMode;fill.bindMatrix.copy(mesh.bindMatrix);fill.bindMatrixInverse.copy(mesh.bindMatrixInverse);}if(mesh.morphTargetInfluences)fill.morphTargetInfluences=mesh.morphTargetInfluences;fill.material=new THREE.MeshBasicMaterial({color,transparent:true,opacity:kind==='selected'?.21:.13,depthWrite:false,depthTest:true,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-3,polygonOffsetUnits:-3});fill.matrixAutoUpdate=false;fill.frustumCulled=false;fill.renderOrder=1000;
   const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geometry,35),new THREE.LineBasicMaterial({color,transparent:true,opacity:kind==='selected'?.95:.75,depthTest:true,depthWrite:false}));edges.matrixAutoUpdate=false;edges.frustumCulled=false;edges.renderOrder=1001;root.add(fill,edges);slot.items.push({source:mesh,fill,edges,owned});
  });
 }
 function update(){root.visible=enabled;for(const slot of Object.values(slots))for(const item of slot.items){let visible=true,node=item.source;while(node){if(!node.visible){visible=false;break;}node=node.parent;}item.source.updateWorldMatrix(true,false);for(const object of [item.fill,item.edges]){object.visible=visible;object.matrix.copy(item.source.matrixWorld);}}}
 return {show,update,setEnabled(value){enabled=!!value;},clearHover(){clear(slots.hover);},get state(){return {enabled,selectedMeshes:slots.selected.items.length,hoverMeshes:slots.hover.items.length,selectedTriangles:slots.selected.items.reduce((n,item)=>n+(item.fill.geometry.index?.count||item.fill.geometry.attributes.position.count)/3,0)};}};
}
