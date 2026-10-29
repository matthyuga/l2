const mod=Process.enumerateModules().find(m=>/system-hud\\d3d9.dll$/i.test(m.path));
const start=Date.now(),atlases=new Set(),hooked=new Set(),events=[],active={};
function textureHook(tex,slot,label){
 const addr=tex.readPointer().add(slot*4).readPointer();const key=addr.toString()+label;
 if(hooked.has(key))return;hooked.add(key);
 Interceptor.attach(addr,{onEnter(args){if(!atlases.has(args[0].toString()))return;this.t=Date.now();this.rec=active[this.threadId];},onLeave(){if(this.t!==undefined&&this.rec)this.rec[label]=(this.rec[label]||0)+Date.now()-this.t;}});
}
Interceptor.attach(mod.base.add(0x65e0),{
 onEnter(args){this.t=Date.now();this.state=args[1];this.built=this.state.add(8).readU64().toString();this.rec={at_ms:this.t-start,lock_ms:0,unlock_ms:0,thread:this.threadId};active[this.threadId]=this.rec;let tex=this.state.add(4).readPointer();if(!tex.isNull()){atlases.add(tex.toString());textureHook(tex,19,'lock_ms');textureHook(tex,20,'unlock_ms');}},
 onLeave(){const dt=Date.now()-this.t;if(this.state.add(8).readU64().toString()!==this.built){this.rec.total_ms=dt;this.rec.compute_and_other_ms=dt-this.rec.lock_ms-this.rec.unlock_ms;events.push(this.rec);}delete active[this.threadId];}
});
setTimeout(()=>send({elapsed_ms:Date.now()-start,events,textureHookAddresses:[...hooked]}),14000);
