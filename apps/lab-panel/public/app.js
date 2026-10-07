(function () {
  'use strict';

  var state = { view: 'overview', characters: [], opponents: [], classes: [], skills: [], fights: [], catalog: [], pairs: [], buildCandidates: [], finalists: [], benchmarks: [], externalReferences: [], nyxCalibration: null, magicProgression: null, coverage: null, selectedCharacter: null, selectedOpponent: null, selectedClass: null, selectedSkill: null, selectedFight: null };
  var titles = { overview: 'Resumen del laboratorio', characters: 'Personajes y equipamiento', creator: 'Crear rival NPC', balance: 'Balance de razas y clases', skills: 'Editor de skills', telemetry: 'Análisis de combate' };

  function $(selector, root) { return (root || document).querySelector(selector); }
  function $$(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
  function escapeHtml(value) { return String(value === null || value === undefined ? '' : value).replace(/[&<>'"]/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]; }); }
  function number(value, digits) { return Number(value || 0).toLocaleString('es-AR', { maximumFractionDigits: digits === undefined ? 0 : digits }); }
  function date(value) { return new Date(Number(value)).toLocaleString('es-AR', { day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit' }); }
  function percent(value, max) { return max > 0 ? Math.max(0, Math.min(100, value / max * 100)) : 0; }
  function slug(value) { return String(value).toLowerCase().replace(/\s+/g, '-'); }
  function skillIcon(item, large) { return item && item.iconUrl ? '<img class="skill-thumb '+(large?'large':'')+'" src="'+escapeHtml(item.iconUrl)+'" alt="" loading="lazy">' : '<span class="skill-thumb placeholder">?</span>'; }

  async function api(url, options) {
    var response = await fetch(url, Object.assign({ headers: { 'Content-Type': 'application/json' } }, options || {}));
    var payload = await response.json().catch(function () { return {}; });
    if (!response.ok) throw new Error(payload.error || ('Error HTTP ' + response.status));
    return payload;
  }

  function toast(message, type) {
    var node = document.createElement('div');
    node.className = 'toast ' + (type || '');
    node.textContent = message;
    $('#toast-root').appendChild(node);
    setTimeout(function () { node.remove(); }, 4600);
  }

  function setView(view) {
    state.view = view;
    $$('.nav-item').forEach(function (item) { item.classList.toggle('active', item.dataset.view === view); });
    $$('.view').forEach(function (item) { item.classList.toggle('active', item.id === 'view-' + view); });
    $('#page-title').textContent = titles[view];
    if (view === 'characters' && !state.characters.length) loadCharacters();
    if (view === 'creator') prepareCreator();
    if (view === 'balance' && $('#race-filter').options.length <= 1) loadClasses();
    if (view === 'skills' && !state.skills.length) searchSkills('');
    if (view === 'telemetry') loadTelemetry();
  }

  async function loadStatus() {
    try {
      var status = await api('/api/status');
      var items = [
        ['◇','Login server',status.login,'Puerto 2106'], ['◆','Game server',status.game,'Puerto 7777'],
        ['▤','MariaDB',status.database,'Puerto 3307'], ['⌁','Eventos medidos',true,number(status.telemetryCount) + ' registros']
      ];
      $('#status-grid').classList.remove('skeleton-block');
      $('#status-grid').innerHTML = items.map(function (item) {
        return '<div class="status-card"><div class="status-icon">'+item[0]+'</div><div><strong>'+item[1]+'</strong><small class="'+(item[2]?'online':'')+'">'+(item[2] ? item[3] : 'No disponible')+'</small></div></div>';
      }).join('');
      $('#side-status-dot').classList.toggle('online', status.officeMode ? status.database : status.login && status.game);
      $('#side-status').textContent = status.officeMode ? 'Modo oficina · datos disponibles' : (status.game ? 'Servidor operativo' : 'Servidor detenido');
      if(status.officeMode){$('#restart-button').disabled=true;$('#restart-button').textContent='Aplicar al volver a casa';$('#restart-button').title='El Game Server no se inicia en modo oficina.';}
      $('#pending-badge').classList.toggle('hidden', !status.state.requiresRestart);
    } catch (error) {
      $('#side-status').textContent = 'Panel sin base de datos';
      toast(error.message, 'error');
    }
  }

  async function loadOverviewFight() {
    try {
      var fights = await api('/api/telemetry/fights');
      if (!fights.length) return;
      var fight = fights[0];
      $('#latest-fight').className = '';
      $('#latest-fight').innerHTML = '<div class="detail-body">' +
        '<div style="display:flex;justify-content:space-between;gap:12px;align-items:start"><div><p class="eyebrow">'+escapeHtml(date(fight.start))+'</p><h3>'+escapeHtml(fight.player.name)+' <span class="muted">vs</span> '+escapeHtml(fight.opponent.name)+'</h3></div><span class="fight-result '+slug(fight.result)+'">'+escapeHtml(fight.result)+'</span></div>' +
        '<div class="metric-row" style="grid-template-columns:repeat(3,1fr);margin:20px 0 0"><div class="metric"><small>DPS</small><strong>'+number(fight.dps,1)+'</strong></div><div class="metric"><small>Daño</small><strong>'+number(fight.dealt)+'</strong></div><div class="metric"><small>Skills</small><strong>'+number(fight.casts)+'</strong></div></div>' +
        '<button class="button ghost full" style="margin-top:16px" data-jump="telemetry">Abrir análisis completo</button></div>';
      bindJumps();
    } catch (_) {}
  }

  async function loadCharacters() {
    $('#character-list').innerHTML = '<div class="loading">Leyendo personajes…</div>';
    try {
      var result = await Promise.all([api('/api/characters'), api('/api/opponents')]);
      state.characters = result[0];
      state.opponents = result[1];
      renderCharacters();
      if (!state.selectedCharacter && !state.selectedOpponent) {
        if (state.opponents.length) selectOpponent(state.opponents[0].id);
        else if (state.characters.length) selectCharacter(state.characters[0].charId);
      }
    } catch (error) { $('#character-list').innerHTML = '<div class="empty-state compact">'+escapeHtml(error.message)+'</div>'; }
  }

  function renderCharacters() {
    var rivals = '<div class="list-section"><span>Rivales de Arena</span><small>NPC editables</small></div>' + state.opponents.map(function (opponent) {
      return '<button class="select-item opponent-item '+(state.selectedOpponent === opponent.id?'active':'')+'" data-opponent="'+opponent.id+'"><div><strong>'+escapeHtml(opponent.name)+'</strong><small>'+escapeHtml(opponent.title)+' · '+escapeHtml(opponent.race)+'</small></div><div style="text-align:right"><span class="npc-pill">RIVAL</span><small>'+opponent.skills.length+' skills</small></div></button>';
    }).join('');
    var players = '<div class="list-section"><span>Tus personajes</span><small>Base de datos</small></div>' + state.characters.map(function (character) {
      return '<button class="select-item '+(state.selectedCharacter === character.charId?'active':'')+'" data-character="'+character.charId+'"><div><strong>'+escapeHtml(character.char_name)+'</strong><small>'+escapeHtml(character.classInfo.path)+'</small></div><div style="text-align:right">'+(character.online?'<span class="online-pill">online</span>':'<span class="level">'+character.level+'</span>')+'<small>'+number(character.adena)+' adena</small></div></button>';
    }).join('');
    $('#character-list').innerHTML = rivals + players;
    $$('[data-character]').forEach(function (button) { button.onclick = function () { selectCharacter(Number(button.dataset.character)); }; });
    $$('[data-opponent]').forEach(function (button) { button.onclick = function () { selectOpponent(Number(button.dataset.opponent)); }; });
  }

  async function selectCharacter(id) {
    state.selectedCharacter = id; state.selectedOpponent = null; renderCharacters();
    $('#character-detail').innerHTML = '<div class="loading">Abriendo ficha…</div>';
    try {
      var rivals=state.opponents.filter(function(item){return item.name==='Ares'||item.name==='Nyx';});
      var result=await Promise.all([api('/api/characters/' + id)].concat(rivals.map(function(item){return api('/api/opponents/'+item.id);}))); 
      renderCharacterDetail(result[0],result.slice(1));
    }
    catch (error) { $('#character-detail').innerHTML = '<div class="empty-state">'+escapeHtml(error.message)+'</div>'; }
  }

  async function selectOpponent(id) {
    state.selectedOpponent = id; state.selectedCharacter = null; renderCharacters();
    $('#character-detail').innerHTML = '<div class="loading">Abriendo rival…</div>';
    try { renderOpponentDetail(await api('/api/opponents/' + id)); }
    catch (error) { $('#character-detail').innerHTML = '<div class="empty-state">'+escapeHtml(error.message)+'</div>'; }
  }

  function opponentField(name, label, value) { return '<div class="field"><label>'+label+'</label><input name="'+name+'" type="number" step="any" min="0" value="'+escapeHtml(value === undefined ? '' : value)+'"></div>'; }
  function opponentSkillRows(skills, kind) {
    return skills.map(function (skill) {
      return '<div class="opponent-skill-row" data-opponent-skill="'+kind+'" data-role="'+escapeHtml(skill.role||'')+'">'+skillIcon(skill)+'<div class="skill-row-name"><strong>'+escapeHtml(skill.name)+'</strong><small>'+(skill.role?escapeHtml(skill.role):'Skill disponible')+'</small></div><div class="field"><label>ID</label><input data-skill-id type="number" min="1" value="'+skill.id+'"></div><div class="field"><label>Nivel</label><input data-skill-level type="number" min="1" value="'+skill.level+'"></div></div>';
    }).join('');
  }

  function readOpponentSkills(kind) {
    return $$('[data-opponent-skill="'+kind+'"]').map(function (row) { return { role: row.dataset.role || '', id:Number($('[data-skill-id]',row).value), level:Number($('[data-skill-level]',row).value) }; });
  }

  function statTile(label,value,note){return '<div class="final-stat"><small>'+label+'</small><strong>'+(value===null||value===undefined?'—':number(value,2))+'</strong>'+(note?'<span>'+note+'</span>':'')+'</div>';}

  function configuredStatTiles(stats){return statTile('P. Atk',stats.pAtk)+statTile('M. Atk',stats.mAtk)+statTile('P. Def',stats.pDef)+statTile('M. Def',stats.mDef)+statTile('Atk. Speed',stats.pAtkSpeed)+statTile('Casting Speed',stats.mAtkSpeed)+statTile('Velocidad',stats.runSpeed,'correr')+statTile('Critical Rate',stats.pCritical,'valor L2, no %')+statTile('Accuracy',stats.accuracy)+statTile('Evasion',stats.evasion)+statTile('Rango',stats.attackRange)+statTile('Critical Power',2,'multiplicador base')+statTile('HP máximo',stats.maxHp)+statTile('MP máximo',stats.maxMp)+statTile('CP máximo',stats.maxCp)+statTile('STR',stats.str)+statTile('DEX',stats.dex)+statTile('CON',stats.con)+statTile('INT',stats.int)+statTile('WIT',stats.wit)+statTile('MEN',stats.men);}

  function liveStatTiles(stats){return statTile('P. Atk',stats.p_atk)+statTile('M. Atk',stats.m_atk)+statTile('P. Def',stats.p_def)+statTile('M. Def',stats.m_def)+statTile('Atk. Speed',stats.p_atk_speed)+statTile('Casting Speed',stats.m_atk_speed)+statTile('Velocidad',stats.run_speed,'correr')+statTile('Critical Rate',stats.p_critical,'valor L2, no %')+statTile('Magic Critical',stats.m_critical,'valor interno')+statTile('Accuracy',stats.accuracy)+statTile('Evasion',stats.evasion)+statTile('Critical Power',stats.critical_multiplier,'× + '+number(stats.critical_add,1))+statTile('HP máximo',stats.max_hp)+statTile('MP máximo',stats.max_mp)+statTile('CP máximo',stats.max_cp)+statTile('STR',stats.stat_str)+statTile('DEX',stats.stat_dex)+statTile('CON',stats.stat_con)+statTile('INT',stats.stat_int)+statTile('WIT',stats.stat_wit)+statTile('MEN',stats.stat_men);}

  function renderOpponentDetail(opponent) {
    var s=opponent.stats,v=opponent.vitals,a=opponent.attack,d=opponent.defence,m=opponent.movement,p=opponent.appearance;
    var buildClasses=opponent.build?[opponent.build.primary].concat(opponent.build.subclasses||[]):[];
    var buildHtml=buildClasses.length?'<div class="npc-build-strip">'+buildClasses.map(function(item,index){return '<div><span>'+(index?'Sub '+index:'Principal')+'</span><strong>'+(item?escapeHtml(item.name):'Sin registrar')+'</strong></div>';}).join('')+'</div>':'';
    var liveHtml=opponent.liveStats?'<div class="final-stats-head"><div><h4>Stats finales observados</h4><p>Lectura real del Game Server con skills y buffs activos · '+escapeHtml(date(opponent.liveStats.observed_ms))+'</p></div><span class="badge success">EN VIVO</span></div><div class="final-stats-grid live">'+liveStatTiles(opponent.liveStats)+'</div>':'<div class="live-stats-empty"><strong>Falta una lectura final</strong><p>Tras aplicar y reiniciar, pelea una vez contra este rival. La telemetría guardará sus números reales, incluidos pasivos y buffs activos.</p></div>';
    $('#character-detail').innerHTML = '<div class="detail-header opponent-header"><div class="identity"><div class="avatar rival-avatar">'+escapeHtml(opponent.name.charAt(0))+'</div><div><p class="eyebrow">RIVAL DE ARENA · NPC #'+opponent.id+'</p><h2>'+escapeHtml(opponent.name)+'</h2><p>'+escapeHtml(opponent.title)+' · '+escapeHtml(opponent.race)+' '+escapeHtml(opponent.sex)+'</p></div></div><span class="badge danger-soft">Requiere reinicio</span></div><div class="detail-body"><div class="notice">Ares y Nyx son NPC con apariencia de personaje. Aquí puedes modificar su cuerpo, equipo, estadísticas, IA y skills. Cada guardado crea una copia de seguridad del XML.</div><form id="opponent-form">'+
      '<div class="stat-group final-stats-section"><div class="final-stats-head"><div><h4>Stats configurados</h4><p>Valores base del XML, antes de pasivos, buffs y efectos temporales.</p></div><span class="badge">BASE</span></div><div class="final-stats-grid">'+configuredStatTiles(opponent.configuredStats)+'</div>'+liveHtml+'</div>'+buildHtml+
      '<div class="stat-group"><h4>Identidad y apariencia</h4><div class="form-grid three"><div class="field"><label>Nombre</label><input name="name" value="'+escapeHtml(opponent.name)+'"></div><div class="field"><label>Título</label><input name="title" value="'+escapeHtml(opponent.title)+'"></div>'+opponentField('level','Nivel',opponent.level)+'<div class="field"><label>Raza</label><select name="race">'+['HUMAN','ELF','DARK_ELF','ORC','DWARF'].map(function(x){return '<option '+(x===opponent.race?'selected':'')+'>'+x+'</option>';}).join('')+'</select></div><div class="field"><label>Sexo</label><select name="sex"><option '+(opponent.sex==='MALE'?'selected':'')+'>MALE</option><option '+(opponent.sex==='FEMALE'?'selected':'')+'>FEMALE</option></select></div>'+opponentField('classId','Class ID visual',p.classId)+opponentField('hair','Cabello',p.hair)+opponentField('hairColor','Color cabello',p.hairColor)+opponentField('face','Rostro',p.face)+'</div></div>'+
      '<div class="stat-group"><h4>Atributos</h4><div class="form-grid six">'+['str','dex','con','int','wit','men'].map(function(k){return opponentField('stats_'+k,k.toUpperCase(),s[k]);}).join('')+'</div></div>'+
      '<div class="stat-group"><h4>Recursos y combate</h4><div class="form-grid three">'+['hp','hpRegen','mp','mpRegen','cp'].map(function(k){return opponentField('vitals_'+k,k,v[k]);}).join('')+['physical','magical','critical','accuracy','attackSpeed','magicSpeed','reuseDelay','range'].map(function(k){return opponentField('attack_'+k,k,a[k]);}).join('')+['physical','magical','evasion'].map(function(k){return opponentField('defence_'+k,'Def. '+k,d[k]);}).join('')+opponentField('movement_walk','Caminar',m.walk)+opponentField('movement_run','Correr',m.run)+opponentField('movement_hitTime','Hit time',m.hitTime)+'</div></div>'+
      '<div class="stat-group"><h4>Equipo visible</h4><div class="form-grid three">'+['equipHead','equipRHand','equipGloves','equipChest','equipLegs','equipFeet','weaponEnchantLevel','armorEnchantLevel'].map(function(k){return opponentField('appearance_'+k,k,p[k]);}).join('')+'</div></div>'+
      '<div class="stat-group"><h4>Inteligencia artificial</h4><div class="form-grid three"><div class="field"><label>Tipo</label><input name="ai_type" value="'+escapeHtml(opponent.ai.type)+'"></div>'+opponentField('ai_aggroRange','Rango de agresión',opponent.ai.aggroRange)+'<div class="field check-field"><label><input name="ai_isAggressive" type="checkbox" '+(opponent.ai.isAggressive?'checked':'')+'> Ataca automáticamente</label></div></div></div>'+
      '<div class="stat-group"><h4>Rotación usada por la IA</h4><p class="group-help">Estos son los ataques que la estrategia intenta ejecutar.</p><div class="opponent-skill-list">'+opponentSkillRows(opponent.strategy,'strategy')+'</div></div>'+
      '<div class="stat-group"><h4>Skills disponibles</h4><p class="group-help">El icono y el nombre se resuelven desde los archivos reales de Interlude.</p><div class="opponent-skill-list">'+opponentSkillRows(opponent.skills,'skills')+'</div></div>'+
      '<div class="form-actions"><p>'+escapeHtml(opponent.file)+'</p><button class="button primary">Guardar rival</button></div></form></div>';
    $('#opponent-form').onsubmit=async function(event){event.preventDefault();var f=new FormData(event.target);function group(prefix,keys){var result={};keys.forEach(function(k){var value=f.get(prefix+'_'+k);if(value!==null&&value!=='')result[k]=Number(value);});return result;}var payload={name:f.get('name'),title:f.get('title'),level:Number(f.get('level')),race:f.get('race'),sex:f.get('sex'),stats:group('stats',['str','dex','con','int','wit','men']),vitals:group('vitals',['hp','hpRegen','mp','mpRegen','cp']),attack:group('attack',['physical','magical','critical','accuracy','attackSpeed','magicSpeed','reuseDelay','range']),defence:group('defence',['physical','magical','evasion']),movement:group('movement',['walk','run','hitTime']),appearance:group('appearance',['classId','hair','hairColor','face','equipHead','equipRHand','equipGloves','equipChest','equipLegs','equipFeet','weaponEnchantLevel','armorEnchantLevel']),ai:{type:f.get('ai_type'),aggroRange:Number(f.get('ai_aggroRange')),isAggressive:f.get('ai_isAggressive')==='on'},strategy:readOpponentSkills('strategy'),skills:readOpponentSkills('skills')};try{await api('/api/opponents/'+opponent.id,{method:'PATCH',body:JSON.stringify(payload)});toast(opponent.name+' fue actualizado. Reinicia el Game Server.','success');$('#pending-badge').classList.remove('hidden');await loadCharacters();selectOpponent(opponent.id);}catch(error){toast(error.message,'error');}};
  }

  function resourceMetric(label, value, max) {
    return '<div class="metric"><small>'+label+'</small><strong>'+number(value)+' <span class="muted" style="font-size:10px">/ '+number(max)+'</span></strong></div>';
  }

  var comparisonStats=[
    {label:'P. Atk',base:'pAtk',live:'p_atk'}, {label:'M. Atk',base:'mAtk',live:'m_atk'},
    {label:'P. Def',base:'pDef',live:'p_def'}, {label:'M. Def',base:'mDef',live:'m_def'},
    {label:'Atk. Speed',base:'pAtkSpeed',live:'p_atk_speed'}, {label:'Casting Speed',base:'mAtkSpeed',live:'m_atk_speed'},
    {label:'Velocidad',base:'runSpeed',live:'run_speed'}, {label:'Critical Rate',base:'pCritical',live:'p_critical'},
    {label:'Magic Critical',base:null,live:'m_critical'}, {label:'Accuracy',base:'accuracy',live:'accuracy'},
    {label:'Evasion',base:'evasion',live:'evasion'}, {label:'HP max.',base:'maxHp',live:'max_hp'},
    {label:'MP max.',base:'maxMp',live:'max_mp'}, {label:'CP max.',base:'maxCp',live:'max_cp'},
    {label:'STR',base:'str',live:'stat_str'}, {label:'DEX',base:'dex',live:'stat_dex'},
    {label:'CON',base:'con',live:'stat_con'}, {label:'INT',base:'int',live:'stat_int'},
    {label:'WIT',base:'wit',live:'stat_wit'}, {label:'MEN',base:'men',live:'stat_men'}
  ];

  function comparisonValue(entity,definition,mode){
    var source=mode==='live'?entity.liveStats:entity.configuredStats;
    var key=mode==='live'?definition.live:definition.base;
    return !source||!key||source[key]===null||source[key]===undefined?null:Number(source[key]);
  }

  function comparisonCell(value,reference,isPlayer){
    if(value===null||!Number.isFinite(value))return '<span class="comparison-missing">—</span>';
    var html='<strong>'+number(value,2)+'</strong>';
    if(!isPlayer&&reference!==null&&Number.isFinite(reference)){
      var delta=value-reference;
      var ratio=reference!==0?delta/Math.abs(reference)*100:null;
      html+='<small class="comparison-delta '+(delta>0?'above':delta<0?'below':'equal')+'">'+(delta>0?'+':'')+number(delta,2)+(ratio===null?'':' · '+(ratio>0?'+':'')+number(ratio,1)+'%')+'</small>';
    }
    return html;
  }

  function comparisonTable(character,opponents,mode){
    var entities=[character].concat(opponents);
    var names=[character.char_name].concat(opponents.map(function(item){return item.name;}));
    var rows=comparisonStats.map(function(definition){
      var reference=comparisonValue(character,definition,mode);
      return '<tr><th>'+definition.label+'</th>'+entities.map(function(entity,index){return '<td>'+comparisonCell(comparisonValue(entity,definition,mode),reference,index===0)+'</td>';}).join('')+'</tr>';
    }).join('');
    return '<table class="comparison-table"><thead><tr><th>Stat</th>'+names.map(function(name,index){return '<th class="'+(index===0?'player-column':'')+'">'+escapeHtml(name)+(index===0?'<small>referencia</small>':'<small>delta vs. '+escapeHtml(character.char_name)+'</small>')+'</th>';}).join('')+'</tr></thead><tbody>'+rows+'</tbody></table>';
  }

  function comparisonPanel(character,opponents){
    if(!opponents.length)return '';
    var missingFinal=!character.liveStats||opponents.some(function(item){return !item.liveStats;});
    return '<div class="stat-group comparison-section"><div class="final-stats-head"><div><h4>Comparar con Ares y Nyx</h4><p>Las diferencias de los rivales se calculan contra '+escapeHtml(character.char_name)+'.</p></div><div class="comparison-switch"><button type="button" class="compare-mode active" data-compare-mode="live">Finales</button><button type="button" class="compare-mode" data-compare-mode="base">Base</button></div></div>'+
      (missingFinal?'<div class="comparison-warning">Falta una lectura final reciente en uno o más participantes.</div>':'')+
      '<div class="comparison-help" id="comparison-help">Comparación real observada por el Game Server con equipo, skills, pasivos y buffs activos.</div><div class="table-wrap comparison-wrap" id="character-comparison-table">'+comparisonTable(character,opponents,'live')+'</div></div>';
  }

  function renderCharacterDetail(character, opponents) {
    opponents=opponents||[];
    var subs = [1,2,3].map(function (slot) { return character.subclasses.find(function (sub) { return sub.class_index === slot; }); });
    var inventory = character.items.slice(0, 60).map(function (item) { return '<tr><td>#'+item.item_id+'</td><td>'+number(item.count)+'</td><td>+'+item.enchant_level+'</td><td>'+escapeHtml(item.loc)+'</td></tr>'; }).join('');
    var liveHtml=character.liveStats?'<div class="final-stats-head"><div><h4>Tus stats finales observados</h4><p>Lectura real de tu personaje con equipo, skills, pasivos y buffs activos · '+escapeHtml(date(character.liveStats.observed_ms))+'</p></div><span class="badge success">EN VIVO</span></div><div class="final-stats-grid live">'+liveStatTiles(character.liveStats)+'</div>':'<div class="live-stats-empty"><strong>Tus stats finales aún no fueron observados</strong><p>Entra con este personaje y pelea una vez contra un rival de la arena. La telemetría guardará todos tus números reales para compararlos con los del NPC.</p></div>';
    var statsHtml='<div class="stat-group final-stats-section player-stats"><div class="final-stats-head"><div><h4>Tus stats base</h4><p>Plantilla de '+escapeHtml(character.classInfo.name)+' a nivel '+character.level+', sin equipo, pasivos ni buffs.</p></div><span class="badge">BASE</span></div><div class="final-stats-grid">'+configuredStatTiles(character.configuredStats)+'</div>'+liveHtml+'</div>';
    $('#character-detail').innerHTML = '<div class="detail-header"><div class="identity"><div class="avatar">'+escapeHtml(character.char_name.charAt(0))+'</div><div><p class="eyebrow">'+escapeHtml(character.account_name)+'</p><h2>'+escapeHtml(character.char_name)+'</h2><p>'+escapeHtml(character.classInfo.path)+'</p></div></div><span class="badge '+(character.online?'success':'')+'">'+(character.online?'Conectado':'Desconectado')+'</span></div>' +
      '<div class="detail-body">'+statsHtml+comparisonPanel(character,opponents)+'<div class="metric-row">'+resourceMetric('CP',character.curCp,character.maxCp)+resourceMetric('HP',character.curHp,character.maxHp)+resourceMetric('MP',character.curMp,character.maxMp)+'<div class="metric"><small>Skills guardados</small><strong>'+number(character.skillCounts.reduce(function(s,x){return s+Number(x.total);},0))+'</strong></div></div>' +
      '<h4 class="section-title">Build acumulativa</h4><div class="build-slots"><div class="build-slot"><span>Principal</span><strong>'+escapeHtml(character.baseClassInfo.path)+'</strong><small>Nivel '+character.level+'</small></div>' +
      subs.map(function (sub,index) { return '<div class="build-slot"><span>Sub '+(index+1)+'</span><strong>'+(sub?escapeHtml(sub.classInfo.path):'Ranura vacía')+'</strong><small>'+(sub?'Nivel '+sub.level:'')+'</small></div>'; }).join('')+'</div>' +
      '<h4 class="section-title">Atributos de la clase activa</h4><div class="notice">STR, DEX, CON, INT, WIT y MEN no se guardan por personaje: pertenecen a la plantilla de <strong>'+escapeHtml(character.classInfo.name)+'</strong>. El cambio afectará a todos los personajes de esta clase y recalculará sus stats finales después de reiniciar el Game Server.</div>'+
      '<form id="character-attributes-form"><div class="form-grid six">'+statInput('str','STR',character.configuredStats.str)+statInput('dex','DEX',character.configuredStats.dex)+statInput('con','CON',character.configuredStats.con)+statInput('int','INT',character.configuredStats.int)+statInput('wit','WIT',character.configuredStats.wit)+statInput('men','MEN',character.configuredStats.men)+'</div><div class="form-actions"><p>'+(character.online?'Cierra sesión para editar la plantilla con seguridad.':'Se creará una copia del XML antes de guardar.')+'</p><button class="button primary" '+(character.online?'disabled':'')+'>Guardar atributos y requerir reinicio</button></div></form>'+
      '<h4 class="section-title">Edición segura</h4><div class="notice">Estos valores se guardan directamente en la base local. El personaje debe estar desconectado. La estructura de clases se sigue gestionando con Build Lab para que Mobius regenere correctamente todos los skills acumulativos.</div>' +
      '<form id="character-form"><div class="form-grid"><div class="field"><label>Título</label><input name="title" maxlength="21" value="'+escapeHtml(character.title || '')+'"></div><div class="field"><label>Nivel</label><input name="level" type="number" min="1" max="80" value="'+character.level+'"></div><div class="field"><label>SP</label><input name="sp" type="number" min="0" value="'+character.sp+'"></div><div class="field"><label>Adena</label><input name="adena" type="number" min="0" value="'+character.adena+'"></div><div class="field"><label>Access level</label><input name="accesslevel" type="number" min="0" max="100" value="'+character.accesslevel+'"></div></div>' +
      '<div class="form-actions"><p>'+(character.online?'Cierra sesión para habilitar el guardado.':'Los cambios se aplican al próximo ingreso.')+'</p><button class="button primary" '+(character.online?'disabled':'')+'>Guardar personaje</button></div></form>' +
      '<h4 class="section-title">Inventario · '+character.items.length+' entradas</h4><div class="table-wrap"><table><thead><tr><th>Item ID</th><th>Cantidad</th><th>Enchant</th><th>Ubicación</th></tr></thead><tbody>'+inventory+'</tbody></table></div></div>';
    $('#character-form').onsubmit = async function (event) {
      event.preventDefault();
      var form = new FormData(event.target);
      var payload = { title:form.get('title'), level:Number(form.get('level')), sp:Number(form.get('sp')), adena:Number(form.get('adena')), accesslevel:Number(form.get('accesslevel')) };
      try { await api('/api/characters/'+character.charId,{method:'PATCH',body:JSON.stringify(payload)}); toast('Personaje actualizado.','success'); await loadCharacters(); }
      catch(error){toast(error.message,'error');}
    };
    $('#character-attributes-form').onsubmit=async function(event){
      event.preventDefault();var form=new FormData(event.target),payload={};['str','dex','con','int','wit','men'].forEach(function(key){payload[key]=Number(form.get(key));});
      try{await api('/api/characters/'+character.charId+'/base-stats',{method:'PATCH',body:JSON.stringify(payload)});toast('Atributos base guardados. Reinicia el Game Server para recalcular los finales.','success');$('#pending-badge').classList.remove('hidden');await selectCharacter(character.charId);}
      catch(error){toast(error.message,'error');}
    };
    $$('[data-compare-mode]').forEach(function(button){button.onclick=function(){var mode=button.dataset.compareMode;$$('[data-compare-mode]').forEach(function(item){item.classList.toggle('active',item===button);});$('#character-comparison-table').innerHTML=comparisonTable(character,opponents,mode);$('#comparison-help').textContent=mode==='live'?'Comparación real observada por el Game Server con equipo, skills, pasivos y buffs activos.':'Valores configurados: XML propio del NPC frente a la plantilla desnuda de la clase del jugador. Es orientativa, no mide fuerza real.';};});
  }

  async function prepareCreator() {
    try {
      if (!state.classes.length) state.classes = await api('/api/classes');
      var finalClasses=state.classes.filter(function(item){return item.stage===3;});
      var races=Array.from(new Set(finalClasses.map(function(item){return item.race;}))).sort();
      var raceSelect=$('#creator-race');
      if (!raceSelect.options.length) raceSelect.innerHTML=races.map(function(race){return '<option>'+escapeHtml(race)+'</option>';}).join('');
      function options(list,empty){return (empty?'<option value="">Sin elegir</option>':'')+list.map(function(item){return '<option value="'+item.id+'">'+escapeHtml(item.name)+' · '+escapeHtml(item.path)+'</option>';}).join('');}
      function refreshPrimary(){var race=raceSelect.value,filtered=finalClasses.filter(function(item){return item.race===race;});$('#creator-primary').innerHTML=options(filtered,false);}
      refreshPrimary();
      ['#creator-sub1','#creator-sub2','#creator-sub3'].forEach(function(selector){if(!$(selector).options.length)$(selector).innerHTML=options(finalClasses,true);});
      raceSelect.onchange=refreshPrimary;
    } catch(error){toast(error.message,'error');}
  }

  $('#creator-form').onsubmit=async function(event){
    event.preventDefault();var f=new FormData(event.target);var button=$('button[type="submit"]',event.target);button.disabled=true;
    var payload={name:f.get('name'),title:f.get('title'),sex:f.get('sex'),level:Number(f.get('level')),profile:f.get('profile'),primaryClassId:Number(f.get('primaryClassId')),subclasses:[f.get('sub1')||null,f.get('sub2')||null,f.get('sub3')||null],accumulateSkills:f.get('accumulateSkills')==='on'};
    try{var result=await api('/api/opponents',{method:'POST',body:JSON.stringify(payload)});toast(result.name+' creado con '+result.skillCount+' skills.','success');$('#pending-badge').classList.remove('hidden');event.target.reset();state.opponents=[];setView('characters');await loadCharacters();selectOpponent(result.id);}catch(error){toast(error.message,'error');}finally{button.disabled=false;}
  };

  async function loadClasses() {
    $('#class-list').innerHTML = '<div class="loading">Leyendo árbol de clases…</div>';
    try {
      state.classes = await api('/api/classes');
      var races = Array.from(new Set(state.classes.map(function (item) { return item.race; }))).sort();
      $('#race-filter').innerHTML = '<option value="">Todas</option>'+races.map(function(r){return '<option>'+escapeHtml(r)+'</option>';}).join('');
      renderClasses();
      if (!state.selectedClass) selectClass(88);
    } catch(error){$('#class-list').innerHTML='<div class="empty-state compact">'+escapeHtml(error.message)+'</div>';}
  }

  function renderClasses() {
    var query = $('#class-search').value.trim().toLowerCase(), race=$('#race-filter').value, stage=$('#stage-filter').value;
    var filtered=state.classes.filter(function(item){return(!query||item.name.toLowerCase().indexOf(query)!==-1||String(item.id)===query)&&(!race||item.race===race)&&(stage===''||String(item.stage)===stage);});
    $('#class-list').innerHTML=filtered.map(function(item){return '<button class="select-item '+(state.selectedClass===item.id?'active':'')+'" data-class="'+item.id+'"><div><strong>'+escapeHtml(item.name)+'</strong><small>'+escapeHtml(item.path)+'</small></div><div style="text-align:right"><span class="skill-id">#'+item.id+'</span><small>'+escapeHtml(item.race)+'</small></div></button>';}).join('')||'<div class="empty-state compact">Sin resultados.</div>';
    $$('[data-class]').forEach(function(button){button.onclick=function(){selectClass(Number(button.dataset.class));};});
  }

  async function selectClass(id) {
    state.selectedClass=id;renderClasses();$('#class-detail').innerHTML='<div class="loading">Abriendo plantilla…</div>';
    try{renderClassDetail(await api('/api/classes/'+id));}catch(error){$('#class-detail').innerHTML='<div class="empty-state">'+escapeHtml(error.message)+'</div>';}
  }

  function statInput(name,label,value){return '<div class="field"><label>'+label+'</label><input name="'+name+'" type="number" step="any" min="0" value="'+escapeHtml(value)+'"></div>';}
  function renderClassDetail(info) {
    var s=info.staticStats,l=info.level80;
    $('#class-detail').innerHTML='<div class="detail-header"><div><p class="eyebrow">'+escapeHtml(info.classInfo.race)+' · '+escapeHtml(info.classInfo.stageName)+' · #'+info.classInfo.id+'</p><h2>'+escapeHtml(info.classInfo.name)+'</h2><p>'+escapeHtml(info.classInfo.path)+'</p></div><span class="badge">XML de servidor</span></div><div class="detail-body"><div class="notice">La edición afecta a todos los personajes de esta clase. Se guarda una copia y el cambio entra en vigor tras reiniciar el Game Server.</div><form id="class-form">' +
      '<div class="stat-group"><h4>Atributos base</h4><div class="form-grid six">'+statInput('baseSTR','STR',s.baseSTR)+statInput('baseDEX','DEX',s.baseDEX)+statInput('baseCON','CON',s.baseCON)+statInput('baseINT','INT',s.baseINT)+statInput('baseWIT','WIT',s.baseWIT)+statInput('baseMEN','MEN',s.baseMEN)+'</div></div>' +
      '<div class="stat-group"><h4>Combate y movimiento</h4><div class="form-grid three">'+statInput('basePAtk','P. Atk base',s.basePAtk)+statInput('baseMAtk','M. Atk base',s.baseMAtk)+statInput('basePAtkSpd','Atk. Speed base',s.basePAtkSpd)+statInput('baseCritRate','Critical base',s.baseCritRate)+statInput('baseAtkRange','Rango de ataque',s.baseAtkRange)+statInput('baseRndDam','Variación de daño',s.baseRndDam)+statInput('walk','Velocidad caminando',s.walk)+statInput('run','Velocidad corriendo',s.run)+'</div></div>' +
      '<div class="stat-group"><h4>Progresión al nivel 80</h4><div class="form-grid three">'+statInput('l80_hp','HP',l.hp)+statInput('l80_mp','MP',l.mp)+statInput('l80_cp','CP',l.cp)+statInput('l80_hpRegen','Regen. HP',l.hpRegen)+statInput('l80_mpRegen','Regen. MP',l.mpRegen)+statInput('l80_cpRegen','Regen. CP',l.cpRegen)+'</div></div>' +
      '<div class="form-actions"><p>'+escapeHtml(info.file)+'</p><button class="button primary">Guardar balance</button></div></form></div>';
    $('#class-form').onsubmit=async function(event){event.preventDefault();var f=new FormData(event.target),staticStats={},level80={};Object.keys(s).forEach(function(k){staticStats[k]=Number(f.get(k));});Object.keys(l).forEach(function(k){level80[k]=Number(f.get('l80_'+k));});try{await api('/api/classes/'+info.classInfo.id,{method:'PATCH',body:JSON.stringify({staticStats:staticStats,level80:level80})});toast('Balance guardado con copia de seguridad.','success');$('#pending-badge').classList.remove('hidden');}catch(error){toast(error.message,'error');}};
  }

  async function searchSkills(query) {
    $('#skill-list').innerHTML='<div class="loading">Indexando skills…</div>';
    try{state.skills=await api('/api/skills?q='+encodeURIComponent(query||'')+'&limit=120');renderSkills();if(state.skills.length&&(!state.selectedSkill||query))selectSkill(state.skills[0].id);}catch(error){$('#skill-list').innerHTML='<div class="empty-state compact">'+escapeHtml(error.message)+'</div>';}
  }
  function renderSkills(){$('#skill-list').innerHTML=state.skills.map(function(skill){return '<button class="select-item skill-select '+(state.selectedSkill===skill.id?'active':'')+'" data-skill="'+skill.id+'">'+skillIcon(skill)+'<div class="select-copy"><strong>'+escapeHtml(skill.name)+'</strong><small>'+escapeHtml(skill.file)+'</small></div><div style="text-align:right"><span class="skill-id">#'+skill.id+'</span><small>'+skill.levels+' niveles</small></div></button>';}).join('')||'<div class="empty-state compact">Sin resultados.</div>';$$('[data-skill]').forEach(function(button){button.onclick=function(){selectSkill(Number(button.dataset.skill));};});}
  async function selectSkill(id){state.selectedSkill=id;renderSkills();$('#skill-detail').innerHTML='<div class="loading">Leyendo skill…</div>';try{renderSkillDetail(await api('/api/skills/'+id));}catch(error){$('#skill-detail').innerHTML='<div class="empty-state">'+escapeHtml(error.message)+'</div>';}}
  function renderSkillDetail(skill){var preferred=['power','mpConsume','ench1Power','ench2MpConsume'];var tableNames=Object.keys(skill.tables).sort(function(a,b){var ai=preferred.indexOf(a),bi=preferred.indexOf(b);if(ai===-1)ai=99;if(bi===-1)bi=99;return ai-bi||a.localeCompare(b);});var tableRows=tableNames.map(function(name){var count=skill.tables[name].trim().split(/\s+/).length;return '<div class="editor-row"><label>#'+escapeHtml(name)+'<small>'+count+' valores</small></label><div class="field"><textarea name="table_'+escapeHtml(name)+'">'+escapeHtml(skill.tables[name])+'</textarea></div></div>';}).join('');var valueRows=Object.keys(skill.values).map(function(name){return '<div class="field"><label>'+escapeHtml(name)+'</label><input name="value_'+escapeHtml(name)+'" value="'+escapeHtml(skill.values[name])+'"></div>';}).join('');$('#skill-detail').innerHTML='<div class="detail-header"><div class="identity">'+skillIcon(skill,true)+'<div><p class="eyebrow">SKILL #'+skill.id+' · '+skill.levels+' NIVELES</p><h2>'+escapeHtml(skill.name)+'</h2><div class="skill-meta"><span class="badge">'+escapeHtml(skill.operateType||'sin operateType')+'</span><span class="badge">Target '+escapeHtml(skill.targetType||'—')+'</span><span class="badge">'+escapeHtml(skill.icon||'sin icono')+'</span></div></div></div><span class="badge">XML</span></div><div class="detail-body"><div class="notice">Los valores separados por espacios corresponden a niveles consecutivos. Mantén la misma cantidad salvo que también cambies la definición de niveles.</div><form id="skill-form"><h4 class="section-title">Valores directos</h4><div class="form-grid three">'+(valueRows||'<p class="muted">Este skill no tiene valores directos editables.</p>')+'</div><h4 class="section-title">Tablas por nivel</h4><div class="editor-list">'+(tableRows||'<p class="muted">Este skill no contiene tablas numéricas.</p>')+'</div><div class="form-actions"><p>'+escapeHtml(skill.file)+'</p><button class="button primary">Guardar skill</button></div></form></div>';$('#skill-form').onsubmit=async function(event){event.preventDefault();var f=new FormData(event.target),tables={},values={};tableNames.forEach(function(name){tables[name]=f.get('table_'+name);});Object.keys(skill.values).forEach(function(name){values[name]=f.get('value_'+name);});try{await api('/api/skills/'+skill.id,{method:'PATCH',body:JSON.stringify({tables:tables,values:values})});toast('Skill guardado con copia de seguridad.','success');$('#pending-badge').classList.remove('hidden');}catch(error){toast(error.message,'error');}};}

  async function loadTelemetry(){
    var loadingIds=['fight-list','telemetry-catalog','telemetry-pairs','telemetry-build-candidates','telemetry-finalists','telemetry-benchmarks','telemetry-coverage','telemetry-external-references','telemetry-nyx-calibration','telemetry-magic-progression'];
    loadingIds.forEach(function(id){var node=$('#'+id);if(node)node.innerHTML='<div class="loading">Actualizando telemetría…</div>';});
    try{
      var result=await Promise.all([
        api('/api/telemetry/fights'),api('/api/telemetry/catalog'),api('/api/telemetry/coverage'),
        api('/api/telemetry/pairs'),api('/api/telemetry/build-candidates'),api('/api/telemetry/finalists'),
        api('/api/telemetry/benchmarks'),api('/api/telemetry/external-references'),api('/api/telemetry/nyx-calibration'),
        api('/api/telemetry/magic-progression')
      ]);
      state.fights=result[0];state.catalog=result[1];state.coverage=result[2];state.pairs=result[3];
      state.buildCandidates=result[4];state.finalists=result[5];state.benchmarks=result[6];
      state.externalReferences=result[7];state.nyxCalibration=result[8];
      state.magicProgression=result[9];
      renderCoverage();renderPairs();renderBuildCandidates();renderFinalists();renderBenchmarks();
      renderExternalReferences();renderNyxCalibration();renderMagicProgression();renderCatalog();renderFights();
      if(state.fights.length){
        if(!state.selectedFight||!state.fights.some(function(f){return f.id===state.selectedFight;}))state.selectedFight=state.fights[0].id;
        selectFight(state.selectedFight);
      }else{
        $('#fight-detail').innerHTML='<div class="panel empty-state"><span>⌁</span><h3>Aún no hay una pelea completa</h3><p>Reinicia el servidor para activar el capturador, entra a la arena y ataca a Ares o Nyx.</p></div>';
      }
    }catch(error){
      loadingIds.forEach(function(id){var node=$('#'+id);if(node)node.innerHTML='<div class="empty-state compact">'+escapeHtml(error.message)+'</div>';});
    }
  }
  function renderCoverage(){var c=state.coverage;if(!c)return;var p=c.pairs||{measured:0,total:465};var b=c.builds||{generated:0,total:125860,measured:0,targetSelected:155};var f=state.finalists||[];var q=state.benchmarks||[];var refs=state.externalReferences||[];var calibration=state.nyxCalibration||{totalRuns:0,expectedRuns:360};var planned=q.reduce(function(sum,item){return sum+item.repetitions;},0);var completed=q.reduce(function(sum,item){return sum+item.completedRuns;},0);var phase5Value=(refs.length?1:0)+(calibration.totalRuns===calibration.expectedRuns?1:0);var phase5State=phase5Value===2?'Completa':phase5Value>0?'En curso':'Pendiente';$('#coverage-count').textContent=number(c.measured)+' / '+number(c.total);var phases=[{name:'Plantel físico',value:c.roster.measured,total:c.roster.total,state:c.roster.measured===c.roster.total?'Completa':'En curso'},{name:'Clases limpias',value:c.measured,total:c.total,state:c.measured===c.total?'Completa':'En curso'},{name:'Parejas',value:p.measured,total:p.total,state:p.measured===p.total?'Completa':p.measured>0?'En curso':'Pendiente'},{name:'Candidatos 4A',value:b.generated,total:b.total,state:b.generated===b.total?'Completa':b.generated>0?'En curso':'Pendiente'},{name:'Builds reales 4B',value:b.measured,total:b.targetSelected,state:b.measured===b.targetSelected?'Completa':b.measured>0?'En curso':'Pendiente'},{name:'Finalistas 4C',value:f.length,total:30,state:f.length===30?'Completa':f.length>0?'En curso':'Pendiente'},{name:'Combate 4D',value:completed,total:planned||285,state:planned&&completed===planned?'Completa':planned?'En curso':'Pendiente'},{name:'Fase 5A',value:phase5Value,total:2,state:phase5State}];var phaseHtml=phases.map(function(item,index){return '<div class="phase-step '+(item.state==='Completa'?'complete':item.state==='En curso'?'current':'')+'"><b>'+(index<9?'0':'')+(index+1)+'</b><span>'+escapeHtml(item.name)+'</span><strong>'+number(item.value)+' / '+number(item.total)+'</strong></div>';}).join('');var stages=c.stages.map(function(item){return '<div class="coverage-cell"><span>'+escapeHtml(item.name)+'</span><strong>'+number(item.measured)+' / '+number(item.total)+'</strong><i><b style="width:'+percent(item.measured,item.total)+'%"></b></i></div>';}).join('');var races=c.races.map(function(item){return '<div class="coverage-race"><span>'+escapeHtml(item.name)+'</span><strong>'+number(item.measured)+' / '+number(item.total)+'</strong></div>';}).join('');var roots=c.roots.map(function(item){return '<div class="coverage-root"><span>'+escapeHtml(item.name)+'</span><small>'+escapeHtml(item.race)+'</small><strong>'+number(item.measured)+' / '+number(item.total)+'</strong></div>';}).join('');var next=c.missing.slice(0,12).map(function(item){return '<span class="coverage-missing">#'+item.id+' '+escapeHtml(item.name)+'</span>';}).join('');$('#telemetry-coverage').innerHTML='<div class="phase-track">'+phaseHtml+'</div><div class="notice">Lectura comparable: '+escapeHtml(c.criteria)+'. Las muestras con buffs o equipo se conservan, pero no completan esta base.</div><div class="coverage-grid">'+stages+'</div><div class="coverage-races">'+races+'</div><div class="coverage-next"><small>NUEVE RAMAS INICIALES</small><div class="coverage-roots">'+roots+'</div></div><div class="coverage-next"><small>PRÓXIMAS CLASES SIN MEDIR</small><div>'+(next||'<span class="context-clean">Cobertura base completa</span>')+'</div></div>';}
  function renderPairs(){var p=state.coverage&&state.coverage.pairs?state.coverage.pairs:{measured:0,total:465,states:0,totalStates:930,skillMismatches:0};$('#pair-count').textContent=number(p.measured)+' / '+number(p.total);var rows=state.pairs.slice(0,150).map(function(pair){var states=pair.states.slice().sort(function(a,b){return a.index-b.index;});var stateHtml=states.map(function(s){return '<strong>'+escapeHtml(s.index===0?'Principal: ':'Sub: ')+escapeHtml(s.active.name)+'</strong><span class="build-mini">P.Atk '+number(s.pAtk,1)+' · M.Atk '+number(s.mAtk,1)+' · P.Def '+number(s.pDef,1)+' · M.Def '+number(s.mDef,1)+'</span>';}).join('');var counts=states.length?states.map(function(s){return number(s.skillCount);}).join(' / '):'—';return '<tr><td><strong>'+escapeHtml(pair.first.name)+' + '+escapeHtml(pair.second.name)+'</strong><span class="build-mini">'+escapeHtml(String(pair.race||'').replace('_',' '))+'</span></td><td>'+number(pair.sharedSkills)+'</td><td>'+number(pair.masteryCollisions)+'</td><td>'+counts+'<span class="build-mini">esperadas '+number(pair.expectedSkills)+'</span></td><td>'+stateHtml+'</td></tr>';}).join('');var summary='<div class="notice">'+number(p.states)+' / '+number(p.totalStates)+' estados limpios · '+number(p.skillMismatches)+' diferencias entre skills esperadas y restauradas. Se muestran primero las 150 parejas con más solapamientos.</div>';$('#telemetry-pairs').innerHTML=summary+'<table><thead><tr><th>Pareja</th><th>Skills compartidas</th><th>Masteries pisadas</th><th>Skills Principal / Sub</th><th>Estados activos</th></tr></thead><tbody>'+(rows||'<tr><td colspan="5">La medición comenzará al reiniciar el Game Server.</td></tr>')+'</tbody></table>';}
  function renderBuildCandidates(){var summary=state.coverage&&state.coverage.builds?state.coverage.builds:{generated:0,total:125860,selected:0,targetSelected:155,skillSets:0,measured:0,states:0,totalStates:620,skillMismatches:0};$('#build-candidate-count').textContent=number(summary.generated)+' / '+number(summary.total);var rows=state.buildCandidates.map(function(build){var subs=build.subclasses.map(function(item){return item.name;}).join(' + ');var measured=(build.states||[]).length;return '<tr><td><strong>'+escapeHtml(build.main.name)+'</strong><span class="build-mini">'+escapeHtml(build.main.race)+' · Principal</span></td><td>'+escapeHtml(subs)+'</td><td><span class="context-clean">'+escapeHtml(build.bucket)+'</span><span class="build-mini">'+escapeHtml(build.composition)+' · '+number(build.races)+' razas</span></td><td><strong>'+number(build.skillCount)+'</strong><span class="build-mini">'+number(build.passiveSkills)+' pasivas · '+number(build.activeSkills)+' activas</span></td><td>'+number(build.sharedScore)+'</td><td>'+number(build.masteryScore)+'</td><td><span class="'+(measured===4?'context-clean':'context-active')+'">'+number(measured)+' / 4</span></td></tr>';}).join('');var notice='<div class="notice">4A: '+number(summary.generated)+' candidatos · '+number(summary.skillSets)+' conjuntos únicos · '+number(summary.selected)+' seleccionados. 4B: '+number(summary.measured)+' / '+number(summary.targetSelected)+' builds y '+number(summary.states)+' / '+number(summary.totalStates)+' estados reales · '+number(summary.skillMismatches)+' diferencias.</div>';$('#telemetry-build-candidates').innerHTML=notice+'<table><thead><tr><th>Principal</th><th>Sub 1 + Sub 2 + Sub 3</th><th>Criterio</th><th>Skills previstas</th><th>Solapamiento</th><th>Masteries</th><th>Estados reales</th></tr></thead><tbody>'+(rows||'<tr><td colspan="7">La Fase 4A todavía no generó candidatos.</td></tr>')+'</tbody></table>';}
  function renderFinalists(){var finalists=state.finalists||[];$('#finalist-count').textContent=number(finalists.length)+' / 30';var scoreKey={'física':'physical','mágica':'magical','tanque':'tank','soporte':'support','summoner':'summoner','híbrida':'hybrid'};var rows=finalists.map(function(build){var subs=build.subclasses.map(function(item){return item.name;}).join(' + ');var key=scoreKey[build.category]||'hybrid';return '<tr><td><strong>#'+number(build.rank)+' '+escapeHtml(build.main.name)+'</strong><span class="build-mini">'+escapeHtml(build.main.race)+' · principal</span></td><td>'+escapeHtml(subs)+'</td><td><span class="context-clean">'+escapeHtml(build.category)+'</span><span class="build-mini">'+escapeHtml(build.type)+'</span></td><td><strong>'+number(build.scores[key],2)+'</strong><span class="build-mini">índice relativo</span></td><td>P.Atk '+number(build.gains.pAtk,1)+'% · M.Atk '+number(build.gains.mAtk,1)+'%<span class="build-mini">P.Def '+number(build.gains.pDef,1)+'% · M.Def '+number(build.gains.mDef,1)+'%</span></td><td>'+number(build.skillCount)+'<span class="build-mini">'+number(build.sharedScore)+' solap. · '+number(build.masteryScore)+' masteries</span></td><td>'+escapeHtml(build.reason)+'</td></tr>';}).join('');var categories={};finalists.forEach(function(build){categories[build.category]=(categories[build.category]||0)+1;});var distribution=Object.keys(categories).map(function(name){return escapeHtml(name)+' '+number(categories[name]);}).join(' · ');$('#telemetry-finalists').innerHTML='<div class="notice">'+(distribution||'La selección todavía no fue generada')+'. Los porcentajes son medias geométricas frente al perfil limpio de cada clase activa.</div><table><thead><tr><th>Principal</th><th>Sub 1 + Sub 2 + Sub 3</th><th>Categoría</th><th>Índice</th><th>Ganancias relativas</th><th>Skills</th><th>Motivo</th></tr></thead><tbody>'+(rows||'<tr><td colspan="7">Ejecuta la Fase 4C para crear los finalistas.</td></tr>')+'</tbody></table>';}
  function renderBenchmarks(){var cases=state.benchmarks||[];var planned=cases.reduce(function(sum,item){return sum+item.repetitions;},0);var completed=cases.reduce(function(sum,item){return sum+item.completedRuns;},0);$('#benchmark-count').textContent=number(completed)+' / '+number(planned||285);function resultText(item){var r=item.result;if(!r||!r.runs)return '<span class="context-active">Pendiente</span>';if(item.code==='salida_fisica'||item.code==='salida_magica')return '<strong>'+number(r.dps,1)+' DPS</strong><span class="build-mini">'+number(r.critRate,1)+'% críticos · '+number(r.mpUsed,0)+' MP</span>';if(item.code==='salida_invocacion')return '<strong>'+number(r.dps,1)+' DPS total</strong><span class="build-mini">dueño '+number(r.ownerDps,1)+' · invocación '+number(r.summonDps,1)+' · '+number(r.summonUptime,1)+' s activa</span>';if(item.code==='soporte_sostenido')return '<strong>'+number(r.hps,1)+' HPS</strong><span class="build-mini">'+number(r.overheal,0)+' overheal · '+number(r.mpUsed,0)+' MP</span>';return '<strong>'+number(r.timeAlive,1)+' s con vida</strong><span class="build-mini">'+number(r.damageReceived,0)+' daño · '+number(r.hpCpRemaining,0)+' HP+CP · '+number(r.controlTime,1)+' s control</span>';}var rows=cases.map(function(item){var build=[item.main].concat(item.subclasses).map(function(c){return c.name;}).join(' + ');var slot=item.activeIndex===0?'Principal':'Sub '+item.activeIndex;return '<tr><td><strong>#'+number(item.rank)+' '+escapeHtml(item.category)+'</strong><span class="build-mini">'+escapeHtml(build)+'</span></td><td><strong>'+escapeHtml(item.code.replace(/_/g,' '))+'</strong><span class="build-mini">prioridad '+number(item.priority)+'</span></td><td>'+escapeHtml(item.active.name)+'<span class="build-mini">'+escapeHtml(slot)+'</span></td><td>'+escapeHtml(item.opponent)+'</td><td>'+escapeHtml(item.equipmentKit.replace(/_/g,' '))+'<span class="build-mini">#'+number(item.weaponId)+' '+escapeHtml(item.weaponName)+' · '+escapeHtml(item.buffKit.replace(/_/g,' '))+'</span></td><td>'+number(item.duration)+' s × '+number(item.repetitions)+'</td><td>'+resultText(item)+'</td><td><span class="'+(item.completedRuns===item.repetitions?'context-clean':'context-active')+'">'+number(item.completedRuns)+' / '+number(item.repetitions)+'</span><span class="build-mini">'+escapeHtml(item.status)+'</span></td></tr>';}).join('');$('#telemetry-benchmarks').innerHTML='<div class="notice">'+number(cases.length)+' casos · '+number(planned)+' pasadas · '+number(completed)+' completadas. Promedios de 3 repeticiones con motor CORE_ACCELERATED: usa clases, objetos y fórmulas reales con reloj acelerado.</div><table><thead><tr><th>Finalista</th><th>Ensayo</th><th>Clase activa</th><th>Objetivo</th><th>Equipo / arma</th><th>Duración</th><th>Resultado medio</th><th>Avance</th></tr></thead><tbody>'+(rows||'<tr><td colspan="8">La Fase 4D todavía no tiene una cola preparada.</td></tr>')+'</tbody></table>';}

  function renderExternalReferences(){
    var references=state.externalReferences||[];
    $('#external-reference-count').textContent=number(references.length)+' referencia'+(references.length===1?'':'s');
    var cards=references.map(function(reference){
      if(reference.status==='invalid')return '<article class="external-reference-card"><h4>'+escapeHtml(reference.name)+'</h4><p class="danger">'+escapeHtml(reference.error)+'</p></article>';
      var identity=reference.identity||{};var model=reference.buildModel||{};var rules=reference.combatRules||{};var comparison=reference.comparisonWithLocalLab||{};
      var sources=(reference.sources||[]).map(function(source){return '<a href="'+escapeHtml(source.url)+'" target="_blank" rel="noreferrer">'+escapeHtml(source.label)+'</a>';}).join(' · ');
      var differences=(comparison.differences||[]).map(function(item){return '<li>'+escapeHtml(item)+'</li>';}).join('');
      return '<article class="external-reference-card"><div class="external-reference-title"><div><p class="eyebrow">CAPTURA '+escapeHtml(String(reference.capturedAt||'').slice(0,10))+'</p><h4>'+escapeHtml(reference.name)+'</h4></div><span class="context-active">'+escapeHtml(reference.status)+'</span></div>'+
        '<div class="external-reference-metrics"><span><small>Crónica</small><strong>'+escapeHtml(identity.chronicle||'—')+' / '+escapeHtml(identity.skillSet||'—')+'</strong></span><span><small>Nivel</small><strong>'+number(identity.maxLevel)+'</strong></span><span><small>Build</small><strong>'+escapeHtml(model.label||'—')+'</strong></span><span><small>Buffs</small><strong>'+number(rules.buffSlotsBase)+' / '+number(rules.buffSlotsWithDivineInspiration)+'</strong></span></div>'+
        '<p>'+escapeHtml(rules.masteries||'Masteries no documentadas.')+'</p><p>'+escapeHtml(rules.frenzyGutsTotems||'Frenzy/Guts/totems no documentados.')+'</p>'+
        (differences?'<details><summary>Diferencias con el laboratorio</summary><ul>'+differences+'</ul></details>':'')+
        '<div class="external-reference-links">'+sources+'</div></article>';
    }).join('');
    $('#telemetry-external-references').innerHTML=cards||'<div class="empty-state compact">Todavía no hay expedientes externos.</div>';
  }

  function renderNyxCalibration(){
    var calibration=state.nyxCalibration||{expectedRuns:360,totalRuns:0,targetSeconds:{min:10,max:20},profiles:[]};
    $('#nyx-calibration-count').textContent=number(calibration.totalRuns)+' / '+number(calibration.expectedRuns);
    var target=calibration.targetSeconds||{min:10,max:20};
    var profiles=calibration.profiles||[];
    var closest=profiles.slice().sort(function(a,b){return Math.abs(a.timeAlive-15)-Math.abs(b.timeAlive-15);})[0];
    var rows=profiles.map(function(profile){
      var within=profile.timeAlive>=target.min&&profile.timeAlive<=target.max;
      var categories=(profile.categories||[]).map(function(item){return escapeHtml(item.name)+' '+number(item.timeAlive,1)+' s';}).join(' · ');
      return '<tr><td><strong>'+escapeHtml(profile.label)+'</strong><span class="build-mini">'+number(profile.cases)+' / 30 casos</span></td><td>'+number(profile.runs)+' / 90</td><td><strong>'+number(profile.timeAlive,2)+' s</strong><span class="build-mini">'+number(profile.minTimeAlive,2)+'–'+number(profile.maxTimeAlive,2)+' s</span></td><td>'+number(profile.damageReceived,0)+'</td><td>'+number(profile.hpCpRemaining,0)+'</td><td>'+number(profile.controlTime,2)+' s</td><td><span class="'+(within?'context-clean':'context-active')+'">'+(within?'En objetivo':'Fuera de 10–20 s')+'</span><span class="build-mini">'+number(profile.targetRuns)+' pasadas en rango</span></td><td><span class="build-mini">'+categories+'</span></td></tr>';
    }).join('');
    var recommendation=closest?'<div class="notice">Perfil más cercano al centro de 15 s: <strong>'+escapeHtml(closest.label)+'</strong> con '+number(closest.timeAlive,2)+' s de media. Esta lectura orienta la siguiente ronda; no modifica el NPC Nyx original.</div>':'<div class="notice">La cola se ejecutará automáticamente cuando el Game Server reinicie y no haya jugadores conectados. La fase 4D permanece intacta.</div>';
    $('#telemetry-nyx-calibration').innerHTML=recommendation+'<table><thead><tr><th>Perfil</th><th>Pasadas</th><th>Supervivencia</th><th>Daño recibido</th><th>HP+CP restante</th><th>Control</th><th>Objetivo</th><th>Por categoría</th></tr></thead><tbody>'+(rows||'<tr><td colspan="8">Calibración pendiente.</td></tr>')+'</tbody></table>';
  }

  function renderMagicProgression(){
    var progression=state.magicProgression||{expectedRuns:12,totalRuns:0,stages:[],elite:null};
    var stages=progression.stages||[];
    var elite=progression.elite;
    $('#magic-progression-count').textContent=number(progression.totalRuns)+' / '+number(progression.expectedRuns);
    var eliteNotice=elite?'<div class="notice">Nyx Élite queda como referencia separada e intacta: <strong>'+number(elite.mAtk,1)+' M.Atk</strong> · '+number(elite.mAtkSpeed,0)+' cast. La progresión usa una Dark Mystic real, Arcana Mace +0, equipo S común, Blessed Spiritshots y Storm Screamer activo en las cuatro etapas.</div>':'<div class="notice">Nyx Élite permanece fuera de esta progresión. La referencia aparecerá cuando el catálogo del NPC esté disponible.</div>';
    var rows=stages.map(function(stage){
      var build=[stage.main].concat(stage.subclasses||[]).filter(Boolean).map(function(item){return item.name;}).join(' + ');
      var gain=stage.index===0?'Base':'M.Atk '+(stage.gains.mAtk>=0?'+':'')+number(stage.gains.mAtk,1)+'% · DPS '+(stage.gains.dps>=0?'+':'')+number(stage.gains.dps,1)+'%';
      return '<tr><td><strong>'+escapeHtml(stage.label)+'</strong><span class="build-mini">'+escapeHtml(build)+'</span></td><td>'+number(stage.runs)+' / 3</td><td><strong>'+number(stage.skillCount,0)+'</strong><span class="build-mini">'+number(stage.passiveSkills,0)+' pasivas · '+number(stage.activeSkills,0)+' activas</span></td><td><strong>'+number(stage.mAtk,1)+'</strong><span class="build-mini">'+escapeHtml(gain)+'</span></td><td>'+number(stage.mAtkSpeed,0)+'<span class="build-mini">'+(stage.gains.mAtkSpeed>=0?'+':'')+number(stage.gains.mAtkSpeed,1)+'%</span></td><td><strong>'+number(stage.dps,1)+'</strong><span class="build-mini">'+number(stage.damage,0)+' daño / 60 s</span></td><td>'+number(stage.casts,1)+'<span class="build-mini">'+number(stage.criticalRate,1)+'% críticos</span></td><td>'+number(stage.mpUsed,0)+'<span class="build-mini">'+escapeHtml(stage.rotation||'—')+'</span></td></tr>';
    }).join('');
    $('#telemetry-magic-progression').innerHTML=eliteNotice+'<table><thead><tr><th>Etapa / build</th><th>Pasadas</th><th>Skills</th><th>M.Atk</th><th>Cast</th><th>DPS</th><th>Lanzamientos</th><th>MP / rotación</th></tr></thead><tbody>'+(rows||'<tr><td colspan="8">La progresión comenzará al reiniciar el Game Server sin jugadores conectados.</td></tr>')+'</tbody></table>';
  }

  function renderCatalog(){var rows=state.catalog.map(function(p){var build=[p.baseClassInfo].concat(p.subclasses||[]).filter(Boolean).map(function(c){return c.name;}).join(' + ');var context=Number(p.effect_count)===0?'Limpio':'Con '+number(p.effect_count)+' efectos';return '<tr><td><strong>'+escapeHtml(p.name)+'</strong><span class="build-mini">'+escapeHtml(build)+'</span></td><td>'+escapeHtml(String(p.race_name||'').replace('_',' '))+'</td><td><strong>'+escapeHtml(p.slotName)+'</strong><span class="build-mini">'+escapeHtml(p.classInfo.name)+'</span></td><td>'+number(p.level)+'</td><td>'+number(p.p_atk,1)+'</td><td>'+number(p.m_atk,1)+'</td><td>'+number(p.p_def,1)+'</td><td>'+number(p.m_def,1)+'</td><td>'+number(p.max_hp)+' / '+number(p.max_cp)+'</td><td>'+number(p.p_atk_speed)+' / '+number(p.m_atk_speed)+'</td><td><span class="'+(Number(p.effect_count)===0?'context-clean':'context-active')+'">'+escapeHtml(context)+'</span><span class="build-mini">'+number(p.equipped_count)+' equipados · '+number(p.skill_count)+' skills</span></td><td>'+escapeHtml(date(p.observed_ms))+'</td></tr>';}).join('');$('#catalog-count').textContent=number(state.catalog.length)+' perfiles';$('#telemetry-catalog').innerHTML='<table><thead><tr><th>Personaje / build</th><th>Raza</th><th>Ranura / clase activa</th><th>Nivel</th><th>P. Atk</th><th>M. Atk</th><th>P.Def</th><th>M.Def</th><th>HP / CP</th><th>Atk / Cast</th><th>Contexto</th><th>Lectura</th></tr></thead><tbody>'+(rows||'<tr><td colspan="12">Todavía no hay perfiles. Reinicia el Game Server y entra con un personaje.</td></tr>')+'</tbody></table>';}
  function renderFights(){ $('#fight-list').innerHTML=state.fights.map(function(fight){return '<button class="select-item fight-item '+(state.selectedFight===fight.id?'active':'')+'" data-fight="'+fight.id+'"><div><strong class="versus">'+escapeHtml(fight.player.name)+' <em>vs</em> '+escapeHtml(fight.opponent.name)+'</strong><small>'+date(fight.start)+' · '+number(fight.duration,1)+' s · '+number(fight.dps,1)+' DPS</small></div><span class="fight-result '+slug(fight.result)+'">'+escapeHtml(fight.result)+'</span></button>';}).join('')||'<div class="empty-state compact">No hay combates registrados.</div>'; $$('[data-fight]').forEach(function(button){button.onclick=function(){selectFight(button.dataset.fight);};}); }
  async function selectFight(id){state.selectedFight=String(id);renderFights();$('#fight-detail').innerHTML='<div class="panel loading">Calculando diagnóstico…</div>';try{renderFightDetail(await api('/api/telemetry/fights/'+id));}catch(error){$('#fight-detail').innerHTML='<div class="panel empty-state">'+escapeHtml(error.message)+'</div>';}}
  function resourceRow(name,current,max,kind){return '<div class="resource-row"><label>'+name+'</label><div class="bar '+kind+'"><i style="width:'+percent(current,max)+'%"></i></div><span>'+number(current)+' / '+number(max)+'</span></div>';}
  function renderFightDetail(fight){var maxDamage=Math.max.apply(Math,[1].concat(fight.skills.map(function(s){return s.damage;})));var rows=fight.skills.map(function(skill){return '<tr><td><div class="telemetry-skill">'+skillIcon(skill)+'<div><strong>'+escapeHtml(skill.name)+'</strong><small>#'+skill.id+'</small><div class="skill-damage-bar"><i style="width:'+(skill.damage/maxDamage*100)+'%"></i></div></div></div></td><td>'+skill.casts+'</td><td>'+skill.hits+'</td><td>'+number(skill.damage)+'</td><td>'+number(skill.hits?skill.damage/skill.hits:0,1)+'</td></tr>';}).join('');var resources=fight.lastPlayer?resourceRow('CP',fight.lastPlayer.cp,fight.lastPlayer.maxCp,'cp')+resourceRow('HP',fight.lastPlayer.hp,fight.lastPlayer.maxHp,'hp')+resourceRow('MP',fight.lastPlayer.mp,fight.lastPlayer.maxMp,'mp'):'<p class="muted">Sin lectura final de recursos.</p>';$('#fight-detail').innerHTML='<article class="panel fight-card"><div class="fight-header"><div class="fight-title"><p class="eyebrow">'+escapeHtml(date(fight.start))+' · '+number(fight.duration,1)+' SEGUNDOS</p><h2>'+escapeHtml(fight.player.name)+' <span class="muted">vs</span> '+escapeHtml(fight.opponent.name)+'</h2><p>'+fight.eventCount+' eventos capturados</p></div><div class="result-large">'+escapeHtml(fight.result)+'</div></div><div class="combat-metrics"><div class="combat-metric"><small>Daño infligido</small><strong class="damage">'+number(fight.dealt)+'</strong></div><div class="combat-metric"><small>DPS</small><strong class="dps">'+number(fight.dps,1)+'</strong></div><div class="combat-metric"><small>Daño recibido</small><strong>'+number(fight.received)+'</strong></div><div class="combat-metric"><small>Skills lanzados</small><strong>'+fight.casts+'</strong></div></div><div class="resource-stack">'+resources+'</div></article><div class="analysis-grid"><article class="panel"><div class="panel-heading"><div><p class="eyebrow">ROTACIÓN</p><h3>Daño por habilidad</h3></div><span class="badge">'+fight.hits+' impactos · '+fight.misses+' fallos</span></div><div class="table-wrap" style="border:0;border-radius:0"><table><thead><tr><th>Skill</th><th>Usos</th><th>Hits</th><th>Daño</th><th>Promedio</th></tr></thead><tbody>'+(rows||'<tr><td colspan="5">Sin daño saliente</td></tr>')+'</tbody></table></div></article><article class="panel"><div class="panel-heading"><div><p class="eyebrow">DIAGNÓSTICO</p><h3>Qué mejorar</h3></div></div><div class="advice-list">'+fight.advice.map(function(item,index){return '<div class="advice"><b>0'+(index+1)+'</b><span>'+escapeHtml(item)+'</span></div>';}).join('')+'</div></article></div>';}

  function bindJumps(){ $$('[data-jump]').forEach(function(button){button.onclick=function(){setView(button.dataset.jump);};}); }
  $$('.nav-item').forEach(function(button){button.onclick=function(){setView(button.dataset.view);};});
  bindJumps();
  $('#refresh-characters').onclick=loadCharacters;
  $('#class-search').oninput=renderClasses;$('#race-filter').onchange=renderClasses;$('#stage-filter').onchange=renderClasses;
  $('#skill-search-button').onclick=function(){searchSkills($('#skill-search').value);};$('#skill-search').onkeydown=function(event){if(event.key==='Enter'){event.preventDefault();searchSkills(event.target.value);}};
  $('#refresh-telemetry').onclick=loadTelemetry;
  $('#restart-button').onclick=async function(){if(!confirm('Primero cierra Lineage II. El panel detendrá y volverá a iniciar el servidor automáticamente; no necesitas usar los archivos 5 y 6. ¿Aplicar los cambios ahora?'))return;try{var result=await api('/api/restart',{method:'POST',body:'{}'});toast(result.message,'success');$('#pending-badge').classList.add('hidden');}catch(error){toast(error.message,'error');}};
  setInterval(function(){ $('#clock').textContent=new Date().toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}); },1000);
  var initialView = new URLSearchParams(location.search).get('view');
  if (titles[initialView]) setView(initialView);
  loadStatus();loadOverviewFight();setInterval(loadStatus,12000);
}());
