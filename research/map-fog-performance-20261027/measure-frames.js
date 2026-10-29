const mod=Process.enumerateModules().find(m=>/system-hud\\d3d9.dll$/i.test(m.path));
if(!mod)throw Error('V8 module missing');
send({module:mod.path,base:mod.base,pid:Process.id});
const start=Date.now(),updates=[],frames=[],screens=[],maps=[],gaps=[];
let updateCalls=0,prev=null,screenCalls=0,mapCalls=0,lastUpdate=null;
Interceptor.attach(mod.base.add(0x65e0),{
 onEnter(args){this.t=Date.now();this.state=args[1];this.built=this.state.add(8).readU64().toString();updateCalls++;},
 onLeave(){const end=Date.now(),built=this.state.add(8).readU64().toString();if(built!==this.built){const event={at_ms:this.t-start,duration_ms:end-this.t,revision:built,thread:this.threadId};updates.push(event);lastUpdate=event;}}
});
Interceptor.attach(mod.base.add(0x3d10),{
 onEnter(){this.t=Date.now();if(prev!==null){let dt=this.t-prev;if(dt>40)gaps.push({at_ms:this.t-start,gap_ms:dt,lastUpdate});}prev=this.t;},
 onLeave(){let dt=Date.now()-this.t;frames.push(dt);}
});
Interceptor.attach(mod.base.add(0x4150),{onEnter(){this.t=Date.now();screenCalls++;},onLeave(){let dt=Date.now()-this.t;if(dt>0)screens.push(dt);}});
Interceptor.attach(mod.base.add(0x53f0),{onEnter(){this.t=Date.now();mapCalls++;},onLeave(){let dt=Date.now()-this.t;if(dt>0)maps.push(dt);}});
function stats(a){a.sort((x,y)=>x-y);return{count:a.length,max_ms:a.length?a[a.length-1]:0,p50_ms:a.length?a[Math.floor(a.length*.5)]:0,p95_ms:a.length?a[Math.floor(a.length*.95)]:0};}
setTimeout(()=>send({elapsed_ms:Date.now()-start,updateCalls,updates,frameCalls:frames.length,present:stats(frames),screenCalls,screenNonzero:stats(screens),mapCalls,mapNonzero:stats(maps),gaps:gaps.slice(-80)}),19000);
