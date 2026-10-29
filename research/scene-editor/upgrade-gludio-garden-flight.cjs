const fs=require('fs'),path=require('path');
const root=__dirname,lab=path.resolve(root,'../..');
const id='gludio-brisas-pink-butterflies-v1',ids=['e66830b1-cf37-4a2e-8a56-f2ad9095b812','1f5ea010-62bb-4711-ad70-2fda4d65c132'];
for(const file of [path.join(root,'projects/gludiobrisas1-animado.json'),path.join(lab,'mapas editados/gludiobrisas1-animado/gludiobrisas1-animado.json')]){
 const p=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const o of p.objects)if(ids.includes(o.id)&&o.effect?.type==='leaves'&&o.effect.size===undefined)o.effect.size=.72;
 const pink=p.objects.find(o=>o.id===ids[1]);if(!pink)throw Error('Missing pink leaf emitter');
 if(!p.objects.some(o=>o.id===id))p.objects.push({id,name:'Mariposas · árbol rosa',asset:'custom_gludio_brisas_decor',node:'',base:false,kind:'effect',parent:pink.parent||null,locked:false,visible:true,position:[pink.position[0],pink.position[1]+.2,pink.position[2]],rotation:[0,0,0],scale:[1,1,1],surfaces:[],parts:[],effect:{type:'butterflies',seed:2931,count:8,color:'#efd4a4',radius:2.45,height:2.2,speed:.8,size:.14}});
 fs.writeFileSync(file,JSON.stringify(p,null,2));console.log({file,leafSize:.72,butterflies:8,effects:p.objects.filter(o=>o.kind==='effect').length});
}
