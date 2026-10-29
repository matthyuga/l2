'use strict';
const endpoint='http://127.0.0.1:9331/json';
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 let page;
 for(let attempt=0;attempt<60&&!page;attempt++){
  try{
   const targets=await(await fetch(endpoint)).json();
   page=targets.find(target=>target.type==='page'&&target.url.startsWith('http://127.0.0.1:32291'));
  }catch{}
  if(!page)await pause(250);
 }
 if(!page)throw new Error('No se encontró la ventana aislada de Giran.');
 const socket=new WebSocket(page.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
 socket.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{awaitPromise:true,expression:`new Promise((resolve,reject)=>{
   let attempts=0;
   const timer=setInterval(()=>{
    const select=document.getElementById('scene');
    const ready=select&&[...select.options].some(option=>option.value==='giran');
    if(ready&&attempts>5){
     clearInterval(timer);
     select.value='giran';
     select.dispatchEvent(new Event('change',{bubbles:true}));
     resolve('Giran seleccionado');
    }else if(++attempts>100){clearInterval(timer);reject(new Error('Giran no apareció en el selector'));}
   },250);
  })`}}));
 await new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>reject(new Error('La selección de Giran agotó el tiempo.')),30000);
  socket.onmessage=event=>{const message=JSON.parse(event.data);if(message.id===1){clearTimeout(timeout);resolve(message);}};
 });
 socket.close();
})().catch(error=>{console.error(error.message);process.exitCode=1;});
