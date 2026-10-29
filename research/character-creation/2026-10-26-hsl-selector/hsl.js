(function(global){
 'use strict';
 const clamp=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
 function hslToRgb(h,s,l){h=((h%360)+360)%360/360;s=clamp(s,0,100)/100;l=clamp(l,0,100)/100;const a=s*Math.min(l,1-l);const f=n=>{let k=(n+h*12)%12;return l-a*Math.max(-1,Math.min(k-3,9-k,1));};return [f(0),f(8),f(4)].map(x=>Math.round(clamp(x,0,1)*255));}
 function rgbToHsl(r,g,b){r/=255;g/=255;b/=255;let max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2,h=0,s=0;if(d){s=d/(1-Math.abs(2*l-1));h=max===r?((g-b)/d)%6:max===g?(b-r)/d+2:(r-g)/d+4;h=(h*60+360)%360;}return [h,s*100,l*100];}
 function toHex(rgb){return '#'+rgb.map(x=>clamp(Math.round(x),0,255).toString(16).padStart(2,'0')).join('').toUpperCase();}
 function fromHex(text){const s=text.trim().replace(/^#/,'');if(!/^[\da-f]{6}$/i.test(s))return null;return [0,2,4].map(i=>parseInt(s.slice(i,i+2),16));}
 global.HSL={clamp,hslToRgb,rgbToHsl,toHex,fromHex};
})(typeof window==='undefined'?globalThis:window);
