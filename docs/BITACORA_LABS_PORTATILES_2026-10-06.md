# Bitácora — Laboratorios L2 portátiles

Fecha: 6 de octubre de 2026  
Ubicación principal: `D:\l2-local`

## Objetivo

Preparar herramientas para continuar trabajando en el proyecto Lineage II desde
una PC de oficina antigua usando solamente el disco portátil, sin instalar Node,
Java o MariaDB en esa computadora y sin necesitar que el Game Server esté activo.

## 1. Laboratorio L2 principal

Ubicación:

`D:\l2-local\lab-panel`

Acceso normal en la PC principal:

- Abrir: `7-ABRIR-PANEL-L2.cmd`
- Cerrar: `8-CERRAR-PANEL-L2.cmd`
- Dirección: `http://127.0.0.1:3210`

### Mejoras incorporadas

- Comparación de Hellkevin contra Ares y Nyx.
- Selector entre stats finales observados y stats base configurados.
- Veinte filas comparables con diferencias absolutas y porcentuales.
- Editor de STR, DEX, CON, INT, WIT y MEN dentro de la ficha del personaje.
- Protección para impedir editar los atributos mientras el personaje está conectado.
- Copia de seguridad del XML de clase antes de guardar.
- Advertencia de que los atributos pertenecen a la plantilla de la clase activa y
  afectan a todos los personajes de esa clase.

### Lecturas finales observadas durante el trabajo

| Stat | Hellkevin | Ares | Nyx |
|---|---:|---:|---:|
| P. Atk | 1.183,83 | 3.490,69 | 298,12 |
| M. Atk | 1.204,25 | 936,94 | 21.277,17 |
| P. Def | 840,38 | 1.690 | 1.318,20 |
| M. Def | 1.379,67 | 1.939,27 | 3.129,04 |
| HP máximo | 4.793 | 40.500 | 24.480 |
| MP máximo | 3.978 | 8.100 | 28.980 |
| CP máximo | 3.198 | 12.000 | 10.000 |
| Atk. Speed | 410 | 576 | 402 |
| Casting Speed | 341 | 333 | 1.999 |
| Critical Rate | 42 | 500 | 500 |

Conclusión inicial:

- Ares domina daño físico, defensa y supervivencia.
- Nyx domina daño mágico y velocidad de casteo.
- Hellkevin es más equilibrado, pero está muy por debajo de ambos en recursos y
  supervivencia.
- Los stats finales no deben escribirse manualmente: el Game Server los recalcula
  usando atributos base, equipo, skills, pasivos y buffs.

Archivos modificados:

- `lab-panel\server.js`
- `lab-panel\public\app.js`
- `lab-panel\public\styles.css`

## 2. Laboratorio de Ideas portátil

Ubicación:

`D:\l2-local\idea-lab`

Accesos:

- Abrir: `9-ABRIR-LAB-IDEAS.cmd`
- Cerrar: `10-CERRAR-LAB-IDEAS.cmd`
- Dirección: `http://127.0.0.1:3212`

### Características

- Funciona sin Internet, Node, Java, MariaDB o Game Server.
- Usa PowerShell incluido en Windows.
- Abre Edge, Chrome o Brave en modo privado.
- El perfil del navegador se ubica dentro del disco portátil.
- No usa cookies, `localStorage` ni almacenamiento de aplicación en la PC ajena.
- Guarda automáticamente cada cambio en el disco.
- Conserva hasta 60 copias automáticas.
- Permite crear copias manuales desde la interfaz.

Datos principales:

- Espacio de trabajo: `idea-lab\data\workspace.json`
- Copias: `idea-lab\data\backups`
- Instrucciones: `idea-lab\README.txt`

### Herramientas incluidas

- Objetivo de la jornada.
- Selección de tres ideas prioritarias.
- Bloques de trabajo de 25, 50 o 90 minutos.
- Bitácora de sesiones terminadas.
- Fichas editables de ideas.
- Impacto, esfuerzo, prioridad y estado.
- Próximo paso comprobable.
- Preguntas abiertas y dependencias.
- Registro de decisiones y sus razones.
- Buscador, filtros y ordenamiento.
- Lector de las conversaciones originales de `docs chatsgpt`.

### Contenido inicial

Se cargaron 18 ideas y 3 decisiones. Los temas iniciales son:

1. Pruebas estructuradas de la Academia PvP.
2. Evaluación y consejos basados en telemetría.
3. Ares y Nyx como instructores con personalidad.
4. Diario anual de recompensas.
5. Tickets y tienda de Academia.
6. Motor genérico de efectos raros.
7. Arma reactiva de cinco golpes.
8. Escudo reactivo contra focus grupal.
9. Memoria persistente de NPC.
10. Facciones con reputación y recuerdos concretos.
11. Svetra como boss humano multifase.
12. Prototipo Blender/Koikatsu a Interlude.
13. Separación entre estadísticas, objeto y apariencia.
14. Endgame horizontal por campañas.
15. Primera anomalía o región oculta.
16. Marca de cacería y percepción alterada.
17. Apariencia dependiente del observador.
18. Crisis de infección conectada con sieges.

Fuentes disponibles en modo lectura:

- `academia.json`
- `endgame.json`
- `importar modelos.json`
- `recompensas.json`
- `recuerdos.json`
- `ropajes.json`

## 3. Laboratorio L2 — modo oficina

Accesos:

- Abrir: `11-ABRIR-LAB-L2-OFICINA.cmd`
- Cerrar: `12-CERRAR-LAB-L2-OFICINA.cmd`
- Dirección: `http://127.0.0.1:3210`

### Funcionamiento

Este modo inicia únicamente:

- MariaDB portátil desde `tools\mariadb-11.8.9-winx64`.
- Node portátil desde `tools\node-portable\node.exe`.
- El panel web del Laboratorio L2.

No inicia:

- Login Server.
- Game Server.
- Cliente Lineage II.

Permite trabajar con:

- Personajes e inventario guardados.
- Ares, Nyx y otros rivales.
- Comparación base/final usando las últimas lecturas disponibles.
- Clases y atributos.
- Skills.
- Telemetría de peleas anteriores.
- Creación y configuración de rivales.

Los cambios de XML y base de datos quedan en el disco. El botón para reiniciar el
Game Server se bloquea en modo oficina. Los cambios se aplican y se prueban al
regresar a la PC principal.

### Portabilidad

- Las rutas se calculan desde la ubicación real del disco.
- No depende de que Windows asigne la letra `D:`.
- Fue probado simulando el proyecto en la unidad `X:`.
- El perfil privado del navegador queda en `lab-panel\office-runtime`.
- Los procesos iniciados por este modo se registran con PID para cerrarlos sin
  afectar otros procesos de la PC.

## 4. Pruebas realizadas

### Laboratorio de Ideas

- Página principal servida correctamente.
- 18 ideas y 3 decisiones cargadas.
- Seis fuentes originales detectadas.
- Guardado y recarga del espacio de trabajo verificados.
- Copia manual verificada.
- Filtros, búsqueda, editor y lector de fuentes probados en navegador real.
- Presentación revisada a 1440 × 1000 y con reglas adaptables a pantallas menores.

### Lab L2 en modo oficina

- Sintaxis de Node y PowerShell verificada.
- Arranque mediante el Node incluido en el disco.
- Arranque en frío de MariaDB portátil.
- Lectura correcta de Hellkevin, Ares, Dominator, 89 clases y cuatro combates.
- Bloqueo del reinicio del Game Server confirmado.
- Arranque y cierre probados con otra letra de unidad (`X:`).
- Cierre limpio de panel y MariaDB confirmado.
- Entorno normal restaurado después de las pruebas.

Estado final tras las pruebas:

- MariaDB principal operativa.
- Login Server operativo.
- Game Server operativo.
- Panel principal funcionando en modo normal.
- Laboratorio de Ideas funcionando.
- Registros de error del panel vacíos.

## 5. Procedimiento recomendado en la oficina

Para diseñar y ordenar ideas:

1. Ejecutar `9-ABRIR-LAB-IDEAS.cmd`.
2. Elegir tres frentes para la jornada.
3. Trabajar en bloques y registrar decisiones.
4. Ejecutar `10-CERRAR-LAB-IDEAS.cmd`.

Para consultar o editar datos reales de L2:

1. Ejecutar `11-ABRIR-LAB-L2-OFICINA.cmd`.
2. Esperar a que abra el navegador privado.
3. Trabajar normalmente, evitando retirar el disco durante un guardado.
4. Cerrar la ventana del navegador.
5. Ejecutar `12-CERRAR-LAB-L2-OFICINA.cmd`.
6. Esperar unos segundos y expulsar el disco de forma segura.

## 6. Limitaciones y seguridad

- Una política corporativa puede bloquear PowerShell, `node.exe` o `mariadbd.exe`.
- No necesitan instalación ni deberían requerir permisos de administrador.
- En modo oficina no se generan peleas ni telemetría nueva porque el Game Server y
  el cliente permanecen apagados.
- No se debe abrir el puerto 3210 en el router: el panel no posee autenticación para
  exposición pública.
- El contenido del proyecto y el perfil utilizado por el Lab permanecen en el disco,
  pero Windows o la red empresarial podrían conservar registros técnicos de que se
  ejecutaron programas.
- Siempre se debe cerrar MariaDB con el acceso preparado antes de retirar el disco.

## 7. Próximos pasos sugeridos

1. Probar ambos accesos en la PC de oficina.
2. Diseñar la primera prueba completa de la Academia.
3. Especificar el formato del motor de efectos raros.
4. Diseñar los primeros 50 días del calendario de recompensas.
5. Convertir decisiones consolidadas del Lab de Ideas en tareas técnicas.
6. Al volver a casa, aplicar cambios pendientes, reiniciar y generar telemetría nueva.

## 8. Adaptación y prueba en Windows 10

Fecha de la prueba: 6 de octubre de 2026  
Ruta usada: `E:\l2-local`  
Cliente usado: `E:\l2\system-hud\L2.exe`

Se corrigieron los accesos normales para que calculen la ruta desde la carpeta del
disco y no dependan de `D:`. La misma copia puede funcionar ahora con `D:`, `E:` u
otra letra, siempre que `l2` y `l2-local` permanezcan como carpetas hermanas.

Correcciones realizadas:

- Accesos `0` a `8` convertidos a rutas portátiles.
- Inicio y detención de MariaDB, Login Server y Game Server convertidos a rutas portátiles.
- Panel L2 normal configurado para usar Node portátil y detectar su raíz automáticamente.
- Scripts auxiliares de GameGuard, HUD y Arena convertidos a rutas portátiles.
- Configuración `FakePlayers.ini` sincronizada entre servidor y fuente.
- Entrada de `hosts` aplicada en esta PC: `L2authd.Lineage2.com -> 127.0.0.1`.
- Copia previa de los archivos modificados guardada en
  `backups\portable-paths-2026-10-06`.

Pruebas completadas correctamente:

- MariaDB en `127.0.0.1:3307`.
- Login Server en `127.0.0.1:2106`.
- Enlace Login/Game en `127.0.0.1:19014`.
- Game Server en `127.0.0.1:7777`, cargado en 94 segundos.
- Panel normal en `127.0.0.1:3210`, con un personaje, 89 clases y cuatro combates.
- Cliente HUD abierto mediante `2-JUGAR.cmd`, con ventana `Lineage II` estable.
- Dependencias de 32 bits del cliente presentes en el sistema o en `system-hud`.

No fue necesario copiar los aproximadamente 20 GB del proyecto al disco interno.

## 9. Capacidad de buffs

El 6 de octubre de 2026 se ajustó la capacidad global del servidor:

- `MaxBuffAmount = 28`.
- `MaxDanceAmount = 16`.
- Divine Inspiration continúa sumando hasta cuatro espacios adicionales.
- Hellkevin, que posee Divine Inspiration nivel 4, queda con 32 espacios totales,
  de los cuales como máximo 16 pueden ser songs/dances.

El cambio fue aplicado en servidor y fuente, respaldado en
`backups\buff-slots-28-16-2026-10-06` y cargado mediante reinicio seguro del
Game Server sin clientes conectados.

## 10. Catálogo telemétrico por raza, clase y ranura

El 6 de octubre de 2026 se amplió `LabTelemetry` para evitar que el último cambio
de clase sobrescriba todas las mediciones anteriores de un personaje.

La tabla nueva `lab_player_stat_profiles` separa cada lectura por:

- personaje y raza de la clase principal;
- Principal, Sub 1, Sub 2 o Sub 3 activa;
- combinación completa de principal más tres subclases;
- nivel y equipo equipado;
- skills acumulados y efectos activos;
- estadísticas finales calculadas por el Game Server.

El perfil se actualiza al entrar, al cambiar de profesión y durante el combate.
El panel muestra estos perfiles en Telemetría bajo “Catálogo vivo”. Para construir
una base comparable se acordó medir a nivel 80, con el mismo equipo y sin efectos;
las pruebas buffeadas quedan identificadas como otro contexto.

La raza continúa perteneciendo a la principal incluso al usar una profesión de
otra raza como Sub. `//buildlab` mantiene “Cambiar raza” como acción separada. En
un servidor público esa acción se conectará a un crédito o permiso de servicio
pagado; no se mezclará con el cambio normal y gratuito de clase activa.

## 11. Reglas de acumulación de clases y efectos

El 6 de octubre de 2026 se consolidaron las siguientes reglas para builds de una
clase principal y hasta tres subclases:

- Guts y Frenzy son mutuamente excluyentes: ambos usan la familia de efecto
  `PINCH`, por lo que al aplicar uno se reemplaza el otro.
- Zealot usa una familia distinta (`PD_UP_SPECIAL`) y puede convivir con Guts o
  Frenzy.
- Bear, Wolf, Ogre, Puma, Bison, Rabbit y Hawk Totem ya se pueden lanzar y
  aprovechar con cualquier arma; dejaron de requerir dual fists o garras.
- Los tótems mantienen la familia `POSSESSION`, por lo que solamente queda activo
  un tótem a la vez.
- Overlord puede seleccionarse directamente en una ranura Sub sin tener que
  convertir primero la clase principal en orco u Overlord.
- Las masteries pasivas equivalentes no se acumulan entre ramas: para skills con
  el mismo nombre se conserva únicamente el nivel más alto. Las especializaciones
  con nombres distintos continúan separadas.
- Cambiar Principal o Sub no cambia la raza visual/base del personaje. El cambio
  de raza sigue siendo una acción especial independiente y actualmente reservada
  al administrador; el cobro todavía requiere definir moneda, precio y entrega.

Se recompiló y desplegó `GameServer.jar`. Después del reinicio respondieron
correctamente Login Server, Game Server, MariaDB y el panel, sin clientes
conectados durante el cambio. El jar anterior está respaldado en
`backups\class-rules-totems-masteries-2026-10-06\GameServer.jar.before`.

## 12. Cobertura de razas y profesiones

Se definió un recorrido base de 89 estados: 9 clases iniciales, 18 primeras
profesiones, 31 segundas y 31 terceras. Aunque existen cinco razas, se necesitan
nueve anclas porque Humano, Elfo, Elfo oscuro y Orco poseen orígenes guerrero y
místico; Enano sólo posee origen guerrero.

El panel de Telemetría ahora contiene un mapa de cobertura por etapa, raza y raíz.
Sólo cuenta como referencia una lectura de nivel 80, sin equipo, sin efectos, sin
subclases y con la principal activa. La clave del perfil también incorpora los
efectos activos para impedir que una muestra buffeada sobrescriba la limpia.

Se corrigieron dos relaciones equivocadas en `classList.xml`: Bladedancer deriva de
Palus Knight y Elemental Master deriva de Elemental Summoner. El procedimiento
completo quedó en `PLAN-COBERTURA-TELEMETRICA.md`.

La primera fase quedó completa con nueve personajes físicos y jugables: Arden,
Eryndor, Vaelkor, Gorvak, Brunna, Selene, Lethiel, Myrentha y Zhurak.
Están repartidos entre las cuentas locales `telemetryf` y `telemetrym`, son nivel 1,
poseen sus skills iniciales y acceso Master/GM para Build Lab. Un segundo reinicio
confirmó que el sembrador es idempotente y no genera duplicados. El respaldo previo
está en `backups\telemetry-anchors-2026-10-06\before.sql`.

## 13. Fase 2: catálogo limpio completo

El 6 de octubre de 2026 se automatizó el recorrido de las 89 clases desde los nueve
personajes físicos del plantel telemétrico. Cada estado se construyó dentro del Game
Server con un objeto `Player` real a nivel 80, skills aprendidas por el motor,
principal activa, sin subclases, equipo ni efectos. Las estadísticas no se insertaron
de forma sintética.

La validación final dio:

- 89/89 clases únicas y 89 filas limpias.
- 9/9 iniciales, 18/18 primeras, 31/31 segundas y 31/31 terceras profesiones.
- Humano 29/29, Elfo 20/20, Elfo oscuro 20/20, Orco 13/13 y Enano 7/7.
- Cero duplicados y cero perfiles con `skill_count=0`.
- Rango de skills por perfil: 11 a 83.
- Los nueve personajes quedaron offline, nivel 1, con su clase racial inicial,
  cero subclases y cero objetos equipados.

Durante la primera auditoría se detectó que el evento asíncrono de cambio de
profesión podía capturar un estado intermedio y sobrescribir el perfil controlado;
Scavenger apareció con cero skills. Se agregó una exclusión temporal para los
personajes bajo recorrido, se eliminaron únicamente las 89 lecturas telemétricas
defectuosas y se regeneró el catálogo. Scavenger quedó validado con 24 skills.

El ejecutor quedó idempotente: con 89/89 no vuelve a modificar el plantel al
reiniciar. El respaldo anterior a esta fase está en
`backups\telemetry-phase2-2026-10-06\before.sql`.

## 14. Fase 3: matriz completa de parejas

Entre el 6 y el 7 de octubre de 2026 se midieron las 465 parejas no ordenadas de
las 31 terceras profesiones. Cada combinación se construyó dentro del Game Server
con objetos `Player` reales y se observó tanto con la primera profesión como
principal activa como con la segunda en Sub 1 activa. El protocolo fue nivel 80,
sin equipo ni efectos, con restauración total del ancla al terminar.

La auditoría final dio:

- 465/465 parejas, 930/930 estados y cobertura de 30 compañeras para cada una de
  las 31 profesiones.
- Cero discrepancias entre los skills esperados y los skills reales completos
  (`ID:nivel`).
- Cero asimetrías de skills entre el estado principal y el estado Sub 1 de una
  misma pareja.
- Rango de 49 a 138 skills y promedio de 105,07.
- Entre 6 y 59 IDs compartidos; entre 2 y 7 colisiones de masteries por pareja.
- Nueve anclajes restaurados offline, nivel 1, sin subclases ni equipo.

La validación estricta reveló y permitió corregir dos problemas del núcleo. El
autolearn de la clase activa podía reemplazar un ID compartido por un nivel inferior,
y las masteries del mismo nombre y nivel no tenían desempate estable. Después de
`rewardSkills()` se restaura ahora la acumulación completa; las masteries conservan
el nivel mayor y, si empatan, el ID menor. Se recompilaron las 1.617 fuentes Java y
se desplegó el nuevo `GameServer.jar`.

El panel de Telemetría incorporó una matriz consultable de parejas y muestra el
progreso de Fase 3. Como extremos descriptivos, `Cardinal + Dominator` alcanzó 138
skills, mientras `Duelist + Dreadnought` compartió 41 IDs y produjo 7 colisiones de
mastery. Estas métricas sirven para seleccionar ensayos; no equivalen todavía a
balance real de combate sin equipo, buffs y mediciones funcionales.

Un reinicio de control verificó la idempotencia: la firma
`930:1791341968836:97712:465` permaneció idéntica y el Game Server informó
`parejas completas (465/465); no se modifica el roster`. MariaDB, Login Server,
enlace Login/Game, Game Server y panel quedaron activos. El respaldo de esta fase
está en `backups\telemetry-phase3-2026-10-06`.

La Fase 4 no recorrerá por fuerza bruta los 125.860 conjuntos posibles de una
principal más tres subclases. Primero se ordenarán candidatos con la matriz de
parejas y se elegirá una muestra dirigida que incluya alta amplitud, alta
redundancia, combinaciones físicas, mágicas, soporte e híbridas.

## 15. Fase 4A: catálogo teórico de cuatro clases

El 7 de octubre de 2026 se completó la etapa analítica de combinaciones de cuatro.
El generador `lab-panel\scripts\generate-phase4a.js` toma los conjuntos exactos de
skills de la Fase 3 y los metadatos XML del servidor. No carga objetos `Player`, no
cambia personajes y no requiere reiniciar el Game Server.

Se generó la tabla `lab_four_class_candidates` con:

- 125.860 builds: 31 principales por 4.060 ternas de Subs.
- 31.465 conjuntos únicos de cuatro clases/skills.
- Conteos de skills totales, pasivas y activas.
- Suma de IDs compartidos y colisiones de mastery entre las seis parejas internas.
- Cantidad de magos, invocadores, razas y clases del mismo arquetipo que la principal.
- Composición física, mágica o híbrida y hash SHA-256 del catálogo normalizado.

El rango previsto es de 88 a 231 skills y el promedio general es 176,42. El conjunto
de mayor amplitud es `Soultaker + Cardinal + Wind Rider + Dominator`, con 231 skills.
Estas cifras describen repertorio y redundancia; todavía no miden eficacia en combate.

Para evitar la fuerza bruta se seleccionaron 155 builds, cinco por cada profesión
principal y 31 por criterio: `amplitud`, `afinidad`, `estrés`, `híbrida` y
`cobertura`. Todas las profesiones aparecen al menos 13 veces y el promedio es 20.
Sólo estas 155 filas conservan el `skill_key` completo; las demás guardan su hash y
métricas, reduciendo el tamaño de la base.

La auditoría verificó:

- 125.860 filas y 4.060 candidatos por principal.
- Cinco seleccionados por principal y 31 por criterio.
- Cero clases repetidas dentro de una build y orden canónico de las Subs.
- Cero hashes incorrectos en las 155 listas completas.
- Cero listas completas innecesarias en las 125.705 filas no seleccionadas.
- Segunda ejecución idempotente con la misma firma
  `125860:22204568:31465:270455410881978`.

El panel incorporó una sección Fase 4A con progreso, resumen y la muestra completa.
El proceso web fue reiniciado sin afectar MariaDB, Login Server ni Game Server. El
respaldo previo está en `backups\telemetry-phase4a-2026-10-07`.

Próximo paso: Fase 4B, construcción y medición real de las 155 builds en sus cuatro
clases activas, para un total de 620 estados limpios.

## 16. Fase 4B: medición real de builds completas

El 7 de octubre de 2026 se construyeron dentro del Game Server las 155 builds
seleccionadas por la Fase 4A. Se utilizaron los nueve personajes ancla, distribuyendo
cada principal al ancla de su raíz natural para mantener el contexto racial correcto.
Cada build añadió tres subclases reales, las llevó a nivel 80 y activó sucesivamente
Principal, Sub 1, Sub 2 y Sub 3.

El resultado fue:

- 155/155 builds y 620/620 estados.
- Cinco builds por cada una de las 31 profesiones principales.
- 31 builds/124 estados para cada criterio de selección.
- Cero fallos durante el recorrido.
- Cero diferencias entre los skills reales y la predicción completa `ID:nivel` de
  Fase 4A.
- Cero hashes inválidos, builds incompletas, ranuras incorrectas o perfiles ajenos a
  la selección.
- Cero cambios de raza al activar Subs.
- 620 estados a nivel 80, sin equipo ni efectos.
- Entre 93 y 231 skills, con promedio de 176,91 en la muestra seleccionada.

La nueva tabla `lab_four_class_profiles` guarda los cuatro estados de cada build,
incluyendo personaje ancla, raza, clase activa, catálogo completo de skills y stats
calculados por el motor. El panel combina ahora Fase 4A y 4B: muestra los 125.860
candidatos, los 155 seleccionados y el avance/resultado de sus 620 estados reales.

La pasada comenzó a las 00:31:40 y terminó a las 00:54:16, con nueve trabajadores
raciales y cero fallos. Al finalizar, Arden, Selene, Eryndor, Lethiel,
Vaelkor, Myrentha, Gorvak, Zhurak y Brunna quedaron offline, nivel 1, con su
clase inicial, sin Subs ni equipo.

Un reinicio de control verificó la idempotencia. La firma
`620:1791345256083:109684:1315944042463` permaneció igual y el servidor informó que
no modificaría el roster. MariaDB, Login Server, enlace Login/Game, Game Server y
panel quedaron activos. El respaldo está en
`backups\telemetry-phase4b-2026-10-07`.

Con 4A y 4B completas, la siguiente etapa del plan es seleccionar finalistas en 4C
y medirlos en combate controlado durante 4D. La comparación con servidores de
referencia queda para la Fase 5. Las pruebas no recorrerán las 125.860 posibilidades.

## 17. Fase 4C: selección analítica de finalistas

El 7 de octubre de 2026 se compararon los 620 estados reales de Fase 4B contra la
línea limpia de su clase activa. Se evitó sumar porcentajes directos porque las
combinaciones desnudas producen multiplicadores muy distintos según la clase. El
analizador usa razones logarítmicas, las resume como medias geométricas y separa
seis funciones: física, mágica, tanque, soporte, summoner e híbrida.

Resultado auditado:

- 30 finalistas, cinco por cada una de las seis categorías.
- Por categoría: dos de rendimiento, uno de amplitud, uno de estrés y uno de
  control/contraste.
- 12 finalistas de rendimiento, seis de amplitud, seis de estrés y seis de control.
- Las 31 terceras profesiones aparecen en la muestra.
- Los 30 grupos de cuatro clases son distintos aunque se ignore cuál es principal.
- Se usan 24 profesiones como principal y ninguna se repite más de dos veces.
- Cada finalista conserva cuatro perfiles reales válidos de Fase 4B.
- Cero diferencias de hash frente al candidato 4A y cero motivos vacíos.
- Segunda ejecución con firma idéntica:
  `ec026f090be9db3da777412d4721e2c6`.

La tabla `lab_build_finalists` guarda categoría, tipo, rango, motivo, índices por
función, skills, solapamientos, colisiones de mastery y ganancias relativas. El
script repetible es `lab-panel\scripts\analyze-phase4c.js` y se expone como
`npm run phase4c`.

El panel recibió la API `/api/telemetry/finalists`, una tabla con los 30 casos y un
nuevo paso de seguimiento que distingue 4C completa de 4D pendiente. La API se
validó con 30 filas, rangos 1–30 y seis categorías; Login Server, Game Server,
MariaDB y el panel permanecieron activos. El control visual automatizado no pudo
arrancar por una ruta interna faltante del componente de automatización de Windows,
pero JavaScript, API y archivos estáticos pasaron sus comprobaciones.

La Fase 4C no modificó personajes ni reinició el Game Server. El respaldo previo
está en `backups\telemetry-phase4c-2026-10-07`. El próximo paso es la Fase 4D:
definir y ejecutar combates comparables con equipo, buffs, rival y rotación fijados
por función antes de consultar referencias externas en la Fase 5.

## 18. Fase 4D: protocolo y cola preparados

El 7 de octubre de 2026 se preparó la ejecución controlada de los 30 finalistas.
La tabla `lab_combat_benchmark_plan` contiene 95 casos y tres repeticiones por caso,
para un total de 285 pasadas todavía pendientes.

La cola separa 15 casos físicos, 10 mágicos, cinco de soporte, cinco de invocación,
30 de resistencia contra Ares y 30 contra Nyx. Todas las builds prueban ambos tipos
de supervivencia; las híbridas prueban además salida física y mágica por separado.
La selección de clase activa utiliza los cuatro estados reales de 4B. La auditoría
dio cero clases ajenas a su build, cero soportes fuera de la familia de soporte y
cero invocadores fuera de las tres profesiones summoner.

El contexto inicial queda fijado a equipo S natural por clase activa, arma compatible
con mastery, joyería Tateossian, enchant +0 y sin buffs externos. Los IDs exactos se
guardan en `lab-panel\phase4d-kits.json`; las 95 filas tienen arma asignada y usan
nueve modelos distintos. La firma reproducible de la cola es
`be540784830299badeae72a3b735cd5ea2651c853c4308fa41b99fbff78f7304`.

Se añadió Atlas (`NPC 900202`) al sur del Coliseo como blanco neutral: nivel 80,
10.000.000 HP, regeneración alta, 1.000 P. Def, 1.000 M. Def, inmóvil, inmortal y
sin agresión. Ares y Nyx siguen reservados para resistencia física y mágica. Los XML
de servidor y fuente quedaron sincronizados.

El panel incorporó `/api/telemetry/benchmarks`, la tabla de 95 casos y un progreso
real de 0/285. Se reinició el Game Server sin jugadores conectados; Login, Game,
MariaDB y panel quedaron activos, con registro de errores vacío. Los nueve anclajes
continúan offline, nivel 1 y sin subclases.

Esto completa la preparación, no la medición. El siguiente bloque debe instrumentar
inicio/fin de cada pasada, carga automática de build/equipo y agregación de daño,
curación, recursos, supervivencia e invocaciones. Respaldo:
`backups\telemetry-phase4d-2026-10-07`.

## 19. Fase 4D: ejecución de combate controlado completada

El 7 de octubre de 2026 se implementó en `LabTelemetry.java` un ejecutor automático,
incremental y reanudable para la cola preparada en la sección anterior. Sólo corre
con cero jugadores online. Para cada caso carga uno de los nueve personajes ancla,
construye la principal y sus tres Subs, activa la clase prevista, crea y equipa el
kit S +0, aplica la rotación y restaura por completo al personaje al terminar.

El modo de medición es `CORE_ACCELERATED`: emplea objetos `Player`, skills, stats,
fórmulas de daño y efectos reales del núcleo, pero avanza un reloj simulado de 45 o
60 segundos según cadencias y reutilizaciones. No incluye latencia, movimiento,
pathfinding ni decisiones humanas. Las curaciones usan la misma fórmula y potencia
del effect handler sin ejecutar sus rutas de red/party sobre un jugador offline; la
salida de invocación conserva por separado el daño del dueño y el de la mascota.

Resultado auditado:

- 95/95 casos completos y 285/285 pasadas, tres por caso.
- 45 pasadas físicas, 30 mágicas, 15 de soporte, 15 de invocación, 90 de resistencia
  ante Ares y 90 ante Nyx.
- Cero casos con cantidad distinta de tres y cero métricas obligatorias inválidas.
- Promedios: 103,56 DPS físico, 67,75 DPS mágico, 119,22 DPS total de invocación y
  407,94 HPS de soporte.
- Supervivencia promedio de 26,79 s contra Ares y 3,22 s contra Nyx; esto identifica
  a Nyx como una prueba demasiado corta para discriminación fina y candidata a una
  futura calibración.
- Picos de la muestra: Ghost Sentinel/finalista 25 con 218,27 DPS físico;
  Mystic Muse/finalista 7 con 94,41 DPS mágico; Elemental Master/finalista 29 con
  159,54 DPS total; Cardinal/finalista 15 con 465,48 HPS.

Durante pilotos forzadamente interrumpidos quedaron 14 objetos temporales en Arden.
Se respaldaron sus filas en
`backups\telemetry-phase4d-2026-10-07\phase4d-leaked-temp-items.sql` y se eliminaron
por ID exacto. El control final dejó los nueve anclajes offline, nivel 1, en sus
clases iniciales, sin Subs y con cero objetos telemétricos. La operación es
recuperable desde ese respaldo.

La API `/api/telemetry/benchmarks` y el panel muestran ahora el promedio de las tres
repeticiones según protocolo. El respaldo íntegro de plan y resultados es
`backups\telemetry-phase4d-2026-10-07\phase4d-results-final.sql`. Login Server, Game
Server, MariaDB y panel quedaron activos. La siguiente etapa es la Fase 5 de
comparación documentada con otros servidores; 4D queda cerrada y no se deben aplicar
buffs o nerfs usando estos picos aislados sin antes analizar dispersión, contexto y
calibración de oponentes.

## 20. Fase 5A: L2Nyx externo y calibración no destructiva de Nyx

Se etiquetó el commit público de la línea base como
`phase4d-baseline-2026-10-07`. A partir de allí se incorporó un formato de
expediente externo y se registró L2Nyx con sus fuentes oficiales, configuración
SubAcu Base +3 y diferencias respecto del laboratorio local.

El panel de Telemetría ahora posee dos bloques nuevos: Servidores externos y
Calibración de Nyx. La API expone
`/api/telemetry/external-references` y
`/api/telemetry/nyx-calibration`.

Para evitar alterar o reemplazar la evidencia de 4D se creó
`lab_nyx_calibration_runs`. El ejecutor reutilizó los 30 casos de resistencia
mágica, tres repeticiones por caso y cuatro escalas de daño final: 100%, 75%, 60%
y 50%. Solo se escaló el daño obtenido de la fórmula real; el resto del protocolo
quedó fijo.

La corrida terminó el 7 de octubre a las 17:36 con 360/360 pasadas y cero fallos.
Las supervivencias medias fueron 3,14 s, 3,29 s, 4,00 s y 4,92 s respectivamente.
Ninguna pasada alcanzó 10 segundos; el máximo del perfil 50% fue 9,12 s. Por lo
tanto no se cambió el XML de Nyx y la siguiente ronda deberá probar escalas menores,
sugeridas en 30%, 25% y 20%.

Auditoría de cierre: 285 filas originales de 4D intactas, 90 filas por cada escala,
tres repeticiones exactas por caso, cero métricas inválidas y los nueve anclajes
offline, nivel 1, sin Subs ni objetos. El volcado recuperable está en
`backups/telemetry-phase5a-2026-10-07/phase5a-nyx-calibration.sql`.

## 21. Fase 5A.2: progresión mágica normal y Nyx Élite separada

Se creó una prueba incremental sobre Myrentha para responder cuánto crece un mago
normal al sumar Subs. El personaje se midió como Storm Screamer puro y luego con
Mystic Muse, Archmage y Soultaker acumulados, manteniendo Storm Screamer activo.
Se fijaron nivel 80, Atlas, Arcana Mace +0, robe S, joyería S común, Blessed
Spiritshots, cero buffs externos, 60 segundos acelerados y tres repeticiones.

La corrida cerró 12/12. El Storm Screamer puro registró 1.308,68 M.Atk, 366 de
casteo y 44,07 DPS con Hurricane. Mystic Muse mantuvo exactamente los atributos,
pero habilitó Aura Flare, elevó los lanzamientos de 15 a 37 y llevó el promedio a
87,38 DPS. Archmage tampoco cambió M.Atk/casteo y promedió 85,19 DPS. Soultaker
añadió una pasiva, elevó M.Atk a 1.344,96 (+2,77%) y promedió 83,45 DPS. La leve
baja de los últimos promedios responde a la variación de críticos; no constituye
evidencia de que una Sub reste daño.

Nyx no fue editada. Se conserva explícitamente como Nyx Élite con 21.277,17 M.Atk
y 1.999 de casteo, entre 15,82 y 16,26 veces el M.Atk de estos perfiles normales.
Esto confirma que sirve como rival especial y referencia extrema, no como modelo
de progresión de un personaje.

Se agregó la tabla `lab_magic_progression_runs`, el endpoint
`/api/telemetry/magic-progression` y una sección del panel con etapas, skills,
atributos, DPS, recursos y rotación. La cola es incremental y, si encuentra un
jugador conectado o todavía no encuentra Atlas, vuelve a intentarlo al minuto.

Auditoría: tres filas por etapa, cero métricas inválidas, 285 resultados 4D y 360
de calibración preservados. Myrentha volvió offline a nivel 1, Dark Mystic, sin
Subs ni objetos. El respaldo está en
`backups/telemetry-phase5a2-2026-10-07`; el repositorio conserva SQL y resumen JSON
en `data/telemetry/`.

La siguiente medición deberá distinguir una skill fija común —para comparar la
contribución pura de stats— de la mejor rotación disponible —para medir la utilidad
real de acumular catálogos de skills—. No se aplicaron buffs ni nerfs.


## 22. Fase 5A.3: stats aislados frente a catálogo práctico

Se añadieron dos carriles comparables a la progresión mágica: Hurricane #1239
nivel 28 fija en todas las etapas y el nuke con mejor potencia/cadencia disponible.
El protocolo conserva Storm Screamer activa, nivel 80, Atlas, Arcana Mace +0, robe
S, joyería común S, Blessed Spiritshots y cero buffs externos.

La muestra inicial de tres repeticiones reveló demasiado ruido de críticos, por lo
que se amplió a treinta repeticiones por carril y etapa: 240/240 pasadas. Hurricane
promedió 44,23; 43,33; 43,57 y 45,70 DPS. El M.Atk fue idéntico en las primeras
tres etapas y subió de 1.308,68 a 1.344,96 con Soultaker. La fórmula de raíz
cuadrada convierte ese +2,77% de M.Atk en aproximadamente +1,38% de daño esperado.

Desde Mystic Muse, el selector práctico elige Aura Flare: 84,03–86,23 DPS, entre
88,67% y 95,17% por encima de Hurricane fija. Aura Flare pega menos por lanzamiento,
pero su ciclo de 1.592 ms permite 37 casteos frente a 15 de Hurricane a 3.821 ms.
El costo es proporcional: 2.553 MP frente a 1.035 MP.

Esto confirma que la build no duplica daño acumulando M.Atk. Duplica la salida
sostenida al adquirir una skill mucho más rápida. Por balance deben medirse juntos
potencia, ciclo, cantidad de casteos, MP y contexto, no sólo el número de M.Atk.

Se creó lab_magic_comparison_runs, el endpoint /api/telemetry/magic-comparison y
el bloque 5A.3 del panel. La auditoría dio cero filas inválidas y preservó 4D,
calibración de Nyx y 5A.2. Myrentha fue restaurada offline, nivel 1, Dark Mystic,
sin Subs ni objetos; Nyx Élite permaneció intacta.

Respaldo recuperable: backups/telemetry-phase5a3-2026-10-07. El repositorio
conserva SQL y resumen JSON en data/telemetry/. No se aplicaron buffs ni nerfs.

## 23. Fase 5A.4: base racial Humana con clases acumuladas

Se creó una prueba física sobre Arden para separar de forma explícita la raza de
nacimiento de las clases adquiridas. Arden nació Human Fighter y mantuvo la raza
Humana durante toda la corrida. Dreadnought quedó activa y se añadieron Titan,
Fortune Seeker y Maestro sin cambiar la raza. Se fijaron nivel 80, Atlas, Saint
Spear +0, heavy S, joyería S común, Soulshots y cero buffs externos.

La corrida cerró 240/240: cuatro etapas, autoataque fijo y una skill física
compatible, con treinta repeticiones por carril. P.Atk quedó en 1.007,28, velocidad
en 351, crítico en 86 y STR/DEX/CON en 42/28/43 en todas las etapas. HP, CP, MP y
precisión tampoco cambiaron. El catálogo sí creció de 59 a 92 skills, pero las
masteries añadidas no aumentaron los atributos físicos de la build.

El autoataque promedió 67,95; 68,16; 68,32 y 69,63 DPS. La diferencia final de
2,48% está dentro de la dispersión y no representa un aumento de stats. Earthquake
fue la skill compatible elegida por potencia/ciclo, pero su cooldown sólo permite
dos acciones por minuto y produjo 9,13–10,68 DPS, muy por debajo del autoataque.
Seis pasadas terminaron sin daño porque ambas acciones fallaron; son resultados
válidos, no registros rotos.

La auditoría verificó 240 claves únicas y cero filas con raza, clase activa, nivel
o equipo incorrectos. Arden quedó restaurada offline, nivel 1, Human Fighter, sin
Subs ni objetos; todo el roster telemétrico quedó limpio. Los resultados anteriores
permanecieron intactos.

Se añadió `lab_physical_race_runs`, el endpoint
`/api/telemetry/physical-race-baseline` y el bloque 5A.4 del panel. El respaldo
recuperable está en `backups/telemetry-phase5a4-human-2026-10-07`; el repositorio
conserva el SQL y resumen JSON en `data/telemetry/`.

Esta etapa es el control Humano, no una comparación racial terminada. El próximo
paso correcto es replicar exactamente el protocolo en otro ancla de nacimiento y
comparar contra esta base sin cambiar clase activa, Subs, equipo ni rival.

## 24. Fase 5A.6: comparación física completa de cinco razas

Se amplió la base Dreadnought + Titan + Fortune Seeker + Maestro a Arden
(Humano), Eryndor (Elfo), Vaelkor (Elfo oscuro), Gorvak (Orco) y Brunna (Enano).
La raza pasó a ser un dato persistente del personaje: cambiar principal o Sub ya
no la reemplaza; `//buildlab` conserva una acción administrativa separada para
cambiarla.

La primera ampliación reveló dos falsos positivos. Arden estaba guardado con 0
HP y Final Frenzy #290 nivel 14 añadía exactamente 129,3 P.Atk. Después, los
anclajes atacaban a Atlas desde las coordenadas de sus aldeas de nacimiento; la
fórmula de acierto de Interlude incorpora altura y orientación, por lo que los
promedios parecían distintos pese a tener los mismos stats. Se corrigió la
limpieza para revivir antes de restaurar HP y eliminar funciones huérfanas, y se
normalizó temporalmente posición/altura durante el benchmark.

La corrida válida cerró **1.200/1.200 pasadas**, 240 por raza. Las cinco
compartieron exactamente 877,9798 P.Atk, 351 de velocidad, 86 de crítico, 123 de
precisión, 6.542 HP, 4.718 CP, 1.794 MP y 42/28/43 STR/DEX/CON. Polearm Mastery
aportó 129,3 P.Atk a todos. El catálogo creció igual de 59 a 92 skills al sumar
Subs y no produjo acumulación adicional de masteries físicas.

El autoataque quedó entre 43,7912 y 44,7144 DPS según raza, frente a desviaciones
de 4,62–4,74; Earthquake quedó entre 7,1152 y 7,9234 con sólo dos acciones por
minuto. Con stats, skills, equipo, posición y rival idénticos, esas variaciones se
interpretan como ruido de aciertos/críticos, no como una ventaja racial.

La conclusión técnica es precisa: la raza persistida conserva cuerpo, apariencia
e identidad; la clase activa Dreadnought aporta la plantilla numérica. Introducir
stats raciales persistentes sería una decisión futura de diseño/balance. No se
aplicó ningún buff o nerf.

Auditoría final: cero filas inválidas, cero grupos incompletos, cinco diagnósticos
idénticos y ningún jugador conectado. Los cinco anclajes volvieron nivel 1, con
HP completo, clase raíz, cero Subs, cero objetos y coordenadas originales. Se
preservaron 285 pasadas 4D, 360 calibraciones de Nyx, 12 progresiones mágicas y
240 comparaciones mágicas. El volcado final y el resumen JSON quedaron en
`data/telemetry/`; el respaldo local está en
`backups/telemetry-phase5a6-five-races-2026-10-07`.

## 25. Telemetría observada de la sala Elven PvP

La primera batalla real de Hellkevin contra las copias confirmó 2.765 eventos
entre las 22:21 y las 22:59. La telemetría anterior podía medir jugador contra
NPC, pero ignoraba NPC contra NPC; por eso Eryndor y Gorvak aparecían sin
actividad aunque estuvieran presentes en la instancia.

Se amplió `lab_combat_events` con `instance_id` y `observer_count`. Los nueve IDs
`901100–901108` ahora se consideran objetivos telemétricos dentro de la plantilla
3051. La captura de NPC contra NPC sólo se habilita cuando hay al menos un jugador
real dentro de esa misma instancia y se detiene automáticamente al quedar vacía.
Esto permite observar el FFA sin generar datos infinitos en segundo plano.

También se incorporaron sus snapshots a `lab_creature_stats` y un endpoint/panel
específico que agrega daño saliente, daño recibido, impactos, fallos, críticos,
bajas, muertes, daño por muerte, barras de HP absorbidas, defensas y skill
principal. El esquema migró sin pérdida de las 5.233 filas históricas. El Game
Server cargó 128 scripts y el panel quedó listo; la próxima entrada con
`.elvenpvp` será la primera sesión completa con NPC contra NPC.

Respaldo previo a la migración:
`backups/elven-pvp-telemetry-2026-10-07/lab-combat-events-before-npc-vs-npc.sql`.

## 26. Coliseo secuencial: nueve duelos 1vs1

El Coliseo global dejó de generar automáticamente a Ares y Nyx. Sus plantillas
`900200` y `900201` no fueron eliminadas y quedan disponibles para comparaciones
especiales mediante spawn manual. Atlas, Thiago y Mirellas permanecen en sus
lugares porque siguen siendo el blanco telemétrico, el buffer y la tienda.

Arden, Selene, Eryndor, Lethiel, Vaelkor, Myrentha, Gorvak, Zhurak y Brunna
esperan en formación junto a la entrada sur, opuesta al punto seguro del jugador.
Fuera de un duelo permanecen inmóviles, con IA detenida e invulnerabilidad. El
comando de macro `.arena iniciar` pone en marcha la serie: el rival activo corre
primero al centro y luego fija exclusivamente al participante como objetivo.

Al morir un rival se abre una preparación real de diez segundos con avisos de
cuenta regresiva. La serie termina después de la novena victoria y muestra el
mensaje de felicitación; `.arena repetir` vuelve a comenzar desde Arden. También
existen `.arena estado` y `.arena cancelar`. Si muere el jugador, la ejecución se
marca como fallida, el roster vuelve a la entrada y se puede repetir tras revivir.

Se agregaron `lab_arena_gauntlet_runs` y `lab_arena_gauntlet_duels` para guardar
los límites exactos de cada serie y duelo, resultado y HP/CP/MP finales. Los
eventos detallados de combate permanecen en `lab_combat_events`. Respaldo previo:
`backups/solo-arena-gauntlet-2026-10-08`.

La primera prueba manual reveló geodata defectuosa en la entrada sur exterior.
Arden completó el recorrido, pero Selene agotó el tiempo de entrada detrás de la
pared y el controlador permitió que comenzara a lanzar magia desde allí. La
ejecución quedó correctamente registrada como una victoria ante Arden y derrota
ante Selene, pero su geometría no era válida.

El roster fue trasladado a una línea sur completamente interior comprendida entre
las antiguas posiciones comprobadas de Ares, Nyx y Atlas. Cada rival activo ahora
es colocado primero en `148900,45800,-3400`, corre un tramo corto y visible hasta
`148900,46100,-3400` y sólo allí pierde la invulnerabilidad. Si el movimiento se
atasca durante seis segundos, se lo traslada al centro antes de habilitar el
combate; ya no existe ninguna ruta que permita atacar desde detrás de una pared.
Respaldo: `backups/solo-arena-gauntlet-geodata-fix-2026-10-08`.

### 8 de octubre: stats de los nueve rivales en el laboratorio

El panel incorpora **Rivales del Coliseo**, accesible también con
`http://127.0.0.1:3210/?view=arena`. Muestra las copias de combate
901100–901108, no los personajes de telemetría de nivel 1. La tabla reúne HP,
CP, MP, P.Atk, M.Atk, P.Def, M.Def y velocidades de ataque/casteo de los nueve.
Al seleccionar un rival aparecen también atributos, críticos, precisión,
evasión, rango y movimiento. Se puede seleccionar Hellkevin u otro personaje
para comparar los nueve y ver diferencias absolutas y porcentuales.

Los valores proceden de `lab_creature_stats`: son la última lectura real del
Game Server, con los efectos activos al capturarla, y no una predicción de
stats desnudos. Se conserva la fecha de captura y se pueden consultar antes
de pelear o con el juego cerrado. Actualmente los nueve tienen datos.
El endpoint de lectura es `/api/arena-roster`; no cambia stats ni balance.
Verificados sintaxis, API, render de las nueve filas, selección de Myrentha y
comparación con Hellkevin. No se pudo realizar revisión visual automática
porque el controlador de navegador no tenía un navegador disponible.

### 8 de octubre: dos pilotos Player humanos, sólo principal

Se preparó `RealHumanPilots.java` para crear Caelan (Sagittarius) e Ignara
(Archmage), ambos sin subclases, humanos al máximo 80, con equipo, SA, enchant +4,
dyes y buffs reales. Receta completa: `PILOTOS-HUMANOS-REALES.md`.
No se escriben stats manuales. La recarga comprueba identidad, raza, ausencia de subclases,
inventario, dyes, cantidad de skills y quince stats calculadas. El laboratorio
puede capturar sus stats sin inventar un combate mediante
`LabTelemetry.capturePilotStatsNow`.

Compilación Java local correcta. Tras comprobar que ya no había cliente ni
jugadores conectados, se cargó el script sin expulsar a nadie. Caelan
`268473939` e Ignara `268473955` ya fueron creados, verificados por recarga y
capturados en `lab_player_stats`. Ambos humanos, nivel 80, cero subclases y
todo el equipo +4; stats y cantidad de skills coinciden antes/después de recarga.
Caelan: P.Atk 3392.22, velocidad 729, HP 6073. Ignara: M.Atk 4221.08,
casteo 1180, HP 5356. No hay todavía IA de combate para estos pilotos y no se
reemplazaron los nueve NPC artificiales.
Respaldo previo: `backups/real-human-pilots-2026-10-08`.

Corrección solicitada: medir primero la principal sola, sin combinaciones.
Las masteries se pisan y no se deben usar clases redundantes para inflar stats.
Cuando se incorporen subclases, sólo la principal tendrá tercera profesión;
las subs conservarán segunda profesión y se incorporarán de a una.

### 8 de octubre: Dominator orco y Mystic Muse elfa reales

Se amplió el preparador con Korvash `268473977` (ORC, Dominator 115) y Aelira
`268473992` (ELF, Mystic Muse 103), tercera profesión, nivel 80 y cero subs.
Mismo equipo mágico +4 y buffs que Ignara. Aelira usa dyes +INT y +WIT; Korvash
sólo +WIT porque el dye +INT no admite Dominator, y no se forzó esa restricción.
Ambos verificados por recarga, stats y skills idénticas, 20 efectos. M.Atk:
Korvash 2372.73, Aelira 3572.15; casteo 922 y 1365 respectivamente. Stats
completas en `PILOTOS-HUMANOS-REALES.md` y Personajes del laboratorio.
No se modificó Hellkevin, no se añadieron subs ni activables automáticos y no
se reemplazaron los nueve NPC. Reinicio sin clientes conectados. Respaldo:
`backups/orc-elf-real-pilots-2026-10-08`.

### 8 de octubre: Soultaker humano y aclaración de Spellhowler

Creado Morvain `268473971`, humano Soultaker (95), nivel 80, cero subs, equipo,
dyes y buffs mágicos iguales a Ignara. Verificado por recarga: 81 skills,
20 efectos, M.Atk 4221.08, casteo 1180, HP 5356, CP 1526 y MP 5060.
Reinicio sin clientes conectados. Respaldo:
`backups/soultaker-storm-pilots-2026-10-08`.

El segundo piloto «elfo Spellhowler» queda pendiente de aclaración explícita:
elfo oscuro original o elfo claro con Storm Screamer. Se detectó que el core
conserva la raza visual/guardada, pero los atributos base provienen de la
plantilla de clase activa. Un ELF con clase 110 no tiene automáticamente los
atributos base raciales de ELF; no se modificó esta regla ni se publicaron
stats de ese personaje como si la raza ya estuviera aislada.
