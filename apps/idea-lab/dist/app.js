(function(){
  'use strict';

  var state=null;
  var sources=[];
  var currentView='today';
  var selectedIdeaId=null;
  var saveTimer=null;
  var sessionTimer=null;
  var titles={today:['TALLER PORTÁTIL','Jornada de diseño'],ideas:['MAPA DE TRABAJO','Ideas y sistemas'],decisions:['MEMORIA DEL PROYECTO','Decisiones'],sources:['ARCHIVO DE ORIGEN','Conversaciones y referencias']};
  var statuses=['bandeja','explorando','diseñado','prototipo','bloqueado','hecho'];
  var priorities=['crítica','alta','media','baja'];

  function $(selector,root){return(root||document).querySelector(selector);}
  function $$(selector,root){return Array.prototype.slice.call((root||document).querySelectorAll(selector));}
  function escapeHtml(value){return String(value===null||value===undefined?'':value).replace(/[&<>"']/g,function(char){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[char];});}
  function uid(prefix){return(prefix||'item')+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);}
  function now(){return new Date().toISOString();}
  function todayKey(){var date=new Date();return date.getFullYear()+'-'+String(date.getMonth()+1).padStart(2,'0')+'-'+String(date.getDate()).padStart(2,'0');}
  function formatDate(value,withTime){if(!value)return '—';var options=withTime?{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}:{day:'2-digit',month:'short',year:'numeric'};return new Date(value).toLocaleString('es-AR',options);}
  function lines(value){return String(value||'').split(/\r?\n/).map(function(item){return item.trim();}).filter(Boolean);}
  function toast(message,type){var node=document.createElement('div');node.className='toast '+(type||'');node.textContent=message;$('#toast-root').appendChild(node);setTimeout(function(){node.remove();},3800);}

  async function api(url,options){
    var response=await fetch(url,Object.assign({cache:'no-store',headers:{'Content-Type':'application/json'}},options||{}));
    var payload=await response.json().catch(function(){return{};});
    if(!response.ok)throw new Error(payload.error||('Error HTTP '+response.status));
    return payload;
  }

  function setSaveState(kind,text){var node=$('#save-state');node.className='save-state '+(kind||'');node.innerHTML='<i></i>'+text;}
  function queueSave(){
    state.meta.updatedAt=now();
    setSaveState('saving','Guardando…');
    clearTimeout(saveTimer);
    saveTimer=setTimeout(saveWorkspace,550);
  }
  async function saveWorkspace(){
    clearTimeout(saveTimer);saveTimer=null;
    try{await api('/api/workspace',{method:'PUT',body:JSON.stringify(state)});setSaveState('','Guardado en el disco');}
    catch(error){setSaveState('error','Error al guardar');toast(error.message,'error');}
  }

  function ideaById(id){return state.ideas.find(function(item){return item.id===id;});}
  function priorityRank(value){return priorities.indexOf(value)===-1?99:priorities.indexOf(value);}
  function ideaScore(idea){return Number(idea.impact||0)/Math.max(1,Number(idea.effort||1));}
  function unique(list){return Array.from(new Set(list));}

  function setView(view){
    currentView=view;
    $$('.nav-item').forEach(function(button){button.classList.toggle('active',button.dataset.view===view);});
    $$('.view').forEach(function(node){node.classList.toggle('active',node.id==='view-'+view);});
    $('#view-eyebrow').textContent=titles[view][0];$('#view-title').textContent=titles[view][1];
    if(view==='ideas')renderIdeas();
    if(view==='decisions')renderDecisions();
    if(view==='sources')renderSources();
  }

  function renderMetrics(){
    var open=state.ideas.filter(function(item){return item.status!=='hecho';});
    var exploring=state.ideas.filter(function(item){return item.status==='explorando';}).length;
    var blocked=state.ideas.filter(function(item){return item.status==='bloqueado';}).length;
    var ready=state.ideas.filter(function(item){return item.status==='diseñado'||item.status==='prototipo';}).length;
    var metrics=[['Ideas abiertas',open.length,'en '+unique(open.map(function(x){return x.area;})).length+' áreas'],['En exploración',exploring,'requieren decisiones'],['Listas para avanzar',ready,'diseñadas o en prototipo'],['Bloqueadas',blocked,'dependen de otra herramienta']];
    $('#metric-grid').innerHTML=metrics.map(function(item){return '<article class="panel metric"><small>'+item[0]+'</small><strong>'+item[1]+'</strong><span>'+item[2]+'</span></article>';}).join('');
    $('#nav-ideas-count').textContent=state.ideas.length;
  }

  function ideaOptions(selected){return state.ideas.filter(function(item){return item.status!=='hecho';}).map(function(item){return '<option value="'+escapeHtml(item.id)+'" '+(item.id===selected?'selected':'')+'>'+escapeHtml(item.title)+'</option>';}).join('');}

  function renderFocus(){
    while(state.today.focusIds.length<3)state.today.focusIds.push(state.ideas[state.today.focusIds.length]?state.ideas[state.today.focusIds.length].id:'');
    $('#focus-list').innerHTML=state.today.focusIds.slice(0,3).map(function(id,index){var idea=ideaById(id)||state.ideas[0];return '<div class="focus-row"><span class="focus-index">'+(index+1)+'</span><div><strong>'+escapeHtml(idea?idea.title:'Sin seleccionar')+'</strong><small>'+(idea?escapeHtml(idea.area+' · '+idea.status):'')+'</small></div><select data-focus-index="'+index+'">'+ideaOptions(idea&&idea.id)+'</select></div>';}).join('');
    $$('[data-focus-index]').forEach(function(select){select.onchange=function(){state.today.focusIds[Number(select.dataset.focusIndex)]=select.value;queueSave();renderFocus();renderNextSteps();};});
  }

  function renderNextSteps(){
    var ideas=state.today.focusIds.map(ideaById).filter(Boolean);
    $('#next-list').innerHTML=ideas.map(function(idea){return '<div class="next-item"><i></i><div><strong>'+escapeHtml(idea.title)+'</strong><small>'+escapeHtml(idea.nextStep||'Definir próximo paso.')+'</small></div></div>';}).join('')||'<div class="history-empty">Selecciona ideas para la jornada.</div>';
  }

  function renderSessionPlanner(){
    var host=$('#session-planner');
    if(state.activeSession){
      var idea=ideaById(state.activeSession.ideaId);
      host.innerHTML='<div class="active-session"><p class="eyebrow">EN CURSO · '+escapeHtml(String(state.activeSession.durationMinutes))+' MINUTOS</p><h3>'+escapeHtml(idea?idea.title:'Trabajo general')+'</h3><p>'+escapeHtml(state.activeSession.goal)+'</p><textarea id="active-session-notes" placeholder="Qué decidiste, qué descartaste, qué falta…">'+escapeHtml(state.activeSession.notes||'')+'</textarea><div class="session-actions"><button class="button ghost" id="cancel-session">Cancelar</button><button class="button cyan" id="finish-session">Cerrar bloque y guardar</button></div></div>';
      $('#active-session-notes').oninput=function(){state.activeSession.notes=this.value;queueSave();};
      $('#cancel-session').onclick=function(){if(confirm('¿Cancelar este bloque sin guardarlo en el historial?')){state.activeSession=null;queueSave();renderToday();}};
      $('#finish-session').onclick=finishSession;
    }else{
      host.innerHTML='<div class="session-form"><label class="wide">Idea<select id="session-idea">'+ideaOptions(state.today.focusIds[0])+'</select></label><label>Duración<select id="session-duration"><option value="25">25 min</option><option value="50" selected>50 min</option><option value="90">90 min</option></select></label><label>Tipo<select id="session-kind"><option>Diseñar</option><option>Investigar</option><option>Decidir</option><option>Revisar</option></select></label><label class="wide">Resultado buscado<input id="session-goal" placeholder="Ej.: dejar cerradas las reglas de activación"></label><div class="wide session-actions"><button class="button cyan" id="start-session">Iniciar bloque</button></div></div>';
      $('#start-session').onclick=startSession;
    }
    updateClock();
  }

  function startSession(){
    var goal=$('#session-goal').value.trim();
    if(!goal){toast('Escribe qué resultado quieres obtener en este bloque.','error');$('#session-goal').focus();return;}
    state.activeSession={id:uid('session'),ideaId:$('#session-idea').value,kind:$('#session-kind').value,goal:goal,durationMinutes:Number($('#session-duration').value),startedAt:now(),notes:''};
    queueSave();renderToday();
  }

  function finishSession(){
    if(!state.activeSession)return;
    var ended=new Date();var started=new Date(state.activeSession.startedAt);var elapsed=Math.max(1,Math.round((ended-started)/60000));
    state.sessions.unshift({id:state.activeSession.id,ideaId:state.activeSession.ideaId,kind:state.activeSession.kind,goal:state.activeSession.goal,notes:state.activeSession.notes||'',plannedMinutes:state.activeSession.durationMinutes,minutes:elapsed,startedAt:state.activeSession.startedAt,endedAt:ended.toISOString()});
    state.sessions=state.sessions.slice(0,100);
    var idea=ideaById(state.activeSession.ideaId);if(idea)idea.updatedAt=now();
    state.activeSession=null;queueSave();renderToday();toast('Bloque guardado en la bitácora.');
  }

  function updateClock(){
    var clock=$('#session-clock'),label=$('#clock-label'),action=$('#session-action');
    if(!clock)return;
    if(!state||!state.activeSession){clock.textContent='00:00';label.textContent='SIN SESIÓN ACTIVA';action.textContent='Iniciar bloque';action.onclick=function(){var button=$('#start-session');if(button)button.click();};return;}
    var end=new Date(state.activeSession.startedAt).getTime()+state.activeSession.durationMinutes*60000;
    var remaining=Math.max(0,end-Date.now());var minutes=Math.floor(remaining/60000),seconds=Math.floor((remaining%60000)/1000);
    clock.textContent=String(minutes).padStart(2,'0')+':'+String(seconds).padStart(2,'0');label.textContent=remaining?'BLOQUE EN CURSO':'TIEMPO CUMPLIDO';action.textContent='Cerrar bloque';action.onclick=finishSession;
  }

  function renderHistory(){
    var sessions=state.sessions.slice(0,8);
    $('#session-history').innerHTML=sessions.length?'<div class="history-list">'+sessions.map(function(session){var idea=ideaById(session.ideaId);return '<div class="history-row"><time>'+formatDate(session.endedAt,true)+'</time><div><strong>'+escapeHtml(idea?idea.title:'Trabajo general')+'</strong><span>'+escapeHtml(session.goal)+(session.notes?' · '+escapeHtml(session.notes):'')+'</span></div><span>'+session.minutes+' min</span></div>';}).join('')+'</div>':'<div class="history-empty">Aún no cerraste ningún bloque de trabajo.</div>';
  }

  function renderToday(){
    $('#today-objective').value=state.today.objective||'';$('#today-notes').value=state.today.notes||'';
    renderMetrics();renderFocus();renderNextSteps();renderSessionPlanner();renderHistory();
  }

  function filteredIdeas(){
    var query=$('#idea-search').value.trim().toLowerCase(),area=$('#area-filter').value,status=$('#status-filter').value,sort=$('#sort-filter').value;
    var list=state.ideas.filter(function(idea){var haystack=[idea.title,idea.summary,idea.nextStep,idea.area,(idea.tags||[]).join(' '),(idea.questions||[]).join(' ')].join(' ').toLowerCase();return(!query||haystack.indexOf(query)!==-1)&&(!area||idea.area===area)&&(!status||idea.status===status);});
    list.sort(function(a,b){if(sort==='priority')return priorityRank(a.priority)-priorityRank(b.priority)||b.impact-a.impact;if(sort==='updated')return String(b.updatedAt).localeCompare(String(a.updatedAt));if(sort==='title')return a.title.localeCompare(b.title);return ideaScore(b)-ideaScore(a)||priorityRank(a.priority)-priorityRank(b.priority);});return list;
  }

  function fillIdeaFilters(){
    var area=$('#area-filter').value,status=$('#status-filter').value;
    $('#area-filter').innerHTML='<option value="">Todas</option>'+unique(state.ideas.map(function(item){return item.area;})).sort().map(function(item){return '<option '+(item===area?'selected':'')+'>'+escapeHtml(item)+'</option>';}).join('');
    $('#status-filter').innerHTML='<option value="">Todos</option>'+statuses.map(function(item){return '<option '+(item===status?'selected':'')+'>'+escapeHtml(item)+'</option>';}).join('');
  }

  function renderIdeas(){
    fillIdeaFilters();var list=filteredIdeas();
    if(!selectedIdeaId||!list.some(function(item){return item.id===selectedIdeaId;}))selectedIdeaId=list.length?list[0].id:null;
    $('#idea-list').innerHTML=list.map(function(idea){return '<button class="idea-card '+(idea.id===selectedIdeaId?'active':'')+'" data-idea="'+escapeHtml(idea.id)+'"><div class="idea-card-top"><div><span class="pill area">'+escapeHtml(idea.area)+'</span><h3>'+escapeHtml(idea.title)+'</h3></div><span class="priority '+escapeHtml(idea.priority)+'">'+escapeHtml(idea.priority)+'</span></div><p>'+escapeHtml(idea.summary)+'</p><div class="idea-card-foot"><span class="pill">'+escapeHtml(idea.status)+'</span><span class="pill">'+(idea.questions||[]).length+' preguntas</span><span class="score">I/E '+Number(ideaScore(idea)).toFixed(1)+'</span></div></button>';}).join('')||'<div class="history-empty">No hay ideas con esos filtros.</div>';
    $$('[data-idea]').forEach(function(button){button.onclick=function(){selectedIdeaId=button.dataset.idea;renderIdeas();};});
    renderIdeaDetail(ideaById(selectedIdeaId));
  }

  function renderIdeaDetail(idea){
    var host=$('#idea-detail');if(!idea){host.innerHTML='<div class="empty"><span>◇</span><h2>Sin resultados</h2><p>Cambia los filtros o crea una idea nueva.</p></div>';return;}
    var dependencyNames=(idea.dependencies||[]).map(ideaById).filter(Boolean).map(function(item){return item.title;});
    host.innerHTML='<div class="detail-head"><div class="detail-head-row"><div><p class="eyebrow">'+escapeHtml(idea.area)+' · '+escapeHtml(idea.status)+'</p><h2>'+escapeHtml(idea.title)+'</h2></div><div class="detail-actions"><button class="button ghost" id="focus-this">Llevar a hoy</button><button class="button secondary" id="edit-idea">Editar</button></div></div><p>'+escapeHtml(idea.summary)+'</p><div class="meta-strip"><div class="meta-item"><small>Prioridad</small><strong>'+escapeHtml(idea.priority)+'</strong></div><div class="meta-item"><small>Impacto</small><strong>'+idea.impact+' / 5</strong></div><div class="meta-item"><small>Esfuerzo</small><strong>'+idea.effort+' / 5</strong></div><div class="meta-item"><small>Fuente</small><strong>'+escapeHtml(idea.source||'Propia')+'</strong></div></div></div><div class="detail-body"><div class="detail-grid"><div class="detail-block wide"><h4>Próximo paso</h4><p>'+escapeHtml(idea.nextStep||'Sin definir')+'</p></div><div class="detail-block"><h4>Preguntas abiertas</h4><div class="question-list">'+((idea.questions||[]).map(function(item){return '<div class="question">'+escapeHtml(item)+'</div>';}).join('')||'<p>Sin preguntas abiertas.</p>')+'</div></div><div class="detail-block"><h4>Dependencias</h4><p>'+(dependencyNames.length?escapeHtml(dependencyNames.join('\n')):'Ninguna registrada')+'</p></div><div class="detail-block wide"><h4>Notas de diseño</h4><p>'+escapeHtml(idea.notes||'Sin notas todavía.')+'</p></div><div class="detail-block wide"><h4>Etiquetas</h4><div class="tag-row">'+(idea.tags||[]).map(function(tag){return '<span class="tag">'+escapeHtml(tag)+'</span>';}).join('')+'</div></div></div></div>';
    $('#edit-idea').onclick=function(){openIdeaEditor(idea);};
    $('#focus-this').onclick=function(){var existing=state.today.focusIds.indexOf(idea.id);if(existing===-1){state.today.focusIds[2]=idea.id;queueSave();}setView('today');renderToday();toast('Idea añadida al enfoque de hoy.');};
  }

  function field(name,label,value,type,options,wide){
    var control;if(type==='textarea')control='<textarea name="'+name+'">'+escapeHtml(value||'')+'</textarea>';else if(type==='select')control='<select name="'+name+'">'+options.map(function(option){return '<option '+(String(option)===String(value)?'selected':'')+'>'+escapeHtml(option)+'</option>';}).join('')+'</select>';else control='<input name="'+name+'" type="'+(type||'text')+'" value="'+escapeHtml(value===undefined?'':value)+'">';
    return '<label class="field '+(wide?'wide':'')+'"><span>'+label+'</span>'+control+'</label>';
  }

  function openModal(title,eyebrow,html,wide){$('#modal-title').textContent=title;$('#modal-eyebrow').textContent=eyebrow||'EDITOR';$('#modal-body').innerHTML=html;$('.modal').classList.toggle('wide',Boolean(wide));$('#modal-backdrop').hidden=false;}
  function closeModal(){$('#modal-backdrop').hidden=true;$('#modal-body').innerHTML='';$('.modal').classList.remove('wide');}

  function openIdeaEditor(idea){
    var isNew=!idea;idea=idea||{title:'',area:'Academia',status:'bandeja',priority:'media',impact:3,effort:3,summary:'',nextStep:'',questions:[],dependencies:[],notes:'',source:'',tags:[]};
    var areas=unique(state.ideas.map(function(item){return item.area;})).sort();if(areas.indexOf(idea.area)===-1)areas.push(idea.area);
    var html='<form id="idea-form"><div class="form-grid">'+field('title','Título',idea.title,'text',null,true)+field('area','Área',idea.area,'select',areas)+field('status','Estado',idea.status,'select',statuses)+field('priority','Prioridad',idea.priority,'select',priorities)+field('impact','Impacto (1–5)',idea.impact,'number')+field('effort','Esfuerzo (1–5)',idea.effort,'number')+field('source','Fuente',idea.source,'text')+field('summary','Resumen',idea.summary,'textarea',null,true)+field('nextStep','Próximo paso comprobable',idea.nextStep,'textarea',null,true)+field('questions','Preguntas abiertas · una por línea',(idea.questions||[]).join('\n'),'textarea',null,true)+field('dependencies','IDs de dependencias · uno por línea',(idea.dependencies||[]).join('\n'),'textarea',null,true)+field('tags','Etiquetas separadas por coma',(idea.tags||[]).join(', '),'text',null,true)+field('notes','Notas de diseño',idea.notes,'textarea',null,true)+'</div><div class="modal-actions"><div>'+(isNew?'':'<button type="button" class="button danger" id="delete-idea">Eliminar</button>')+'</div><div><button type="button" class="button ghost" id="cancel-modal">Cancelar</button> <button class="button primary">Guardar idea</button></div></div></form>';
    openModal(isNew?'Nueva idea':'Editar idea','SISTEMA DE TRABAJO',html);
    $('#cancel-modal').onclick=closeModal;
    if(!isNew)$('#delete-idea').onclick=function(){if(!confirm('¿Eliminar esta idea? La copia automática permitirá recuperarla.'))return;state.ideas=state.ideas.filter(function(item){return item.id!==idea.id;});state.today.focusIds=state.today.focusIds.filter(function(id){return id!==idea.id;});selectedIdeaId=null;queueSave();closeModal();renderAll();};
    $('#idea-form').onsubmit=function(event){event.preventDefault();var form=new FormData(event.target),saved=isNew?{id:uid('idea')}:idea;saved.title=String(form.get('title')).trim();saved.area=String(form.get('area')).trim()||'General';saved.status=form.get('status');saved.priority=form.get('priority');saved.impact=Math.max(1,Math.min(5,Number(form.get('impact'))||3));saved.effort=Math.max(1,Math.min(5,Number(form.get('effort'))||3));saved.source=String(form.get('source')).trim();saved.summary=String(form.get('summary')).trim();saved.nextStep=String(form.get('nextStep')).trim();saved.questions=lines(form.get('questions'));saved.dependencies=lines(form.get('dependencies'));saved.tags=String(form.get('tags')).split(',').map(function(x){return x.trim();}).filter(Boolean);saved.notes=String(form.get('notes')).trim();saved.updatedAt=now();if(!saved.title){toast('La idea necesita un título.','error');return;}if(isNew)state.ideas.unshift(saved);selectedIdeaId=saved.id;queueSave();closeModal();renderAll();setView('ideas');};
  }

  function renderDecisions(){
    $('#decision-grid').innerHTML=state.decisions.map(function(item){return '<article class="panel decision-card" data-decision="'+escapeHtml(item.id)+'"><span class="pill">'+escapeHtml(item.state)+'</span><h3>'+escapeHtml(item.title)+'</h3><p>'+escapeHtml(item.context)+'</p><p class="decision-text"><strong>Decisión:</strong> '+escapeHtml(item.decision)+'</p><footer><span class="pill area">'+escapeHtml(item.area)+'</span><time>'+escapeHtml(item.date)+'</time></footer></article>';}).join('')||'<div class="history-empty">No hay decisiones registradas.</div>';
    $$('[data-decision]').forEach(function(card){card.onclick=function(){openDecisionEditor(state.decisions.find(function(item){return item.id===card.dataset.decision;}));};});
  }

  function openDecisionEditor(decision){
    var isNew=!decision;decision=decision||{title:'',area:'General',state:'provisional',context:'',decision:'',reason:'',date:todayKey()};var areas=unique(state.ideas.map(function(item){return item.area;})).sort();if(areas.indexOf(decision.area)===-1)areas.push(decision.area);
    var html='<form id="decision-form"><div class="form-grid">'+field('title','Título',decision.title,'text',null,true)+field('area','Área',decision.area,'select',areas)+field('state','Estado',decision.state,'select',['provisional','aceptada','revisar','descartada'])+field('date','Fecha',decision.date,'date')+field('context','Contexto',decision.context,'textarea',null,true)+field('decision','Decisión',decision.decision,'textarea',null,true)+field('reason','Razón',decision.reason,'textarea',null,true)+'</div><div class="modal-actions"><div>'+(isNew?'':'<button type="button" class="button danger" id="delete-decision">Eliminar</button>')+'</div><div><button type="button" class="button ghost" id="cancel-modal">Cancelar</button> <button class="button primary">Guardar decisión</button></div></div></form>';
    openModal(isNew?'Registrar decisión':'Editar decisión','MEMORIA DEL PROYECTO',html);$('#cancel-modal').onclick=closeModal;
    if(!isNew)$('#delete-decision').onclick=function(){if(confirm('¿Eliminar esta decisión?')){state.decisions=state.decisions.filter(function(item){return item.id!==decision.id;});queueSave();closeModal();renderDecisions();}};
    $('#decision-form').onsubmit=function(event){event.preventDefault();var form=new FormData(event.target),saved=isNew?{id:uid('decision')}:decision;['title','area','state','date','context','decision','reason'].forEach(function(key){saved[key]=String(form.get(key)||'').trim();});if(!saved.title||!saved.decision){toast('Completa el título y la decisión.','error');return;}if(isNew)state.decisions.unshift(saved);queueSave();closeModal();renderDecisions();};
  }

  function renderSources(){
    $('#source-grid').innerHTML=sources.map(function(item){var label=item.name.replace(/\.json$/,'');return '<article class="panel source-card" data-source="'+escapeHtml(item.name)+'"><p class="eyebrow">CONVERSACIÓN</p><h3>'+escapeHtml(label.charAt(0).toUpperCase()+label.slice(1))+'</h3><p>'+Math.round(item.size/1024)+' KB · ideas originales y razonamiento de diseño.</p><footer><span>Modificado '+formatDate(item.modified,false)+'</span><span class="pill area">Leer</span></footer></article>';}).join('')||'<div class="history-empty">No se encontró la carpeta docs chatsgpt junto al Lab.</div>';
    $$('[data-source]').forEach(function(card){card.onclick=function(){openSource(card.dataset.source);};});
  }

  async function openSource(name){
    try{var source=await api('/api/source?name='+encodeURIComponent(name));openModal(source.name,'FUENTE ORIGINAL','<div class="source-tools"><input id="source-search" placeholder="Buscar dentro de la conversación…"><button class="button secondary" id="source-find">Buscar</button></div><div class="source-reader" id="source-reader"></div>',true);var reader=$('#source-reader');reader.textContent=source.content;function find(){var query=$('#source-search').value.trim();if(!query){reader.textContent=source.content;return;}var index=source.content.toLowerCase().indexOf(query.toLowerCase());if(index===-1){toast('No se encontró ese texto.','error');return;}var before=source.content.slice(0,index),match=source.content.slice(index,index+query.length),after=source.content.slice(index+query.length);reader.innerHTML=escapeHtml(before)+'<mark class="source-highlight">'+escapeHtml(match)+'</mark>'+escapeHtml(after);var mark=$('mark',reader);if(mark)mark.scrollIntoView({block:'center'});}$('#source-find').onclick=find;$('#source-search').onkeydown=function(event){if(event.key==='Enter')find();};}
    catch(error){toast(error.message,'error');}
  }

  function renderAll(){renderToday();renderMetrics();if(currentView==='ideas')renderIdeas();if(currentView==='decisions')renderDecisions();}

  async function init(){
    try{
      var result=await Promise.all([api('/api/workspace'),api('/api/sources')]);state=result[0];sources=result[1];
      state.today=state.today||{date:'',objective:'',notes:'',focusIds:[]};state.sessions=state.sessions||[];state.decisions=state.decisions||[];state.activeSession=state.activeSession||null;
      if(!state.today.date)state.today.date=todayKey();
      renderAll();renderSources();
      $('#today-objective').oninput=function(){state.today.objective=this.value;queueSave();};$('#today-notes').oninput=function(){state.today.notes=this.value;queueSave();};
      $$('.nav-item').forEach(function(button){button.onclick=function(){setView(button.dataset.view);};});
      ['#idea-search','#area-filter','#status-filter','#sort-filter'].forEach(function(selector){$(selector).oninput=renderIdeas;$(selector).onchange=renderIdeas;});
      $('#new-idea-button').onclick=function(){openIdeaEditor(null);};$('#new-decision-button').onclick=function(){openDecisionEditor(null);};
      $('#modal-close').onclick=closeModal;$('#modal-backdrop').onclick=function(event){if(event.target===this)closeModal();};document.onkeydown=function(event){if(event.key==='Escape')closeModal();};
      $('#backup-button').onclick=async function(){try{await saveWorkspace();var result=await api('/api/backup',{method:'POST',body:'{}'});toast('Copia creada: '+result.file);}catch(error){toast(error.message,'error');}};
      clearInterval(sessionTimer);sessionTimer=setInterval(updateClock,1000);updateClock();
    }catch(error){document.body.innerHTML='<div class="empty"><h2>No se pudo abrir el Laboratorio de Ideas</h2><p>'+escapeHtml(error.message)+'</p></div>';}
  }

  window.addEventListener('beforeunload',function(){if(saveTimer&&state){fetch('/api/workspace',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(state),keepalive:true});}});
  init();
})();

