'use strict';
// Local, original geometry. Only replaces Kenney flower instances in Gludio Brisas.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=__dirname,lab=path.resolve(root,'../..'),catalog=path.join(root,'../model-catalog');
const out=path.join(catalog,'exports/gludio-botanical');
const targets=['gludiobrisas1','gludiobrisas1-animado'];
const ids={web_kenney_nature_flower_purplea:'custom_gludio_cosmos_lavender',web_kenney_nature_flower_yellowa:'custom_gludio_cosmos_ivory'};
const json=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2));
(async()=>{
 const T=await import(pathToFileURL(path.join(catalog,'vendor/three.module.js')).href);
 function mergeGeometries(list){const result=new T.BufferGeometry();for(const name of ['position','normal','color']){const values=new Float32Array(list.reduce((n,g)=>n+g.attributes[name].array.length,0));let offset=0;for(const geo of list){values.set(geo.attributes[name].array,offset);offset+=geo.attributes[name].array.length;}result.setAttribute(name,new T.BufferAttribute(values,3));}return result;}
 const backup=path.join(lab,'backups/gludio-flores-20261020');
 const files=['data.json','custom-assets.json',...targets.map(n=>'projects/'+n+'.json')].map(f=>path.join(root,f));
 files.push(path.join(catalog,'gallery.json'),...targets.map(n=>path.join(lab,'mapas editados',n,n+'.json')));
 for(const f of files){const dest=path.join(backup,path.relative(lab,f));fs.mkdirSync(path.dirname(dest),{recursive:true});if(!fs.existsSync(dest))fs.copyFileSync(f,dest);}
 fs.mkdirSync(out,{recursive:true});
 const report={projects:[],assets:[],backup:path.relative(lab,backup)};
 for(const [variant,id] of [['lavender',ids.web_kenney_nature_flower_purplea],['ivory',ids.web_kenney_nature_flower_yellowa]]){
  const buckets=[[],[],[]],chunks=[];let length=0;
  const g={asset:{version:'2.0',generator:'L2 Lab original botanical geometry'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'Cosmos '+variant,mesh:0}],meshes:[{primitives:[]}],buffers:[],bufferViews:[],accessors:[],materials:[
   {name:'Petalos satinados '+variant,doubleSided:true,pbrMetallicRoughness:{baseColorFactor:[1,1,1,1],metallicFactor:0,roughnessFactor:.94}},
   {name:'Hojas y tallos mate',doubleSided:true,pbrMetallicRoughness:{baseColorFactor:[1,1,1,1],metallicFactor:0,roughnessFactor:1}},
   {name:'Polen ocre',pbrMetallicRoughness:{baseColorFactor:[1,1,1,1],metallicFactor:0,roughnessFactor:1}}
  ]};
  function add(geo,mat,color){if(geo.index)geo=geo.toNonIndexed();geo.deleteAttribute('uv');if(!geo.attributes.color){const c=new T.Color(color),a=[];for(let i=0;i<geo.attributes.position.count;i++)a.push(c.r,c.g,c.b);geo.setAttribute('color',new T.Float32BufferAttribute(a,3));}buckets[mat].push(geo);}
  function tube(points,r,color){const geo=new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),10,r,5,false);add(geo,1,color);}
  // A thin curled surface, with a cupped cross section and subtle colour veins.
  function blade(len,width,leaf,phase){const positions=[],colors=[],indices=[],rows=9,cols=5;
   const base=new T.Color(leaf?'#263f19':variant==='lavender'?'#67314f':'#c5a053');
   const tip=new T.Color(leaf?'#66824b':variant==='lavender'?'#b990b5':'#f3e7c9');
   for(let i=0;i<=rows;i++){const t=i/rows;for(let j=0;j<=cols;j++){const u=j/cols*2-1;
    const w=width*Math.pow(Math.sin(Math.PI*t*(leaf?1:.85)),leaf?.85:.55)*(leaf?1:Math.min(1,t*2.5))*(.96+.04*Math.sin(t*19+phase));
    positions.push(t*len*(leaf?1:1-.12*t*t*u*u),.006*Math.sin(t*Math.PI)*u*u+(leaf?.012:.008)*t*t+.0005*Math.sin(t*20+phase)*(1-u*u),u*w);
    const c=base.clone().lerp(tip,Math.min(1,t*.95+.06*Math.cos(u*19+t*6+phase)));c.multiplyScalar(1-.07*Math.abs(u));colors.push(c.r,c.g,c.b);
    if(i<rows&&j<cols){const a=i*(cols+1)+j,b=a+cols+1;indices.push(a,b,a+1,b,b+1,a+1);}
   }}const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(positions,3));geo.setAttribute('color',new T.Float32BufferAttribute(colors,3));geo.setIndex(indices);geo.computeVertexNormals();return geo;}
  const blooms=[{x:0,z:0,h:.187,r:.050,tilt:.17},{x:-.043,z:.024,h:.140,r:.038,tilt:-.25},{x:.042,z:-.021,h:.157,r:.041,tilt:.30}];
  blooms.forEach((b,k)=>{
   tube([[b.x*.2,0,b.z*.2],[b.x*.5,b.h*.48,b.z*.75],[b.x,b.h,b.z]],.0018,'#38562a');
   for(let l=0;l<4;l++){const t=.24+l*.14,a=l*2.4+k;const geo=blade(.040,.008,true,l);geo.rotateX(.25);geo.rotateZ(.35);geo.rotateY(a);geo.translate(b.x*t,b.h*t,b.z*t);add(geo,1);}
   const q=new T.Quaternion().setFromEuler(new T.Euler(b.tilt,k*.7,b.tilt*.5));
   function place(geo,mat,color){geo.applyQuaternion(q);geo.translate(b.x,b.h,b.z);add(geo,mat,color);}
   for(let layer=0;layer<2;layer++)for(let p=0;p<9;p++){
    const geo=blade(b.r*(layer?.70:1),b.r*.31,false,p+k);geo.rotateY(p*Math.PI*2/9+layer*.31);geo.translate(0,layer*.009,0);place(geo,0);
   }
   const center=new T.SphereGeometry(.010,12,6);center.scale(1,.48,1);center.translate(0,.010,0);place(center,2,'#9a6a26');
   for(let p=0;p<24;p++){const a=p*2.39996,r=.0088*Math.sqrt((p+.5)/24),geo=new T.SphereGeometry(.00125,4,3);geo.scale(1,1.8,1);geo.translate(Math.cos(a)*r,.014+Math.sqrt(1-(r/.010)**2)*.002,Math.sin(a)*r);place(geo,2,p%3?'#d0a344':'#a97b27');}
   // Small green sepals under the flower head.
   for(let p=0;p<5;p++){const geo=blade(.016,.0035,true,p);geo.rotateZ(-.45);geo.rotateY(p*Math.PI*2/5);geo.translate(0,-.004,0);place(geo,1);}
  });
  function accessor(a){const pad=(4-length%4)%4;if(pad){chunks.push(Buffer.alloc(pad));length+=pad;}const b=Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength),view=g.bufferViews.length;g.bufferViews.push({buffer:0,byteOffset:length,byteLength:b.length});chunks.push(b);length+=b.length;const v={bufferView:view,componentType:5126,count:a.count,type:'VEC3'};if(a===currentPosition){const box=new T.Box3().setFromBufferAttribute(a);v.min=box.min.toArray();v.max=box.max.toArray();}g.accessors.push(v);return g.accessors.length-1;}
  let currentPosition,triangles=0,bounds;
  for(let m=0;m<buckets.length;m++){const geo=mergeGeometries(buckets[m]);currentPosition=geo.attributes.position;const attrs={};for(const [name,attr] of Object.entries(geo.attributes))attrs[{position:'POSITION',normal:'NORMAL',color:'COLOR_0'}[name]]=accessor(attr);g.meshes[0].primitives.push({attributes:attrs,material:m});triangles+=currentPosition.count/3;geo.computeBoundingBox();bounds=bounds?bounds.union(geo.boundingBox):geo.boundingBox.clone();}
  g.buffers=[{uri:variant+'.bin',byteLength:length}];write(path.join(out,variant+'.gltf'),g);fs.writeFileSync(path.join(out,variant+'.bin'),Buffer.concat(chunks));
  report.assets.push({id,variant,triangles,bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()}});
 }
 const assets=report.assets.map(a=>({id:a.id,title:a.variant==='lavender'?'Cosmos lavanda · pétalos finos':'Cosmos crema · centro dorado',path:'exports/gludio-botanical/'+a.variant+'.gltf',thumbnail:'thumbs/'+a.id+'.png',mesh:'Cosmos '+a.variant,category:'Vegetación',native:false,batch:'Gludio · Flores botánicas'}));
 for(const file of ['data.json','custom-assets.json']){const f=path.join(root,file),v=json(f),list=Array.isArray(v)?v:v.assets;for(const a of assets){const i=list.findIndex(x=>x.id===a.id);if(i>=0)list[i]=a;else list.push(a);}write(f,v);}
 const gf=path.join(catalog,'gallery.json'),gallery=json(gf);for(const a of assets){const m={key:a.id,title:a.title,gltf:a.path,thumbnail:a.thumbnail,mesh:a.mesh,category:a.category,native:false,batch:a.batch,status:'ready',names:[],types:['StaticMesh']};gallery.models=gallery.models.filter(x=>x.key!==a.id);gallery.models.push(m);}write(gf,gallery);
 for(const name of targets)for(const f of [path.join(root,'projects',name+'.json'),path.join(lab,'mapas editados',name,name+'.json')]){
  const p=json(f);let count=0;for(const o of p.objects){if(!ids[o.asset])continue;o.asset=ids[o.asset];count++;}
  if(count){write(f,p);}report.projects.push({file:path.relative(lab,f),replaced:count,botanical:p.objects.filter(o=>Object.values(ids).includes(o.asset)).length});
 }
 write(path.join(out,'manifest.json'),report);console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
