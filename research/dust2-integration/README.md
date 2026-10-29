> Versión actual: ../dust2-scale-v2/README.md. Escala reducida al41.67%, espejoY y UVvertical corregidos; colisiones/geodata regeneradas. Pendiente prueba de cliente para esta versión.

> Confirmación posterior de Kevin, 14/10/2026: «Sí, ahora pisos y paredes funcionan». Suelo y bloqueo de paredes confirmados por el usuario dentro de L2 tras instalar native-walls. Las incidencias y pendientes anteriores se conservan debajo como historial; no equivalen al estado actual. El critical de salida sigue sin confirmación de resolución.

> Estado posterior: se añadió envolvente de paredes nativas en native-walls/README.md tras reporte de atravesar el mapa. Suelo mejoró parcialmente; falta comprobar paredes/puertas/rampas dentro del cliente.

> Estado posterior: las dos bases nativas sostuvieron al personaje localmente. Se instaló soporte nativo continuo en native-floor/README.md, pendiente recorrido ingame y critical sin resolver.

> Reporte posterior: Kevin cayó al vacío al aparecer. Se instaló una corrección de colisiones en floor-fix/README.md; falta confirmación de aterrizaje en cliente. Las pruebas de servidor no certifican física del cliente.

# Dust2 incorporado a L2 â€” 14/10/2026

Instalado en cliente `E:/l2` y servidor `E:/l2-local/server/game`. Primera versiÃ³n de **exploraciÃ³n en zona de paz**, sin equipos, bombas, rondas ni lÃ³gica de CS. No se cambiaron los puntos de nacimiento ni el equipo de personajes.

## Acceso

- `.dust2` / `.dust2 ct`: sector CT, llegada efectiva observada 141672,60696,7853.
- `.dust2 t`: sector T, llegada efectiva 139752,55944,8237.
- `.dust2 salir` / `.dust2 volver`: regresa al punto previo a entrar. Tras reconexiÃ³n/reinicio, si falta el registro temporal, vuelve al muelle aÃ©reo.
- `.dust2 estado`: coordenadas y diagnÃ³stico.
- `.muelle` sigue disponible para volver al muelle.

Los viajes exigen estar vivo, fuera de combate, estado PvP, karma, Olimpiadas e instancias, sin vuelo ni teleport pendiente. Si se muere en la parcela, la zona de respawn dirige al muelle. No se cambiaron reglas de combate en otras zonas.

## Cliente y geodata

Se reutilizÃ³ la conversiÃ³n comprobada en `../dust2`. `HGDust2Arena.usx` contiene 37 piezas, 34 texturas y 34 materiales FinalBlend de doble cara; 9.932 triÃ¡ngulos. Se aÃ±aden 37 StaticMeshActors al mapa **actual** `24_19.unr` con Location141000,57000,8000 y DrawScale0.48: 1.5 unidades L2 por unidad GoldSrc. Es una escala inicial para el recorrido, pendiente ajuste con cÃ¡mara/personaje real.

Se preservan byte por byte los 5.066 payloads previos fuera de myLevel, incluidas nave y muelle. myLevel recibe las referencias de los actores nuevos. Ambos archivos de cliente se cifraron Ver121, con verificaciÃ³n Ã­ntegra por roundtrip y CRC.

La geodata de `24_19.l2j` aÃ±ade 87.390 celdas; 2.153 tienen varias alturas de Dust2. Se preservan las capas anteriores; se modifican 1.648 bloques. Las superficies se extraen de los meshes nativos compilados; se comprueba el espacio vacÃ­o con planos/nodos/hojas del BSP original para excluir pisos dentro de sÃ³lidos o fuera del mapa. Bordes sin soporte se cierran. Todos los 40 puntos originales CT/T pertenecen al mismo componente navegable de 61.234 capas. Las cajas rompibles quedan estÃ¡ticas; los estados dinÃ¡micos y la semÃ¡ntica completa de todos los brushes de GoldSrc no se trasladan automÃ¡ticamente.

## Despliegue y verificaciÃ³n

Respaldo previo: `E:/l2-local/backups/dust2-integration-20261014-131945`. `installation.json` conserva hashes antes/despuÃ©s de 12 archivos. Se instalaron tambiÃ©n el handler, zonas y la entrada de CustomScriptFolders en runtime/source/cloud. Cada perfil de WorldContent.ini conservÃ³ su propio contenido y solo recibiÃ³ Dust2Arena; el perfil cloud tenÃ­a una lista diferente y no se sustituyÃ³ por la del runtime.

GameServer anterior18080 se apagÃ³ ordenadamente sin clientes conectados. Arranque con Start-L2Local.ps1; GameServer nuevo21308, puerto7777, registrado en LoginServer18184. No se detuvo LoginServer ni base de datos.

Comprobaciones realizadas:

- UModel modo L2 vuelve a leer los 105 recursos nativos sin referencias faltantes.
- PreservaciÃ³n de payloads originales, cifrado/CRC y hashes de instalaciÃ³n.
- CompilaciÃ³n Java del handler; carga real en el GameServer nuevo.
- Agent de prueba con Player transitorio, sin cuenta/personaje persistente: 40 alturas de inicio, ocho pasos permitidos, ocho bloqueados, diez consultas de pisos superpuestos, zona de paz y respawn, viajes reales CT/T y regreso al origen. PASS en `server-smoke.txt`.
- Se verifican los pisos anteriores del muelle, aeronave y Coliseo inferior.

**No se ha observado todavÃ­a en el cliente L2.** Falta revisar texturas/luz, cÃ¡mara, navegaciÃ³n completa por tÃºneles y detalles de escalones. No se certifica aÃºn lÃ­nea de visiÃ³n de skills ni preparaciÃ³n para PvP competitivo. Usa el cielo/luz de la regiÃ³n de L2; no reproduce el skybox ni los lightmaps de CS. No hay capacidad de sala, equipos ni evento activado.

## Herramientas y restauraciÃ³n

`build.py` prepara el paquete/mapa; `build_geodata.py` prepara capas; `prepare_server.py` prepara handler y perfiles preservados; `install.py --wrap` cifra; `install.py` instala con guardas, respaldo y rollback ante fallo. `prepare_smoke.py` genera la prueba Java desde la auditorÃ­a.

Para quitarlo: cerrar cliente y GameServer de forma sostenida (comprobar lanzadores), ejecutar `python research/dust2-integration/restore.py`. Verifica hashes actuales antes de restaurar. **Retirar Dust2 antes de intentar cualquier rollback histÃ³rico de aeronave o muelle.** No ejecutar instaladores antiguos sobre este mapa actualizado. No hay commit ni push.
