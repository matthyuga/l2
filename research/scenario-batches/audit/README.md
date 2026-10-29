# Auditoria de escenarios ? 13/10/2026

45 archivos revisados,44integridad correcta y1original FantasyIsland ya defectuoso; el ZIP reparado pasa integridad. 373paquetes nativos y71mapas leidos sin errores de formato. Los71declaran terreno, lo cual no prueba que sus dependencias esten presentes ni la conversion completa.

20archivos sin referencias visuales pendientes frente al paquete y cliente local;15con avisos directos de malla/terreno;9con referencias adicionales pendientes (pueden pertenecer a recursos no utilizados);1original defectuoso. Corregido tratamiento de referencias internas agrupadas Height.xx para evitar falsos faltantes.

Caso confirmado: Kamaloka Labyrinth solicita T_19_12.Height.19_12 y T_20_12.Height.20_12, sin paquetes correspondientes en biblioteca ni cliente. No mezclar recursos de otras cronicas automaticamente.

8vistas actuales:0enlaces rotos a buffers o imagenes;43slots sin textura base (incluye efectos/colores solidos, no43archivos necesariamente ausentes). R4,Canon yVeilmarSuperficie tienen terreno. VeilmarUnderground omite superficie intencionalmente. Las4estructuras aereas son arquitectura parcial. Fichas rotuladas segun alcance, con claves/favoritos conservados. Sin certificacion visual completa o pruebas ingame de toda la biblioteca.

Informes K:\assets descargables de l2\AUDITORIA-ESCENARIOS.html, .md y .json. Enlace agregado a CATALOGO.html. Evidencia y extracciones aisladas en E:\l2-local\research\scenario-batches\audit. Scripts audit_library.py/audit_viewer.py/report_audit.py y criterios IMPORTACION-ESCENARIOS.md. Cliente y servidor sin cambios.

Heart of Steel, CrowIsland, WorldTree, GardenofEva yGenesis/Orbis/Octavis/ForestDuel tienen referencias localizadas. Faltan preparar suelos, arquitectura,BSP cuando corresponda y comprobar vistas antes de declarar su conversion completa. Esto no certifica compatibilidad Interlude ni transitabilidad.
