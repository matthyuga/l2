# Plan de cobertura telemétrica de razas y clases

Fecha de inicio: 6 de octubre de 2026.

## Estado de fases

- Fase 1 — plantel físico: **completa, 9/9 anclas**.
- Fase 2 — cobertura limpia de clases: **completa, 89/89 perfiles**.
- Fase 3 — interacciones por parejas: **completa, 465/465 parejas y 930/930 estados**.
- Fase 4 — combinaciones de cuatro clases: **completa; 4A, 4B, 4C y 4D terminadas, 285/285 pasadas**.
- Fase 5 — contraste y balance: **5A en curso; L2Nyx documentado, Nyx calibrada
  (360/360), comparación mágica terminada (240/240) y base racial Humana
  terminada (240/240)**.

Personajes físicos creados:

| Cuenta | Personaje | Raza | Clase inicial |
| --- | --- | --- | --- |
| `telemetryf` | Arden | Humano | Human Fighter |
| `telemetryf` | Eryndor | Elfo | Elven Fighter |
| `telemetryf` | Vaelkor | Elfo oscuro | Dark Fighter |
| `telemetryf` | Gorvak | Orco | Orc Fighter |
| `telemetryf` | Brunna | Enano | Dwarf Fighter |
| `telemetrym` | Selene | Humano | Human Mystic |
| `telemetrym` | Lethiel | Elfo | Elven Mystic |
| `telemetrym` | Myrentha | Elfo oscuro | Dark Mystic |
| `telemetrym` | Zhurak | Orco | Orc Mystic |

El 7 de octubre de 2026 los nombres técnicos `Tele*` se sustituyeron por estos
nombres provisionales. La migración incluyó los personajes y sus perfiles históricos;
el respaldo anterior está en `backups\anchor-renames-2026-10-07`.

Todos son personajes persistentes de nivel 1, poseen sus skills iniciales reales y
acceso Master/GM para operar Build Lab sin depender de Hellkevin. El sembrador local
es idempotente: sólo crea un ancla si su nombre no existe.

## Objetivo

Construir un catálogo reproducible de estadísticas reales calculadas por el Game
Server antes de evaluar builds acumulativas de una principal y tres subclases.

La lectura base comparable será a nivel 80, sin equipo, sin efectos, sin subclases
y con la clase principal activa. El catálogo puede conservar otras lecturas, pero
no las contará como cobertura base.

## Tamaño del árbol

Interlude tiene cinco razas, pero nueve clases iniciales porque cuatro razas poseen
origen guerrero y místico:

| Raza | Origen | Inicial | Primera | Segunda | Tercera | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Humano | Human Fighter | 1 | 3 | 6 | 6 | 16 |
| Humano | Human Mystic | 1 | 2 | 5 | 5 | 13 |
| Elfo | Elven Fighter | 1 | 2 | 4 | 4 | 11 |
| Elfo | Elven Mystic | 1 | 2 | 3 | 3 | 9 |
| Elfo oscuro | Dark Fighter | 1 | 2 | 4 | 4 | 11 |
| Elfo oscuro | Dark Mystic | 1 | 2 | 3 | 3 | 9 |
| Orco | Orc Fighter | 1 | 2 | 2 | 2 | 7 |
| Orco | Orc Mystic | 1 | 1 | 2 | 2 | 6 |
| Enano | Dwarf Fighter | 1 | 2 | 2 | 2 | 7 |
| **Total** | **9 orígenes** | **9** | **18** | **31** | **31** | **89** |

Por raza, el total es: Humano 29, Elfo 20, Elfo oscuro 20, Orco 13 y Enano 7.

## Recorrido recomendado

1. Crear cinco personajes ancla: Humano, Elfo, Elfo oscuro, Orco y Enano. **Hecho.**
2. Crear cuatro anclas adicionales para las raíces místicas. **Hecho.**
3. Registrar las nueve raíces limpias. **Hecho.**
4. Recorrer las 18 primeras profesiones, reiniciando la rama entre recorridos. **Hecho.**
5. Recorrer las 31 segundas profesiones. **Hecho.**
6. Recorrer las 31 terceras profesiones. **Hecho.**

No es necesario conservar 89 personajes. Los nueve anclajes pueden recorrer todas
las ramas y `lab_player_stat_profiles` conservará cada estado por separado.

## Resultado de la fase 2

El 6 de octubre de 2026 el Game Server recorrió automáticamente los nueve anclajes
físicos y capturó los 89 estados desde objetos `Player` reales. No se fabricaron
stats mediante sentencias SQL: cada lectura fue calculada por las fórmulas, templates
y skills cargados por el servidor.

Resultado auditado:

- 89 clases únicas y 89 perfiles limpios, sin duplicados.
- 9 iniciales, 18 primeras, 31 segundas y 31 terceras profesiones.
- Humano 29/29, Elfo 20/20, Elfo oscuro 20/20, Orco 13/13 y Enano 7/7.
- Cero perfiles sin skills; rango observado de 11 a 83 skills.
- Los nueve anclajes terminaron offline, nivel 1, en su clase inicial, sin equipo
  ni subclases.

El recorrido bloquea temporalmente la captura automática de eventos de profesión
para que una lectura intermedia no sobrescriba el perfil controlado. También es
idempotente: si los 89 perfiles ya existen, un reinicio no vuelve a recorrer ni
modificar el plantel.

## Resultado de la fase 3

Entre el 6 y el 7 de octubre de 2026 se recorrieron las 465 parejas no ordenadas
posibles entre las 31 terceras profesiones. Cada pareja se midió en dos estados
reales: primero con la profesión A como principal activa y después con la profesión
B como Sub 1 activa. En total quedaron 930 estados a nivel 80, sin equipo ni
efectos.

El control final dio:

- 465/465 parejas y 930/930 estados.
- Las 31 terceras profesiones aparecen contra sus 30 compañeras posibles.
- Cero diferencias entre el conteo y el catálogo exacto esperado de skills.
- Cero parejas asimétricas: ambos estados de cada pareja conservaron el mismo
  conjunto exacto `ID:nivel` de skills acumuladas.
- Entre 49 y 138 skills por pareja, con promedio de 105,07.
- Entre 6 y 59 IDs de skill compartidos y entre 2 y 7 colisiones de masteries.
- Los nueve anclajes terminaron nuevamente offline, nivel 1, en su clase racial
  inicial, sin subclases ni objetos equipados.

La validación estricta descubrió dos casos que una simple cuenta de skills no habría
detectado: `rewardSkills()` podía restaurar un nivel inferior de un ID compartido y
dos masteries pasivas con el mismo nombre y nivel podían resolverse de forma distinta
según la clase activa. El núcleo ahora restaura la acumulación después del autolearn
y aplica una regla determinista: mayor nivel; en empate, menor ID. Se recompiló y
desplegó `GameServer.jar`.

Como señales iniciales, `Cardinal + Dominator` presenta el catálogo más amplio
(138 skills), mientras que `Duelist + Dreadnought` concentra 41 IDs compartidos y
7 colisiones de mastery. Esto mide amplitud y redundancia, no poder de combate: aún
faltan arma, equipo, buffs, coste de recursos, reutilizaciones y pruebas de daño,
curación y supervivencia.

El ejecutor de parejas es incremental e idempotente. Un reinicio de control conservó
exactamente la misma firma de las 930 filas y registró que no debía modificar el
plantel. El respaldo previo está en
`backups\telemetry-phase3-2026-10-06`.

## Resultado de la fase 4A

El 7 de octubre de 2026 se enumeraron las 125.860 builds posibles formadas por una
principal distinguida y tres Subs sin orden entre las 31 terceras profesiones. Esta
etapa es analítica: reutiliza los conjuntos exactos `ID:nivel` validados en la matriz
de parejas y los metadatos XML de skills; no carga ni modifica personajes.

Resultado auditado:

- 125.860/125.860 candidatos, 4.060 por cada una de las 31 principales.
- 31.465 conjuntos de skills distintos al ignorar cuál de las cuatro clases ocupa
  la principal.
- Entre 88 y 231 skills previstos por build, con promedio de 176,42.
- Cero principales repetidas como Sub, cero Subs duplicadas o fuera de orden.
- Hashes SHA-256 completos para todos los candidatos. Los 155 seleccionados guardan
  además su catálogo completo para poder auditarlos en la siguiente fase.

Se eligieron cinco candidatos por profesión principal, 155 en total:

1. `amplitud`: máximo repertorio con desempate por menor solapamiento;
2. `afinidad`: cuatro clases del mismo arquetipo físico/mágico cuando es posible;
3. `estrés`: máximo solapamiento y máximo conflicto de masteries;
4. `híbrida`: equilibrio de clases físicas y mágicas y diversidad racial;
5. `cobertura`: compensación determinista de las profesiones menos representadas.

Cada criterio contiene 31 builds. Todas las profesiones aparecen al menos 13 veces
en la muestra dirigida y el promedio es 20 apariciones. `pair_shared_score` y
`mastery_collision_score` son sumas de las seis parejas internas de la build; miden
presión de redundancia, no cantidad de conflictos distintos ni poder de combate.

La amplitud máxima prevista es de 231 skills para el conjunto
`Soultaker + Cardinal + Wind Rider + Dominator`. La clasificación es reproducible: una segunda ejecución
conservó exactamente la firma
`125860:22204568:31465:270455410881978`.

La tabla resultante es `lab_four_class_candidates`. El generador repetible está en
`lab-panel\scripts\generate-phase4a.js` y puede ejecutarse mediante
`npm run phase4a` usando el Node portátil del proyecto. El panel muestra el progreso,
los totales y las 155 builds seleccionadas. El respaldo previo está en
`backups\telemetry-phase4a-2026-10-07`.

La fase 4B construyó esas 155 builds con objetos `Player` reales y midió sus cuatro
clases activas: 620 estados controlados a nivel 80, sin equipo ni efectos.

## Resultado de la fase 4B

El 7 de octubre de 2026 las 155 builds seleccionadas en 4A se construyeron con los
nueve personajes ancla reales. Cada principal fue asignada al ancla de su raíz
racial natural y se añadieron sus tres Subs en las ranuras 1, 2 y 3. Después se
midieron las cuatro clases activas de cada build.

Resultado auditado:

- 155/155 builds completas y 620/620 estados reales.
- 31 profesiones principales con cinco builds y 20 estados cada una.
- 31 builds y 124 estados por criterio: amplitud, afinidad, estrés, híbrida y
  cobertura.
- Cero diferencias de conteo, hash SHA-256 o catálogo completo `ID:nivel` respecto
  de la predicción 4A.
- Cero builds incompletas, ranuras mal asociadas o perfiles de candidatos no
  seleccionados.
- Cero razas incorrectas: las cuatro ranuras conservaron la raza natural de la
  principal.
- Todos los estados son nivel 80, sin equipo y sin efectos.
- Rango de la muestra: 93 a 231 skills, con promedio de 176,91.
- Los nueve anclajes terminaron offline, nivel 1, en su raíz original, sin Subs ni
  objetos equipados.

La tabla `lab_four_class_profiles` conserva la build completa, clase/ranura activa,
raza persistente, skills exactos y estadísticas calculadas por el Game Server. El
panel muestra el progreso 4B y los cuatro estados reales dentro de cada candidato.

El ejecutor es incremental e idempotente. Tras un reinicio de control, la firma
`620:1791345256083:109684:1315944042463` permaneció idéntica y el servidor registró
`builds completas (155/155, estados=620/620); no se modifica el roster`. El respaldo
previo está en `backups\telemetry-phase4b-2026-10-07`.

Con esto queda cerrada la cobertura limpia de combinaciones. La Fase 4C reduce esta
muestra a finalistas representativos y la 4D medirá su comportamiento en combate
controlado. El contraste con otros servidores corresponde a la Fase 5 y se hará
después, para no contaminar primero la referencia local.

## Resultado de la fase 4C

El 7 de octubre de 2026 se analizaron los 620 estados reales de la Fase 4B contra
el perfil limpio de su respectiva clase activa. Para que los multiplicadores grandes
de estadísticas desnudas no dominaran por suma directa, se usaron razones
logarítmicas y su equivalente como media geométrica. Esto permite ordenar casos de
prueba, pero todavía no representa daño, curación ni supervivencia real.

Se eligieron 30 finalistas, cinco en cada categoría:

- física;
- mágica;
- tanque;
- soporte;
- summoner;
- híbrida.

Cada categoría contiene dos casos de rendimiento, uno de amplitud, uno de estrés
por solapamiento y uno de control/contraste. La selección global conserva 30 grupos
de cuatro clases distintos, cubre las 31 terceras profesiones y utiliza 24 de ellas
como principal. Ninguna principal aparece más de dos veces.

La auditoría verificó:

- 30/30 filas y seis categorías de 5/5;
- 12 casos de rendimiento, seis de amplitud, seis de estrés y seis de control;
- 31/31 profesiones cubiertas y 30/30 grupos no ordenados únicos;
- cuatro perfiles reales válidos por finalista;
- cero hashes diferentes respecto del candidato 4A y cero motivos vacíos;
- selección reproducible con firma `ec026f090be9db3da777412d4721e2c6`.

La tabla es `lab_build_finalists`. El analizador repetible está en
`lab-panel\scripts\analyze-phase4c.js` y se ejecuta con `npm run phase4c`. El panel
incluye la API `/api/telemetry/finalists`, la distribución completa y los índices y
ganancias relativas de cada build. Esta fase es sólo analítica y no modificó los
nueve personajes ancla ni reinició el Game Server.

El respaldo anterior está en `backups\telemetry-phase4c-2026-10-07`. La siguiente
etapa es la Fase 4D: protocolo de combate controlado sobre estos finalistas, con
equipo, buffs, rival y rotación fijados por función. La Fase 5 queda después de 4D.

## Preparación de la fase 4D

El 7 de octubre de 2026 se generó una cola determinista de 95 casos sobre los 30
finalistas, con tres repeticiones por caso: 285 pasadas reales previstas.

Distribución:

- 15 casos de salida física, 45 pasadas;
- 10 casos de salida mágica, 30 pasadas;
- 5 casos de soporte sostenido, 15 pasadas;
- 5 casos de salida de invocación, 15 pasadas;
- 30 casos de resistencia frente a Ares, 90 pasadas;
- 30 casos de resistencia frente a Nyx, 90 pasadas.

Cada finalista tiene resistencia física y mágica. Las categorías física, mágica,
tanque, soporte y summoner tienen tres protocolos; las híbridas tienen cuatro para
separar salida física y mágica. La clase activa se elige entre sus cuatro estados
reales según la función. Se verificó que todos los casos usan una clase perteneciente
a la build; soporte e invocación usan exclusivamente profesiones de esas familias.

Se fijó el primer contexto de equipo:

- Imperial Crusader, Draconic Leather o Major Arcana según el tipo natural de la
  clase activa;
- arma S compatible con la mastery de cada una de las 31 profesiones;
- joyería Tateossian común;
- todo a +0 y sin buffs externos;
- Soulshots y Blessed Spiritshots S contabilizados por separado.

El detalle está en `lab-panel\phase4d-kits.json`. El script repetible
`lab-panel\scripts\prepare-phase4d.js` crea `lab_combat_benchmark_plan`; su firma
actual es `be540784830299badeae72a3b735cd5ea2651c853c4308fa41b99fbff78f7304`.

También se añadió Atlas (`NPC 900202`) al Coliseo: nivel 80, 10.000.000 HP, 1.000
P. Def, 1.000 M. Def, inmóvil, inmortal y sin contraataque. Atlas servirá sólo para
salida; Ares y Nyx conservan las pruebas de supervivencia. El Game Server se reinició
sin jugadores conectados y volvió a responder sin errores. El panel mostró
inicialmente la cola y el progreso 4D como `0/285`.

Esta preparación no contó como resultados de combate. El respaldo previo está en
`backups\telemetry-phase4d-2026-10-07`.

## Resultado de la fase 4D

El 7 de octubre de 2026 se ejecutaron los 95 casos con tres repeticiones cada uno:
**285/285 pasadas completas**. El ejecutor vive en `LabTelemetry.java`, es
incremental y reanudable, y sólo comienza cuando no hay jugadores conectados.

Se utilizó el modo `CORE_ACCELERATED`: construye objetos `Player` reales, activa la
clase y las tres Subs de cada finalista, equipa instancias temporales S +0 y usa las
skills, estadísticas, fórmulas de daño y efectos cargados por el núcleo. El reloj de
45 o 60 segundos se simula según cadencias y reutilizaciones; no espera ese tiempo
en el mundo ni reproduce latencia de red, movimiento o decisiones humanas. Por eso
es una prueba funcional reproducible, no una pelea manual ni una simulación completa
de PvP.

Auditoría final:

- 95/95 casos y 285/285 pasadas; exactamente tres resultados por caso.
- 45 salidas físicas, 30 mágicas, 15 de invocación, 15 de soporte, 90 resistencias
  contra Ares y 90 contra Nyx.
- Cero filas con modo, rotación, acciones, duración o métrica principal inválidos.
- Promedios globales: 103,56 DPS físico; 67,75 DPS mágico; 119,22 DPS de invocación
  y 407,94 HPS de soporte.
- Supervivencia media: 26,79 s contra Ares y 3,22 s contra Nyx. Tres casos agotaron
  el límite de 45 s contra Ares; Nyx resulta deliberadamente mucho más severa y
  deberá calibrarse antes de extraer conclusiones finas de balance.
- Mejor salida física de esta muestra: Ghost Sentinel del finalista 25, 218,27 DPS.
  Mejor salida mágica: Mystic Muse del finalista 7, 94,41 DPS.
- Mejor salida de invocación: Elemental Master del finalista 29, 159,54 DPS total
  (96,72 del dueño y 62,82 de la invocación).
- Mejor soporte sostenido: Cardinal del finalista 15, 465,48 HPS.
- Los nueve anclajes terminaron offline, nivel 1, en su clase racial inicial, sin
  Subs ni objetos. Catorce objetos temporales de pilotos interrumpidos se respaldaron
  y eliminaron antes del cierre; el inventario telemétrico quedó en cero.

La tabla de resultados es `lab_combat_benchmark_runs`. El panel agrega las tres
repeticiones y muestra DPS, HPS, supervivencia, recursos y separación de daño del
dueño y la invocación. El volcado final está en
`backups\telemetry-phase4d-2026-10-07\phase4d-results-final.sql`; los pilotos
descartados y los objetos temporales retirados tienen respaldos separados en la
misma carpeta.

Estos rankings comparan únicamente los 30 finalistas seleccionados, con el equipo y
protocolos fijados; no representan todavía todas las builds posibles ni justifican
buffs o nerfs. La Fase 5 podrá contrastar esta línea local con otros servidores y
documentar diferencias de crónica y configuración.

## Protocolo por lectura

- Nivel 80.
- Principal activa; Sub 1, Sub 2 y Sub 3 vacías.
- Sin arma, armadura, joyería ni accesorios equipados.
- Sin buffs, debuffs, toggles, transformaciones, cubics ni invocaciones.
- HP, MP y CP completos.
- Skills de la etapa maximizados mediante Build Lab.
- Esperar al menos dos segundos después del cambio de profesión antes de consultar
  el panel.

Opcionalmente se pueden conservar lecturas históricas a nivel 1, 20, 40 y 76. Esas
lecturas no deben mezclarse con la referencia común de nivel 80.

## Combinaciones acumulativas

Con 31 terceras profesiones, una principal y tres Sub distintas producirían:

- 125.860 conjuntos si el orden de Sub 1-3 no importa.
- 755.160 builds si cada permutación de las tres ranuras se considera diferente.
- 503.440 estados si se mide cada una de las cuatro clases activas por conjunto no
  ordenado.

No conviene medir ese espacio por fuerza bruta. La fase 3 ya cubrió las 465 parejas
posibles de terceras profesiones. La fase 4 debe usar esos resultados para elegir
una muestra dirigida de combinaciones de cuatro con sinergias, solapamientos o
conflictos relevantes, en vez de recorrer automáticamente los 125.860 conjuntos.

## Comparación con otros servidores

La investigación externa se realizará después de obtener la línea base local. Para
cada servidor se debe registrar crónica, rates, archivos/mods, fecha, fuente y si el
cambio es un buff, nerf o modificación mecánica. Una cifra externa no se aplicará
directamente si usa otra crónica, equipo, enchant, buffs o fórmulas.

## Herramientas activas

El panel, dentro de Telemetría, muestra la cobertura total y por etapa, raza y raíz.
Las muestras con equipo o efectos permanecen en el catálogo, pero no avanzan el
contador limpio. Los efectos forman parte de la clave del perfil para que una lectura
buffeada no sobrescriba la lectura sin buffs.

## Fase 5A — referencia externa y primera calibración de Nyx

El 7 de octubre de 2026 se fijó la línea base de 4D con la etiqueta Git
`phase4d-baseline-2026-10-07` y se abrió la Fase 5A sin modificar esos resultados.

Primer servidor documentado: **L2Nyx externo**. Su expediente está en
`research/external-servers/l2nyx-2026-10-07.{md,json}` y se muestra en el panel.
Se usa ese nombre completo para no confundirlo con **Nyx, rival mágico interno**.
La ficha conserva fuentes, fecha y diferencias de crónica/configuración; una regla
no publicada queda como desconocida.

La primera calibración interna repitió los 30 casos de resistencia contra Nyx tres
veces en cuatro escalas de daño final: 100%, 75%, 60% y 50%. Rotación, control,
debuffs, casteo, equipo, clases y fórmulas permanecieron iguales. Los resultados
se guardaron en una tabla independiente, `lab_nyx_calibration_runs`, por lo que
las 285 filas de 4D no se sobrescribieron.

Resultado auditado:

| Escala | Pasadas | Supervivencia media | Mínimo | Máximo | Pasadas entre 10–20 s |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100% | 90 | 3,14 s | 2,05 s | 5,32 s | 0 |
| 75% | 90 | 3,29 s | 2,05 s | 3,42 s | 0 |
| 60% | 90 | 4,00 s | 2,05 s | 7,21 s | 0 |
| 50% | 90 | 4,92 s | 2,05 s | 9,12 s | 0 |

La ronda cerró 360/360 pasadas, cero grupos con repeticiones incorrectas y cero
filas con métricas obligatorias inválidas. Los nueve anclajes quedaron offline,
nivel 1, en su clase base, sin Subs ni objetos. Ninguna escala alcanzó el objetivo
exploratorio de 10–20 segundos, de modo que **no se eligió todavía un valor para
el NPC real**. La próxima ronda debe concentrarse alrededor de 30%, 25% y 20%.

Respaldo local:
`backups/telemetry-phase5a-2026-10-07/phase5a-nyx-calibration.sql`.
El repositorio conserva el mismo volcado y un resumen JSON en `data/telemetry/`.

## Fase 5A.2 — Storm Screamer y crecimiento por Subs

El 7 de octubre de 2026 se ejecutó una progresión real sobre Myrentha, el ancla
Dark Mystic. En cada etapa Storm Screamer quedó como clase activa a nivel 80 y se
añadieron, en orden acumulativo, Mystic Muse, Archmage y Soultaker. Las cuatro
etapas usaron Atlas, Arcana Mace +0, robe S, joyería S común, Blessed Spiritshots,
sin buffs externos y tres repeticiones de 60 segundos acelerados.

| Etapa | Skills | Pasivas | M.Atk | Cast | DPS medio | Rotación |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Storm Screamer | 74 | 24 | 1.308,68 | 366 | 44,07 | Hurricane |
| + Mystic Muse | 103 | 24 | 1.308,68 | 366 | 87,38 | Aura Flare |
| + Archmage | 118 | 24 | 1.308,68 | 366 | 85,19 | Aura Flare |
| + Soultaker | 139 | 25 | 1.344,96 | 366 | 83,45 | Aura Flare |

La medición separa dos fenómenos. Las Subs no acumularon linealmente las masteries:
M.Atk y casteo permanecieron iguales hasta que Soultaker añadió una sola pasiva y
2,77% de M.Atk. El salto tras Mystic Muse se produjo porque el selector encontró
Aura Flare y realizó 37 lanzamientos, frente a 15 Hurricanes del perfil puro; no
fue un crecimiento del atributo mágico. Las diferencias pequeñas entre las tres
últimas etapas están dentro de la variación crítica de solo tres repeticiones.

Nyx quedó intacta como **Nyx Élite**: 21.277,17 M.Atk y 1.999 de casteo, frente a
1.308,68/366 del Storm Screamer puro y 1.344,96/366 de la build completa. Es una
referencia especial —15,82 a 16,26 veces el M.Atk normal de esta prueba— y no una
meta alcanzable mediante tres Subs normales.

Auditoría: 12/12 pasadas, tres por etapa, cero métricas inválidas, 285 filas de 4D
y 360 de calibración preservadas. Myrentha terminó offline, nivel 1, Dark Mystic,
sin Subs ni objetos. Antes de ajustar balance, la siguiente comparación debe tener
dos carriles: una skill fija común para aislar stats y una mejor rotación por build
para medir el valor práctico del catálogo acumulado.

Respaldo local:
`backups/telemetry-phase5a2-2026-10-07/phase5a2-magic-progression.sql`.
El volcado y su resumen JSON también están en `data/telemetry/`.


## Fase 5A.3 — Hurricane fija frente a mejor skill

El 7 de octubre de 2026 se ejecutó la comparación que separa stats de catálogo.
Cada uno de los cuatro estados de la progresión 5A.2 se midió en dos carriles:
Hurricane #1239 nivel 28 fija, y el nuke con mejor relación potencia/cadencia
disponible. Se ampliaron las muestras de tres a treinta repeticiones por carril y
etapa para reducir el ruido de críticos: **240/240 pasadas**.

| Etapa | M.Atk | DPS Hurricane | Mejor skill | DPS mejor | Ventaja práctica |
| --- | ---: | ---: | --- | ---: | ---: |
| Storm Screamer | 1.308,68 | 44,23 | Hurricane | 44,48 | +0,56% |
| + Mystic Muse | 1.308,68 | 43,33 | Aura Flare | 84,03 | +93,91% |
| + Archmage | 1.308,68 | 43,57 | Aura Flare | 85,03 | +95,17% |
| + Soultaker | 1.344,96 | 45,70 | Aura Flare | 86,23 | +88,67% |

El resultado aclara el origen de la mejora. Mystic Muse y Archmage no elevan M.Atk
ni casteo; Hurricane permanece alrededor de 43–44 DPS. Soultaker añade 2,77% de
M.Atk. Como la fórmula local escala aproximadamente con la raíz cuadrada de M.Atk,
su aporte teórico puro es sólo **+1,38% de daño mágico**, antes de variación y
críticos.

Aura Flare tiene menos poder y daño por lanzamiento que Hurricane, pero su ciclo
es de 1.592 ms frente a 3.821 ms. En 60 segundos realiza 37 lanzamientos en lugar
de 15: +146,67%. Esto produce cerca del doble de DPS, a cambio de consumir 2.553 MP
en vez de 1.035 MP, también +146,67%. La ganancia dominante procede de la cadencia
y del catálogo de skills, no de inflar el atributo mágico.

Auditoría: treinta filas exactas por etapa/carril, cero métricas inválidas, 285
resultados 4D, 360 calibraciones de Nyx y 12 progresiones preservadas. Myrentha
terminó offline, nivel 1, Dark Mystic, sin Subs ni objetos. Nyx Élite no fue
modificada.

Respaldo: backups/telemetry-phase5a3-2026-10-07/phase5a3-magic-comparison.sql.
El repositorio conserva el SQL y el resumen JSON en data/telemetry/.

## Fase 5A.4 — primera base racial física: Humano

El 7 de octubre de 2026 se fijó el primer control para estudiar razas sin mezclar
su efecto con cambios de clase. Arden conserva Human Fighter como raíz racial;
Dreadnought queda activa a nivel 80 y se añaden Titan, Fortune Seeker y Maestro
como Subs acumulativas. El equipo es Saint Spear +0, heavy S, joyería S común,
Soulshots, cero buffs externos y Atlas como objetivo.

Se midieron dos carriles durante 60 segundos acelerados: autoataque fijo y la
skill física compatible con mejor relación potencia/ciclo. Cada carril tuvo
treinta repeticiones por etapa, para un total de **240/240 pasadas**.

| Etapa | Skills | Pasivas | P.Atk | Velocidad | DPS auto | Skill compatible | DPS skill |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Dreadnought | 59 | 21 | 1.007,28 | 351 | 67,95 | Earthquake | 10,68 |
| + Titan | 75 | 24 | 1.007,28 | 351 | 68,16 | Earthquake | 9,13 |
| + Fortune Seeker | 86 | 28 | 1.007,28 | 351 | 68,32 | Earthquake | 9,46 |
| + Maestro | 92 | 29 | 1.007,28 | 351 | 69,63 | Earthquake | 9,44 |

La raza permaneció `HUMAN` en las 240 filas, incluso al incorporar clases cuya
raíz natural es orca o enana. P.Atk, velocidad, crítico, precisión, HP/CP/MP y
STR/DEX/CON fueron exactamente iguales en las cuatro etapas. El aumento aparente
de 2,48% en el último promedio de autoataque es menor que su dispersión y, con
stats idénticos, se atribuye a críticos y fallos aleatorios. No hay evidencia de
que estas masteries físicas se acumulen.

Earthquake fue elegida en las cuatro etapas, pero su ciclo de 28.461 ms permite
sólo dos acciones por minuto. Por eso el carril de skill no representa “mejor DPS
total”: describe la mejor relación potencia/ciclo dentro de las skills físicas
compatibles, mientras el autoataque sigue siendo muy superior en este protocolo.

La fase valida persistencia racial y establece el control humano; todavía no
cuantifica una ventaja de raza. El siguiente experimento debe repetir la misma
build, equipo y objetivo sobre otro ancla racial, y luego comparar cada atributo
y carril contra esta tabla.

Auditoría: 240 claves únicas, cero diferencias de raza, clase o equipo y seis
filas sin daño explicadas por dos fallos consecutivos de Earthquake. Arden volvió
offline, nivel 1, Human Fighter, sin Subs ni objetos. Se preservaron 285 resultados
4D, 360 calibraciones de Nyx, 12 progresiones mágicas y 240 comparaciones mágicas.

Respaldo local:
`backups/telemetry-phase5a4-human-2026-10-07/phase5a4-human-physical-baseline.sql`.
El SQL y su resumen JSON también quedan en `data/telemetry/`.

## Fase 5A.6 — cinco razas con posición y estado controlados

El 7 de octubre de 2026 se completó la ampliación del protocolo físico a las
cinco razas: Humano, Elfo, Elfo oscuro, Orco y Enano. Cada anclaje mantuvo su
raza de nacimiento mientras usó Dreadnought como clase activa y añadió Titan,
Fortune Seeker y Maestro. Se conservaron nivel 80, Saint Spear +0, heavy S,
joyería S común, Atlas y cero buffs externos. El total final fue **1.200/1.200
pasadas**: 240 por raza y 30 por raza, etapa y carril.

Antes de aceptar los datos se corrigieron dos contaminantes del protocolo. Arden
había quedado persistido con 0 HP; al cargarlo, Final Frenzy seguía aportando
129,3 P.Atk y elevaba la base humana de 877,98 a 1.007,28. Además, cada anclaje
conservaba las coordenadas de su aldea natal y la fórmula de acierto aplica
bonificaciones por altura y lado respecto del objetivo. La limpieza ahora revive
primero al personaje y elimina funciones huérfanas de skills/efectos; la prueba
lo coloca temporalmente en una posición común frente a Atlas y restaura después
sus coordenadas originales.

La captura corregida dio exactamente los mismos atributos en las cinco razas:
877,9798 P.Atk, 351 de velocidad, 86 de crítico, 123 de precisión, 6.542 HP,
4.718 CP, 1.794 MP y 42/28/43 STR/DEX/CON. Polearm Mastery #216 nivel 45 estuvo
presente en todos y aportó 129,3 P.Atk. Los catálogos también fueron idénticos:
59/21, 75/24, 86/28 y 92/29 skills/pasivas en las cuatro etapas.

El autoataque agrupado promedió 44,3296 DPS con desviación 4,6665. Por raza los
promedios quedaron entre 43,7912 y 44,7144 DPS, dentro de la dispersión de las
muestras y sin una diferencia de atributos que los explique. Earthquake fue la
skill compatible común y promedió 7,3388 DPS agrupados. Estos valores no
demuestran bonificación racial: en esta arquitectura la raza persistida controla
identidad y apariencia, mientras la plantilla de la clase activa determina los
stats numéricos medidos.

Auditoría: cero filas inválidas, treinta registros exactos por grupo, cinco
diagnósticos de mastery y cero personajes conectados al finalizar. Arden,
Eryndor, Vaelkor, Gorvak y Brunna quedaron nivel 1, con HP completo, clase raíz,
sin Subs ni objetos y en sus posiciones originales. El SQL y el resumen están
en `data/telemetry/phase5a6-five-race-physical-comparison.*`; el respaldo local
recuperable está en `backups/telemetry-phase5a6-five-races-2026-10-07`.

La Fase 5A.4 se conserva únicamente como antecedente del error de estado. Si se
desea que la raza modifique atributos aun usando una profesión ajena, eso debe
definirse como una política de balance explícita y medirse en una fase nueva; no
es un efecto presente que la telemetría haya ocultado.
