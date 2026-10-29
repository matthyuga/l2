from pathlib import Path
import json,collections,html,shutil
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent/'audit';K=Path(r'K:\assets descargables de l2')
reports=json.loads((D/'library-audit.json').read_text(encoding='utf-8'));views=json.loads((D/'viewer-audit.json').read_text(encoding='utf-8'))
counts=collections.Counter();rows=[];details=[]
for r in reports:
 maps=r['maps'];source=r['source'];terrain=sum(len(m.get('terrains',[])) for m in maps);bsp=sum(m.get('classes',{}).get('Engine.Model',0) for m in maps)
 essential=[a for m in maps for a in m['actor_dependencies']+m['terrain_dependencies'] if a['status'] not in ['resolved','internal']]
 missing=[a for a in r['dependencies'] if a['status']=='missing_package'];wrong=[a for a in r['dependencies'] if a['status']=='missing_object'];other=[a for a in r['dependencies'] if a['status']=='other_archive']
 if source.get('error') or source.get('integrity_exit')!=0:
  status='Original defectuoso conservado; existe copia reparada' if '_original-con-error' in source['archive'] else 'Problema de archivo o extracción';counts['archive_issue']+=1
 elif r['parse_errors']:status='Lectura parcial: requiere otra herramienta';counts['partial_read']+=1
 elif essential:status='Revisar dependencias directas del mapa';counts['direct_dependency_review']+=1
 elif missing or wrong or other or any(a['status']=='unreadable_dependency' for a in r['dependencies']):status='Mapa leído; referencias adicionales pendientes';counts['declared_dependency_review']+=1
 elif not maps:status='Sin mapa .unr localizado';counts['no_map']+=1
 else:status='Dependencias declaradas localizadas; falta prueba visual';counts['references_resolved']+=1
 counts['archives']+=1;counts['maps']+=len(maps);counts['integrity_pass']+=source.get('integrity_exit')==0;counts['maps_with_terrain']+=sum(bool(m.get('terrains')) for m in maps)
 rows.append((source['name'],len(maps),terrain,bsp,len(essential),len(missing),len(wrong),len(other),len(r['parse_errors']),status))
 detail=dict(name=source['name'],status=status,integrity=source.get('integrity_exit'),source=source['archive'],direct_warnings=essential,declared_unresolved=r['dependencies'],parse_errors=r['parse_errors'],maps=[{k:m.get(k) for k in ['file','version','license','actors','terrains','floor_named_refs','classes']} for m in maps]);details.append(detail)
summary=dict(counts=counts,viewer_scenes=len(views),viewer_broken_links=sum(bool(v['missing_links']) for v in views),viewer_material_slots_without_texture=sum(len(v['materials_without_basecolor_texture']) for v in views),limits=['Referencias declaradas pueden pertenecer a recursos no usados por el mapa.','Pisos por nombre, TerrainInfo y BSP no prueban colisiones o transitabilidad.','No se declara compatibilidad con Interlude por resolver dependencias.','Sin certificacion visual o prueba en juego de toda la biblioteca.'])
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');(D/'classified-audit.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
text='# Auditoría de escenarios — 13/10/2026\n\n'+f"Revisados {counts['archives']} archivos originales. Integridad correcta: {counts['integrity_pass']}. Mapas .unr localizados y leídos: {counts['maps']}; con TerrainInfo: {counts['maps_with_terrain']}. Las variantes y copias cuentan por separado.\n\n"
text+='## Alcance\n\nComprobación de archivos comprimidos, lectura de paquetes Unreal, referencias de mallas y capas de terreno, materiales declarados y dependencias del cliente local. La auditoría incluye dependencias de recursos no utilizados; una referencia adicional sin resolver exige revisión y no demuestra por sí sola que el escenario jugable esté roto. Un mapa con todas sus referencias presentes aún requiere conversión completa y prueba visual. No se instalaron escenarios en el cliente ni servidor.\n\n'
text+='## Estado por archivo\n\n| Archivo | Mapas | Terrenos | Avisos directos | Lectura incompleta | Estado |\n|---|---:|---:|---:|---:|---|\n'
for name,maps,terrain,bsp,direct,missing,wrong,other,parse,status in rows:text+=f'| {name} | {maps} | {terrain} | {direct} | {parse} | {status} |\n'
text+='\n## Vistas actuales del visor\n\n| Vista | Terreno en glTF | Materiales sin textura base | Enlaces rotos |\n|---|---|---:|---:|\n'
for v in views:text+=f"| {v['title']} | {'Sí' if v['terrain_nodes'] else 'No'} | {len(v['materials_without_basecolor_texture'])} | {len(v['missing_links'])} |\n"
text+='\nLos materiales sin textura base pueden ser efectos o colores sólidos: no todos equivalen a una textura faltante. Gludio/Keucereus/Gracia/Superion son vistas de arquitectura, no sus mapas completos. Veilmar subterráneo omite la superficie intencionalmente. R4 y Canon tienen terreno; Canon lo oculta inicialmente para no tapar sus salas. BSP, agua, partículas, iluminación original y colisiones se comprueban por separado.\n\nDetalles exactos: classified-audit.json, library-audit.json y viewer-audit.json en E:\\l2-local\\research\\scenario-batches\\audit.\n'
(D/'AUDITORIA-ESCENARIOS.md').write_text(text,encoding='utf-8');(K/'AUDITORIA-ESCENARIOS.md').write_text(text,encoding='utf-8')
escape=html.escape
body=''
for r in details:
 body+='<details><summary>'+escape(r['name'])+' — '+escape(r['status'])+'</summary><pre>'+escape(json.dumps(r,ensure_ascii=False,indent=2))+'</pre></details>'
table='<table><thead><tr><th>Vista actual</th><th>Terreno</th><th>Materiales sin textura base</th><th>Enlaces rotos</th></tr></thead><tbody>'
for v in views:table+='<tr><td><a href="http://127.0.0.1:32280/?model='+escape(v['key'])+'&amp;view=3d">'+escape(v['title'])+'</a></td><td>'+('Incluido' if v['terrain_nodes'] else 'No incluido')+'</td><td>'+str(len(v['materials_without_basecolor_texture']))+'</td><td>'+str(len(v['missing_links']))+'</td></tr>'
table+='</tbody></table>'
page='<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Auditoría de escenarios L2</title><style>body{font:16px system-ui;background:#111a22;color:#dae5ed;max-width:1200px;margin:32px auto;padding:20px;line-height:1.5}a{color:#edc27d}table{border-collapse:collapse;width:100%;margin:20px 0}td,th{border:1px solid #3d5261;padding:10px;text-align:left}details{padding:12px;background:#1b2b37;margin:8px 0}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}</style><h1>Auditoría de escenarios</h1><p>13/10/2026. '+str(counts['archives'])+' archivos originales; '+str(counts['integrity_pass'])+' pasan integridad. '+str(counts['maps'])+' mapas leídos (incluye variantes).</p><p>Esto comprueba archivos y referencias, no certifica la apariencia completa ni el funcionamiento en el juego. Expandí cada archivo para ver dependencias concretas. Las referencias adicionales pueden pertenecer a recursos no usados.</p><h2>Escenarios actuales del visor</h2>'+table+'<p>Sin textura base no significa siempre archivo faltante: hay efectos y materiales de color sólido. Las cuatro estructuras aéreas son vistas parciales de arquitectura. Veilmar subterráneo omite terreno intencionalmente.</p><h2>Paquetes descargados</h2>'+body+'</html>'
(K/'AUDITORIA-ESCENARIOS.html').write_text(page,encoding='utf-8');(D/'AUDITORIA-ESCENARIOS.html').write_text(page,encoding='utf-8');(K/'AUDITORIA-ESCENARIOS.json').write_text(json.dumps(dict(summary=summary,archives=details,viewer=views),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
