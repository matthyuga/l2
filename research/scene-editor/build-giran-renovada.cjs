'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{pathToFileURL}=require('url');
const catalog=path.resolve(__dirname,'../model-catalog'),out=path.join(catalog,'exports/giran-renovada');
const basePath=path.join(__dirname,'projects/giranmodificado1.json');
if(fs.existsSync(path.join(__dirname,'projects/giranrenovada1.json'))&&!process.argv.includes('--rebuild'))throw Error('Project exists. Edit in the workshop; --rebuild explicitly replaces the generated version.');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{
 const THREE=await import(pathToFileURL(path.join(catalog,'vendor/three.module.js')).href);
 fs.mkdirSync(out,{recursive:true});
 const originalHash=sha(basePath),mapFile=path.join(catalog,'exports/scene-giran-city/scene.gltf'),mapHash=sha(mapFile);
 const original=JSON.parse(fs.readFileSync(mapFile)),city=structuredClone(original);
 for(const ref of [...city.buffers,...city.images])if(ref.uri)ref.uri='../scene-giran-city/'+ref.uri;
 city.images.push({uri:'../cc0-textures/ambientcg/RoofingTiles005/RoofingTiles005_2K-JPG_Color.jpg'});
 city.textures.push({source:city.images.length-1,sampler:0});const slate=city.textures.length-1;
 let roofs=0,leaves=0;
 for(const material of city.materials){const p=material.pbrMetallicRoughness;
  if(/Giran_roof/i.test(material.name)){p.baseColorTexture={index:slate};p.baseColorFactor=[.82,.90,1,1];p.roughnessFactor=.88;roofs++;}
  if(/leaf|leaves/i.test(material.name)){p.baseColorFactor=[.54,.82,.47,1];leaves++;}
  if(/WaterShader01/.test(material.name)){p.baseColorFactor=[.035,.22,.29,1];p.roughnessFactor=.22;}
 }
 fs.writeFileSync(path.join(out,'city.gltf'),JSON.stringify(city));

 // Textured furniture made from ordinary geometry; all materials already local.
 const kit={asset:{version:'2.0',generator:'L2 Lab - Giran renovada'},scene:0,scenes:[{nodes:[]}],nodes:[],meshes:[],materials:[],images:[],textures:[],samplers:[{wrapS:10497,wrapT:10497,magFilter:9729,minFilter:9987}],buffers:[],bufferViews:[],accessors:[]};
 const chunks=[];let byteLength=0;const meshCache=new Map();
 function accessor(array,components,type){const padding=(4-byteLength%4)%4;if(padding){chunks.push(Buffer.alloc(padding));byteLength+=padding;}const b=Buffer.from(array.buffer,array.byteOffset,array.byteLength),view=kit.bufferViews.length;kit.bufferViews.push({buffer:0,byteOffset:byteLength,byteLength:b.length});chunks.push(b);byteLength+=b.length;const a={bufferView:view,componentType:array instanceof Uint32Array?5125:array instanceof Uint16Array?5123:5126,count:array.length/components,type};if(type==='VEC3'){a.min=[Infinity,Infinity,Infinity];a.max=[-Infinity,-Infinity,-Infinity];for(let i=0;i<array.length;i++) {const k=i%3;a.min[k]=Math.min(a.min[k],array[i]);a.max[k]=Math.max(a.max[k],array[i]);}}kit.accessors.push(a);return kit.accessors.length-1;}
 function material(name,color,texture,extra={}){const p={baseColorFactor:[...color,1],metallicFactor:0,roughnessFactor:.86};if(texture){kit.images.push({uri:path.relative(out,path.join(catalog,texture)).replaceAll('\\','/')});kit.textures.push({source:kit.images.length-1,sampler:0});p.baseColorTexture={index:kit.textures.length-1};}kit.materials.push({name,doubleSided:true,pbrMetallicRoughness:p,...extra});return kit.materials.length-1;}
 const stone=material('Piedra clara restaurada',[.46,.44,.37],'exports/cc0-textures/ambientcg/Marble001/Marble001_2K-JPG_Color.jpg');
 const wood=material('Madera de Giran',[.72,.57,.37],'exports/scene-giran-city/Giran_wood.png');
 const iron=material('Hierro azulado',[.028,.045,.052]);
 const gold=material('Bronce envejecido',[.42,.26,.075]);kit.materials[gold].pbrMetallicRoughness.metallicFactor=.65;
 const soil=material('Tierra de jardinera',[.16,.13,.08],'exports/cc0-textures/ambientcg/Ground004/Ground004_2K-JPG_Color.jpg');
 const cloth=material('Azul de la ciudad',[.024,.12,.19],'exports/cc0-textures/ambientcg/Fabric001/Fabric001_2K-JPG_Color.jpg');
 const glass=material('Vidrio ambar',[.85,.49,.15],null,{emissiveFactor:[.5,.22,.045]});
 const water=material('Agua de fuente',[.025,.20,.24],null);kit.materials[water].pbrMetallicRoughness.roughnessFactor=.18;
 const grass=material('Cesped de patio',[.30,.34,.26],'exports/cc0-textures/ambientcg/Grass005/Grass005_2K-JPG_Color.jpg');
 function mesh(geometry,mat){const key=geometry.type+JSON.stringify(geometry.parameters)+'/'+mat;if(meshCache.has(key))return meshCache.get(key);const attrs={};for(const [name,value]of Object.entries(geometry.attributes)){const target={position:'POSITION',normal:'NORMAL',uv:'TEXCOORD_0'}[name];if(target)attrs[target]=accessor(value.array,value.itemSize,value.itemSize===2?'VEC2':'VEC3');}const primitive={attributes:attrs,material:mat};if(geometry.index)primitive.indices=accessor(geometry.index.array,1,'SCALAR');kit.meshes.push({primitives:[primitive]});const id=kit.meshes.length-1;meshCache.set(key,id);return id;}
 function group(name){const id=kit.nodes.length;kit.nodes.push({name,children:[]});kit.scenes[0].nodes.push(id);return id;}
 function part(root,name,geometry,mat,position,rotation){const n={name,mesh:mesh(geometry,mat),translation:position};if(rotation)n.rotation=new THREE.Quaternion().setFromEuler(new THREE.Euler(...rotation)).toArray();kit.nodes[root].children.push(kit.nodes.length);kit.nodes.push(n);}
 const box=(root,name,size,mat,pos)=>part(root,name,new THREE.BoxGeometry(...size),mat,pos);
 const cylinder=(root,name,rt,rb,h,mat,pos)=>part(root,name,new THREE.CylinderGeometry(rt,rb,h,24),mat,pos);
 const ring=(root,name,r,t,mat,pos)=>part(root,name,new THREE.TorusGeometry(r,t,8,32),mat,pos,[Math.PI/2,0,0]);
 const bench=group('Banco');
 for(const x of [-.85,.85]){box(bench,'Soporte de hierro',[.13,.52,.62],iron,[x,.26,0]);box(bench,'Apoyo lateral',[.12,.08,.82],iron,[x,.72,0]);box(bench,'Pata trasera',[.10,.82,.10],iron,[x,.50,-.25]);}
 for(let i=0;i<5;i++)box(bench,'Tablon del asiento',[2.18,.075,.095],wood,[0,.51,-.23+i*.115]);
 for(let i=0;i<3;i++)box(bench,'Tablon del respaldo',[2.18,.12,.075],wood,[0,.76+i*.15,-.29]);
 const planter=group('Jardinera');
 box(planter,'Base',[3.25,.16,.90],stone,[0,.08,0]);box(planter,'Cuerpo',[3.10,.43,.77],stone,[0,.34,0]);box(planter,'Borde',[3.30,.10,.92],stone,[0,.59,0]);box(planter,'Tierra',[3.00,.035,.65],soil,[0,.65,0]);
 for(const x of [-1.32,1.32])box(planter,'Banda de bronce',[.075,.45,.79],gold,[x,.36,0]);
 const urn=group('Urna');cylinder(urn,'Pie',.32,.39,.16,stone,[0,.08,0]);cylinder(urn,'Copa',.43,.24,.66,stone,[0,.48,0]);ring(urn,'Labio',.43,.065,gold,[0,.83,0]);cylinder(urn,'Tierra',.38,.38,.025,soil,[0,.84,0]);
 const lamp=group('Farol');cylinder(lamp,'Zocalo',.21,.29,.24,stone,[0,.12,0]);cylinder(lamp,'Fuste',.045,.075,2.45,iron,[0,1.45,0]);ring(lamp,'Collarin',.10,.03,gold,[0,2.35,0]);box(lamp,'Vidrio',[.24,.40,.24],glass,[0,2.75,0]);box(lamp,'Base de linterna',[.36,.07,.36],iron,[0,2.52,0]);cylinder(lamp,'Techo',0,.29,.27,iron,[0,3.05,0]);for(const x of [-.15,.15])for(const z of [-.15,.15])box(lamp,'Barrote',[.035,.46,.035],iron,[x,2.75,z]);
 const banner=group('Estandarte');cylinder(banner,'Pie',.22,.30,.22,stone,[0,.11,0]);cylinder(banner,'Asta',.035,.055,3.6,iron,[0,1.9,0]);box(banner,'Travesano',[1.38,.055,.055],gold,[0,3.50,0]);box(banner,'Tela',[1.05,1.65,.025],cloth,[0,2.64,.045]);for(const x of [-.50,.50])box(banner,'Orla',[.035,1.65,.035],gold,[x,2.64,.07]);box(banner,'Borde inferior',[1.03,.05,.035],gold,[0,1.82,.07]);ring(banner,'Sello de la ciudad',.22,.032,gold,[0,2.65,.08]);kit.nodes.at(-1).rotation=[0,0,0,1];box(banner,'Lanza del sello',[.04,.67,.04],gold,[0,2.65,.09]);
 const fountain=group('Fuente');cylinder(fountain,'Plataforma',2.18,2.28,.18,stone,[0,.09,0]);cylinder(fountain,'Balsa',1.98,2.06,.30,stone,[0,.33,0]);cylinder(fountain,'Espejo de agua',1.86,1.86,.018,water,[0,.497,0]);ring(fountain,'Borde circular',1.98,.15,stone,[0,.53,0]);cylinder(fountain,'Pilar central',.18,.43,1.24,stone,[0,.95,0]);cylinder(fountain,'Taza superior',.79,.25,.28,stone,[0,1.61,0]);cylinder(fountain,'Agua superior',.70,.70,.02,water,[0,1.76,0]);cylinder(fountain,'Remate',.06,.12,.80,gold,[0,1.98,0]);
 const treeBase=group('Alcorque');box(treeBase,'Piedra exterior',[1.85,.15,1.85],stone,[0,.075,0]);box(treeBase,'Tierra',[1.58,.02,1.58],soil,[0,.16,0]);
 const lawn=group('Jardin');box(lawn,'Base del jardin',[8.25,.10,8.25],stone,[0,.05,0]);const turf=new THREE.BoxGeometry(8,.035,8);for(let i=0;i<turf.attributes.uv.count;i++){turf.attributes.uv.setXY(i,turf.attributes.uv.getX(i)*4,turf.attributes.uv.getY(i)*4);}part(lawn,'Cesped',turf,grass,[0,.115,0]);for(const x of [-4.08,4.08])box(lawn,'Bordillo',[.12,.12,8.25],stone,[x,.15,0]);for(const z of [-4.08,4.08])box(lawn,'Bordillo',[8.25,.12,.12],stone,[0,.15,z]);
 // Space the collection for adding it as a whole from the library.
 for(let i=0;i<kit.scenes[0].nodes.length;i++)kit.nodes[kit.scenes[0].nodes[i]].translation=[i*4,0,0];
 kit.buffers=[{uri:'furniture.bin',byteLength}];fs.writeFileSync(path.join(out,'furniture.bin'),Buffer.concat(chunks));fs.writeFileSync(path.join(out,'furniture.gltf'),JSON.stringify(kit));

 const galleryPath=path.join(catalog,'gallery.json'),dataPath=path.join(__dirname,'data.json');const gallery=JSON.parse(fs.readFileSync(galleryPath)),data=JSON.parse(fs.readFileSync(dataPath));
 function register(id,title,file,category){const model={key:id,title,mesh:title,package:'Giran renovada',category,gltf:'exports/giran-renovada/'+file,thumbnail:null,status:'ready',native:false,batch:'Proyectos personales · Giran renovada',names:[],types:['StaticMesh']};gallery.models=gallery.models.filter(m=>m.key!==id);gallery.models.push(model);data.assets=data.assets.filter(m=>m.id!==id);data.assets.push({id,title,path:model.gltf,thumbnail:null,mesh:title,category,native:false,batch:model.batch});}
 const mapId='custom_giran_renovada_city',kitId='custom_giran_renovada_furniture';register(mapId,'Giran renovada · arquitectura y río','city.gltf','Escenarios');register(kitId,'Giran renovada · mobiliario urbano','furniture.gltf','Objetos');fs.writeFileSync(galleryPath,JSON.stringify(gallery,null,2));fs.writeFileSync(dataPath,JSON.stringify(data,null,2));

 // Build a ground-only raycast from the original BSP/terrain/bridges.
 const bytes=fs.readFileSync(path.join(path.dirname(mapFile),original.buffers[0].uri));
 function attr(index){const a=original.accessors[index],v=original.bufferViews[a.bufferView],n={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],size={5126:4,5125:4,5123:2}[a.componentType],list=[];for(let i=0;i<a.count;i++)for(let k=0;k<n;k++){const offset=(v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||n*size)+k*size;list.push(a.componentType===5126?bytes.readFloatLE(offset):size===4?bytes.readUInt32LE(offset):bytes.readUInt16LE(offset));}return {a,n,list};}
 const actorInfo=new Map(JSON.parse(fs.readFileSync(path.join(__dirname,'../giran-city/actors.json'))).map(a=>[a.actor,a.StaticMesh||'']));const ground=[];
 for(const node of original.nodes){const name=node.name||'',meshName=actorInfo.get(name.replace(/_\d+$/,''))||'';if(node.mesh===undefined||!(/BSP|Terrain/.test(name)||/bridge|stair|floor|walk|elevation|btm|bottom/i.test(meshName)))continue;const group=new THREE.Group();group.position.fromArray(node.translation||[0,0,0]);group.quaternion.fromArray(node.rotation||[0,0,0,1]);group.scale.fromArray(node.scale||[1,1,1]);for(const primitive of original.meshes[node.mesh].primitives){const geo=new THREE.BufferGeometry(),positions=attr(primitive.attributes.POSITION);geo.setAttribute('position',new THREE.Float32BufferAttribute(positions.list,3));if(primitive.indices!==undefined)geo.setIndex(attr(primitive.indices).list);geo.computeVertexNormals();const m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));group.add(m);}group.updateMatrixWorld(true);ground.push(group);}
 const roofsBounds=[];
 for(const node of original.nodes){if(node.mesh===undefined)continue;const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...node.translation||[0,0,0]),new THREE.Quaternion(...node.rotation||[0,0,0,1]),new THREE.Vector3(...node.scale||[1,1,1]));const bbox=new THREE.Box3();for(const p of original.meshes[node.mesh].primitives){if(!/roof/i.test(original.materials[p.material].name))continue;const a=original.accessors[p.attributes.POSITION];if(a.min&&a.max)bbox.union(new THREE.Box3(new THREE.Vector3(...a.min),new THREE.Vector3(...a.max)).applyMatrix4(matrix));}if(!bbox.isEmpty()&&bbox.max.y>2)roofsBounds.push({name:node.name,bbox});}
 const ray=new THREE.Raycaster(),groundAudit=[],collisions=[];
 function height(x,z){ray.set(new THREE.Vector3(x,20,z),new THREE.Vector3(0,-1,0));const hits=ray.intersectObjects(ground,true).filter(h=>h.point.y<=3.2&&h.point.y> -3.4&&Math.abs(h.face.normal.y)>.65);if(!hits.length)throw Error('No paved ground at '+x+','+z);return hits[0].point.y;}
 const project=JSON.parse(fs.readFileSync(basePath));for(const e of project.objects)if(e.asset==='scene_giran_city')e.asset=mapId;
 const bsp=project.objects.find(e=>e.node==='Giran_BSP');bsp.surfaces=[{slot:'BSP_Giran_Village_T_Giran_floor03',texture:'acg_PavingStones006',mode:'replace',repeat:1.35,opacity:1},{slot:'BSP_Giran_V_TX_Gi_floor',texture:'acg_PavingStones006',mode:'replace',repeat:1.35,opacity:1},{slot:'BSP_Giran_Village_T_Giran_floor01',texture:'acg_PavingStones002',mode:'replace',repeat:1.2,opacity:1}];
 let zone=null;const counts={},positions=[];
 function add(name,asset,node,x,y,z,scale=[1,1,1],yaw=0){const e={id:crypto.randomUUID(),name,asset,node,base:false,locked:false,visible:true,position:[x,y,z],rotation:[0,yaw,0],scale,kind:'model',parent:zone,surfaces:[],parts:[]};project.objects.push(e);return e;}
 function district(name){const e=add(name,kitId,'',0,0,0);e.kind='group';e.parent=null;zone=e.id;counts[name]=0;return e;}
 function prop(type,x,z,yaw=0,scale=1,lift=0){const y=height(x,z)+lift;groundAudit.push({type,x,z,y});const sizes=type==='Fuente'?[2.1,2.1]:type==='Jardinera'?[1.65,.46]:type==='Banco'?[1.1,.42]:type==='Alcorque'?[.93,.93]:type==='Jardin'?[4.13,4.13]:[.28,.28];const rx=(Math.abs(Math.cos(yaw))*sizes[0]+Math.abs(Math.sin(yaw))*sizes[1])*scale,rz=(Math.abs(Math.sin(yaw))*sizes[0]+Math.abs(Math.cos(yaw))*sizes[1])*scale;const roof=roofsBounds.find(({bbox:b})=>x+rx>b.min.x&&x-rx<b.max.x&&z+rz>b.min.z&&z-rz<b.max.z);if(roof)collisions.push({type,x,z,roof:roof.name,box:{min:roof.bbox.min.toArray(),max:roof.bbox.max.toArray()}});counts[project.objects.find(e=>e.id===zone).name]++;return add(type,kitId,type,x,y,z,[scale,scale,scale],yaw);}
 function tree(x,z,size=3.6){const y=height(x,z);prop('Alcorque',x,z);add('Árbol urbano', 'custom_giranmodificado1_tree','',x,y+.17,z,[size/8.784,size/8.784,size/8.784]);}
 function flowers(x,z,yaw=0){const base=height(x,z);prop('Jardinera',x,z,yaw);for(let i=-2;i<=2;i++){const dx=i*.55*Math.cos(yaw),dz=-i*.55*Math.sin(yaw);const id=i%2?'web_kenney_nature_flower_purplea':'web_kenney_nature_flower_yellowa';add('Flor de jardinera',id,'',x+dx,base+.66,z+dz,[1.3,1.3,1.3]);}for(const i of [-1,1])add('Follaje de jardinera','custom_giranmodificado1_tree','',x+i*.70*Math.cos(yaw),base+.66,z-i*.70*Math.sin(yaw),[.07,.065,.055]);}
 function urnFlowers(x,z){const base=height(x,z);prop('Urna',x,z);for(let i=0;i<3;i++)add('Flor de urna','web_kenney_nature_flower_purplea','',x+(i-1)*.15,base+.87,z,[1.6,1.6,1.6]);}
 district('01 · Plaza de la Aguja');
 for(const x of [-20.65,-8.75])for(const z of [-2.8,2.8])prop('Banco',x,z,x<-14?Math.PI/2:-Math.PI/2,1,.08);
 for(const x of [-21.5,-7.9])for(const z of [-4.3,4.3])prop('Farol',x,z,0,1,.08);
 for(const x of [-18.5,-10.9])for(const z of [-3.7,3.8])urnFlowers(x,z);
 for(const z of [-10.3,10.9]){flowers(-22.2,z);flowers(-10.8,z);}
 district('02 · Avenida de los Comercios');
 for(const x of [-59,-50,-41,-32]){prop('Farol',x,1.7);urnFlowers(x,-1.3);}
 for(const x of [-46,-35])prop('Estandarte',x,1.9,Math.PI/2,.85);
 for(const z of [-41,-35,-25,20,31]){prop('Farol',-21.1,z);urnFlowers(-17.7,z);}
 district('03 · Patio del Mercado');
 prop('Fuente',-29.0,-18.2,0,.62);
 flowers(-38,-13.5);flowers(-29.0,-24.3);prop('Banco',-29.0,-22.1);prop('Banco',-38,-24.0);
 for(const x of [-39,-28.5])for(const z of [-24.4,-13.5])prop('Farol',x,z);
 tree(-30,-14.0,2.6);tree(-38,-14.8,2.6);
 district('04 · Jardín del Monumento Norte');
 for(const z of [-35,-28]){flowers(-29,z);prop('Banco',-31,z,Math.PI/2);prop('Farol',-26.8,z);}
 tree(-28.5,-36.5,3.8);urnFlowers(-31.0,-26.5);urnFlowers(-31,-36.8);
 district('05 · Atrio de la Catedral');
 for(const z of [-10.0,10.6]){flowers(4.7,z);flowers(9.5,z);prop('Farol',.1,z);}
 for(const z of [-4.2,4.2]){prop('Estandarte',7.5,z,Math.PI/2,1.12);urnFlowers(7.5,z<0?-3.2:3.2);}
 for(const z of [-19,-33,-40]){prop('Farol',3.5,z);urnFlowers(5.7,z);}
 district('06 · Paseo del Río');
 for(const z of [-8,0,8]){prop('Banco',z===0?48.1:46,z===0?2.6:z,-Math.PI/2);if(z!==0)flowers(49,z,Math.PI/2);prop('Farol',48,z);}
 for(const z of [22,28,33])for(const x of [23.0,25.1])prop('Farol',x,z,0,.9);
 for(const x of [18.6,28.0]){prop('Banco',x,45,x<24?Math.PI/2:-Math.PI/2);prop('Estandarte',x,36.9,0,.88);}
 district('07 · Patio de los Artesanos');
 flowers(-31,16.2);flowers(-31,21.2);prop('Banco',-30,18.6,Math.PI/2);prop('Farol',-27,17);prop('Farol',-30,24.2);tree(-27.5,21,3.2);
 // Additional green anchors soften long paved streets without occupying the lane.
 for(const [x,z]of [[-33,30],[-38.8,36]])tree(x,z,3.8);
 district('08 · Jardín de la Memoria');prop('Jardin',-28.1,-31.5,0,.60);
 for(const z of [-33.0,-30.0])tree(-28.1,z,2.4);
 project.name='giranrenovada1';project.reference={...project.reference,design:'Giran · Jardines de Alba',notes:'Renovación visual integral a partir de giranmodificado1: pizarra, piedra, jardines, mercado, catedral y paseo del río. No instala cambios en el cliente.'};
 project.cameras=[{position:[-54,31,41],target:[-15,2,0],fov:42},{position:[-36,12,18],target:[-14.8,3,0],fov:42},{position:[-24,13,-9],target:[-31,0,-18],fov:42},{position:[-24,22,24],target:[8,3,0],fov:42},{position:[41,17,37],target:[24,1,28],fov:42},{position:[-40,13,-47],target:[-33,1,-32],fov:42},{position:[-19,13,-23],target:[-30,0,-31.5],fov:42},{position:[-48,10,7],target:[-44,1,0],fov:42},{position:[64,32,21],target:[23,1,0],fov:42},{position:[-5,155,.01],target:[-5,0,0],fov:42}];project.camera=project.cameras[0];
 fs.writeFileSync(path.join(__dirname,'projects/giranrenovada1.json'),JSON.stringify(project,null,2));
 if(originalHash!==sha(basePath)||mapHash!==sha(mapFile))throw Error('Original unexpectedly modified');
 const report={name:project.name,objects:project.objects.length,newObjects:project.objects.length-1945,roofMaterials:roofs,foliageMaterials:leaves,zones:counts,groundedProps:groundAudit.length,groundAudit,roofOverlaps:collisions,sourceHashes:{project:originalHash,map:mapHash}};fs.writeFileSync(path.join(out,'design-manifest.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({...report,groundAudit:undefined},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
