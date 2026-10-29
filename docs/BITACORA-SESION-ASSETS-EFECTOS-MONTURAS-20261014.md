# HELLGAMES — Bitácora de esta sesión

Actualizada el 14/10/2026, horario de Argentina. Esta bitácora resume esta conversación y el trabajo comprobado en E:\l2-local. Se conserva separada de la bitácora de la otra sesión; no se han conciliado sus cambios.

## 1. Proyecto e ideas generales

El nombre elegido es HELLGAMES. La idea del usuario es convertir L2 en un parque temático: aventureros que llegan a Giran en barcos voladores, academia centrada en practicar PvP con equipo inicial, arenas y eventos, economía y progresión opcionales. También se habló de campañas desde nivel 1 con historia y ambientación propia. Son ideas de diseño, no un conjunto de sistemas ya implementado por esta sesión.

Otros temas recordados: sets personalizados antiguos, indicadores de buffs sobre personajes, nuevos monstruos y NPCs, edición de agua/lava/nieve/suelos/estructuras con UnrealEd, cámaras y cinemáticas, importación de personajes y assets de Koikatsu y paneles de precarga/carga con identidad HELLGAMES. Las capturas históricas y las ideas no acreditan implementaciones actuales.

## 2. Biblioteca descargada

- Biblioteca central: K:\assets descargables de l2; catálogo CATALOGO.html.
- Escenarios/estructuras: 45 archivos conservados, incluyendo variantes, copias y el original defectuoso de Fantasy Island junto con su ZIP reparado. Tamaño registrado: 2.833.431.067 bytes.
- Monstruos, bosses y NPCs: 165 archivos 7z para 166 referencias; tamaño registrado: 985.712.566 bytes. Integridad comprobada y escaneo de Defender previo sin amenazas detectadas; eso no certifica compatibilidad ni seguridad absoluta.
- Fly Island sigue pendiente de una descarga utilizable; no confundirla con Fantasy Island ni Primeval Isle.
- Ningún código o DLL de los paquetes se ejecutó para esta preparación. Los contenidos de otras crónicas se conservan como recursos para inspección, sin presuponer compatibilidad Interlude.

## 3. Monstruos y NPCs en el visor

Se conservaron las 843 entradas anteriores como «Tanda original». Se añadieron 1.509 fichas «Tanda 2»: 1.379 vistas disponibles y 130 sin vista exportable. Las fichas incluyen variantes, piezas, objetos y efectos; no son 1.509 especies distintas. El visor permite filtrar por tanda y conserva las claves de favoritos.

Se corrigieron dos errores del importador: rutas con espacios truncadas al buscar materiales y sustitución incorrecta de argumentos cuando el paquete y el objeto tenían el mismo nombre. Recuperación registrada: 929 vistas adicionales con alguna textura. Resultado: 1.090 vistas con alguna textura y 1.075 con todos sus materiales texturados; todavía hay 289 sin textura resuelta y 15 parcialmente texturadas. Esto no equivale a 289 descargas dañadas.

El paquete «Monsters Pack With Skills and Effects» solicita EXS_MonstersTex, ausente en la descarga. Se marcaron 23 fichas con diagnóstico específico. Se buscaron alternativas Embryo, pero no se recuperó una descarga completa utilizable. Mallas disponibles no significan criaturas listas para jugar: faltan integrar IDs, estadísticas, IA y habilidades cuando corresponda.

Evidencia: research/npc-batch2/MATERIALES-CORREGIDOS.md y EXS-TEXTURAS-AUSENTES.md.

## 4. Escenarios: auditoría e importación terminada

La auditoría inspeccionó 45 archivos, 373 paquetes nativos y 71 archivos de mapa, contando copias y variantes. 44 archivos pasan integridad; el restante es el original conocido defectuoso de Fantasy Island, cuya copia reparada pasa integridad. Clasificación: 20 archivos sin referencias pendientes, 15 con avisos directos de mallas/terreno y 9 con referencias adicionales por revisar. Estas últimas pueden pertenecer a recursos no usados. Referencias presentes no certifican apariencia, colisiones, transitabilidad o compatibilidad.

Ejemplo concreto: Kamaloka Labyrinth solicita T_19_12.Height.19_12 y T_20_12.Height.20_12 sin paquetes correspondientes en biblioteca ni cliente local.

Primero se habilitó el filtro «Escenarios» para seis vistas existentes y se añadieron R4 Arena y Canon Cathedral. El usuario señaló suelo ausente: se recuperó el terreno original de ambas. R4 tiene siete capas activas; Canon tiene ocho capas activas y una entrada vacía. Las salas de Canon están bajo el relieve exterior, así que el terreno queda oculto al abrirlo y puede mostrarse con el botón correspondiente. No se confirmó conexión física entre todas las salas.

Después se deduplicaron los mapas pendientes por SHA256 y se procesaron 64 mapas/variantes. El supervisor terminó sus dos pasadas:

- 63 vistas nuevas publicadas de 64 tareas.
- 46 de esas 63 incluyen terreno; 17 siguen sin terreno incorporado.
- Una conversión fallida: Crystal-Island · 24_22. Existe otra vista de Crystal Island Bundle Pack · 24_22, pero conserva 14 actores omitidos; no son necesariamente archivos idénticos.
- 13 vistas nuevas tienen algún actor estático omitido. Destacan Elven Village de Salvation (449), Gludio Classic (44), Gludio GoD (29) y Crystal Island Bundle 24_22 (14). Un actor puede ser una pieza o adorno, no un edificio entero.
- Total actual del catálogo: 2.417 fichas; 71 son vistas de escenarios (8 anteriores + 63 nuevas).

Ya visibles, entre otros: Crow Island, World Tree Village, Garden of Eva, Genesis/Orbis/Octavis/Forest of Duel, Heart of Steel en ambas variantes, Aden Classic, Astatine, Disron, Fantasy Island y otras zonas de la biblioteca. La revisión visual realizada aquí fue de miniaturas representativas, no de todos los escenarios en WebGL ni en el juego. Las vistas siguen siendo parciales: no certifican BSP, agua, partículas, iluminación original, NPCs o colisiones.

La preparación de este lote no instaló estos nuevos escenarios en el cliente ni GameServer. Veilmar tenía integración previa documentada en VEILMAR-PVP.md; no atribuirla a este lote ni confundirla con validación completa de las nuevas vistas.

Accesos:

- Galería: http://127.0.0.1:32280/?category=Escenarios
- Estado final y enlaces: http://127.0.0.1:32280/import-progress.html
- Lanzador: GALERIA-MODELOS-L2.cmd
- Auditoría en K: AUDITORIA-ESCENARIOS.html, .md y .json.
- Resultados: research/scenario-batches/live-import-final.json y remaining-import-results.json.
- Pendientes actualizados: K:\assets descargables de l2\PENDIENTES-VISOR.md.

## 5. Efectos, buffs y skills

Se revisaron publicaciones de Blue Hero Aura, Mod Abnormal Effect, Six New Skills, Recompiled Interface con animaciones de songs/dances/chants, Dark Hero Aura/Hello Kitty y ejemplos de armas con efectos. Las nuevas descargas e instalaciones de estos efectos no se hicieron en esta sesión. Algunos son muestras o servicios comerciales, no paquetes gratuitos completos.

Ya hay paquetes descargados de NPCs con efectos: buffers, gatekeepers, eventos, Freya, Lindvior, Scarlet Van Halisha y otros. Su presencia en archivo no demuestra que funcionen en nuestro cliente. El visor glTF no reproduce automáticamente emisores Unreal ni la secuencia temporal de un skill; se propuso una sala de demostración dentro del cliente.

Distinguir efecto visual de habilidad mecánica: daños, buffs, duración y reglas dependen del servidor. Las estadísticas de Six New Skills son de ejemplo y necesitarían balance. Ideas propuestas: auras de eventos/facciones, avisos de ataques de bosses, portales, estados PvP legibles y celebraciones.

Fuentes y estado: research/visual-effects/README.md.

## 6. Monturas, alas y exploración vertical

Se localizaron publicaciones de Strider de L2 Revolution adaptado a Interlude, Queen Ant montable y un sistema Interlude Multi-Mounts publicado en octubre de 2026. El último anuncia integración comercial y comparte un paquete descrito como 13 modelos, con reportes de huesos faltantes o rotos. No se descargó ni probó ese paquete aquí; no afirmar que son 13 monturas funcionales.

Ya descargados como NPCs: Cobalt Horse, Phantom Horse, Rusty Steel Horse y otros caballos/jinetes. No se verificó que sirvan como monturas del jugador.

Idea del usuario: aprovechar techos, terrazas y plataformas flotantes para NPCs con historia, misiones, mercaderes secretos, objetos y easter eggs; algunas rutas se desbloquearían con vuelo. Se debe verificar suelo, colisión, acceso y aterrizaje.

Las alas de adorno no activan vuelo por sí solas. Pueden reducir trabajo artístico, pero no se ha comprobado que resulten más baratas técnicamente que una montura existente. Sin el video concreto no se identificó el skill del administrador ni se confirmó que desactivara geodata.

Comprobaciones en nuestro código local:

- Montar desequipa arma/escudo, detiene toggles y retira la mascota como entidad independiente.
- El Strider permite skills mágicos; Hydro Blast montado no se probó en el juego.
- La Wyvern activa el estado de vuelo y limita skills a los propios de la Wyvern.
- El vuelo cambia el tratamiento de altura, pero no elimina todas las comprobaciones de geodata o puertas.

Idea de combate del usuario: lanzar Hydro Blast desde una montura tanque que absorba golpes antes que el jinete. No existe así ni se implementó. Se propuso un pool de HP lógico de montura que reciba daño y provoque desmontaje al agotarse; una criatura independiente seleccionable sería un trabajo mayor. Habría que definir curación, CP, daño continuo, debuffs y caída/aterrizaje si muere volando.

Evidencia y fuentes: research/mounts/README.md y VUELO-Y-COMBATE.md.

## 7. Qué sigue pendiente

1. Resolver Crystal-Island 24_22 y revisar los 17 terrenos pendientes y las 13 vistas con actores omitidos.
2. Corregir materiales pendientes y comprobar escenarios visualmente antes de llamarlos completos.
3. Evaluar efectos en una sala de demostración del cliente, con respaldos y sin reemplazar mods completos a ciegas.
4. Descargar y evaluar modelos de monturas; comprobar esqueleto, posición del jinete y animaciones antes de integrarlos.
5. Prototipar vuelo de exploración y, por separado, combate montado con HP propio, cuando se retome su implementación.
6. Contrastar esta bitácora con la otra sesión antes de consolidar decisiones o atribuir cambios a un mismo trabajo.

No reejecutar finalizadores históricos de build_gallery.py sobre todo el catálogo: pueden perder tandas y escenarios personalizados. Los scripts nuevos tienen cachés, manifiestos y respaldos propios.
