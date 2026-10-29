// Shared by the browser and Node 24: validate persisted hierarchy, parts and merge recipes.
import {validEffect} from './effect-schema.js';
export function validStructure(objects,{assetIds,validSurfaces}){
 if(!Array.isArray(objects)||objects.length>4000)return false;let budget=10000;
 const vec=(v,scale=false)=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<1e7&&(!scale||n>=.001));
 const transforms=o=>vec(o.position)&&vec(o.rotation)&&vec(o.scale,true);
 function model(o,depth=0){if(--budget<0||depth>6||!o||typeof o.id!=='string'||o.id.length>100||typeof o.name!=='string'||o.name.length>200||!assetIds.has(o.asset)||typeof o.node!=='string'||o.node.length>200||!['base','visible','locked'].every(k=>typeof o[k]==='boolean')||!transforms(o)||!validSurfaces(o.surfaces))return false;
  if(o.kind!==undefined&&!['model','group','merged','effect'].includes(o.kind))return false;if(o.parent!==undefined&&o.parent!==null&&(typeof o.parent!=='string'||o.parent.length>100))return false;
  if(o.kind==='effect'){if(!validEffect(o.effect)||o.base||o.parts?.length||o.surfaces?.length)return false;}else if(o.effect!==undefined)return false;
  if(o.parts!==undefined&&(!Array.isArray(o.parts)||o.parts.length>2000||new Set(o.parts.map(p=>p?.path)).size!==o.parts.length||!o.parts.every(p=>p&&typeof p.path==='string'&&/^(\d{1,5})(\/\d{1,5}){0,29}$/.test(p.path)&&typeof p.name==='string'&&p.name.length<=200&&typeof p.visible==='boolean'&&typeof p.locked==='boolean'&&transforms(p)&&validSurfaces(p.surfaces))))return false;
  if(o.kind==='merged'){if(!Array.isArray(o.components)||o.components.length<2||o.components.length>2000||!o.components.every(c=>c&&c.kind!=='group'&&c.kind!=='effect'&&!c.parent&&model(c,depth+1)))return false;}
  else if(o.components!==undefined)return false;
  return true;
 }
 if(!objects.every(o=>model(o)))return false;const byId=new Map(objects.map(o=>[o.id,o]));if(byId.size!==objects.length)return false;
 for(const o of objects){let current=o;const seen=new Set([o.id]);while(current.parent){const parent=byId.get(current.parent);if(!parent||parent.kind!=='group'||seen.has(parent.id))return false;seen.add(parent.id);current=parent;}}
 return true;
}
