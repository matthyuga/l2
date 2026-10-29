'use strict';

// Read-only integration check: current NPC sheets against their real Player sources.
const http = require('http');
const expected = [
  [89,91,116,114], [97,90,101,115], [102,91,98,114], [103,90,96,115],
  [108,107,95,116], [110,107,111,97], [113,90,114,116], [115,99,96,94],
  [118,107,114,116], [92,114,113,106], [93,114,113,106], [115,97,106,111],
  [92,93,113,88], [94,103,110,115], [103,94,95,115], [115,94,103,95],
  [95,110,103,115], [110,94,103,115], [110,94,103,115],
  [88,114,113,116], [90,97,100,116], [91,111,114,116], [96,97,106,98], [98,97,105,115], [89,113,100,116], [99,105,100,116], [100,97,99,116], [104,97,106,98], [105,97,115,99], [106,111,97,116], [107,114,113,116], [109,114,113,116], [111,97,106,115], [112,97,115,99], [114,113,106,116], [116,97,100,115], [88,114,113,116], [117,114,113,116], [90,97,100,116]
];
const expectedRace = [0,0,1,1,2,2,3,3,4,0,0,3,0,0,1,3,0,1,2,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,3,3,3,4,4];
function get(route) {
  return new Promise((resolve,reject) => {
    http.get('http://127.0.0.1:3210'+route,res => {
      let body='';res.on('data',chunk => body+=chunk);
      res.on('end',() => {
        try {if(res.statusCode!==200) throw Error(body);resolve(JSON.parse(body));}
        catch(error) {reject(error);}
      });
    }).on('error',reject);
  });
}
function check(condition,message) {if(!condition) throw Error(message);}
(async () => {
  const roster=await get('/api/arena-roster');
  const characters=await get('/api/characters');
  check(roster.length===39,'Se requieren 39 NPC');
  for(let i=0;i<roster.length;i++) {
    const npc=roster[i];
    const character=characters.find(c => c.char_name==='Arena'+npc.name);
    check(character,'Falta perfil de '+npc.name);
    const source=await get('/api/characters/'+character.charId);
    const classes=[Number(source.classInfo.id),...source.subclasses.map(s => Number(s.class_id))];
    check(JSON.stringify(classes)===JSON.stringify(expected[i]),'Build incorrecta: '+npc.name);
    check(Number(source.race)===expectedRace[i],'Raza incorrecta: '+npc.name);
    check(source.subclasses.every(s => Number(s.level)===80),'Sub sin nivel 80: '+npc.name);
    check(npc.liveStats && source.liveStats,'Falta captura: '+npc.name);
    check(source.liveStats.rules_version==='fixed-racial-hybrid-third-v1','Regla antigua: '+npc.name);
    for(const key of ['p_atk','m_atk','p_def','m_def','p_atk_speed','m_atk_speed','max_hp','max_mp','max_cp']) {
      check(Math.abs(Number(npc.liveStats[key])-Number(source.liveStats[key]))<0.00001,'NPC distinto al Player: '+npc.name+' '+key);
    }
    console.log('PASS '+npc.name+' '+classes.join('/')+' PAtk='+Number(npc.liveStats.p_atk).toFixed(2)+' MAtk='+Number(npc.liveStats.m_atk).toFixed(2));
  }
  for(const name of ['Caelan','Ignara','Aelira','Korvash','Morvain','Sylira','Velith']) {
    const npc=roster.find(n => n.name===name);
    const original=characters.find(c => c.char_name===name);
    check(original,'Falta piloto original: '+name);
    const player=await get('/api/characters/'+original.charId);
    for(const key of ['p_atk','m_atk','p_def','m_def','p_atk_speed','m_atk_speed','max_hp','max_mp','max_cp']) {
      check(player.liveStats && Math.abs(Number(npc.liveStats[key])-Number(player.liveStats[key]))<0.00001,'Copia distinta al piloto original: '+name+' '+key);
    }
    console.log('COPY PASS '+name+' stats NPC=piloto original');
  }
  console.log('SUCCESS 39/39: recetas, raza, nivel, regla actual y stats NPC=Player; copias 7/7');
})().catch(error => {console.error(error.message);process.exitCode=1;});
