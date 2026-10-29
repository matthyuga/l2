# Bitácora — experiencia de jugadores, endgame e ideas de eventos

Fecha: 13/10/2026. Proyecto real: `E:\l2-local`, laboratorio Lineage II Interlude. Registro solicitado por Kevin para conservar lo conversado y poder retomar entre sesiones.

## 1. Contexto y separación de trabajos

Kevin señaló que se habían mezclado dos sesiones: una dedicada a assets, equipo, mapas y territorios; esta conversación pasó a estudiar experiencia de jugadores y endgame. Los recursos visuales pueden servir al diseño, pero descargarlos o integrarlos no demuestra que exista una actividad jugable nueva.

Antecedentes de la conversación: búsqueda por capas de guías, experiencias, equipo, interfaces y eventos; packs de armas, armaduras y accesorios; Fafurion y GM shop; maniquíes de equipo en Giran; contenidos de campañas y quests; identificación de cascos/sets y posible recoloreado con fuego azul. También se habló de alojamiento, equipos domésticos y consumo eléctrico. Esta bitácora no vuelve a auditar esas tareas ni certifica su estado técnico actual.

Referencias para el contexto anterior:

- [Biblioteca general de recursos](../../resource-library/README.md).
- [Bitácora previa de ideas y pendientes](../../resource-library/2026-10-12/BITACORA-IDEAS-Y-PENDIENTES.md).
- [Selección de recursos por capas](../../resource-library/2026-10-12/RECURSOS-POR-CAPAS.md).
- [Escenarios y estado de preparación para el visor](../../scenario-batches/README.md).

El set negro/rojo de la referencia y su posible variante azul quedan pendientes de identificación de archivos exactos. No registrar como realizado un recoloreado o efecto animado.

## 2. Problemas expresados por Kevin

Kevin mencionó L2 Fenix y otras historias que suelen terminar en decepción. Los ejemplos abarcan servidores que cierran al poco tiempo, poca actividad, aparente abandono del administrador y jugadores pidiendo que el GM reactive el mundo.

Otro problema fue el esfuerzo para conseguir sets caros: mucho farmeo, llegada de un set superior y debilitamiento del anterior. También planteó si una experiencia limitada puede atraer de nuevo a veteranos o interesar a generaciones nuevas ante la oferta actual de juegos.

Se guardó un [registro separado de su testimonio](TESTIMONIO-KEVIN.md). No se atribuyen todos los episodios a Fenix ni se afirman causas comerciales: faltan fechas, versiones y cambios concretos para estudiar cada caso.

## 3. Investigación realizada

Se consultaron segmentos de 13 hilos/publicaciones en seis sitios: Reddit, MaxCheaters, L2Classic.Club, Lineage2Dex, Ars OpenForum y MMORPG.com. El corpus incluye material histórico y discusiones recientes. Las fichas conservan enlaces, fechas disponibles, alcance de lectura y desacuerdos.

Resultado guardado:

- [FUENTES.md](FUENTES.md): corpus comentado, incluidas pistas cuya apertura falló.
- [ANALISIS.md](ANALISIS.md): síntesis e implicaciones de diseño.
- [MATRIZ-DE-DECISIONES.md](MATRIZ-DE-DECISIONES.md): hipótesis y pruebas antes de implementar.

No se archivaron íntegramente los foros. La muestra es cualitativa y parcial; no demuestra tasas de cierre, tamaño de la población ni eficacia de una fórmula de servidor. Las acusaciones de participantes no se adoptaron como hechos verificados.

## 4. Conclusiones provisionales que discutimos

Estas son interpretaciones propias del análisis, no resultados de pruebas con nuestro público:

- Estudiar disponibilidad técnica, participación social y confianza por separado. Un mundo puede seguir online y ofrecer pocas oportunidades de jugar con otros.
- El farmeo no es rechazado por todos. Importan su finalidad, variedad, coste de tiempo y las experiencias a las que permite acceder.
- Proteger el valor del esfuerzo previo: considerar variantes por función, evolución que aproveche equipo anterior y reglas de balance previsibles. No descartar nerfs necesarios; explicar sus motivos y consecuencias.
- Contar actividades accesibles, no únicamente quests, NPCs, bosses o mapas presentes en archivos. Horarios, grupos, monopolios y diferencia de equipo pueden cerrar el acceso real.
- Estudiar vías de entrada, regreso después de una pausa y participación después de perder una guerra.
- Considerar veteranos con menos tiempo y principiantes que no conocen clases, economía, controles o finalidad de la progresión. Hay casos de interés nuevo, también en español, pero no datos para asegurar demanda masiva.
- Revisar monetización y abuso por sus efectos sobre oportunidades y economía, no solo por las estadísticas finales.
- Ajustar espacios activos y objetivos a la concurrencia; más mapas abiertos pueden dispersar jugadores.

Se mantuvieron opiniones contrapuestas: progresión lenta o rápida, persistencia o temporadas, autofarmeo o participación manual, fidelidad clásica o custom. Ninguna se convirtió en decisión definitiva.

## 5. Campañas y contenido nativo

Kevin ya había observado que Seven Signs, Ketra/Varka y las partes de Noblesse pertenecen al juego existente. No presentarlos como campañas nuevas descargadas.

Interés que se conserva: comprender el sistema para crear quests y campañas propias con personajes, motivos, decisiones y consecuencias. Cambiar el texto de una tarea repetitiva no garantiza una experiencia narrativa diferente. Guías de autoría y prototipo de campaña quedan para trabajo posterior.

## 6. Idea nueva de Kevin: evento inspirado en CS 1.6

Propuesta: equipos azul (CT) y rojo (T), partidas delimitadas y equipo exclusivo del evento.

| Modo | Idea de Kevin | Aspectos a resolver |
|---|---|---|
| C4 | Un jugador lleva bomba, sitio marcado en rojo, plantado con barra y sonido | Portador, recogida al morir, desactivación, interrupciones, reloj y victoria |
| Rehenes | Hablar con NPCs para que sigan al jugador hasta zona segura | Guía asignado, caminos, atascos, rescate y desconexiones |
| VIP | Un integrante debe escapar protegido por su equipo | Selección/rotación, rutas, movilidad, muerte y tiempo agotado |
| Iceworld/Poolday | Armas en el suelo para tomar y combatir | Recogida controlada, reposición, eliminación o respawn |

Condición expresa de Kevin: las armas se usan en ese lugar o partida y no se llevan al mundo persistente.

Documento completo: [EVENTO-CS-INTERLUDE.md](EVENTO-CS-INTERLUDE.md).

## 7. Viabilidad revisada en código

La lectura del código local encontró infraestructura de TvT con equipos e instancia dinámica; `SetupGauge` para barra; `PlaySound` para pedir reproducción de un recurso del cliente; intención FOLLOW utilizada por un controlador de escuadras; restricciones de intercambio, depósito y drop en objetos.

Esto confirma piezas reutilizables, no un evento CS terminado. Faltan lógica de rondas, objetivos, normalización de perfiles, recuperación del personaje, restricciones y limpieza completa de objetos temporales.

Para sonidos o modelos nuevos hay que instalar recursos compatibles en el cliente. El mensaje de sonido no transporta el archivo. La barra informa: el servidor tiene que validar duración e interrupciones.

Igualar equipo no iguala automáticamente nivel, buffs, habilidades o builds acumuladas. Se propusieron perfiles del evento o clases con reglas acotadas; no se eligió todavía una opción.

## 8. Importar mapas de Counter-Strike

Se investigó la diferencia entre BSP de GoldSrc y los escenarios/paquetes que necesita el cliente Interlude. La ruta candidata requiere extraer o reconstruir geometría, texturas y UVs; preparar el escenario; resolver colisión del cliente, geodata, alturas, caminos y línea de visión del servidor; recrear puntos iniciales y zonas de objetivos.

No se encontró durante esta búsqueda un port CS 1.6 → Interlude ya comprobado. Una herramienta de conversión de geometría no importa automáticamente entidades, reglas o comportamiento de CS.

Quedó propuesto comenzar por una arena pequeña tipo Iceworld o una reconstrucción propia inspirada en su distribución. Un mapa visible en el visor no demuestra jugabilidad. También habrá que adaptar espacios al movimiento, cámara y combate de L2, e identificar condiciones de uso de los assets concretos antes de redistribuirlos.

Las referencias técnicas y su alcance están en el documento del evento; no se descargó ni ejecutó un conversor en esta investigación.

## 9. Próximos pasos posibles — pendientes, no órdenes de ejecución

1. Ampliar historias de Kevin y corpus de experiencias latinoamericanas, incluyendo personas satisfechas y operadores de comunidades duraderas.
2. Definir la experiencia deseada de primera semana y primer mes para nuevo, veterano casual, grupo organizado y jugador que vuelve.
3. Mapear actividades nativas realmente disponibles en nuestro servidor y sus requisitos de acceso.
4. Si se retoma el evento, prototipar C4 en un escenario de L2 ya jugable. Se sugirió 3 contra 3, un sitio, seis rondas y cambio de lado; son números tentativos.
5. Probar conservación de personaje y recuperación tras salida/desconexión/reinicio antes de repartir equipo temporal.
6. Investigar una arena pequeña estilo Iceworld para validar la cadena de mapas; después rehenes cuando haya navegación fiable.
7. Retomar sockets/gemas y campañas como diseños separados, con límites de poder y pruebas de abuso antes de incorporarlos.

## 10. Estado al cerrar esta anotación

Investigación, propuesta y bitácora guardadas localmente y enlazadas desde el índice. Hay nota de continuidad en Nexus para coordinar sesiones. En esta fase de experiencia de jugadores y evento CS no se modificó el cliente ni el servidor, no se implementaron modos y no se realizaron pruebas de jugabilidad del evento. Las integraciones históricas de equipo se documentan por separado.

## 11. Dirección aportada por Kevin — 14/10/2026

Se distinguen L2 Academy (singleplayer offline de entrenamiento, Coliseo inicial y aeronave de Gludio/otro mapa como alternativa en evaluación), Hell Games en prelanzamiento (viaje de bienvenida volando a Giran, NPCs, preparación de clases al máximo para formar build, PvP y salas sin adena por ahora) y lanzamiento oficial (posterior a estabilidad y comunidad formada, inicio aún sin decidir).

Kevin quiere sets nuevos y joyas únicas con efectos que creen especializaciones, y contempla expediciones de nivel bajo con farmeo y trama. El inicio y mapas se desarrollan en otra sesión. Alcance, decisiones y preguntas abiertas: [dirección de Academy y Hell Games](DIRECCION-ACADEMY-HELLGAMES-2026-10-14.md). Estas decisiones orientan los próximos pasos propuestos anteriormente; no implican implementación ni una economía oficial elegida.

## 12. Interfaces: referencias recuperadas — 14/10/2026

Kevin solicitó guardar lo conversado y preguntó si aquí se habían repasado sitios de interfaces. Se revisaron las notas locales del 12/10: sí existe una primera selección, pero no una comparación exhaustiva ni packs de interfaz verificados para instalar.

- [Abstract Interface para Interlude](https://mmo-dev.info/resources/abstract-interface-for-interlude.3866/): referencia registrada en MMO-DEV. Notas anteriores indican cambios de DLL y acceso parcial; descarga y compatibilidad con nuestro HUD pendientes.
- [Silent Interface Interlude Style](https://maxcheaters.com/topic/241747-silent-interface-interlude-style/): hilo registrado en MaxCheaters; binarios, condiciones y compatibilidad pendientes.
- [L2Eirin: actualización de interfaz](https://forum.l2eirin.com/topic/4055-update-%E2%84%9647-interlude-x1x30x300/): referencia de funciones de ese servidor, no un pack público descargable comprobado.
- [Neophron: iconos de buffs sobre la cabeza con timer](https://maxcheaters.com/topic/206809-neophron-symbols-buffs-over-the-head-with-a-timer/), con [republicación](https://maxcheaters.com/topic/212056-re-share-neophron-symbols-buffs-over-the-head/): mejora visual específica, no interfaz completa; recuperación y prueba pendientes.

Antecedentes: [capa de interfaces](../../resource-library/2026-10-12/RECURSOS-POR-CAPAS.md) y sección 7 de la [bitácora anterior](../../resource-library/2026-10-12/BITACORA-IDEAS-Y-PENDIENTES.md). Kenney UI/Sounds son recursos genéricos de prototipo, no reemplazos listos de la interfaz L2.

Estos enlaces se recuperaron de documentación ya guardada; no se volvió a verificar disponibilidad web en esta actualización. Kevin menciona haber visto interfaces interesantes, todavía sin identificar cuáles. Próximo paso posible: comparar esas referencias por aspecto, funciones, archivos necesarios y compatibilidad con el cliente actual antes de elegir.

También se conserva el trabajo de splash Hell Games por separado: [registro de instalación y correcciones](../../client-branding/2026-10-13/README.md). Última corrección elimina el color transparente dentro de la imagen; confirmación visual del usuario pendiente. El splash no es una interfaz completa.

## 13. Descargas de interfaces autorizadas — 14/10/2026

Kevin encontró el indicador de target en otra sesión y pidió descargar interfaces disponibles, avisando cuáles se recuperarían. Se anunciaron las familias y se guardaron 19 archivos (2,92 GiB) en `E:\l2-local\descarga de assets\interfaces\2026-10-14`: variantes de Celestine, Classic/Ona, Iordanov, Wellinton, Essence, Dandilo, Neophron y Silent, más ShooteR, Visual Patch NexuS, parches Atlas/Moon, fuentes InterfaceEvolved y texturas bonus. Dos distribuciones Wellinton se conservan como mirrors/variantes, no como diseños únicos comprobados.

Todos los RAR/ZIP pasaron integridad; procedencia, tamaños, hashes e inventarios registrados. Sin instalación ni ejecución. Abstract/Athena y algunos hilos requieren sesión; original Silent no disponible, alternativa V2 recuperada. [Catálogo y pendientes](../../interfaces/2026-10-14/README.md).

Comparación posterior: los dos mirrors Wellinton contienen los mismos 27 archivos, con nombres y hashes de contenido idénticos. El catálogo distingue 19 archivos de descarga frente a 18 paquetes distintos; no confundir variantes con diseños únicos. Integridad de todos los archivos comprobada; no quedan descargas parciales en esta tanda.

Kevin aportó cinco nuevos hilos: animaciones de Community Board/splash (oferta comercial sin descarga), NPC Dwarf con efectos, Board sin marco con PSD, Board de Dragic con marco y Simple Interface con complementos. Recuperados cinco archivos de cuatro publicaciones, 81,38 MiB adicionales; todos con RAR comprobado. Total 24 archivos, aproximadamente 3,00 GiB. Sin instalación/ejecución. [Resultados e inventarios](../../interfaces/2026-10-14/ENLACES-APORTADOS-POR-KEVIN.md).
