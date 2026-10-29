export const defaultAtmosphere=()=>({sky:null,rotation:0,brightness:1,weather:'none',density:1,wind:.5,fog:0,particle:null});
export function validAtmosphere(v,items){
 if(v===undefined)return true;
 if(!v||typeof v!=='object'||Array.isArray(v))return false;
 const bounded=(k,min,max)=>Number.isFinite(v[k])&&v[k]>=min&&v[k]<=max;
 const id=(key,type)=>v[key]===null||(typeof v[key]==='string'&&/^[a-f0-9]{20}$/.test(v[key])&&(!items||items.some(i=>i.id===v[key]&&i.type===type)));
 return id('sky','sky')&&id('particle','particle')&&bounded('rotation',0,360)&&bounded('brightness',.1,3)&&bounded('density',.1,2)&&bounded('wind',0,3)&&bounded('fog',0,1)&&['none','rain','storm','snow','sand','wind','ash','mist'].includes(v.weather);
}
