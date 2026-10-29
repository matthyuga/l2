export function validEffect(effect){
 if(!effect||!['wind','leaves','fountain','pool','butterflies','fire','smoke'].includes(effect.type))return false;
 if(effect.size!==undefined&&(!Number.isFinite(effect.size)||effect.size<.02||effect.size>2))return false;
 if(effect.type==='butterflies'&&effect.count>40)return false;
 return Number.isInteger(effect.seed)&&effect.seed>=0&&effect.seed<2147483647&&Number.isInteger(effect.count)&&effect.count>=8&&effect.count<=400&&/^#[0-9a-f]{6}$/i.test(effect.color)&&['radius','height','speed'].every(k=>Number.isFinite(effect[k])&&effect[k]>=.05&&effect[k]<=20);
}
