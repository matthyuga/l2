from pathlib import Path
import json
r=Path(__file__).resolve().parent
records={}
for name in ['download-manifest.json','collection-manifest.json','source-manifest.json']:
 for row in json.loads((r/name).read_text()):records[row['id']]=row
checks={x['file']:x for x in json.loads((r/'archive-checks.json').read_text())}
names={'opal-snow':'Classic Ona / OpalSnow','iordanov-update':'Iordanov 3.6.9','interface-compilation-2021':'Dandilo Personal Editions 2021','collection-last-variant':'Bonus texturas Aden/Giran/Goddard','wellinton-v3-collection':'Wellinton V3 mirror','recompiled-interface':'Recompiled Interface','neophron-classic':'Neophron Classic Start Edition','essence-sanyou':'Essence Sanyou','iordanov-full-functions':'Iordanov Full Functions','celestine-mxc':'Celestine MxC','silent-v2':'Silent V2 Visual Essence 2021','essence-aikon-2.0':'Essence 2.0 AikoN','iordanov-3.6.10':'Iordanov 3.6.10'}
lines=['# Interfaces descargadas — 14/10/2026','','19 archivos, 3.138.502.362 bytes: 2,92 GiB / 3,14 GB decimales. Guardados en `E:\\l2-local\\descarga de assets\\interfaces\\2026-10-14`. Sin instalación ni ejecución. Todos pasaron integridad RAR/ZIP; no se hicieron pruebas en juego ni análisis antivirus. Los hashes y fuentes están en [manifest.json](manifest.json), y los inventarios por archivo en esta carpeta.','','| Recurso | MiB | Tipo | Procedencia |','|---|---:|---|---|']
for ident,row in records.items():
 row['title']=names.get(ident,row['title'])
 if row['status']!='downloaded':continue
 c=checks[Path(row['path']).name];assert c['sha256']==row['sha256']
 row.update(archive_crc_ok=c['archive_crc_ok'],inventory_entries=c['entries'],ui_files=c['ui_files'])
 kind='Pack/variante de interfaz'
 if ident in ['atlas-v9.6-interface','moon-modern-interface']:kind='Parche de servidor con interfaz'
 elif ident=='nexus-interlude-visual':kind='Visual: 3 UTX y 2 imágenes, sin Interface.u/XDAT'
 elif ident=='collection-last-variant':kind='Texturas de ciudades, no interfaz'
 elif ident=='interface-evolved-source':kind='Fuentes experimentales; dependencias externas faltantes'
 elif ident=='wellinton-v3-collection':kind='Mirror de Wellinton: 27 archivos idénticos comprobados'
 row['kind']=kind
 lines.append(f'| {row["title"]} | {row["bytes"]/1048576:.2f} | {kind} | [Publicación]({row["source"]}) |')
lines.extend(['','## Alcance y pendientes','','Se recuperaron los archivos comprimidos públicos localizados en esta búsqueda. No es una colección de todas las interfaces existentes en Internet. Cuando la recopilación ofrecía instalador y archivo del mismo pack, se descargó el archivo. No se extrajo al cliente ni se ejecutaron DLL o instaladores.','','Los parches Atlas y Moon incluyen archivos de sus servidores y muchos assets; no son interfaces independientes listas para copiar al cliente. Las dos distribuciones de Wellinton tienen igual tamaño y distinto SHA-256; se conservan como mirrors/variantes sin contarlas como dos diseños únicos. Algunas publicaciones etiquetan sus versiones como cracked; se conserva el nombre original en el manifest, sin haber verificado permisos ni protecciones.','','La integridad de un archivo no acredita seguridad, autorización de redistribución o compatibilidad. InterfaceEvolved es código fuente y requiere componentes externos ausentes. MEGA: tamaño y archivo comprimido comprobados; MAC externo no verificado independientemente.','','## Referencias no recuperadas','','- [Abstract](https://mmo-dev.info/resources/abstract-interface-for-interlude.3866/) y [Athena](https://athena-project.eu/interface/): requieren sesión para revelar contenido/descarga. No se creó cuenta ni se eludió acceso. Las familias recuperadas de otras fuentes no necesariamente son las mismas versiones.','- [Silent original](https://maxcheaters.com/topic/241747-silent-interface-interlude-style/): MEGA devolvió -9, no disponible. Silent V2 recuperado como alternativa, sin afirmar equivalencia. Linktree devolvió 406/timeout.','- NEW Menu View y Classic + Auto Pots VIP: sin enlace de descarga público expuesto en la lectura.','- Iconos Neophron sobre la cabeza: sin enlace público recuperado en los dos hilos previos. Neophron Classic es otro pack.','- Emudevs Classic Plus y L2Massacre: host no resuelto al consultar.','','Próximo paso posible: comparar apariencias y funciones y probar candidatos en copia aislada, antes de elegir cambios al HUD.'])
(r/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with (r/'README.md').open('a',encoding='utf-8') as f:
 f.write('\n## Comparación de mirrors\n\nLos dos RAR Wellinton V3 contienen los mismos 27 archivos con nombres y SHA-256 de contenido idénticos. Son dos copias del mismo pack, aunque cambie el hash del contenedor. [Comparación](wellinton-mirror-comparison.json). Quedan 19 archivos descargados y 18 paquetes con contenido diferente: 13 packs/variantes de interfaz, 2 parches de servidor, 1 pack visual, 1 bonus de texturas y 1 proyecto fuente, más el mirror duplicado. Estas cantidades describen paquetes, no diseños únicos ni compatibilidad probada.\n')
(r/'manifest.json').write_text(json.dumps(list(records.values()),indent=2,ensure_ascii=False),encoding='utf-8')
assert len(checks)==19 and all(x['archive_crc_ok'] for x in checks.values())
print('Catalog:',len(records),'entries; 19 archives OK')
