from pathlib import Path
import json,hashlib,shutil,collections
R=Path(r'E:\l2-local');G=R/'research/model-catalog';S=R/'research/npc-batch2';p=G/'gallery.js';s=p.read_text(encoding='utf-8');s=s.replace("m.status==='failed'?'La referencia del catálogo no pudo leerse en este cliente.':m.note", "m.status==='failed'?(m.note||'La referencia del catálogo no pudo leerse en este cliente.'):m.note");p.write_text(s,encoding='utf-8')
j=json.loads((G/'gallery.json').read_text(encoding='utf-8'));new=[m for m in j['models'] if m['batch']=='Tanda 2'];group=collections.defaultdict(list)
for m in new:
 if m.get('gltf'):group[m['gltf']].append(m)
for groupmodels in group.values():
 if len(groupmodels)>1:
  for m in groupmodels:m['note']=m.get('note','')+' Variantes del mismo cuerpo comparten una vista representativa; los colores y efectos exactos deben revisarse en el cliente.'
summary={'original':843,'batch2_entries':len(new),'ready':sum(m['status']=='ready' for m in new),'unavailable':sum(m['status']!='ready' for m in new),'total':len(j['models']),'archives':165,'source_references':166,'limits':['Vistas de mallas y piezas, no especies unicas.','Sin particulas/sonidos/IA en WebGL; materiales aproximados.','Algunas variantes comparten vista representativa.','No se modificaron cliente ni GameServer.'],'native_sample':json.loads((S/'native-test.json').read_text())}
(G/'gallery.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');(S/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# Galeria L2: Tanda original y Tanda 2

13/10/2026. Incorporados los165paquetes de NPCs descargados enK. El visor portable conserva843entradas previas como Tanda original y agrega1509entradasTanda2:1379mallas conglTF yminiatura;130fichas sinvista disponible. Las fichas incluyen mallas, variantes y piezas deefectos/objetos: no representan1509NPCs distintos.

Abrir GALERIA-MODELOS-L2.cmd y elegir el filtro Tanda. Acceso directo: http://127.0.0.1:32280/?batch=Tanda%202 . Tambien se puede buscar Tanda2 por su etiqueta en busqueda. Activar Mostrar recursos sin imagen para revisar130fichas pendientes.

843claves/metadataoriginales conservadas salvo el campo batch. Favoritos priorizan claveexacta para evitar confundir misma malla deotra tanda. Tarjetas ydialogos muestran etiqueta. CategoriaBosses agregada. RecursosTanda2 aislados porarchivoDrive enresearch/npc-batch2/packages; no se copiaron acliente. nativeAssetRoot resuelto dentro delproyecto para UModel, conextensionesukx/usx/u.

Verificados todos losbuffers,texturas yminiaturas de1379vistas. APIcatalog2352entradas y dosfiltros de tanda. APIaperturaBalok200 y UModelresponding. No se pudo inspeccionar navegador nativo porque ComputerUsepipe estaba indisponible; no afirmar validacionvisual completa deWebGL/UI. Hoja de6miniaturas revisada visualmente encontact-sheet.jpg: mallas presentes, materiales aproximados y algunos colores pendientes deafinacion.

130no disponibles incluyen100exportaciones congeometriavacia yotroserrores/recursos sinmalla. Freya cuerpo/trono original deeste pack exporta geometriavacia conUModel; sus accesorios legibles siguenvisibles. Paquetes originales yerrores conservados. No ejecutar DLL/codigo de lospacks. Stats/IA/servidor nointegrados. Particulas/sonidos/animaciones nativas no equivalen aWebGL. Algunasvariantes comparten unarepresentacion de material.

Backup: backups/npc-tanda2-20261013-153746. Scripts/manifest/logs enresearch/npc-batch2. No reejecutar build_gallery/finalizadores historicos para regenerar todo sinpreservar Tanda2. Elimportador guarda resultadosporpaquete; repeticiones requieren revisar gallery.json yvariantes.
'''
(S/'README.md').write_text(text,encoding='utf-8');(R/'GALERIA-TANDA-2.md').write_text(text,encoding='utf-8')
for n in ['gallery.html','gallery.js','server.js','Open-L2Models.ps1','gallery.json']:
 q=R/'cloud-repo/research/model-catalog'/n;q.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(G/n,q)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
 (R/folder/'GALERIA-TANDA-2.md').write_text(text,encoding='utf-8')
note='# HELLGAMES: Tanda2 incorporada al visor\n\n'+text
Path(r'K:\_CodexNexus\inbox\20261013-lineage2-visor-tanda2.md').write_text(note,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
