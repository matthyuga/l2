# Continuidad: comunidad, aventuras, rendimiento y mundo social

Fecha: 28/10/2026, hora de Argentina. Conversación iniciada el 27/10.
Proyecto real en esta PC: `E:\l2-local`. Cliente asociado: `E:\l2`.

## Leer primero al retomar

Esta bitácora conserva la conversación de diseño y las investigaciones de esta sesión. No describe funciones ya instaladas. El usuario cambiará pronto de PC y pidió conservar toda esta información.

La letra de unidad puede cambiar. Localizar la raíz real de `l2-local` y el cliente hermano antes de usar rutas. Nexus es un mapa de memoria, no la carpeta operativa. Si K: no está disponible, este documento y sus copias W10/W11 permiten continuar.

No se implementaron las nuevas salas, vehículos, torretas, impuestos ni eventos de esta conversación. No se modificaron configuraciones de juego ni se iniciaron pruebas de carga. No se hicieron commit/push, migración de datos o respaldo consistente de la base. Guardar esta bitácora no equivale a preparar una copia ejecutable del servidor en otra PC. No reiniciar ni cerrar juego/servicios por inferencia de estas ideas.

## Dirección expresada por Kevin

- Construir una comunidad sólida dispuesta a experimentar sensaciones además de competir. La competencia permanece, pero ahora el foco de interés son las aventuras y la vida compartida.
- Escuadrones de cuatro como unidad importante del servidor. Evitar en lo posible que toda la diversión y progresión obliguen a concentrarse en agites masivos.
- Mantener base +3 acumulativa como estándar principal del servidor y de los asedios habituales; experimentar con otras reglas en salas o circunstancias anunciadas.
- Eventos custom ocasionales, quizá fines de semana alternados o cada tanto, sin saturar ni exigir una frecuencia rígida. Quiere que se sientan como planes recreativos de un sábado por la noche.
- Reunión/festival, bromas y actividades sociales pueden desembocar en una expedición o mazmorra. Busca momentos emotivos de distintas clases, no solamente recompensas y ranking.
- Aprovechar mapas poco usados, modelos personalizados y descargas de assets para crear aventuras con identidad.
- La homogeneidad de servidores existía también antes; veinte años después se percibe diferente porque los veteranos ya conocen el recorrido. Interesa devolver descubrimiento y sorpresa.

Las recomendaciones del asistente que siguen son propuestas para evaluar, no decisiones definitivas de Kevin.

## Comentarios que originaron la charla

Capturas de comentarios públicos proporcionadas por Kevin:

1. Alexis Cerda: «Arregla el motor de juego para que no se frizee en masivo plzz».
2. Sabatino Sergio: broma sobre «la montura del lobo» y que nunca estará.
3. Elias Gonzalez: juega por nostalgia y diversión, pero ningún servidor le gusta al 100%; es exigente con la creatividad de Lineage 2.

Interpretación: deseos distintos de rendimiento, novedades y creatividad. La queja de congelación no identifica por sí sola si fallan FPS, red o servidor. La broma de montura puede referirse a expectativas sobre ese staff, no a imposibilidad técnica. Importar un modelo visible tampoco demuestra montaje, animaciones y funcionamiento jugable completos.

## Investigaciones de población: límites importantes

### L2 Sudamérica

- Web: https://www.l2sudamerica.com/ . Lo consultado anuncia Interlude x10, estado online y asedios dominicales a las 21 h; no se obtuvo contador verificable de simultáneos.
- Testimonio de agosto de 2026: estima 1.200–1.500 jugadores diarios y alrededor de 2.000 fines de semana. No es medición independiente ni aclara simultáneos/personas únicas/cuentas. https://www.reddit.com/r/chilegames/comments/1viyjm3/con_ganas_de_jugar_lineage_por_primera_vez/
- El índice del buscador mostró 1.867 para https://l2database.net/ ; al abrir la página el contador era «—». DESCARTAR 1.867 como medición actual.
- No se encontró conteo fiable de participantes de un único masivo.

### Ares: identidad pendiente de resolver

- No se halló cifra verificable actual ni récord histórico del Ares argentino.
- https://l2ares.com/ muestra Icons x3 y Origins x5 sin contador numérico en lo revisado.
- https://l2ares.com/news/ares-regresa (15/06/2026) declara expresamente un proyecto independiente sin relación con los antiguos administradores, apertura anunciada 03/07 22 h.
- Referencias de diciembre de 2006 nombran Ares x5 con subs acumulativas: https://foros.3dgames.com.ar/threads/351966-mejor-server-de-l2 . No dan población comprobable de Ares.
- Testimonio de 2007 menciona más de 1.000 usuarios de VENUS x10, otro servidor de MORPG, no Ares: https://www.elotrolado.net/hilo_lineage-2_760891 . No atribuir esa cifra a Ares.
- También aparecen La2Ares ruso, clanes y proyectos homónimos: no mezclar sus contadores.
- CORRECCIÓN/AMPLIACIÓN DE LA RESPUESTA PREVIA: una búsqueda posterior de acumulativas encontró https://gamear.com.ar/ con ARES WINTER C4 SubAcu x10 (14/08/2026), ERIS C4 SubAcu x25, HERA Interlude Main x10 y YIANA H5 Main x15. El usuario nunca confirmó cuál Ares quería investigar. La respuesta anterior se centró en l2ares.com; no debe tratarse como investigación exhaustiva del Ares de GameAr ni prueba de continuidad administrativa entre proyectos.

## Rendimiento: evidencia local recuperada

Leer los informes originales antes de volver a medir o cambiar configuración:

- `reports/capacity-benchmark-2026-10-11/INFORME.md`
- `reports/agite-100-2026-10-22/INFORME.md`
- `reports/multiroom-32-2026-10-22/INFORME.md`
- `diagnostics/ESTADO-Y-MONITOR-L2-20261023.md`
- `ANALISIS-TVT-2026-10-10-RUN2.md` es análisis de combate, no certificación de capacidad.

Prueba 22/10 de agite en una sala:

| Bots | Muestra | Ciclo IA p95 | Observación |
|---:|---:|---:|---|
| 25 | 58,9 s | 58,7 ms | Completó fase corta |
| 50 | 59,9 s | 88,6 ms | Completó fase corta |
| 75 | 89,5 s | 182,1 ms | Pico registrado de 1.555,9 ms |
| 100, repetición con escritura por lotes | 173,2 s | 315,9 ms | Se detuvo por timeouts SQL |

Primera pasada de 100: corte por ciclo superior a 10 segundos, que no llegó a escribirse como muestra normal. No ocultarlo al citar máximos. GameServer no se cerró, pero 100 bots juntos NO quedaron validados como carga fiable. Se observaron esperas Hikari en consumibles, telemetría y summons, además de trabajo frecuente de geodata/pathfinding. No atribuir todos los picos a una sola causa.

Varias salas: 32 participantes por sala (16vs16). Una sala p95 de barrido 58,3 ms; dos salas/64 bots 80,8 ms; tres salas/96 bots 120,1 ms. Tres salas completaron 180 s sin timeouts SQL ni daño cruzado observado, pero el objetivo era 100 ms y hubo retrasos. No son pruebas idénticas a 100 en una sala, por lo que no prueban causalmente una mejora exclusiva por instanciar.

Todas estas pruebas fueron SIN clientes humanos conectados: no certifican FPS, tráfico hacia espectadores, latencia real, estabilidad de horas ni capacidad para 1.000 humanos. Bots implican decisiones de IA/pathfinding adicionales; 100 bots no equivalen directamente a 100 jugadores humanos. Tampoco hay que extrapolar RAM por bot para deducir capacidad.

Entorno de las pruebas: i9-11900K, 8 núcleos/16 hilos, ~31,86 GiB RAM utilizable, JDK 25.0.4.1, ZGC, heap máximo 8 GiB. Es antecedente de esa máquina, no garantía del hardware de la próxima PC.

Lectura de configuración durante esta sesión:

- `server/game/config/Database.ini`: `MaximumDatabaseConnections = 10`.
- `server/game/config/Server.ini`: `MaximumOnlineUsers = 2000`; es límite de admisión, NO capacidad validada.
- `server/game/config/Threads.ini`: scheduled e instant en `-1` (cálculo automático).
- E: figuraba como «Seagate Portable Drive»; no se determinó tecnología/velocidad del medio.

Para 1.000 simultáneos: corregir SQL/IA, probar conexiones reales en escalones 100/250/500/750/1.000, distribución y concentración, login masivo y sesiones largas. Observar respuesta, colas, memoria/GC, SQL, red y cliente. CPU global baja no garantiza ausencia de bloqueo en un hilo. Se sugirió como punto de partida de infraestructura CPU de buen rendimiento por núcleo, 64 GB RAM, NVMe y red de datacenter con protección DDoS; NO es dimensionamiento medido ni recomendación de compra definitiva.

No aumentar el pool a 1.000 por tener 1.000 jugadores: se comparte. Referencias: https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing ; https://docs.oracle.com/en/java/java-components/jdk-mission-control/9/user-guide/using-jdk-flight-recorder.html

## Qué significa coordinador y separación normal/masivo

Se aclaró un uso demasiado amplio del término en respuestas previas. El coordinador medido organiza salas/bots custom, NO toda la simulación L2. El GameServer ya tiene administradores de movimiento, efectos, IA, etc.

Código inspeccionado: `server/game/data/scripts/custom/ElvenPvpRoom/PvpRoundRooms.java` programa `tick()` cada 100 ms (línea ~62); `public synchronized void tick()` (línea ~225) recorre salas/visitas y llama `bots.tick(now)`. Otras operaciones también usan el monitor del controlador. `PvpTacticalEngine.java` contiene decisiones tácticas. Núcleo de hilos: `source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/commons/threads/ThreadPool.java`.

Una tarea periódica lenta no se divide por añadir más hilos. Java no solapa sus ejecuciones sucesivas: https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledThreadPoolExecutor.html

Kevin planteó dos sistemas (mundo normal y masivo), después advirtió que duplicar el cálculo de personajes podría aumentar consumo/conflictos. Se explicó: repartir responsabilidades con un único responsable por estado/acción; no dos simulaciones independientes del mismo personaje. Separar colas/presupuestos puede aislar retrasos, pero comparte SQL/CPU y cuesta coordinación. Separar asedio completo o migrarlo a otra máquina es un cambio de núcleo mucho mayor. No arregla directamente FPS del cliente.

Kevin prefiere también controlar indirectamente la concentración mediante atractivos repartidos: salas limitadas a 32, varios objetivos, expediciones para cuatro, rutas/suministros/posiciones. Atención: varios objetivos no reparten gente si la mejor estrategia sigue siendo recorrerlos todos como una masa. Evitar obligar al masivo como centro de todo. No se implementó esa arquitectura.

## Subs acumulativas: público y salas experimentales

No se encontró encuesta representativa para afirmar qué elige la mayoría. Diferenciar:

- Main/clase única: un repertorio activo.
- Subs normales: alternar profesiones sin mezclar sus repertorios completos simultáneamente (según crónica pueden existir bonificaciones específicas).
- Base +1 acumulativa: combina dos clases; no equivale a «sin acumulativas».
- Base +3: combina cuatro, según restricciones del servidor.

Crítica documentada: balance e interacciones. Interpretaciones de diseño, NO encuesta: pérdida de identidad, menor complementariedad, combinaciones dominantes, reglas/excepciones difíciles de aprender. También hay seguidores de 1+1 por experimentación, autonomía y nostalgia de Dragon Network.

Fuentes: https://www.reddit.com/r/Lineage2/comments/qi7d1j/ ; https://www.reddit.com/r/Lineage2/comments/1k7mejf/lineage_2_dragon_network/ ; https://forum.pmfun.com/viewtopic.php?f=14&start=30&t=50973&view=print ; https://www.reddit.com/r/Lineage2/comments/kvtjcg/lineage_2_history_to_the_best_of_my_recollection/

Propuesta concreta de Kevin:

1. Sala especial de una clase seleccionable mediante interfaz.
2. Otra sala base +1.
3. Otra estándar base +3.
4. Asedios normales base +3; eventos/circunstancias anunciadas podrían restringir a base solamente.

Pendiente definir si «solo base» significa clase original o elegir cualquiera ya desarrollada. Sugerencia del asistente: permitir elección de clases poseídas, bloquear elección durante ronda y usar perfiles temporales sin borrar progresión. Deben cubrir activas/pasivas/masteries/stats, buffs previos, summons, equipo, consumibles, cooldowns, recursos y restauración al morir/salir/desconectarse. Ocultar botones no basta. Evaluar equipo propio vs normalizado como pruebas diferentes. Sugerencia inicial: una sala experimental rotativa para no fragmentar colas. Ninguna modalidad nueva fue instalada.

## Video de referencia: Project Gorgon

https://www.youtube.com/watch?v=_cAxMwJ8xV4
Título: «El Peor MMORPG de la HISTORIA - Project Gorgon», Bill el Botas. Publicado 31/10/2025, duración 1.053 s (~17:33). El nombre de la serie NO es un veredicto negativo sobre el juego.

Se obtuvo metadata y transcripción automática española completa por yt-dlp. No se hizo revisión visual plano a plano ni se descargó el video. Evidencia en `research/video-project-gorgon-20261027/metadata.json`, `captions.json`, `transcript.txt`. La transcripción puede errar nombres y mecánicas; escenas narradas no prueban comportamiento técnico exacto ni población.

Momentos y lecturas:

- ~1:20: derrota/maldición de cabeza grande genera un problema personal y una aventura para resolverlo.
- ~2:10–6:20: ayuda de jugadores, rutas y mazmorras conectadas; conocimiento del mundo como valor social.
- ~8:45–10:25: festival de poesía, música/bailes, reunión y posterior salida a mazmorra. Fue la escena que Kevin destacó como plan de sábado por la noche.
- ~11:55–12:35: formación del grupo; una jugadora adopta vaca para tanquear. Transformación con función, no solo estética.
- ~12:35–14:30: mundo de hadas, esperar la noche, palabras de poder, vuelo y transformación; descubrir y mostrar lugares también es recompensa.
- ~15:50: ayudar a otros como motivo para seguir entrando.

Interés inferido y confirmado por la conversación: curiosidad, consecuencias que abren aventuras, comunidad reconocible, cooperación y ocio sin obligación de ganar. No copiar la confusión/frustración como objetivo; orientar sin revelar todo. No se puede fabricar una comunidad amable solo programando un festival.

## The Endless Forest

Kevin recordó un juego social de ciervos/alces con gestos y experimentación. Candidato muy probable: The Endless Forest, Tale of Tales; Kevin aún no confirmó el nombre.

Fuentes: https://www.endlessforest.org/community/endless-forest ; https://www.indiegogo.com/en/projects/aurieamichaelharveysamyn/the-endless-forest-second-decade

Todos ciervos; sonidos/gestos y magia social; cambiar apariencia de otros fomenta interacción; sin objetivos obligatorios ni combate. Testimonio de junio 2026 menciona 20–40 conectados, no medición actual ni prueba de abandono: https://www.endlessforest.org/community/greetings-and-salutations-community-members-help-me-get-settled

Inspiración para L2: plazas/tabernas/bosques donde se pueda experimentar, tocar música, responder a acciones y compartir efectos sin optimizar estadísticas constantemente.

## Aventuras y comunidad: propuestas conversadas

Kevin quiere preparar mazmorras custom en mapas sin uso con modelos propios/descargados; presentó como ejemplo https://sketchfab.com/Vasian-Digital3D/models . No se auditó ese catálogo completo en esta sesión.

Sugerencias: reunión social -> incidente/pista -> expedición voluntaria -> regreso y relatos. Dar herramientas y pausas para improvisación; no guionizar cada minuto ni hacer obligatoria toda la velada. Base técnica reutilizable de puertas/pistas/diálogos/encuentros, historias distintas. Evitar recompensas de poder imprescindibles que castiguen faltar; valorar recuerdos, cosméticos y crónicas. Mantener actividades cotidianas entre eventos. Primer ensayo sugerido: una aventura breve para pocos escuadrones con lugar memorable, decisión compartida y cierre. Pendiente elegir y diseñar; nada construido.

## Fortaleza caminante: idea de Kevin

Capturas del visor local `127.0.0.1:32280` muestran una máquina amarilla con patas y cuerpo central, malla `ExternalAssets.ext3_6b9626c3ec83bc`. Esa ficha indica adaptación Interlude pendiente, sin NPC asociado.

Kevin imagina una araña mecánica gigante al estilo western, fortaleza móvil/gólem tripulable, NO montura individual ni aeroship. Escuadrón entra arriba o dentro; remodelar cuerpo para espacio hueco central. Pasajeros pueden atacar y vehículo tiene habilidad como fuego por la boca.

Propuestas: piloto orienta/mueve, operador maneja fuego, otros combaten/desembarcan. Preparación visible, arco frontal y calor podrían dar coordinación/contrajuego. Límites de tamaño, rutas, combustible/componentes vulnerables son ideas, no especificación aprobada.

Separar dificultades: remodelado interior; colisiones/geodata; pasajeros que acompañan movimiento/giro; origen/visibilidad de ataques. Hueco visual no implica piso transitable. Prototipo sugerido: máquina quieta con cuatro puestos y ataques; luego puestos fijos en movimiento; caminar libremente dentro en movimiento requiere investigación adicional. No afirmar viabilidad ya demostrada ni adaptación/rig completados.

## Defensas estáticas

Kevin propone torretas o artefactos que lanzan ataques/técnicas a distancia. Posibles variantes: proyectiles, lanzallamas de entrada, obelisco con técnica interrumpible y contención/revelado. Algunas operadas por jugador para dar función al escuadrón; automáticas limitadas.

Usos de aventura: reparar refugio, capturar arma, defender entrada mientras otro abre paso. Deben definir cantidad, duración, munición/recarga, rango, visión, selección de blancos y posibilidad de destruir/desactivar. Más accesibles como primer ensayo que transportar pasajeros, pero sin validación concreta. Primer prototipo sugerido: torreta operable fija con un disparo especial en escenario preparado. No implementado.

## Estancias, impuestos y fondos de ciudad

Idea de Kevin: ciertos lugares/ciudades cobran adena por estar allí, con componente social/lore. Un encargado administra fondos para fortificar o expandir el lugar. Solo moneda del juego.

Sugerencias para evaluar: no penalizar a quien conversa/espera amigos; alternativas de posada, residencia voluntaria, tasa por mercado/taller o contribución a obra. Un lugar autoritario puede tener impuesto de entrada/permanencia anunciado, importe/duración/tope claros, salida segura y sin deuda o confiscación automática.

Tesorería con registro público de ingresos/gastos/proyectos. Administrador inicialmente NPC; cargo de jugador posible con permisos de gasto restringidos, sin convertir fondos en retiro personal. Obras por etapas visibles preparadas, no construcción libre inicial. Adena + materiales/expediciones permite contribuir sin ser rico. Primer caso sugerido: reparar refugio o construir una torre. Importes pendientes de medir contra ingresos reales; no definidos ni instalados.

## Assets: estado real y nuevas descargas

Entrada: `descarga de assets/` en la raíz. Galería: `research/model-catalog/`, servidor local puerto 32280. Favoritos/planes se guardan en localStorage del navegador por PC; NO suponer que viajan solo copiando archivos. La galería tiene exportación de selecciones/planes; en esta sesión no se exportaron favoritos del usuario.

Trabajo de otra sesión encontrado: `research/external-assets-20261028/REVISION.md` documenta Tanda 3 a las ~11:52: 85 modelos listos GLB/miniatura, 1 pendiente Scary Guy/DAE, 2 duplicados agrupados, 29 con huesos fuente, 13 con clips exportados; 12 con texturas pendientes, 1 sin imágenes. Son vistas previas, NO paquetes UKX/UTX ni NPC jugables. No confundir con lo realizado en esta conversación. Documentación señala licencias/procedencia por ficha. No ejecutar lote entero para una reparación; usar `--keys` según su guía.

Después de «bajé más modelos», se compararon nombres de paquetes contra `research/external-assets-20261028/inventory.json`: 55 archivos nuevos, ~2,52 GiB. Son archivos nuevos por ruta, NO 55 modelos únicos validados. Se inspeccionaron directorios ZIP sin extraer: 29 FBX y 17 GLB a ese nivel; nueve paquetes sin modelo reconocido en ese nivel requieren revisar contenidos anidados/otros formatos. No se añadieron estas descargas a galería ni se verificaron visualmente.

Nombres nuevos registrados:

```text
alastor.zip
apex-legends-car-smg-mythic-allfathers-fury.zip
apex-legends-volt-smg-cyber-gradient.zip
apex-legends-volt-smg-graduate-thesis.zip
apex-legends-volt-smg-high-dosage.zip
apex-legends-volt-smg-neutralizer.zip
apex-legends-volt-smg-void-touched.zip
arachnida.zip
assault-drone-concept.zip
astro-armor-titan-cameraman-blaster.zip
astro-armor-titan-cameraman-fire-cannon.zip
beyond-resurreccion-grimmjow.zip
crimson-cup-plants.zip
deep-monstrosity.zip
deep-sea-angler-abyssal-horror-creature.zip
empire-flamethrower-energy-cannon.zip
female-spirit-character-3d-model-free.zip
grimmjow-jaegerjaquez.zip
hollow-ichigo-bankai.zip
kenpachi-zaraki-battle-damaged.zip
kukaku-shiba.zip
kurosaki-ichigo.zip
leocetus-leader.zip
lizard-man-warrior.zip
low-poly-female-warrior-character-3d-model.zip
lust.zip
mai-shiranui-anime-hot-girl-street-fighter.zip
martial-arts-fighter-girl-png-to-stl-supavoxel.zip
maw.zip
micheal-jackson-toilet.zip
mugetsu-ichigo.zip
primrose-egypt (1).zip
primrose-egypt.zip
quincy-ichigo.zip
reaper-aa-gun.zip
redhead-anime-swordswoman-png-to-stl-supavoxel.zip
rhythm-guardian-angel-3d-model-free.zip
sci-fi-toilet-mech.zip
serephina.zip
streer-fighter-juri-han-t-pose.zip
titanfall-2-weapon-car-smg.zip
titanfall-2-weapon-volt-smg.zip
twisted-disabler-gun.zip
u-concept.zip
ulquiorra-cifer.zip
ultron-cannon.zip
valak.zip
volt-ash-lord-bloodstrike.zip
w-o-d-reworkig.zip
watchman-of-doom.zip
wod-re-model.zip
yammy-llargo.zip
z-gravity-gun.zip
zaraki-kenpachi.zip
zeromus.zip
```

Arachnida y armas pesadas son candidatos por nombre para revisar junto a fortaleza/torretas; no se comprobó su correspondencia visual. No ejecutar assets o scripts de archivos descargados sin revisión. Próxima tarea posible: inventario incremental, extracción segura, formatos/rig/texturas/polígonos y publicación de previews conservando fichas/favoritos existentes; después elegir qué adaptar realmente a L2.

## Próximos pasos posibles, sin ejecución automática autorizada

1. Retomar con Kevin qué idea quiere priorizar: aventura inicial, salas experimentales, vehículo, torreta o ciudad.
2. Revisar incrementalmente los 55 paquetes y actualizar galería si ese es el trabajo solicitado.
3. Para prototipo jugable, definir primero alcance y reglas; validar capacidades del cliente/servidor antes de prometer movimiento de plataformas o remodelado de mapas.
4. Para rendimiento público, volver a los informes y resolver SQL/coordinación antes de escalar.
5. Para traslado, conservar proyecto + cliente + recursos y datos por un procedimiento consistente; no restaurar automáticamente respaldos históricos de octubre sobre el progreso actual. Consultar `CAMBIO-DE-PC-CONTINUIDAD.md` distinguiendo sus instrucciones históricas de la situación actual.

Frase para retomar: «Leé BITACORA-DISENO-COMUNIDAD-AVENTURAS-20261028.md en la raíz de l2-local; seguimos con las aventuras sociales, los modos de clases, la fortaleza caminante, las torretas y la ciudad financiada con adena».
