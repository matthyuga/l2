'use strict';
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=__dirname,lab=path.resolve(root,'../..'),cat=path.resolve(root,'../model-catalog'),out=path.join(cat,'exports/gludio-carved-bench');
const id='custom_gludio_brisas_carved_bench';
const selected=['dfe8dd19-a1f3-4074-868e-304f82c21dcc','134fd162-e6e5-49e6-aa0b-8150524a94d0'];
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2));
(async()=>{
 const T=await import(pathToFileURL(path.join(cat,'vendor/three.module.js')).href);
 const backup=path.join(lab,'backups/gludio-bancos-pergolas-20261020');
 const files=['app.js','data.json','custom-assets.json',...['gludiobrisas1','gludiobrisas1-animado'].map(n=>'projects/'+n+'.json')].map(f=>path.join(root,f));
 files.push(path.join(cat,'gallery.json'),...['gludiobrisas1','gludiobrisas1-animado'].map(n=>path.join(lab,'mapas editados',n,n+'.json')));
 for(const f of files){const dest=path.join(backup,path.relative(lab,f));fs.mkdirSync(path.dirname(dest),{recursive:true});if(!fs.existsSync(dest))fs.copyFileSync(f,dest);}
 fs.mkdirSync(out,{recursive:true});
 const g={asset:{version:'2.0',generator:'L2 Lab original carved bench'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'Banco',children:[]}],meshes:[],materials:[],images:[],textures:[],samplers:[{wrapS:10497,wrapT:10497,magFilter:9729,minFilter:9987}],buffers:[],bufferViews:[],accessors:[]};
 const chunks=[];let length=0,triangles=0;
 function mat(name,color,metal=0,rough=.7,texture){const m={name,pbrMetallicRoughness:{baseColorFactor:[...new T.Color(color).toArray(),1],metallicFactor:metal,roughnessFactor:rough}};if(texture){g.images.push({uri:path.relative(out,path.join(cat,texture)).replaceAll('\\','/')});g.textures.push({source:g.images.length-1,sampler:0});m.pbrMetallicRoughness.baseColorTexture={index:g.textures.length-1};}g.materials.push(m);return g.materials.length-1;}
 const wood=mat('Nogal tallado','#98724e',0,.78,'exports/scene-giran-city/Giran_wood.png'),edge=mat('Relieve de madera miel','#86552f',0,.65,'exports/scene-giran-city/Giran_wood.png'),bronze=mat('Bronce antiguo','#b19250',.72,.42),dark=mat('Bronce de las hendiduras','#4c492d',.65,.65),gem=mat('Turquesa tallada','#44c6ba',.22,.19);
 function accessor(a,position=false){const pad=(4-length%4)%4;if(pad){chunks.push(Buffer.alloc(pad));length+=pad;}const b=Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength),view=g.bufferViews.length;g.bufferViews.push({buffer:0,byteOffset:length,byteLength:b.length});chunks.push(b);length+=b.length;const v={bufferView:view,componentType:a.array instanceof Uint32Array?5125:a.array instanceof Uint16Array?5123:5126,count:a.count,type:{1:'SCALAR',2:'VEC2',3:'VEC3'}[a.itemSize]};if(position){const box=new T.Box3().setFromBufferAttribute(a);v.min=box.min.toArray();v.max=box.max.toArray();}g.accessors.push(v);return g.accessors.length-1;}
 const bounds=new T.Box3();
 function part(name,geo,m,pos=[0,0,0],rot=[0,0,0]){geo.applyMatrix4(new T.Matrix4().makeRotationFromEuler(new T.Euler(...rot)));geo.translate(...pos);geo.computeBoundingBox();bounds.union(geo.boundingBox);const attrs={};for(const [k,v] of Object.entries(geo.attributes)){const dest={position:'POSITION',normal:'NORMAL',uv:'TEXCOORD_0'}[k];if(dest)attrs[dest]=accessor(v,k==='position');}const primitive={attributes:attrs,material:m};if(geo.index)primitive.indices=accessor(geo.index);triangles+=(geo.index?.count||geo.attributes.position.count)/3;const mesh=g.meshes.length;g.meshes.push({primitives:[primitive]});g.nodes[0].children.push(g.nodes.length);g.nodes.push({name,mesh});}
 function extrude(shape,depth,bevel=.012){const geo=new T.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSize:bevel,bevelThickness:bevel,bevelSegments:3,curveSegments:18,steps:1});geo.translate(0,0,-depth/2);return geo;}
 function rounded(w,h,r){const s=new T.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;}
 function rail(name,w,h,d,m,pos){part(name,extrude(rounded(w,h,Math.min(h/3,.028)),d,.009),m,pos);}
 function vine(name,points,r,m){part(name,new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),40,r,8,false),m);}
 function jewel(name,x,y,z,size){const s=new T.Shape();s.moveTo(0,size*1.2);s.bezierCurveTo(-size*.25,size*.7,-size*.85,0,-size*.65,-size*.42);s.bezierCurveTo(-size*.4,-size, size*.4,-size,size*.65,-size*.42);s.bezierCurveTo(size*.85,0,size*.25,size*.7,0,size*1.2);part(name+' engaste',extrude(s,.025,.010),bronze,[x,y,z]);const geo=extrude(s,.032,.009);geo.scale(.75,.75,1);part(name+' turquesa',geo,gem,[x,y,z+.022]);}
 // Curved, individually edged seat boards; front is +Z.
 for(let i=0;i<6;i++)rail('Tabla de nogal con canto redondeado',2.14,.063,.085,wood,[0,.505+Math.pow((i-2.5)/2.5,2)*.012,-.235+i*.097]);
 rail('Faldon frontal tallado',2.20,.13,.070,wood,[0,.408,.326]);
 for(const y of [.366,.454])rail('Filete de bronce del faldon',2.12,.009,.008,bronze,[0,y,.367]);
 for(const x of [-.84,.84])for(const z of [-.235,.255]){
  const profile=[[.055,0],[.068,.025],[.062,.055],[.038,.10],[.042,.20],[.061,.28],[.048,.36],[.065,.43]].map(p=>new T.Vector2(...p));
  part('Pata torneada',new T.LatheGeometry(profile,20),wood,[x,0,z]);
  for(const y of [.045,.28,.40])part('Collarin de bronce',new T.TorusGeometry(y===.28?.060:.062,.009,6,20),bronze,[x,y,z],[Math.PI/2,0,0]);
 }
 rail('Travesano bajo el asiento',1.73,.07,.07,wood,[0,.25,-.22]);
 // Shaped posts and a three-lobed carved crown, with an openwork back.
 for(const sign of [-1,1]){
  vine('Montante curvo de nogal',[[sign*.99,.44,-.27],[sign*1.04,.78,-.29],[sign*1.02,1.05,-.34],[sign*.91,1.21,-.36]],.055,wood);
  jewel('Remate lateral',sign*.99,1.05,-.283,.055);
 }
 const crown=new T.Shape();crown.moveTo(-1.03,1.04);crown.bezierCurveTo(-.97,1.32,-.72,1.31,-.54,1.24);crown.bezierCurveTo(-.30,1.18,-.22,1.47,0,1.48);crown.bezierCurveTo(.22,1.47,.30,1.18,.54,1.24);crown.bezierCurveTo(.72,1.31,.97,1.32,1.03,1.04);crown.lineTo(.98,.995);crown.bezierCurveTo(.85,1.19,.68,1.20,.51,1.15);crown.bezierCurveTo(.24,1.08,.18,1.37,0,1.38);crown.bezierCurveTo(-.18,1.37,-.24,1.08,-.51,1.15);crown.bezierCurveTo(-.68,1.20,-.85,1.19,-.98,.995);crown.closePath();part('Couronnement de bois sculpte',extrude(crown,.08,.016),edge,[0,0,-.34]);
 rail('Traverse basse du dossier',2.02,.105,.09,wood,[0,.68,-.29]);
 for(const sign of [-1,1]){
  vine('Volute vegetale du dossier',[[sign*.91,.73,-.29],[sign*.68,.77,-.31],[sign*.40,1.02,-.33],[sign*.48,1.17,-.34],[sign*.71,1.11,-.34],[sign*.74,.95,-.32],[sign*.59,.92,-.31],[sign*.55,1.01,-.32]],.031,edge);
  vine('Rameau interieur du dossier',[[sign*.09,.72,-.28],[sign*.20,.85,-.30],[sign*.34,.93,-.31],[sign*.32,1.06,-.33],[sign*.21,1.07,-.33]],.024,wood);
  vine('Nervure de bronze',[[sign*.91,.73,-.253],[sign*.68,.77,-.273],[sign*.40,1.02,-.293],[sign*.48,1.17,-.303],[sign*.71,1.11,-.303]],.006,bronze);
  // Rolled armrests sweep forward, ending in a carved scroll.
  vine('Accoudoir en crosse',[[sign*.99,.92,-.28],[sign*1.08,.84,-.04],[sign*1.09,.79,.23],[sign*1.07,.75,.35],[sign*1.04,.67,.34],[sign*1.04,.65,.25],[sign*1.04,.71,.22]],.043,edge);
  vine('Support ajoure de l accoudoir',[[sign*.86,.43,.24],[sign*.93,.58,.13],[sign*1.05,.70,.18]],.027,wood);
  jewel('Gemme de l accoudoir',sign*1.08,.77,.278,.033);
  for(let i=0;i<4;i++){
   const x=sign*(.28+i*.165),y=.80+Math.sin(i*.9)*.10;
   const leaf=new T.Shape();leaf.moveTo(0,0);leaf.bezierCurveTo(-.06,.035,-.045,.10,0,.13);leaf.bezierCurveTo(.045,.10,.06,.035,0,0);part('Feuille sculptee',extrude(leaf,.015,.004),edge,[x,y,-.281],[0,0,sign*(-.6+i*.15)]);
  }
 }
 // Central crest, raised turquoise cabochon and a small gold setting.
 rail('Nervio de soporte del blason',.065,.72,.065,wood,[0,1.03,-.34]);
 const crest=new T.Shape();crest.moveTo(0,.80);crest.bezierCurveTo(-.15,.91,-.18,1.10,0,1.35);crest.bezierCurveTo(.18,1.10,.15,.91,0,.80);part('Blason central sculpte',extrude(crest,.065,.012),wood,[0,0,-.285]);
 jewel('Gemme centrale',0,1.085,-.22,.095);
 for(const x of [-.93,.93])for(const y of [.68,1.04])part('Clou de bronze',new T.SphereGeometry(.014,10,6),bronze,[x,y,-.225]);
 g.buffers=[{uri:'bench.bin',byteLength:length}];write(path.join(out,'bench.gltf'),g);fs.writeFileSync(path.join(out,'bench.bin'),Buffer.concat(chunks));
 const asset={id,title:'Banco de las Brisas · nogal tallado y turquesas',path:'exports/gludio-carved-bench/bench.gltf',thumbnail:null,mesh:'Banco',category:'Objetos',native:false,batch:'Gludio · Mobiliario tallado'};
 for(const file of ['data.json','custom-assets.json']){const f=path.join(root,file),v=read(f),list=Array.isArray(v)?v:v.assets;const i=list.findIndex(a=>a.id===id);if(i>=0)list[i]=asset;else list.push(asset);write(f,v);}
 const gf=path.join(cat,'gallery.json'),gallery=read(gf);gallery.models=gallery.models.filter(m=>m.key!==id);gallery.models.push({key:id,title:asset.title,gltf:asset.path,thumbnail:null,mesh:'Banco',category:asset.category,native:false,batch:asset.batch,status:'ready',names:[],types:['StaticMesh']});write(gf,gallery);
 const projects=[];
 for(const name of ['gludiobrisas1','gludiobrisas1-animado'])for(const file of [path.join(root,'projects',name+'.json'),path.join(lab,'mapas editados',name,name+'.json')]){const p=read(file),benches=p.objects.filter(o=>selected.includes(o.id));if(benches.length!==2)throw Error('Expected exactly two pergola benches');for(const o of benches){if(o.asset!=='custom_gludio_brisas_decor'&&o.asset!==id)throw Error('Unexpected asset');o.asset=id;}write(file,p);projects.push(path.relative(lab,file));}
 const report={id,selected,triangles,parts:g.nodes.length-1,bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()},projects,backup:path.relative(lab,backup),inspiration:'Original geometry inspired by carved fantasy furniture; no third party model copied.'};write(path.join(out,'manifest.json'),report);console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
