# Integracion de escenarios en curso ? 13/10/2026

Peticion del usuario: agregar todos los escenarios descargados faltantes al visor. Preparacion masiva aislada iniciada para64mapas/variantes tras deduplicar porSHA256 mapas exactos y excluirR4/Canon existentes.4trabajadores. No dar por completada toda la importacion hasta consultar resultados.

Scripts prepare.py/assemble.py/terrain.py/add_terrain.py generalizados; import_remaining.py reanudable y publicacion atomica con lockentrethreads; watch_import.py supervisa proceso principal, actualiza import-progress.json/html y reintenta fallos y terrenos pendientes una vez. Estado actual en http://127.0.0.1:32280/import-progress.html, enlazado desde CATALOGO enK. Tareas remaining-tasks.json; resultado individual import-result.json y model.json por library_HASH; reporte agregado remaining-import-results.json. No sobrescribir toda galeria con finalizadores historicos.

Vistas publicadas hasta ahora: CrowIsland,Genesis/Orbis/Octavis/ForestDuel,GardenofEva,WorldTree yAstatineHF con terreno;PrimevalGarden publicado inicialmente sin terreno (se amplio lectorLicense18 y altura ya recuperada; supervisor debe rehacervista).HeartSteel fallo por referenciaNone y colision temporal cachecompartido; corregidos ambos y preparacionreintentada. Scripts no ejecutan DLL/codigo de lospacks; solo UModel/Blender propios.

MiniaturaCrow revisada: suelo y arquitectura visibles; materiales de efecto verdes/aproximados, no vista final deljuego. Todasfichas marcanvista parcial, posiblesactoresomitidos/terreno pendiente. No certificaBSP/agua/particulas/iluminacion/collisiones/compatibilidadInterlude. Cliente yGameServer sinmodificaciones.

Supervisor en proceso separado oculto, registra watch-import.log/error.log y resultado final enRESULTADO-IMPORTACION.md/KRESULTADO-IMPORTACION-VISOR.md cuando termine. Puede retomarse ejecutando import_remaining.py: conserva modelos existentes y cacheporpieza. No afirmar que64mapas esten ya listos. Backupgallery-before-remaining-scenes.json.
