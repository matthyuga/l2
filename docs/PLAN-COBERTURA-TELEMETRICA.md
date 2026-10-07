# Plan de cobertura telemétrica de razas y clases

Fecha de inicio: 6 de octubre de 2026.

## Estado de fases

- Fase 1 — plantel físico: **completa, 9/9 anclas**.
- Fase 2 — cobertura limpia de clases: **completa, 89/89 perfiles**.
- Fase 3 — interacciones por parejas: **completa, 465/465 parejas y 930/930 estados**.
- Fase 4 — combinaciones de cuatro clases: **completa; 4A, 4B, 4C y 4D terminadas, 285/285 pasadas**.
- Fase 5 — contraste con otros servidores: pendiente.

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
