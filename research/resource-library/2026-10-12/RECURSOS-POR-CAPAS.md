# Recursos por capas para nuestro server

Primera tanda: **12 de octubre de 2026**. Proyecto: `E:\l2-local`, cliente `E:\l2`, Mobius CT_0 Interlude con subclases acumulativas, pilotos, Amber y escenarios de Giran.

Pedido de Kevin: buscar ampliamente y ordenar por capas, incluyendo guías, experiencias, equipo, interfaces y eventos. Esta selección abre una biblioteca ampliable; no pretende agotar todo lo publicado.

## Cómo leer los estados

- **Local**: encontré archivos o documentación en nuestro disco. No implica que la función esté habilitada o probada.
- **Consultado**: pude leer la página del autor/proyecto o el hilo. Compatibilidad y descargas pendientes, salvo indicación expresa.
- **Descargado**: conservamos original, licencia y hash. Todavía no está integrado en L2.
- **Pista**: acceso incompleto, enlace dudoso o resultado indexado que no pude confirmar directamente.

Las recomendaciones y experimentos son propuestas nuestras. Las capacidades anunciadas por otros proyectos y los relatos de usuarios se identifican como tales.

## 1. Guías y herramientas

| Recurso | Utilidad para nosotros | Estado y encaje |
|---|---|---|
| [UModel / UE Viewer, Gildor](https://www.gildor.org/en/projects/umodel) | Inspeccionar mallas, huesos, animaciones y materiales; exportar para estudio. | Consultado y local en `research/amber-l2/tools`. Ya alimenta nuestra galería; priorizar su uso. El visor tiene limitaciones de materiales y animación. |
| [L2ClientDat, Mobius](https://github.com/MobiusDevelopment/L2ClientDat) | Abrir/guardar DAT y estudiar las estructuras de los catálogos. | Consultado y local en `research/amber-l2/tools/L2ClientDat`. Usar la estructura exacta de nuestro cliente; comprobar ida y vuelta antes de editar. |
| [L2Tool, acmi](https://github.com/acmi/l2tool) | Visor y reemplazo de texturas de L2. | Consultado; MIT en el repositorio. Ya existe `tools/Sedona-L2Tool`, que debe identificarse por su propia versión. No asumir que es idéntico al original. |
| [io_scene_psk_psa, DarklightGames](https://github.com/DarklightGames/io_scene_psk_psa) | Importación/exportación PSK/PSA en Blender. | Consultado; copia local 5.0.6. La documentación actual separa Blender 4.2+ y versiones anteriores. Conservar la versión usada con Blender 3.5.1 hasta probar otra. |
| [Adapting Skills And Effects To Interlude, GLO](https://maxcheaters.com/topic/211019-adapting-skills-and-effects-to-interlude/) | Guía original de adaptación de efectos y skills entre crónicas. | Consultado; publicada en 2016. Interesa por su explicación de paquetes/UCC y límites del cliente. Sus binarios y adjuntos antiguos no se comprobaron. |
| [Herramientas de edición Classic/IL, Lucera2](https://forum.lucera2.com/threads/all-programs-for-client-edit-classic-il.8192/) | Mapa de herramientas para DAT, texturas y cliente. | Consultado. Usar como índice y rastrear la fuente de cada herramienta; Lucera no es nuestro core Mobius. |

**Guía práctica propuesta:** recorrer un solo recurso de punta a punta: fuente → exportación → adaptación → paquete → DAT → referencia del servidor → cliente. En cada paso guardar nombres, versión y dependencias. Amber ya nos proporciona un ejemplo local bastante más específico que un tutorial genérico.

## 2. Equipo, armaduras y cosméticos

| Recurso | Qué aporta | Estado y siguiente comprobación |
|---|---|---|
| Catálogos nativos del cliente y XML de `source/L2J_Mobius_CT_0_Interlude/dist/game/data/stats/items` | Base para armas, armaduras, joyas y accesorios coherentes con el juego. | Local. Cruzar ID de objeto, nombre, malla y textura antes de importar novedades. La galería actual está centrada en NPC/mallas y no constituye un catálogo completo de equipo. |
| `custom/Transmog/Transmog.java` y `config/custom/Transmog.ini` | Sistema de apariencia de equipo ya presente en nuestra base. | Local. `TransmogEnabled = False` en el archivo de **source** consultado; no se comprobó la configuración del runtime. Revisar soporte de paquetes cliente, SQL y slots antes de activarlo. |
| [Fafurion weapons H5 and IL, Asuki](https://maxcheaters.com/topic/223065-fafurion-weapons-h5-and-il/) | Candidato concreto de armas visuales para Interlude. | Consultado; el publicador distingue H5 e IL. Enlaces de archivos visibles, no descargados ni auditados. Permisos de redistribución sin confirmar. |
| [All Weapon Shares, CriticalError](https://maxcheaters.com/topic/240151-all-weapon-shares-by-criticalerror-merged/) | Colección para localizar diseños y sus publicaciones. | Consultado. Es un índice de shares: comprobar crónica, procedencia y disponibilidad de cada entrada por separado. |
| [L2Custom: features](https://l2custom.com/page/features) | Referencia de diseño: skins, equipo custom y reglas diferenciadas para Olympiad. | Consultado; describe su propio server, no ofrece una biblioteca con licencia de assets. Sirve para comparar decisiones de progresión. |

**Propuesta nuestra:** primero un arma o apariencia que conserve las estadísticas del equipo base. Comparar lectura de silueta, tamaño, agarre, animaciones y efectos. Una armadura requiere revisar cuerpos/razas/sexos y slots; no la trataría como una textura intercambiable. Las builds acumulativas de nuestro server necesitan mediciones propias: una guía vanilla no decide su balance.

## 3. Interfaces, iconos y mapas de ayuda

| Recurso | Uso posible | Estado y condiciones |
|---|---|---|
| [Kenney UI Pack — RPG Expansion](https://kenney.nl/assets/ui-pack-rpg-expansion) | Botones, barras, paneles y flechas para el laboratorio, prototipos o un nuevo panel. | **Descargado**, CC0. En `assets/kenney-ui-rpg/source`. Preview inspeccionada: estilo sencillo, más próximo a un prototipo que a la interfaz ornamental de L2. No reemplaza `Interface.u`/XDAT. |
| [Game-icons.net](https://game-icons.net/about.html) | Iconos para órdenes, estados, eventos, contratos y roles. | Consultado; CC BY 3.0, requiere crédito al autor. Elegir iconos individuales y mantener atribuciones. Rasterizar y empaquetar para cliente; SVG sirve directamente en herramientas web. |
| [Abstract Interface, Petr](https://mmo-dev.info/resources/abstract-interface-for-interlude.3866/) | Referencia de interfaz Interlude, party e inventario. | Consultado parcialmente. El autor indica protocolo 746 y cambios en `nwindow.dll`/`engine.dll`; contenido completo requiere cuenta. No se comprobó descarga ni compatibilidad con nuestro HUD. |
| [Silent Interface Interlude Style](https://maxcheaters.com/topic/241747-silent-interface-interlude-style/) | Otra referencia visual de HUD para comparar densidad y organización. | Hilo consultado, publicado por Celestine. Binarios, permisos y compatibilidad pendientes. |
| [TownMap para IT, Petr](https://mmo-dev.info/resources/%D0%A2%D0%B5%D0%BA%D1%81%D1%82%D1%83%D1%80%D1%8B-townmap-%D0%B4%D0%BB%D1%8F-it.3767/) | Mapas de ciudades y mazmorras como ayuda de orientación. | Página consultada; contenido/descarga y licencia por verificar. |
| [Minimapa para IT, estilo Essence, Petr](https://mmo-dev.info/resources/%D0%A2%D0%B5%D0%BA%D1%81%D1%82%D1%83%D1%80%D1%8B-%D0%BC%D0%B8%D0%BD%D0%B8%D0%BA%D0%B0%D1%80%D1%82%D1%8B-%D0%B4%D0%BB%D1%8F-it-%D0%BF%D0%BE-%D1%82%D0%B8%D0%BF%D1%83-essence.3756/) | Referencia de legibilidad para exploración. | Página consultada; verificar versión y recursos necesarios. |

**Experiencia relevante:** en [MetaMan Buffer / Lucera2](https://forum.lucera2.com/threads/metaman-version-buffer.6539/page-2), usuarios describen errores al llevar un buffer a Interlude, límites de HTML y dificultades con iconos y tabs. Son reportes del hilo, no un diagnóstico de nuestro cliente. Para nosotros: un panel que funciona en otra crónica necesita una prueba mínima de tamaño, etiquetas, navegación y bypass.

## 4. NPC, criaturas, monturas y animaciones

| Recurso | Uso posible | Estado y encaje |
|---|---|---|
| Nuestra [galería de modelos](../../model-catalog/README.md) | Elegir guardianes, mercaderes, invocaciones y jefes con estética nativa. | Local. La documentación informa 643 registros/642 miniaturas tras añadir Amber. Verificar la ficha de cada candidato y sus animaciones; algunas entradas tienen limitaciones de materiales. |
| [Quaternius Ultimate Monsters](https://quaternius.com/packs/ultimatemonsters.html) | 50 monstruos animados como materia prima para criaturas propias. | Consultado; el autor declara CC0 y ofrece formatos de trabajo. No es un pack UKX listo para Interlude. Necesita conversión, materiales y animaciones adaptadas. Estética estilizada. |
| [Guardian Strider y Armored Flying Dragon, johnscott](https://maxcheaters.com/topic/139241-shareinterludeguardian-strider-and-armored-flying-dragon-m0unts/) | Candidatos históricos de monturas para IL. | Consultado. Descarga, animaciones, colisiones y permisos pendientes. Una montura exige validar comportamiento además del modelo. |
| [Dwarf Stylish Update, NevesOma](https://maxcheaters.com/topic/248850-free-dwarf-stylish-update-new-bow-animation-in-lineage-2/) | Curiosidad: postura y animación de arco de la enana. | El autor declara Interlude; un comentario posterior informa enlace caído. **Referencia**, no descarga disponible confirmada. |

**Propuesta nuestra:** seleccionar en la galería cinco roles —guardián, explorador, mercader, healer y jefe— antes de traer más mallas. Comparar altura, escala, selección y alcance visible. Con Amber ya sabemos que nombre correcto y spawn correcto no bastan para demostrar carga de malla o animación.

## 5. Materiales, efectos y sonido

| Recurso | Uso posible | Estado y adaptación |
|---|---|---|
| [Kenney Particle Pack](https://kenney.nl/assets/particle-pack) | Humo, destellos y máscaras para efectos. | Consultado; CC0, 80 archivos anunciados. **Ya existe** en `research/amber-l2/assets/external/kenney-particle-pack`; no se duplicó. Texturas fuente, no efectos L2 terminados. |
| [Effekseer Recorder](https://effekseer.github.io/Help_Tool/en/ToolReference/record.html) | Diseñar un efecto y exportar frames/spritesheets, incluyendo separación de mezcla/aditivo. | Consultado; ya hay material local. Nuestro cliente no tiene runtime Effekseer: adaptar la salida a materiales y emisores nativos. Comprobar licencia de cada ejemplo usado. |
| [Poly Haven](https://polyhaven.com/license) | Materia prima para piedra, cuero, metal y modelos de referencia. | Consultado; sus assets son CC0. Adaptar resolución y apariencia al render antiguo. La licencia de assets no equivale a permiso para copiar toda la web. |
| [ambientCG](https://ambientcg.com/) | Biblioteca de materiales para trabajo en Blender y nuevas superficies. | Consultado; declara CC0. Los mapas PBR no se instalan directamente como materiales de Interlude: diseñar una versión para su sistema de shaders. |
| [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds) | Confirmación, cancelación, error y navegación del panel/lab. | **Descargado**, 100 OGG y licencia CC0. En `assets/kenney-interface-sounds/source`. No se escucharon ni probaron en L2. |
| [Freesound](https://freesound.org/help/faq/#licenses) | Campanas, ambiente, impactos y sonidos de eventos. | Consultado. Licencia por archivo: CC0, BY o BY-NC, entre otras históricas. Seleccionar muestras con autor/licencia guardados; no considerar libre toda la biblioteca. |

**Propuesta nuestra:** un destello breve de orden recibida y una señal audible en el panel. Después probar humo o una zona de peligro con pocas entidades y luego durante Giran. Medir visibilidad y coste en cliente; un efecto vistoso en aislamiento puede tapar objetivos en combate.

## 6. Eventos, PvE, PvP y curiosidades nativas

Ya hay material aprovechable en **nuestra propia source**, sin descargar otro datapack. No activé estos sistemas ni comprobé su ejecución:

| Material local | Ruta bajo `dist/game/data/scripts` | Qué explorar |
|---|---|---|
| Christmas, HeavyMedal, L2Day | `events/` | Eventos de colección e intercambio; revisar NPC, drops, calendario y recompensas. |
| CaptureTheFlag | `custom/events/CaptureTheFlag` | Objetivo de bandera para comparar con el combate puro. En el `config.xml` leído, el ejemplo de horario está comentado. |
| TeamVsTeam y Deathmatch | `custom/events/` | Bases de eventos por equipos y todos contra todos; revisar inscripción, respawn y limpieza. |
| Race y Elpies | `custom/events/` | Actividades ligeras para alternar con PvP. Leer reglas antes de diseñar recompensas. |
| Wedding | `custom/events/Wedding` | Capa social que podríamos estudiar si encaja con el mundo. |
| RainbowSpringsChateau, WildBeastReserve, BanditStronghold y otras | `conquerablehalls/` | Mecánicas de clan hall como referencia de objetivos alternativos. Presencia de scripts no garantiza contenido completo. |

La ruta base es `source/L2J_Mobius_CT_0_Interlude/`. Nuestro runtime es `server/`; las decisiones de activación deben comprobarse allí.

**Fuentes externas:** [respuesta del propio Mobius sobre HeavyMedal](https://l2jmobius.org/forum/index.php?topic=10236.0) y [discusión de adaptación de TvT a C6](https://l2jmobius.org/forum/index.php?topic=11600.0). La segunda es de 2024; no describe necesariamente nuestra revisión actual. Un [reporte de friendly fire en eventos](https://l2jmobius.org/forum/index.php?topic=15372.0) apareció indexado, pero el acceso directo devolvió 403: queda como **pista**, no como bug confirmado.

**Ideas propias para una tanda de prototipos:** escolta de caravana entre dos puntos ya transitables; defensa de un servicio de Giran; captura de tres posiciones; rescate de un aliado; cacería de élite con pistas; torneo de builds con condiciones fijas. Todos necesitan reglas de victoria, derrota, desconexión, limpieza y recompensas antes de construirlos.

## 7. IA, compañeros y mundo vivo

| Recurso | Qué podemos estudiar | Estado |
|---|---|---|
| [L2Everdream — features](https://l2everdream.com/features) | Declara Mobius Interlude, modo local, sims reclutables y economía simulada. Muy cercano a nuestro objetivo de mundo vivo. | Consultado; afirmaciones del proyecto. No se instaló ni se validó su capacidad. |
| [Everdream — Smart Roam](https://l2everdream.com/wiki/systems/smart-roam) | Parties que reconsideran el lugar de caza y explican su decisión; jugador con opción de mantener el destino. | Consultado. Nos interesa adaptar la idea de órdenes comprensibles y decisiones por party; no copiar sus constantes sin medir. |
| [Everdream — Party Composition](https://l2everdream.com/wiki/systems/party-composition) | Formaciones, roles y composición de grupos por contenido. | Consultado; referencia para nuestros pilotos y soportes. Sus tablas no están calibradas para subclases acumulativas. |
| [Everdream — How the world thinks](https://l2everdream.com/wiki/systems/how-the-world-thinks) | Cadencia compartida y observabilidad de decisiones. Publica una medición de desarrollo con consumo considerable de CPU/RAM. | Consultado. Son métricas de su entorno, no una capacidad extrapolable a nuestro heap de 8 GiB ni a nuestro cliente. |
| [Teravibes / L2-Living-Worlds](https://github.com/Teravibes/L2-Living-Worlds) | El README indexado describe tiendas, parties reclutables y chat LLM opcional sobre CT_0. | **Pista**: búsqueda mostró el README, pero la apertura directa devolvió 404. No considerar código disponible hasta reconfirmarlo. |

**Experimento propio sugerido:** primero una party de tres miembros con agenda de patrulla/descanso/servicio y órdenes explícitas. Medir atascos, latencia de decisión, curación útil y respuesta al usuario. El número de bots por sí solo no mide cuánto vive el mundo.

## 8. Mapas, geodata y navegación

| Recurso | Uso posible | Estado y límites |
|---|---|---|
| [l2mapconv-public, fork m49n](https://github.com/m49n/l2mapconv-public) | Visor, generación de geodata y laboratorio de rutas. | Consultado; MIT. El README enumera clientes probados C1/HF/Essence P542 y navmesh experimental. No demuestra compatibilidad con nuestro Interlude ni integración directa en Mobius. |
| [Disron Village + area, deMEV](https://maxcheaters.com/topic/240813-share-disron-village-area-for-interlude-and-lower/) | Candidato histórico de zona nueva para IL y anteriores. | Consultado. Comentarios advierten falta de geodata y problemas de presentación. Archivo/licencia no auditados; sería una prueba aislada, no un mapa listo para combate. |

Separar cuatro cosas al diagnosticar: superficie visible del cliente, alturas/paso de geodata, ruta que calcula el servidor e intención que emite la IA. Nuestra prueba mínima debería incluir puerta, escalera, esquina, piso elevado y persecución con summon, registrando origen/destino y resultado.

## 9. Experiencias de jugadores y dueños

Estos casos son testimonios y discusiones, no una muestra representativa de toda la comunidad. Conviene leer también respuestas y desacuerdos.

### Mundo simulado: el síntoma no decide la causa

En [esta discusión de proyectos offline](https://www.reddit.com/r/Lineage2/comments/1w6zm6o/found_some_interesting_lineage_2_simulatedoffline/), jugadores valoran Everdream y reportan clipping/atascos. Su desarrollador responde que genera geodata propia y atribuye varios problemas a navegación y lógica del servidor. Ambos lados coinciden en que hay incidencias, pero discrepan sobre su causa. **Aplicación propuesta:** reproducir el atasco con coordenadas y ruta antes de reemplazar geodata.

### Bandos: contar registrados no mide una batalla

En [WARFRONT: balance de facciones](https://www.reddit.com/r/Lineage2/comments/1wkmvx8/faction_pvp_servers_always_end_up_unbalanced_how/), el creador plantea actividad reciente, incentivos y mercenarios temporales. Las respuestas discuten equipos por evento, conservar grupos de amigos y evitar que las recompensas agranden la ventaja del ganador. **Aplicación propuesta:** comparar presencia, roles, equipo y contribución en nuestro Giran; cualquier regla de compensación debe ensayarse con población pequeña.

### Beta: probar lo que los jugadores realmente hacen

El [balance posterior a la beta de WARFRONT](https://www.reddit.com/r/Lineage2/comments/1wyyuqn/you_guys_helped_to_develop_the_server_heres_how/) relata cambios a partir de feedback y primeras batallas. Es el testimonio del creador, no una auditoría. **Aplicación propuesta:** una sesión corta con escenarios y preguntas concretas sobre orientación, control de aliados y claridad de objetivos, además de nuestras mediciones técnicas.

### Soportes: comodidad y roles necesitan una decisión

En [una consulta para jugar en dúo](https://www.reddit.com/r/Lineage2/comments/1wdabm6/finding_a_populated_server_for_duo/), aparece explícitamente la pregunta de si los soportes siguen haciendo falta cuando hay NPC buffer. **Aplicación propuesta:** definir qué aportan healer, buffer y bardos durante combate, y comprobarlo con nuestros pilotos. Evitar decidirlo solo por daño infligido.

### Economía: una incidencia también afecta a terceros

En [una discusión de 2024 sobre Reborn](https://www.reddit.com/r/Lineage2/comments/1gsb1r6/l2reborn_is_a_failed_server/), participantes disputan el impacto de supuestos errores económicos y cómo recuperar moneda ya intercambiada. No verifiqué esas acusaciones ni sus cifras. **Aplicación propuesta:** registrar creación/destrucción de Adena y movimientos de objetos, y ensayar restauración en una copia antes de abrir intercambios a terceros.

### Cosméticos y recompensas

[L2Custom](https://l2custom.com/page/features) sirve como ejemplo publicado por un dueño de cómo separar algunas reglas de equipo de Olympiad. Para nuestro laboratorio, propongo estudiar premios visuales antes de añadir poder permanente; esa preferencia es nuestra, no evidencia de que un modelo sea universalmente mejor.

## 10. Operación, mediciones y prioridades

Ya contamos con backups, telemetría, perfiles de builds y documentación de fallos de geodata. Conviene conectar cada incorporación a esa infraestructura.

| Orden propuesto | Trabajo concreto | Qué permite decidir |
|---|---|---|
| 1 | Selección de cinco modelos nativos y seis iconos de órdenes | Identidad visual con poco trabajo de conversión. |
| 2 | Revisar Transmog en nuestra revisión y una apariencia de arma | Viabilidad de personalización sin introducir una nueva escala de stats. |
| 3 | Leer reglas/config de CTF, Race y HeavyMedal locales | Qué eventos podemos aprovechar de la base que ya tenemos. |
| 4 | Party con tres roles y agenda acotada | Si la actividad se siente comprensible y controlable. |
| 5 | Prueba de rutas con puerta/escalera/summon | Distinguir problemas de movimiento antes de ampliar escenarios. |
| 6 | Primer VFX breve y señales del panel con los sonidos descargados | Legibilidad y coste visual/audio. |
| 7 | Informe de batalla por bando: participación, daño, curación, bajas y objetivos | Balance que incluya soportes y cumplimiento de objetivos. |

Para assets: conservar autor, URL, licencia, archivos fuente, nombres de paquete y dependencias. Para mods: además, crónica/protocolo, versión del core, alcance de cambios y forma de volver atrás. En el cliente verificar luz exterior/interior, movimiento, selección y carga junto a otros actores; en eventos, inicio/fin, salida del jugador y limpieza. Son criterios para futuras pruebas; no se ejecutaron en esta búsqueda.

## Material reunido y límites de esta tanda

- Dos packs originales descargados desde Kenney, extraídos en esta carpeta; licencias CC0 leídas y SHA-256 calculados. Total de ambos ZIP: 1.048.930 bytes, aproximadamente 1 MiB.
- UI: 87 PNG individuales bajo `PNG/`, además de preview, sample, spritesheet y vector. El sitio anuncia 85 recursos; el conteo del ZIP se conserva por separado, sin equiparar ambos números.
- Sonido: 100 OGG; inventariados, todavía sin audición ni conversión.
- Particle Pack y herramientas de Amber: ya estaban en disco; se enlazan en lugar de duplicarse.
- Enlaces de foro consultados no equivalen a descargas verificadas. Algunas páginas requieren cuenta; hay una pista con 404 y otra con 403, indicadas arriba.
- No se compraron recursos ni se integraron estos materiales al cliente/runtime durante la búsqueda.
- Siguiente ampliación útil: armaduras por raza/sexo, mapas con geodata demostrable, sonidos de ambiente concretos y relatos posteriores al lanzamiento de servidores pequeños.

