import * as THREE from 'three';
import {mergeGeometries} from '/assets/vendor/addons/utils/BufferGeometryUtils.js';
export function mergeStaticMeshes(root){
 root.updateMatrixWorld(true);const inverse=new THREE.Matrix4().copy(root.matrixWorld).invert(),geometries=[],materials=[];let count=0;
 try{root.traverse(mesh=>{
  if(!mesh.isMesh)return;let ancestor=mesh;while(ancestor&&ancestor!==root){if(!ancestor.visible)return;ancestor=ancestor.parent;}
  if(mesh.isSkinnedMesh||mesh.isInstancedMesh||Object.keys(mesh.geometry.morphAttributes||{}).length)throw new Error('La fusión admite mallas estáticas, sin esqueletos, instancias ni morphs.');
  const raw=mesh.geometry.index?mesh.geometry.toNonIndexed():mesh.geometry.clone();count+=raw.attributes.position.count;if(count>3000000){raw.dispose();throw new Error('La selección supera el límite de 3 millones de vértices para fusionar.');}
  if(!raw.attributes.normal)raw.computeVertexNormals();const list=Array.isArray(mesh.material)?mesh.material:[mesh.material],groups=raw.groups.length?raw.groups:[{start:0,count:raw.attributes.position.count,materialIndex:0}];
  for(const group of groups){if(!list[group.materialIndex||0])continue;const g=new THREE.BufferGeometry();for(const [name,size] of [['position',3],['normal',3],['uv',2],['color',3]]){const source=raw.getAttribute(name),array=new Float32Array(group.count*size);for(let i=0;i<group.count;i++)for(let j=0;j<size;j++)array[i*size+j]=source?(j===0?source.getX(i+group.start):j===1?source.getY(i+group.start):source.getZ(i+group.start)):(name==='color'?1:0);g.setAttribute(name,new THREE.BufferAttribute(array,size));}g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse,mesh.matrixWorld));geometries.push(g);materials.push(list[group.materialIndex||0]);}raw.dispose();
 });if(!geometries.length)throw new Error('No hay geometría estática visible para fusionar.');const geometry=mergeGeometries(geometries,true);if(!geometry)throw new Error('No se pudieron combinar las geometrías.');const merged=new THREE.Group(),mesh=new THREE.Mesh(geometry,materials);mesh.name='Malla fusionada';merged.add(mesh);return merged;
 }finally{for(const g of geometries)g.dispose();}
}
