import * as T from 'three';

// Each emitter owns its resources. Transforms and visibility belong to the editor;
// animation only changes child geometry, so it never dirties a saved project.
const tau=Math.PI*2;
function random(seed){let n=seed||1;return()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296;};}
function shader(color,fragment,extra={}){return new T.ShaderMaterial({uniforms:{time:{value:0},tint:{value:new T.Color(color)},...extra},vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform float time;uniform vec3 tint;varying vec2 vUv;'+fragment,transparent:true,depthWrite:false,side:T.DoubleSide});}
function instanced(root,geometry,material,count){const mesh=new T.InstancedMesh(geometry,material,count);mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.frustumCulled=false;root.add(mesh);return mesh;}

export function createSceneEffect(config){
 const root=new T.Group(),rand=random(config.seed),updates=[],dummy=new T.Object3D();let particles=0,sample=()=>[];
 const set=(mesh,i,x,y,z,sx,sy=sx,sz=sx,rx=0,ry=0,rz=0)=>{dummy.position.set(x,y,z);dummy.rotation.set(rx,ry,rz);dummy.scale.set(sx,sy,sz);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);};
 if(config.type==='fire'||config.type==='smoke'){
  const fire=config.type==='fire',canvas=document.createElement('canvas');canvas.width=canvas.height=128;
  const ctx=canvas.getContext('2d'),gradient=ctx.createRadialGradient(64,64,2,64,64,64);
  gradient.addColorStop(0,fire?'rgba(255,170,50,.9)':'rgba(150,150,150,.85)');gradient.addColorStop(.35,fire?'rgba(240,70,12,.65)':'rgba(110,110,110,.65)');gradient.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,128,128);
  const texture=new T.CanvasTexture(canvas);root.userData.effectTextures=[texture];
  const seeds=[],offsets=new Float32Array(config.count*3),sizes=new Float32Array(config.count*2),alphas=new Float32Array(config.count),angles=new Float32Array(config.count);
  const plane=new T.PlaneGeometry(1,1),geometry=new T.InstancedBufferGeometry();geometry.index=plane.index;geometry.attributes.position=plane.attributes.position;geometry.attributes.uv=plane.attributes.uv;geometry.instanceCount=config.count;
  geometry.setAttribute('offset',new T.InstancedBufferAttribute(offsets,3).setUsage(T.DynamicDrawUsage));geometry.setAttribute('size',new T.InstancedBufferAttribute(sizes,2).setUsage(T.DynamicDrawUsage));geometry.setAttribute('alpha',new T.InstancedBufferAttribute(alphas,1).setUsage(T.DynamicDrawUsage));geometry.setAttribute('angle',new T.InstancedBufferAttribute(angles,1));
  const material=new T.ShaderMaterial({uniforms:{map:{value:texture},tint:{value:new T.Color(config.color)}},transparent:true,depthWrite:false,side:T.DoubleSide,blending:fire?T.AdditiveBlending:T.NormalBlending,
   vertexShader:'attribute vec3 offset;attribute vec2 size;attribute float alpha;attribute float angle;varying vec2 vUv;varying float vAlpha;void main(){vUv=uv;vAlpha=alpha;vec2 p=position.xy*size;float c=cos(angle),s=sin(angle);p=mat2(c,-s,s,c)*p;vec4 center=modelViewMatrix*vec4(offset,1.);center.xy+=p*vec2(length(modelMatrix[0].xyz),length(modelMatrix[1].xyz));gl_Position=projectionMatrix*center;}',
   fragmentShader:'uniform sampler2D map;uniform vec3 tint;varying vec2 vUv;varying float vAlpha;void main(){vec4 tex=texture2D(map,vUv);gl_FragColor=vec4(tex.rgb*tint,tex.a*vAlpha);}' });
  const mesh=new T.Mesh(geometry,material);mesh.frustumCulled=false;root.add(mesh);
  for(let i=0;i<config.count;i++){
   angles[i]=rand()*tau;
   seeds.push({phase:rand(),angle:rand()*tau,radius:Math.sqrt(rand())*config.radius,duration:fire?1.6+rand()*1.8:8+rand()*6,size:(.7+rand()*.6)*(config.size??1)});
  }
  updates.push(t=>{for(let i=0;i<seeds.length;i++){const s=seeds[i],life=(s.phase+t*config.speed/s.duration)%1,angle=s.angle+life*.7;
   offsets[i*3]=Math.cos(angle)*s.radius+life*(fire?.25:3);offsets[i*3+1]=.15+life*config.height;offsets[i*3+2]=Math.sin(angle)*s.radius;
   const scale=s.size*(fire?(1.1-life*.65)*config.radius:(.7+life*2.2)*config.radius);
   sizes[i*2]=scale*(fire?.65:1);sizes[i*2+1]=scale*(fire?1.7:1);alphas[i]=Math.min(1,life*10,(1-life)*5)*(fire?.65:.48);
  }for(const key of ['offset','size','alpha'])geometry.attributes[key].needsUpdate=true;});particles=config.count;sample=()=>Array.from(offsets.slice(0,3));
 }else if(config.type==='leaves'){
  const shape=new T.Shape();shape.moveTo(0,-.52);shape.bezierCurveTo(-.43,-.12,-.35,.23,0,.56);shape.bezierCurveTo(.35,.23,.43,-.12,0,-.52);
  const geometry=new T.ShapeGeometry(shape,3),positions=geometry.attributes.position;for(let i=0;i<positions.count;i++)positions.setZ(i,.13*Math.sin(positions.getY(i)*3));geometry.computeVertexNormals();
  const mesh=instanced(root,geometry,new T.MeshStandardMaterial({color:0xffffff,roughness:.85,side:T.DoubleSide}),config.count),color=new T.Color(config.color),seeds=[];
  for(let i=0;i<config.count;i++){const variation=color.clone().offsetHSL((rand()-.5)*.04,(rand()-.5)*.16,(rand()-.5)*.16);mesh.setColorAt(i,variation);seeds.push({phase:rand(),angle:rand()*tau,radius:Math.sqrt(rand())*config.radius,duration:7+rand()*7,size:(.13+rand()*.11)*(config.size??1),wobble:rand()*tau});}
  updates.push(t=>{for(let i=0;i<seeds.length;i++){const s=seeds[i],life=(s.phase+t*config.speed/s.duration)%1,angle=s.angle+t*.20*config.speed+Math.sin(t*.6+s.wobble)*.18,r=s.radius+life*.55,x=Math.cos(angle)*r+Math.sin(t*.9+s.wobble)*.28,z=Math.sin(angle)*r+Math.cos(t*.7+s.wobble)*.25,y=.10+(1-life)*config.height,fade=Math.min(1,life*14,(1-life)*12);set(mesh,i,x,y,z,s.size*fade,s.size*fade,s.size*fade,t*1.4+s.wobble,t*.8+s.angle,Math.sin(t*2.4+s.wobble)*.8);}mesh.instanceMatrix.needsUpdate=true;});
  particles=config.count;sample=()=>Array.from(mesh.instanceMatrix.array.slice(12,15));
 }else if(config.type==='butterflies'){
  // Two hinged, patterned wings per insect. Local -Z is the direction of flight.
  const shape=new T.Shape();shape.moveTo(.03,.02);shape.bezierCurveTo(.22,.48,.72,.82,.94,.67);shape.bezierCurveTo(1.04,.46,.82,.16,.56,.04);shape.bezierCurveTo(.85,-.08,.78,-.52,.55,-.59);shape.bezierCurveTo(.25,-.69,.10,-.26,.03,.02);
  const geometry=new T.ShapeGeometry(shape,16),uv=geometry.attributes.uv,pos=geometry.attributes.position;
  for(let i=0;i<pos.count;i++)uv.setXY(i,pos.getX(i)/1.04,(pos.getY(i)+.70)/1.55);
  geometry.rotateX(-Math.PI/2);
  const canvas=document.createElement('canvas');canvas.width=canvas.height=512;const ctx=canvas.getContext('2d');
  const gradient=ctx.createLinearGradient(0,0,512,512);gradient.addColorStop(0,'#fff5c3');gradient.addColorStop(.5,'#e9bb78');gradient.addColorStop(1,'#b47a9c');ctx.fillStyle=gradient;ctx.fillRect(0,0,512,512);
  // Fine veins, dark distal band and cream spots remain visible on both faces.
  ctx.strokeStyle='rgba(72,43,44,.72)';ctx.lineWidth=5;
  for(let j=0;j<9;j++){ctx.beginPath();ctx.moveTo(12,290);ctx.quadraticCurveTo(160,235+j*7,490,20+j*58);ctx.stroke();}
  ctx.fillStyle='#433440';ctx.beginPath();ctx.moveTo(388,0);ctx.bezierCurveTo(470,170,450,340,358,512);ctx.lineTo(512,512);ctx.lineTo(512,0);ctx.fill();
  for(let j=0;j<10;j++){ctx.fillStyle=j%2?'#f6dfb7':'#fff3d5';ctx.beginPath();ctx.ellipse(408+Math.sin(j*.6)*22,20+j*49,8,12,-.3,0,tau);ctx.fill();}
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=4;
  const material=new T.MeshStandardMaterial({map:texture,roughness:.88,side:T.DoubleSide}),left=instanced(root,geometry,material,config.count),rightGeometry=geometry.clone();rightGeometry.scale(-1,1,1);
  const right=instanced(root,rightGeometry,material,config.count),bodyGeo=new T.CapsuleGeometry(.032,.45,3,6);bodyGeo.rotateX(Math.PI/2);
  const body=instanced(root,bodyGeo,new T.MeshStandardMaterial({color:'#493c38',roughness:.9}),config.count),seeds=[],flight=new T.Object3D(),hinge=new T.Matrix4(),matrix=new T.Matrix4();
  for(let i=0;i<config.count;i++){seeds.push({phase:rand()*tau,angle:rand()*tau,radius:config.radius*(.72+rand()*.35),height:rand(),rate:.23+rand()*.16,flutter:5+rand()*2,size:(config.size??.11)*(.85+rand()*.3)});const tint=new T.Color().setHSL(.05+(i%3)*.04,.18,.86);left.setColorAt(i,tint);right.setColorAt(i,tint);}
  const route=(s,t)=>{const a=s.angle+t*s.rate*config.speed,r=s.radius+Math.sin(t*.63+s.phase)*.25;return new T.Vector3(Math.cos(a)*r+Math.sin(t*.37+s.phase)*.28,.35+config.height*(.18+s.height*.62)+Math.sin(t*.95+s.phase)*.26,Math.sin(a)*r*.84+Math.sin(t*.72+s.phase)*.22);};
  updates.push(t=>{for(let i=0;i<seeds.length;i++){const s=seeds[i],p=route(s,t),next=route(s,t+.03),direction=next.clone().sub(p),yaw=Math.atan2(-direction.x,-direction.z),flap=.18+(.5+.5*Math.sin(t*s.flutter*tau+s.phase))*1.10;
   flight.position.copy(p);flight.rotation.set(-Math.atan2(direction.y,Math.hypot(direction.x,direction.z))*.45,yaw,Math.sin(t*.8+s.phase)*.18);flight.scale.setScalar(s.size);flight.updateMatrix();body.setMatrixAt(i,flight.matrix);
   hinge.makeRotationZ(flap);matrix.multiplyMatrices(flight.matrix,hinge);left.setMatrixAt(i,matrix);hinge.makeRotationZ(-flap);matrix.multiplyMatrices(flight.matrix,hinge);right.setMatrixAt(i,matrix);
  }left.instanceMatrix.needsUpdate=right.instanceMatrix.needsUpdate=body.instanceMatrix.needsUpdate=true;});
  particles=config.count;sample=()=>[...body.instanceMatrix.array.slice(12,15),left.instanceMatrix.array[5]];
  root.userData.effectTextures=[texture];
 }else if(config.type==='wind'){
  const segments=12,positions=new Float32Array(config.count*(segments+1)*6),uv=[],indices=[],seeds=[];
  for(let i=0;i<config.count;i++){seeds.push({phase:rand(),angle:rand()*tau,radius:Math.sqrt(rand())*config.radius,duration:2.3+rand()*2.5,width:.018+rand()*.028});for(let j=0;j<=segments;j++){uv.push(0,j/segments,1,j/segments);if(j<segments){const a=i*(segments+1)*2+j*2;indices.push(a,a+1,a+2,a+1,a+3,a+2);}}}
  const geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(positions,3).setUsage(T.DynamicDrawUsage));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(indices);
  const mat=shader(config.color,'void main(){float edge=pow(sin(vUv.x*3.14159),.7);float tail=pow(sin(vUv.y*3.14159),1.3);gl_FragColor=vec4(tint,edge*tail*.38);}'),mesh=new T.Mesh(geo,mat);mesh.frustumCulled=false;root.add(mesh);
  updates.push(t=>{let offset=0;for(const s of seeds){const life=(s.phase+t*config.speed/s.duration)%1,fade=Math.sin(life*Math.PI),angle=s.angle+t*.18;for(let j=0;j<=segments;j++){const f=j/segments,y=.08+life*config.height+f*.85,a=angle+f*.34,x=Math.cos(a)*s.radius+Math.sin(y*1.7+t)*.12,z=Math.sin(a)*s.radius+Math.cos(y*1.5+t)*.12,w=s.width*fade;for(const side of [-1,1]){positions[offset++]=x+side*w*Math.cos(a);positions[offset++]=y;positions[offset++]=z+side*w*Math.sin(a);}}}geo.attributes.position.needsUpdate=true;});
  // A few pale motes reinforce the direction without hiding the grille.
  const dust=instanced(root,new T.SphereGeometry(1,5,4),new T.MeshBasicMaterial({color:config.color,transparent:true,opacity:.36,depthWrite:false}),config.count);
  updates.push(t=>{for(let i=0;i<seeds.length;i++){const s=seeds[i],p=(s.phase+t*config.speed/(s.duration*1.2))%1,a=s.angle+p*.65;set(dust,i,Math.cos(a)*s.radius,.12+p*config.height,Math.sin(a)*s.radius,.018*Math.sin(p*Math.PI));}dust.instanceMatrix.needsUpdate=true;});
  particles=config.count*2;sample=()=>Array.from(positions.slice(0,3));
 }else if(config.type==='pool'){
  const surface=new T.PlaneGeometry(37.6,11.6,96,32);surface.rotateX(-Math.PI/2);
  const water=shader(config.color,`void main(){vec2 p=vUv*vec2(38.,12.);float a=sin(p.x*3.7+time*1.4+sin(p.y*2.3-time*.8));float b=sin(p.y*5.8-time*1.9+sin(p.x*2.+time));float c=pow(clamp((a+b)*.25+.5,0.,1.),9.);float glint=pow(.5+.5*sin(p.x*6.+p.y*3.-time*2.),28.);gl_FragColor=vec4(mix(tint,vec3(.51,.88,.92),c*.68+glint*.12),.89);}`);
  const mesh=new T.Mesh(surface,water);root.add(mesh);
  const base=surface.attributes.position.array.slice();
  updates.push(t=>{water.uniforms.time.value=t*config.speed;const a=surface.attributes.position;for(let i=0;i<a.count;i++){const x=base[i*3],z=base[i*3+2];a.setY(i,.025*Math.sin(x*1.7+t*1.3)*Math.sin(z*2.1-t*.8));}a.needsUpdate=true;});
  const fall=shader('#b9ecf1',`void main(){float streams=pow(.5+.5*sin(vUv.x*90.+sin(vUv.y*17.-time*6.)),5.);float pulses=pow(.5+.5*sin(vUv.y*65.+time*12.+vUv.x*18.),8.);float edge=sin(vUv.x*3.14159);gl_FragColor=vec4(mix(tint,vec3(1.),streams*.5),edge*(.20+streams*.42+pulses*.22));}`);
  for(const z of [-3,0,3]){
   const geo=new T.BufferGeometry(),pos=[],uv=[],idx=[];
   for(let j=0;j<=24;j++){const f=j/24;for(const side of [-1,1]){pos.push(-17.5+f*.88,1.40*(1-f*f),z+side*(.17+.12*f));uv.push((side+1)/2,f);}if(j<24){const a=j*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
   geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);root.add(new T.Mesh(geo,fall));
  }
  const bubbles=instanced(root,new T.SphereGeometry(1,6,4),new T.MeshBasicMaterial({color:0xddfaff,transparent:true,opacity:.48,depthWrite:false}),config.count),seeds=[];
  for(let i=0;i<config.count;i++)seeds.push({phase:rand(),angle:rand()*tau,r:rand()*.8,size:.018+rand()*.033});
  const foam=instanced(root,new T.TorusGeometry(1,.025,4,24),new T.MeshBasicMaterial({color:0xd6faff,transparent:true,opacity:.22,depthWrite:false}),18);
  updates.push(t=>{fall.uniforms.time.value=t*config.speed;for(let i=0;i<seeds.length;i++){const s=seeds[i],p=(s.phase+t*.65)%1,z=[-3,0,3][i%3],x=-16.62+Math.cos(s.angle)*s.r;set(bubbles,i,x,.02+Math.sin(p*Math.PI)*(.12+s.r*.20),z+Math.sin(s.angle)*s.r,s.size*Math.sin(p*Math.PI));}bubbles.instanceMatrix.needsUpdate=true;for(let i=0;i<18;i++){const p=(i*.618+t*.30)%1,z=[-3,0,3][i%3];set(foam,i,-16.62,.035,z,.05+p*.85,.05+p*.85,.05+p*.85,Math.PI/2,0,0);}foam.instanceMatrix.needsUpdate=true;});
  particles=config.count+18;sample=()=>Array.from(bubbles.instanceMatrix.array.slice(12,15));
 }else if(config.type==='fountain'){
  // Water surfaces sit just above the static bowls, in the fountain's own units.
  const water=shader(config.color,`void main(){vec2 p=vUv*2.-1.;float r=length(p);float wave=sin(r*48.-time*4.+sin(p.x*11.+time)*.8)*.5+.5;float ripple=pow(wave,10.);float caustic=pow(.5+.5*sin(p.x*25.+time*1.2)*sin(p.y*22.-time*.9),7.);vec3 c=mix(tint,vec3(.69,.94,.96),ripple*.36+caustic*.22);gl_FragColor=vec4(c,.78);}`);
  for(const [r,y]of [[1.86,.511],[.70,1.782]]){const m=new T.Mesh(new T.CircleGeometry(r,64),water);m.rotation.x=-Math.PI/2;m.position.y=y;root.add(m);}
  const sheet=shader(config.color,`void main(){float band=.5+.5*sin(vUv.x*410.+sin(vUv.y*28.-time*5.)*.8);float streams=pow(band,5.);float drops=pow(.5+.5*sin(vUv.y*95.+time*13.+sin(vUv.x*210.)*3.),12.);float alpha=(.055+streams*.21+drops*.20)*(.6+.4*sin(vUv.y*3.14159));gl_FragColor=vec4(mix(tint,vec3(.85,.98,1.),streams*.7+drops*.3),alpha);}`);
  const curtain=new T.Mesh(new T.CylinderGeometry(.76,.92,1.24,72,12,true),sheet);curtain.position.y=1.15;root.add(curtain);
  const droplet=instanced(root,new T.SphereGeometry(1,5,4),new T.MeshBasicMaterial({color:0xc5f4fa,transparent:true,opacity:.63,depthWrite:false}),config.count),seeds=[];
  for(let i=0;i<config.count;i++)seeds.push({phase:rand(),angle:rand()*tau,size:.016+rand()*.026,speed:.8+rand()*.4});
  updates.push(t=>{water.uniforms.time.value=sheet.uniforms.time.value=t*config.speed;for(let i=0;i<seeds.length;i++){const s=seeds[i],p=(s.phase+t*config.speed*s.speed)%1,a=s.angle;let r,y;if(i%3===0){r=.14+p*.50;y=1.79+Math.sin(p*Math.PI)*.84;}else{r=.76+p*.22;y=1.76-p*p*1.24;}set(droplet,i,Math.cos(a)*r,y,Math.sin(a)*r,s.size,s.size*1.9,s.size);}droplet.instanceMatrix.needsUpdate=true;});
  const bubbles=instanced(root,new T.SphereGeometry(1,8,6),new T.MeshBasicMaterial({color:0xcdf7fc,transparent:true,opacity:.37,wireframe:true,depthWrite:false}),32),foam=instanced(root,new T.TorusGeometry(1,.035,4,20),new T.MeshBasicMaterial({color:0xdcfbff,transparent:true,opacity:.32,depthWrite:false}),24);
  updates.push(t=>{for(let i=0;i<32;i++){const p=(i*.618+t*.53*config.speed)%1,a=i*2.4,r=.85+(i%5)*.12;set(bubbles,i,Math.cos(a)*r,.46+p*.16,Math.sin(a)*r,(.018+p*.028)*Math.sin(p*Math.PI));}bubbles.instanceMatrix.needsUpdate=true;for(let i=0;i<24;i++){const p=(i*.618+t*.64*config.speed)%1,a=i*2.4,r=.90+(i%3)*.06,scale=.025+p*.17;set(foam,i,Math.cos(a)*r,.527+Math.sin(p*Math.PI)*.012,Math.sin(a)*r,scale,scale,scale,Math.PI/2,0,0);}foam.instanceMatrix.needsUpdate=true;});
  particles=config.count+56;sample=()=>Array.from(droplet.instanceMatrix.array.slice(12,15));
 }
 // Select the emitter from the scene tree or its node; its moving particles
 // must not block placement on the floor or generate static selection ghosts.
 root.traverse(n=>{if(n.isMesh){n.userData.sceneEffectParticle=true;n.raycast=()=>{};}});
 root.userData.sceneEffect={update(t){for(const fn of updates)fn(t);},state(){return {type:config.type,particles,sample:sample()};},dispose(){const geometries=new Set(),materials=new Set();root.traverse(n=>{if(n.geometry)geometries.add(n.geometry);for(const m of Array.isArray(n.material)?n.material:n.material?[n.material]:[])materials.add(m);});for(const g of geometries)g.dispose();for(const m of materials)m.dispose();for(const texture of root.userData.effectTextures||[])texture.dispose();}};
 root.userData.sceneEffect.update(0);return root;
}
