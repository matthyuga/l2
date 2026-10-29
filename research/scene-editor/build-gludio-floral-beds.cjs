'use strict';
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=__dirname,lab=path.resolve(root,'../..'),cat=path.resolve(root,'../model-catalog'),out=path.join(cat,'exports/gludio-floral-beds');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2));
(async()=>{
 const T=await import(pathToFileURL(path.join(cat,'vendor/three.module.js')).href);
 const backup=path.join(lab,'backups/gludio-arbustos-florales-20261020'),names=['gludiobrisas1','gludiobrisas1-animado'];
 const files=['app.js','data.json','custom-assets.json',...names.map(n=>'projects/'+n+'.json')].map(f=>path.join(root,f));files.push(path.join(cat,'gallery.json'),...names.map(n=>path.join(lab,'mapas editados',n,n+'.json')));
 for(const f of files){const dest=path.join(backup,path.relative(lab,f));fs.mkdirSync(path.dirname(dest),{recursive:true});if(!fs.existsSync(dest))fs.copyFileSync(f,dest);}
 const p=read(path.join(root,'projects/gludiobrisas1.json')),slots=p.objects.filter(o=>o.name==='Flores del arriate').map(o=>o.id);if(slots.length!==16)throw Error('Expected 16 bed plants');
 fs.mkdirSync(out,{recursive:true});const assets=[],statistics=[];
 for(let variant=0;variant<4;variant++){
  let seed=8723+variant*391;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const buckets=[[],[],[],[],[]],chunks=[];let length=0;
  const g={asset:{version:'2.0',generator:'L2 Lab original mixed floral underplanting'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'Mata floral mixta '+(variant+1),mesh:0}],meshes:[{primitives:[]}],materials:['Hojas nervadas mate','Margaritas marfil','Rosetas rosa empolvado','Espigas azul lavanda','Polen ocre'].map(name=>({name,doubleSided:true,pbrMetallicRoughness:{baseColorFactor:[1,1,1,1],metallicFactor:0,roughnessFactor:.95}})),buffers:[],bufferViews:[],accessors:[]};
  function add(geo,mat,color){if(geo.index)geo=geo.toNonIndexed();geo.deleteAttribute('uv');if(!geo.attributes.color){const c=new T.Color(color),a=[];for(let i=0;i<geo.attributes.position.count;i++)a.push(c.r,c.g,c.b);geo.setAttribute('color',new T.Float32BufferAttribute(a,3));}buckets[mat].push(geo);}
  function tube(points,r=.0014){add(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),7,r,5,false),0,'#49613b');}
  function surface(len,width,leaf,from,to,phase=0){const pos=[],colors=[],ix=[],rows=7,cols=4,a=new T.Color(from),b=new T.Color(to);
   for(let i=0;i<=rows;i++){const t=i/rows;for(let j=0;j<=cols;j++){const u=2*j/cols-1,w=width*Math.pow(Math.sin(Math.PI*t*(leaf?1:.86)),leaf?.85:.55)*(leaf?1:Math.min(1,t*2.5));
    pos.push(t*len*(leaf?1:1-.10*t*t*u*u),len*(.10*Math.sin(Math.PI*t)*(1-u*u)+(leaf?.14:.12)*t*t)+len*.008*Math.sin(t*28+phase)*(1-u*u),w*u);
    const c=a.clone().lerp(b,.15+t*.7).multiplyScalar(1-.13*Math.abs(u)+.04*Math.cos(t*24+u*8));colors.push(c.r,c.g,c.b);
    if(i<rows&&j<cols){const k=i*(cols+1)+j;ix.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
   }}const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('color',new T.Float32BufferAttribute(colors,3));geo.setIndex(ix);geo.computeVertexNormals();return geo;}
  function leaf(x,y,z,len,angle,tilt){const geo=surface(len,len*(.22+rnd()*.12),true,['#203e2b','#2b4728','#344d2d'][Math.floor(rnd()*3)],'#557747',rnd()*6);geo.rotateZ(tilt);geo.rotateY(angle);geo.translate(x,y,z);add(geo,0);}
  // A low branching mound; individual leaf blades replace solid foliage blobs.
  for(let i=0;i<27;i++){
   const a=i*2.39996+variant*.8,r=.078*Math.sqrt((i+.4)/27),x=Math.cos(a)*r,z=Math.sin(a)*r,h=.045+rnd()*.055;
   tube([[x*.35,0,z*.35],[x*.7,h*.5,z*.7],[x,h,z]]);
   for(let j=0;j<6;j++){const t=.28+j*.125;leaf(x*t,h*t,z*t,.042+rnd()*.027,a+j*2.1,-.10+rnd()*.65);}
   leaf(x,h,z,.043+rnd()*.017,a,.08);
  }
  function bloom(x,y,z,r,type,k){const q=new T.Quaternion().setFromEuler(new T.Euler((rnd()-.5)*.8,rnd()*6.28,(rnd()-.5)*.7));
   function place(geo,mat,color){geo.applyQuaternion(q);geo.translate(x,y,z);add(geo,mat,color);}
   const layers=type===2?3:1,petals=type===2?7:11;
   for(let l=0;l<layers;l++)for(let j=0;j<petals;j++){
    const geo=surface(r*(1-l*.23),r*(type===2?.47:.17),false,type===2?'#a95778':'#cfbd8f',type===2?'#e2b0c3':'#f0ead9',k+j);
    geo.rotateY(j*Math.PI*2/petals+l*.42);geo.translate(0,l*.004,0);place(geo,type);
   }
   const center=new T.SphereGeometry(r*.20,8,4);center.scale(1,.6,1);center.translate(0,type===2?.011:.003,0);place(center,4,'#c39b47');
   for(let j=0;j<7;j++){const a=j*2.39996,rr=r*.13*Math.sqrt((j+.5)/7),g=new T.SphereGeometry(r*.035,4,3);g.translate(Math.cos(a)*rr,type===2?.014:.006,Math.sin(a)*rr);place(g,4,'#e0ba57');}
  }
  // Daisies and layered rosettes differ in silhouette, height and petal structure.
  const blooms=variant%2?10:12;
  for(let i=0;i<blooms;i++){
   const a=i*2.39996+variant*.9,r=.080*Math.sqrt((i+.5)/blooms),x=Math.cos(a)*r,z=Math.sin(a)*r,h=.094+rnd()*.067,type=(i+variant)%3===0?2:1;
   tube([[x*.75,.028,z*.75],[x*.9,h*.66,z*.95],[x,h,z]]);leaf(x*.9,h*.55,z*.9,.035,a+1,.2);bloom(x,h,z,(type===2?.021:.024)*( .8+rnd()*.4),type,i);
  }
  // Taller blue-lavender spires carry multiple small bell flowers.
  for(let i=0;i<4;i++){
   const a=i*Math.PI/2+variant*.65,x=Math.cos(a)*.065,z=Math.sin(a)*.065,h=.175+rnd()*.025;
   tube([[x*.6,.015,z*.6],[x*.85,.12,z*.85],[x,h,z]],.0012);
   for(let j=0;j<7;j++){
    const angle=j*2.4,yy=h-.055+j*.007,xx=x+Math.cos(angle)*.007,zz=z+Math.sin(angle)*.007;
    const positions=[],indices=[],rings=5,segments=12;
    for(let v=0;v<=rings;v++)for(let u=0;u<=segments;u++){const t=v/rings,a=u/segments*Math.PI*2,r=.002+.004*Math.pow(1-t,2);positions.push(Math.cos(a)*r,(t-.5)*.010+(v===0?.001*Math.cos(a*5):0),Math.sin(a)*r);if(v<rings&&u<segments){const k=v*(segments+1)+u;indices.push(k,k+1,k+segments+1,k+1,k+segments+2,k+segments+1);}}
    const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(positions,3));geo.setIndex(indices);geo.computeVertexNormals();geo.rotateZ(.6);geo.rotateY(angle);geo.translate(xx,yy,zz);add(geo,3,j%2?'#aaa0ca':'#827bad');
   }
  }
  function accessor(a,position=false){const pad=(4-length%4)%4;if(pad){chunks.push(Buffer.alloc(pad));length+=pad;}const b=Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength),view=g.bufferViews.length;g.bufferViews.push({buffer:0,byteOffset:length,byteLength:b.length});chunks.push(b);length+=b.length;const v={bufferView:view,componentType:5126,count:a.count,type:'VEC3'};if(position){const box=new T.Box3().setFromBufferAttribute(a);v.min=box.min.toArray();v.max=box.max.toArray();}g.accessors.push(v);return g.accessors.length-1;}
  let triangles=0;const bounds=new T.Box3();
  for(let m=0;m<buckets.length;m++){const geo=new T.BufferGeometry();for(const name of ['position','normal','color']){const values=new Float32Array(buckets[m].reduce((n,g)=>n+g.attributes[name].array.length,0));let offset=0;for(const source of buckets[m]){values.set(source.attributes[name].array,offset);offset+=source.attributes[name].array.length;}geo.setAttribute(name,new T.BufferAttribute(values,3));}geo.scale(1.28,1,1.28);geo.computeBoundingBox();bounds.union(geo.boundingBox);const attrs={};for(const [name,a] of Object.entries(geo.attributes))attrs[{position:'POSITION',normal:'NORMAL',color:'COLOR_0'}[name]]=accessor(a,name==='position');g.meshes[0].primitives.push({attributes:attrs,material:m});triangles+=geo.attributes.position.count/3;}
  g.buffers=[{uri:'mixed-'+variant+'.bin',byteLength:length}];write(path.join(out,'mixed-'+variant+'.gltf'),g);fs.writeFileSync(path.join(out,'mixed-'+variant+'.bin'),Buffer.concat(chunks));
  const id='custom_gludio_flower_shrub_'+variant,bedObjectIds=slots.filter((_,i)=>(i+Math.floor(i/8))%4===variant);
  assets.push({id,title:'Mata floral mixta '+(variant+1)+' · margaritas, rosetas y espigas',path:'exports/gludio-floral-beds/mixed-'+variant+'.gltf',thumbnail:null,mesh:g.nodes[0].name,category:'Vegetación',native:false,batch:'Gludio · Arriates florales',bedObjectIds});statistics.push({id,triangles,foliageBranches:27,leaves:193,blooms,flowerTypes:3,bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()}});
 }
 for(const f of ['data.json','custom-assets.json']){const file=path.join(root,f),v=read(file),list=Array.isArray(v)?v:v.assets;for(const a of assets){const i=list.findIndex(x=>x.id===a.id);if(i>=0)list[i]=a;else list.push(a);}write(file,v);}
 const gf=path.join(cat,'gallery.json'),gallery=read(gf);for(const a of assets){gallery.models=gallery.models.filter(x=>x.key!==a.id);gallery.models.push({key:a.id,title:a.title,gltf:a.path,thumbnail:a.thumbnail,mesh:a.mesh,category:a.category,batch:a.batch,native:false,status:'ready',names:[],types:['StaticMesh']});}write(gf,gallery);
 const projects=[];for(const name of names)for(const file of [path.join(root,'projects',name+'.json'),path.join(lab,'mapas editados',name,name+'.json')]){const p=read(file);let count=0;for(const o of p.objects){const a=assets.find(a=>a.bedObjectIds.includes(o.id));if(a){o.asset=a.id;count++;}}if(count!==16)throw Error('Missing bed instances');write(file,p);projects.push({file:path.relative(lab,file),changed:count});}
 const report={statistics,projects,assignments:Object.fromEntries(assets.flatMap(a=>a.bedObjectIds.map(id=>[id,a.id]))),backup:path.relative(lab,backup)};write(path.join(out,'manifest.json'),report);console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
