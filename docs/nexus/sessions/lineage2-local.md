# Lineage II Interlude Lab

Ruta operativa: `E:\l2-local`  
Cliente local: `E:\l2`  
Repositorio: `https://github.com/matthyuga/l2`
Clon local de sincronización: `E:\l2-local\cloud-repo`

## Estado al 7 de octubre de 2026

- Servidor basado en L2J Mobius Interlude con panel de laboratorio e Idea Lab.
- Fase 1: 9 personajes ancla.
- Fase 2: 89/89 clases limpias.
- Fase 3: 465/465 parejas y 930/930 estados.
- Fase 4A: 125.860 candidatos; 155 seleccionados.
- Fase 4B: 155 builds reales y 620 estados.
- Fase 4C: 30 finalistas.
- Fase 4D: 95 casos, tres repeticiones y 285/285 pasadas válidas.
- Fase 5A: L2Nyx documentado y primera calibración de Nyx completa, 360/360.
- Fase 5A.2: progresión Storm Screamer completa, 12/12 pasadas.
- Fase 5A.3: Hurricane fija frente a mejor skill completa, 240/240 pasadas.
- Fase 5A.6: comparación física de Humano, Elfo, Elfo oscuro, Orco y Enano
  completa, 1.200/1.200 pasadas con posición y estado controlados.
- Próxima decisión racial: mantener la arquitectura actual —raza para identidad y
  apariencia, clase activa para stats— o diseñar coeficientes raciales explícitos.
- Alternativa pendiente: segunda ronda de Nyx en 30%, 25% y 20%.

## GitHub

El repositorio público se pobló con el commit `a5aae7b` (`Add L2 Interlude lab
project snapshot`). Contiene documentación, paneles, scripts, notas conceptuales,
datos finales de 4D y un overlay de 29 archivos modificados/nuevos sobre el commit
Mobius `d47756357`.

Quedan fuera deliberadamente el cliente, binarios, runtimes completos, herramientas,
MariaDB activa, cuentas, credenciales, logs, perfiles de navegador y backups
generales. La acción `Validar snapshot` terminó correctamente.

La línea base 4D quedó etiquetada como `phase4d-baseline-2026-10-07`. La Fase 5A
se publicó en `eedb912` y su acción `Validar snapshot` terminó correctamente. El
repositorio contiene el expediente externo de L2Nyx, el panel ampliado y el volcado
de 360 pasadas de calibración. Las escalas 100%, 75%, 60% y 50% dieron 3,14 s,
3,29 s, 4,00 s y 4,92 s de supervivencia media; ninguna alcanzó 10–20 s y el XML
del NPC Nyx no fue modificado.

La progresión 5A.2 midió Storm Screamer puro y luego con Mystic Muse, Archmage y
Soultaker acumulados, siempre con Storm Screamer activo. Dio 1.308,68 M.Atk y 366
de casteo en las primeras tres etapas; Soultaker elevó M.Atk a 1.344,96 (+2,77%).
Mystic Muse casi duplicó el DPS al habilitar Aura Flare, no por inflar M.Atk. Nyx
quedó intacta y separada como Nyx Élite (21.277,17 M.Atk, 1.999 cast). Los 12
resultados, SQL, JSON, panel y bitácora están listos para publicar. Myrentha fue
restaurada offline, nivel 1, Dark Mystic, sin Subs ni objetos.

La Fase 5A.2 se publicó en el commit `f7faa26` (`Add Storm Screamer progression
telemetry`). La acción `Validar snapshot` terminó correctamente:
`https://github.com/matthyuga/l2/actions/runs/37688128951`.

La Fase 5A.3 comparó Hurricane fija con el mejor nuke durante 30 repeticiones por
carril y etapa, 240/240. Mystic Muse y Archmage no modificaron M.Atk ni casteo;
Soultaker añadió 2,77% M.Atk, equivalente a +1,38% de daño teórico por la fórmula
de raíz cuadrada. Aura Flare dio 84,03–86,23 DPS frente a 43,33–45,70 de Hurricane
porque permite 37 casteos en lugar de 15, usando 2.553 MP frente a 1.035. Myrentha
fue restaurada y Nyx Élite no cambió. La fase se publicó en `f416237`; la acción
`Validar snapshot` terminó correctamente:
`https://github.com/matthyuga/l2/actions/runs/37691775630`.

La Fase 5A.4 fijó el control físico Humano con Arden: Dreadnought activa y Titan,
Fortune Seeker y Maestro como Subs acumulativas, Saint Spear +0, heavy S,
Soulshots, sin buffs y Atlas como objetivo. Cerró 240/240 pasadas. Todas las filas
conservaron `race_id=0`, `HUMAN`; P.Atk 1.007,28, velocidad 351, crítico 86 y
STR/DEX/CON 42/28/43 permanecieron idénticos. El catálogo creció de 59 a 92
skills sin acumulación observable de masteries físicas. Earthquake fue la skill
compatible elegida, pero sus dos acciones por minuto quedaron en 9,13–10,68 DPS,
frente a 67,95–69,63 del autoataque. Las diferencias del autoataque están dentro
del ruido estadístico. Arden volvió offline, nivel 1, Human Fighter, sin Subs ni
objetos. Respaldo: `E:\l2-local\backups\telemetry-phase5a4-human-2026-10-07`.

La fase se publicó en `fe43ae1` (`Add human physical race baseline`) y la acción
`Validar snapshot` terminó correctamente:
`https://github.com/matthyuga/l2/actions/runs/37695332151`.

La revisión 5A.6 demostró que la base 5A.4 estaba contaminada: Arden se cargó
muerto y Final Frenzy #290 nivel 14 añadió exactamente 129,3 P.Atk. También se
descubrió que las coordenadas de las aldeas iniciales alteraban aciertos mediante
las bonificaciones de altura/lado. La limpieza ahora revive antes de restablecer
HP/efectos, purga funciones huérfanas y coloca temporalmente a todos los anclajes
en la misma posición frente a Atlas.

La captura válida cerró 1.200/1.200, 240 por raza. Las cinco razas dieron
exactamente 877,9798 P.Atk, 351 velocidad, 86 crítico, 123 precisión, 6.542 HP,
4.718 CP, 1.794 MP y 42/28/43 STR/DEX/CON. Polearm Mastery aportó 129,3 P.Atk a
todas. El autoataque quedó entre 43,7912 y 44,7144 DPS con desviaciones de
4,62–4,74; no hay evidencia de bonificación racial. Los cinco anclajes terminaron
offline, nivel 1, HP completo, clase inicial, sin Subs ni objetos y en sus
coordenadas originales. Respaldo:
`E:\l2-local\backups\telemetry-phase5a6-five-races-2026-10-07`.

La raza ya está persistida de forma independiente de la clase. Los cambios de
principal/Sub la conservan; sólo la acción dedicada de `//buildlab` la modifica.
La Fase 5A.6 se publicó en `0dbcba8` (`Preserve race identity and catalog five
physical races`). La acción `Validar snapshot` terminó correctamente:
`https://github.com/matthyuga/l2/actions/runs/37716407741`.

La sala Elven PvP aislada y sus ajustes acompañantes también se incorporaron al
overlay: instancia 3051, comando `.elvenpvp`, nueve FakePlayers, Noblesse y
recursos al entrar/reaparecer, Scheme Buffer de 7.200 s con Noblesse, Mana Potion
por 2.000 Adena y límite de tres cubics sin mastery. Se publicó en `34d341e`
(`Add Elven PvP room and gameplay hotfixes`). Requiere aún validación manual de
pathfinding, selección de blancos, daño y supervivencia desde el cliente.

La batalla de Hellkevin en Elven produjo 2.765 eventos observables, pero la
telemetría original sólo conservaba encuentros con el jugador. Se amplió para
registrar NPC contra NPC entre los IDs 901100–901108 dentro de la instancia 3051.
La captura se habilita únicamente mientras haya al menos un jugador real en la
sala y se detiene cuando queda vacía. `lab_combat_events` ahora incluye
`instance_id` y `observer_count`; `lab_creature_stats` acepta también los nueve
combatientes. El panel ofrece `/api/telemetry/elven-pvp` con daño infligido y
recibido, impactos, críticos, fallos, bajas, muertes, HP/defensas y skill
principal. Está activo y esperando la próxima entrada a `.elvenpvp` para generar
la primera muestra NPC contra NPC.

Respaldo previo: `E:\l2-local\backups\elven-pvp-telemetry-2026-10-07`. Publicado
en `f740f72` (`Capture observed Elven NPC combat telemetry`). La acción
`Validar snapshot` terminó correctamente:
`https://github.com/matthyuga/l2/actions/runs/37717576692`.

El 8 de octubre de 2026 el Coliseo global pasó a una prueba secuencial de nueve
duelos 1vs1. Ares y Nyx dejaron de tener spawn automático, pero sus plantillas
permanecen intactas para comparaciones manuales. Arden, Selene, Eryndor, Lethiel,
Vaelkor, Myrentha, Gorvak, Zhurak y Brunna esperan protegidos en la entrada sur.
`.arena iniciar` lanza cada rival hacia el centro y después contra el jugador;
cada victoria abre diez segundos de preparación. `.arena estado`, `cancelar` y
`repetir` completan el control por macro. La victoria nueve muestra el cierre y
una muerte del jugador marca la serie como fallida y devuelve el roster a espera.

Las tablas `lab_arena_gauntlet_runs` y `lab_arena_gauntlet_duels` delimitan cada
ejecución y duelo con resultado y recursos finales; `lab_combat_events` conserva
los golpes detallados. El servidor cargó el controlador sin errores y quedó
activo. Respaldo: `E:\l2-local\backups\solo-arena-gauntlet-2026-10-08`.
Publicado en `6db9c92` (`Add sequential Coliseum gauntlet`); validación exitosa:
`https://github.com/matthyuga/l2/actions/runs/37751967307`.

La primera prueba manual encontró geodata rota en la puerta sur exterior: Arden
llegó, pero Selene comenzó a lanzar desde detrás de una pared al vencer el timeout.
Se movió todo el roster al piso sur interior, dentro del rectángulo ya probado por
Ares/Nyx/Atlas. Cada rival aparece primero en `148900,45800,-3400` y corre hasta
`148900,46100,-3400`; si el movimiento tarda seis segundos, se teletransporta al
centro antes de poder atacar. Respaldo:
`E:\l2-local\backups\solo-arena-gauntlet-geodata-fix-2026-10-08`.
Corrección publicada en `5a00c42` (`Keep Coliseum gauntlet inside playable floor`),
con validación exitosa: `https://github.com/matthyuga/l2/actions/runs/37753908066`.

El 8 de octubre se añadió al Laboratorio L2 la vista **Rivales del Coliseo**
(`http://127.0.0.1:3210/?view=arena`), con los stats reales guardados de los nueve
NPC de combate 901100–901108, detalles completos y comparación contra Hellkevin
u otro personaje. No usa los personajes de nivel 1 como sustituto. Los nueve
tienen captura; se muestra su fecha y se conservan los datos en modo oficina.
Sólo se modificó el panel, sin tocar balance ni reiniciar el Game Server.

Preparación siguiente: `RealHumanPilots.java` crea Caelan (arquero) e Ignara
(maga de fuego), ambos humanos Player reales, nivel 80, sólo principal, equipo
y arma +4, SA, dyes y buffs. Receta en `E:\l2-local\PILOTOS-HUMANOS-REALES.md`.
Ya ejecutado después de comprobar que el usuario cerró el cliente: Caelan
`268473939`, Ignara `268473955`, ambos HUMAN nivel 80 y cero subclases.
`lab_real_human_pilots.verified_ms` confirma recarga con stats y skills idénticas;
`lab_player_stats` contiene P.Atk 3392.22 de Caelan y M.Atk 4221.08 de Ignara.
Visibles en Personajes del panel. No hay IA autónoma todavía ni reemplazo del
roster del Coliseo. Cambios espejados a source y cloud-repo.

Corrección explícita del usuario: Caelan sólo Sagittarius, Ignara sólo Archmage,
sin subclases por ahora. En pruebas futuras, sólo principal con tercera profesión,
subs en segunda profesión, masteries que se pisan; evitar combinaciones redundantes.

## Archivos locales clave

Solicitud siguiente: humano Soultaker (Morvain) y «elfo Spellhowler». Morvain se
preparó con el mismo equipo/buffs/dyes mágicos, sólo principal 95, nivel 80.
Ya creado/verificado: `268473971`, cero subs, 81 skills, 20 efectos, M.Atk
4221.08, casteo 1180, HP 5356. Visible en Personajes. Para Spellhowler se pidió
aclarar si es DARK_ELF original o ELF claro con clase 110. Importante: el core
actual conserva `_race` en Player para identidad/apariencia, pero CreatureStat
obtiene STR/DEX/CON/INT/WIT/MEN de `getTemplate()` de la clase activa. Por tanto,
un ELF con Storm Screamer seguiría recibiendo atributos de plantilla DARK_ELF;
no afirmar que esos números aíslan los atributos raciales del elfo claro.
No se modificó el core para cambiar esta semántica sin autorización.
Después el usuario pidió ambas variantes: ya creadas Velith `268473890`
DARK_ELF y Sylira `268473929` ELF, clase 110 nivel 80 cero subs, cuenta de
agrupación `telemetryx`. Verificadas tras recarga. Equipo/enchant/dyes/buffs
idénticos, 74 skills y 20 efectos cada una. Los 29 stats comparados coinciden:
M.Atk 4727.93, casteo 1125, INT/WIT/MEN 49/24/27. Prueba empírica del problema
raza guardada vs atributos de plantilla de clase. No implica equivalencia
real de las razas. Cambiar el core sigue pendiente de autorización.

Ampliación del mismo preparador: Korvash `268473977` (orco Dominator) y Aelira
`268473992` (elfa Mystic Muse), reales nivel 80, cero subs, equipo mágico +4
y mismos buffs que Ignara. Dye +INT excluido de Korvash por restricción real;
sólo +WIT. Verificados por recarga y visibles en Personajes. M.Atk 2372.73 y
3572.15; casteo 922 y 1365. Sin IA de combate todavía. Receta y stats completas
en `PILOTOS-HUMANOS-REALES.md`.

- `E:\l2-local\BITACORA_LABS_PORTATILES_2026-10-06.md`
- `E:\l2-local\PLAN-COBERTURA-TELEMETRICA.md`
- `E:\l2-local\ARENA-DE-PRUEBAS.txt`
- `E:\l2-local\lab-panel`
- `E:\l2-local\idea-lab`
- `E:\l2-local\source`

## 2026-10-08 — Regla racial fija autorizada e implementada

Core activo: seis atributos proceden de raza guardada + perfil inicial
FIGHTER/MYSTIC persistido en character_variables.RACIAL_PROFILE. Profesión
y sub no reescriben perfil. 17 personajes migrados según principal guardada
(no clase activa). Hellkevin humano FIGHTER, main Paladin5, activa MysticMuse103:
mantiene atributos de humano fighter; anterior INT/WIT élfico ya no aplica.
Su fila characters se comparó con el respaldo y está intacta. Recapturar al
ingresar; panel no usa lecturas anteriores como actuales.

Build Lab: Cambiar SOLO raza, GM, mantiene build/perfil. RESET origen+principal
es operación diferente. No hay servicio público VIP ni precio aún. Nuevas
capturas lab_player_stats rules_version=fixed-racial-v1; anteriores excluidas
de comparaciones actuales sin borrarlas. Fases históricas permanecen, rerun
sería otro trabajo. No tocar nueve NPC ni añadir subs a pilotos.

Siete pilotos reales recargados/verificados. Ocho checks con RacialProbe
(cuenta técnica racialtest, sin cliente/IA): humano40/30/43/21/11/25 conserva
atributos en Sagittarius, Tyrant, Spellsinger y reload mago; cambio explícito
orco40/26/47/18/12/27 persiste y mantiene build. Restaurado humano/main92.
Velith MAtk4727.93/casteo1125 vs Sylira3572.15/1365, mismo110/equipo/dyes/buffs.

Alcance: seis atributos + derivados normales; curvas HP/MP/CP por nivel,
velocidad base y bases de ataque/defensa siguen con clase activa. Dwarf sin
mystic nativo usa plantilla53. No afirmar independencia racial total de curvas.
Documento E:\l2-local\RAZA-Y-PERFIL-FIJO.md; backup previo completo
E:\l2-local\backups\fixed-racial-profile-2026-10-08. Primer ensayo corrigió
getScript null con getVariables; posiciones de siete pilotos restauradas
del respaldo. Último arranque y verificaciones sin fallos.

Sincronizado con GitHub `matthyuga/l2`, commit `19839bc` (main), sin subir
dump SQL, credenciales ni binarios. Se preservaron cambios locales previos
en mensajes de daño: no se incluyeron mezclados en el commit racial.

## 2026-10-08 — Perfiles normales para el gauntlet

Los nueve rivales del Coliseo ahora reciben stats copiados desde personajes
Player técnicos nivel 80, tercera activa, sin subs, raza fija, equipo +4, dyes
y buffs. Los anclajes originales se preservan. P.Atk/M.Atk: Arden
1259,65/330,40; Selene 496,23/4101,03; Eryndor 3074,18/363,84; Lethiel
483/3572,15; Vaelkor 1250,75/389,98; Myrentha 516,08/4727,93; Gorvak
1746,90/298,58; Zhurak 582,24/2372,73; Brunna 1329,43/322,30.
Detalle: `E:\l2-local\NUEVE-NPC-PVP-NORMAL.md`. Script compilado, roster 9/9
aplicado en arranque. IA/consumibles aún pendientes; falta validar daño y
supervivencia manualmente.

## 2026-10-08 — Tres subs de tercera con skills por slot activo

Regla global autorizada: CumulativeSubclassSkills=False; todos los skills de
segunda y tercera, pasivos y masteries son del slot activo, conservando raza
y perfil FIGHTER/MYSTIC. No sumar los cuatro árboles. Siete pilotos con tres
subs nivel 80/tercera: Caelan (93/113/88), Ignara (103/110/115), Aelira
(94/95/115), Korvash (94/103/95), Morvain (110/103/115), Velith y Sylira
(94/103/115). Principales y raza originales; volvieron a principal al finalizar.
RealHumanPilots migra receta a human-pilots-v2-active-slot, usa APIs Mobius y
dyes legales por slot. 35/35 verificaciones en vivo: cuatro slots más recarga
en Sub3 por piloto. No skills exclusivos ajenos, origen racial persistido y
stats de principal iguales antes/después. No cambiar arma automáticamente al
cambiar slot; Caelan requiere armas compatibles para combatir como sus subs.
Panel/Build Lab actualizados; capturas fixed-racial-active-slot-v1, anteriores
históricas. Nueve NPC sin nuevas subs; su roster sigue activo. Compilación Java
y checks de sintaxis del panel OK. Backup SQL previo y archivos en
E:\l2-local\backups\active-class-skills-2026-10-08.
Detalle E:\l2-local\CLASE-ACTIVA-Y-TRES-SUBS.md.

Publicado en main de matthyuga/l2: commit 48166c1. Repositorio limpio; sin
dump SQL ni binarios. El panel también oculta lecturas finales de otra clase.

## 2026-10-08 — CORRECCIÓN: segunda acumulada, tercera sólo activa

El usuario aclaró que sólo tercera debe depender del slot: la interpretación
de 48166c1 (todos los skills exclusivos) fue demasiado amplia y está revocada.
Core corregido: CumulativeSubclassSkills=True y
CumulativeSubclassThirdSkillsActiveOnly=True. Player restaura todos los slots:
inactivos limitados al árbol completo del antecesor de segunda; tercera
exclusiva y aumentos de nivel de tercera sólo si ese slot está activo. Mismo
ID usa nivel máximo permitido; masteries repetidas por nombre una sola ganadora.
Skills permanecen aprendidos por slot; no se borraron. Raza/perfil fijo.
Siete combinaciones conservadas; no introducir las alternativas mixtas aún.
Receta human-pilots-v3-hybrid-third y capturas fixed-racial-hybrid-third-v1;
panel y Build Lab actualizados. 35/35 checks y 7/7 recargas sin errores:
acumulación de segunda, exclusión de terceras inactivas, niveles correctos,
masteries no duplicadas, stats iguales antes/después de recarga y origen fijo.
Caelan Sagittarius 111 skills efectivos frente a 54 con regla anterior;
Ignara Archmage 158 frente a 74. Build completo 1617 fuentes y scripts OK.
Fuente local Player tenía cambios previos de mensajes de daño; se preservaron
y sólo el delta de esta corrección se aplicó al overlay de GitHub.
Detalle E:\l2-local\SUBACU-SEGUNDA-Y-TERCERA-ACTIVA.md. Backup jar/core/SQL
E:\l2-local\backups\hybrid-third-active-2026-10-08.

Corrección publicada en GitHub main: b11d5a2. Repositorio limpio. API del
laboratorio confirma 7/7 capturas híbridas compatibles y principal activa.

## 2026-10-08 — Doce rivales con tres subs complementarias

Usuario aprobó nueve candidatas mixtas y pidió tres adicionales. Añadidos Kaelis
(humano Sagittarius/Tyrant/Destroyer/SK), Riven (humano Adventurer con mismas subs)
y Noctis (orco Dominator/Bishop/SK/Phantom Summoner), todos con tercera aprendida.
NormalNpcRoster receta normal-pvp-s4-hybrid-v2 migra nueve perfiles anteriores y
crea tres: nivel80, regla híbrida, raza fija, equipo/joyas+4, dyes legales y buffs.
No cambiar builds de siete pilotos ni anclajes nivel1. Recetas completas y stats:
E:\l2-local\DOCE-RIVALES-SUBACUMULATIVOS.md.

Coliseo901100–901111: doce duelos .arena, diez segundos entre victorias, última
terna en segunda fila interior. Entrada segura previa preservada. Inicio bloqueado
hasta roster listo. Panel muestra doce, subs y stats; captura NPC síncrona tras
aplicar perfil corrige snapshots antiguos. Selene/Noctis usan Steal Essence1245/14
en vez de Prominence ajeno. IA de summons/TP/cubics/curas/potas/defensivos pendiente.

Arranque final21:48:19, listo21:49:31. 96checks slots y12recargas PASS;
lab-panel/scripts/verify-twelve-roster.js SUCCESS12/12: recetas, raza, nivel,
regla actual y nueve stats NPC=Player fuente. Java/sintaxis/XML OK. Falta combate
manual y ver segunda fila en cliente. Kaelis PAtk3392.22/MAtk330.40/atk764;
Riven1214.80/330.40/1129; Noctis593.34/2372.73/casteo922. Backup SQL/archivos:
E:\l2-local\backups\twelve-hybrid-roster-2026-10-08.

Fuente/overlay/apps/docs sincronizados en cloud-repo local, SIN commit/push en
este turno. GameServer/panel activos, sin cliente conectado. Documento antiguo
NUEVE-NPC-PVP-NORMAL marcado histórico sin subs; rankings antiguos no revalidados.

## 2026-10-09 — Preparados19 rivales y selector de duelo individual

Usuario quiere enfrentar a los19 uno por uno. Preparadas copias NPC de los
siete pilotos (originales intactos), ArenaCaelan…ArenaVelith cuenta
telemetryarena3, ids901112–901118. NormalNpcRoster conserva doce existentes
y añade siete con mismas builds/raza/equipo/buffs. Gauntlet añade `.arena lista`
y `.arena probar nombre|numero`, sin siguiente automático en modo individual;
secuencia completa19 con iniciar/repetir. Run agrega test_mode/selected_npc_id,
victorias separadas del índice del rival. Telemetría/panel ampliados a901118.

Código compila,19templates XML, selector57válidos+6inválidos PASS. Pendiente
activar reiniciando: había cliente conectado7777 y NO se desconectó. Se pidió
salir del juego por pregunta asíncrona. No afirmar19preparados en runtime hasta
logs19/19 y verify-arena-roster.js SUCCESS19/19+copias7/7. Documentación:
E:\l2-local\DIECINUEVE-DUELOS-INDIVIDUALES.md. Backup SQL/archivos:
E:\l2-local\backups\nineteen-individual-arena-2026-10-09.

## 2026-10-09 — Activacion del roster19 verificada

Roster activo19/19 a06:02:41;152checks slots/recarga antes de readiness.
verify-arena-roster.js SUCCESS19/19: nueve stats NPC=Player, copias7/7 iguales
a pilotos originales. Fallo inicial de Sylira corregido en paralelo por otra
sesion con origen racial explicito y recuperacion del perfil incompleto.
Se instalaron jars compatibles ya compilados de player-combat-pilots y se
retiraron cuatro GameServer duplicados, preservando DB/login y Amber.
Usuario confirma otra sesion dedicada a conductas humanas; no se editaron
sus modulos IA. Esa sesion reinicio instancia9592 y ejecuta pruebas AI_SMOKE.
Documentacion DIECINUEVE-DUELOS-INDIVIDUALES actualizada; prueba manual en
cliente pendiente. Evidencia: backups/nineteen-individual-arena-2026-10-09/
activation-verification.json. No confundir roster NPC de stats reales con19
bots Player de IA completa. Usar PID del listener7777, pues run/game.pid viejo.

## 2026-10-09 06:05 — Sesion IA: validacion en curso

LabCombatPilots instalado con Player headless real. Listener actual PID13544;
run/game.pid actualizado. Reinicio seguro sin cliente para autoprueba privada.
Se detecto error historico de receta SK:107 es Spectral Dancer,106 es Shillien
Templar. Se corrigen SOLO perfiles tecnicos ArenaKaelis/ArenaRiven/ArenaNoctis
mediante modifySubClass, conservando raza/equipo/principal y maximizando la sub.
verify-arena-roster.js ya espera106 en esas tres posiciones. Otros107 intactos.
No reiniciar ni editar modulos IA mientras se completa AI_SMOKE. Resultado final
pendiente; primera corrida fallo por cubic SK ausente, no por handler de summon.

### IA finalizada 06:07:45

AI_SMOKE SUCCESS10/10, runs3/4 SMOKE_PASS: Nightshade en instancia privada,
phantom/vampiric cubics, TP, Puma, UD aumenta defensa, cura propia/summon,
CP y MP con consumo real. Ambos Players retirados/offline0. Runs1/2 fallo
historico SK conservados. Check19/19 y copias7/7 nuevamente PASS tras106.
335 checks de politica PASS. .ia fisico=Riven, .ia mago=Noctis, estado/cancelar;
GM sin invul, Coliseo PvP,20s prep,6min limite, bloqueo mutuo con .arena.
Player real/headless usa flag efimero labControlled para broadcast online2;
sin FuncSet, stats naturales, skills aprendidas/condiciones/reuse reales.
Presupuesto HP10/CP50/MP30, shots/reagentes reales. Noctis summon/TP/curas/
cubics/toggles/controles/drain; Riven cubics/totem/blows/Bluff/Trick/Switch/
defensivos con Guts-Frenzy exclusivos. No inventar Anchor en esta build.
Solo estos DOS pilotos usan IA nueva;19 NPC conservan IA anterior.
Falta duelo manual y tacticas avanzadas; no afirmar combate PvP validado.
Fuente/runtime/overlay/docs sincronizados localmente, sin commit ni push.
Documento E:\l2-local\IA-PILOTOS-PLAYER.md; backup player-combat-pilots-2026-10-09
incluye SQL previo y jar anterior. Listener13544, pid actualizado, panel3210.

2026-10-09 reinicio pedido por usuario: GameServer PID=17348. Elevacion Windows necesaria y aprobada; cliente cerrado antes del reinicio. DB/login preservados. Roster19/19 preparado y verify-arena-roster SUCCESS19/19+copias7/7. Evidencia backups/arena-restart-20261009-061912/verified-ready.json y roster-verification.log. Sin cambios de codigo en este reinicio.

## 2026-10-09 — Personalizacion racial GM implementada

Usuario autorizo version basica antes de mejorar visual. .raza abre menu HTML
GM gratuito; macro con .raza. Dos toggles separados apariencia/atributos,
selectores5razas/9origenes,30valores Actual/Nuevo/dif/% en3paginas, Actualizar,
resumen y confirmacion con token de un uso y vigencia60s. Aplicar requiere
ciudad PEACE, fuera combate/duelo/olimpiada/instancia/comercio/pesca/montura.
No cura; cabello/rostro0 al cambiar aspecto, conserva sexo y clases/progreso.

Core: characters.race visual; RACIAL_STAT_RACE+RACIAL_PROFILE origen stats.
Sin variable nueva usa raza vigente (migracion compatible). setRace legado
sigue cambiando ambos; setAppearanceRace conserva stats. Contexto ThreadLocal
por Player proyecta con formulas reales, sin mutar raza ni guardar; PlayerStat
omite efectos de maxHP/CP/MP al proyectar. Vars se sincronizan al guardar.
Telemetria incluye origen/aspecto/perfil y nueva clave de captura; panel usa
origen de stats y descarta lecturas incompatibles. BuildLab agrega acceso al
menu propio. Modulos IA sin cambios. Fuente/dist/overlay/apps/docs sincronizados
localmente; sin commit/push. Start-L2Local -VerifyRacialCustomization permite
pruebas opt-in; arranques normales no las ejecutan.

Final PASS47checks:9origenes proyeccion=aplicacion, aislamiento entre hilos,
limpieza por excepcion, tres modos, recursos, principal/skills/3subs y recarga.
RacialProfileVerification8PASS y verify-arena-roster19/19+copias7/7PASS. Probe
RaceMenuProbe cuenta racialmenutest queda offline/invisible, no NPC/spawn.
Hellkevin conserva apariencia/origen HUMAN/FIGHTER; no se aplico cambio suyo.
GameServer15048 y panel3210 activos al finalizar. Cliente no abierto por agente.
Falta revision visual/manual del menu y aspecto en cliente real, no afirmar
preview3D. NPC VIP/precio/acceso publico pendientes. Docs:
E:\l2-local\PROBAR-PERSONALIZACION-RACIAL.md y SERVICIOS-RAZA-Y-ATRIBUTOS.md.
Backup/Evidencia E:\l2-local\backups\race-customization-2026-10-09.

## 2026-10-09 - .raza v2 selector de principal/subclases

Activo tras cierre L2 confirmado. Selector slots0..3 toma raza/perfil nativos;
no activa clase, origen global. Confirmar/Cancelar/Aplicar antes de tabla,
texturas Interlude; manual libre preservado. Compilacion y68checks motor PASS,
RacialProfile8PASS, roster19/19+copias7/7PASS. Listener13276. IA/core/Amber
sin cambios. Falta revision cliente. Detalle inbox/20261009-lineage2-race-class-selector-active.md.

## 2026-10-09 — Noctis v2 y observacion de duelos IA

Usuario autoriza mejorar Noctis/telemetria y confirma cierre cliente. Reinicio
seguro sin L2/conexiones, core actual preservado (personalizacion racial),
solo scripts nuevos. Listener13064, run/game.pid actualizado. DB/login/panel
preservados. Sin modificaciones de stats, equipo, raza, build o19NPC `.arena`.

LabCombatPilots: observa summon antes de curas incluso muerto, max2solicitudes
aceptadas incluyendo inicial (interrumpidas consumen presupuesto), bloqueo
durante invocacion pendiente; no resummon en combateHP<=60%. Apagado de337/
1283/1262 antes de curas y aun silenciado, misma retirada que useMagic de
Player. Cura no urgente espaciada4s, emergencia<25% sin pausa; control cercano
antes de cura no urgente. Recall de summon bajoHP fuera de rango/LOS, pausa
ataque3s para regreso. No prometer eficacia PvP hasta revancha manual.

DuelObservation: tabla lab_duel_observations, cada500ms Player operador+bot y
sus summons; recursos/maximos/posicion/target/casteo/muerte/silencio/root/stun/
cubics; baseline y aparicion/desaparicion skill:nivel:effector; presencia de
actores. Cola4096/batches512 SQL async; perdidas en log. Solo .ia, no global.
NO exact resist/cancel reason; ausencia no demuestra resistencia, desaparicion
puede ser expiracion/muerte/retirada. No cura/item consumption exacto usuario,
efectos<500ms/reaplicaciones identicas pueden faltar. No retroactivo.

PASS108 pruebas nuevas+335anteriores; Java compilado contra jar vigente.
AI_SMOKE SUCCESS10/10 runs10/11PASS, nuevas observaciones reales run11 incluyen
Nightshade y TP/totem/UD; reporte sin error, ambos perfilesoffline0.
verify-arena-roster19/19+copias7/7PASS. CLI read-only lab-panel/scripts/
duel-report.js [run_id], JSON decisiones/eventos/observaciones/limites; sin
numero ultimo manual. Sin vista nueva del panel. Fuente/runtime/overlay/docs
sincronizados localmente, sin commit/push. Documento NOCTIS-IA-Y-TELEMETRIA-V2.md.
Backup scripts/SQL/log E:\l2-local\backups\noctis-observation-v2-2026-10-09.

## 2026-10-09 — HUD de pilotos y dano recibido en cliente

Usuario pide barra comoNPC, efectos y numeros/chat enemigo. Scripts IA:
updateHud en tick envia ExOlympiadMode2 +UserInfo(Player,1) CP/HP500ms al
targetear bot; ExOlympiadSpelledInfo efectos no pasivos/inUse1s. Limpia al
cambiar target/terminar y restauraHUD NPCfake si nuevo target lo es.
Sin flags reales Olimpiadas. `.ia efectos` listaHTML max36 buffs/debuffs con
nombre/nivel/tiempo, actualizacion manual. Alt+F NO confirmado ni cambiado.

Listener OnCreatureDamageDealt SOLO piloto/summon al operador durante prueba
manual envia PilotDamageMessage con protocolo SystemMessage estandar id2204-7,
2params nombre+entero. Fisico naranja/critico rojo/magico rosa/critico rosa
intenso, [ENEMIGO] nombre, numero -cantidad en pantalla, posicion nativa5.
No anclado al mundo3D, no sombra negra individual. Cantidad=impacto evento,
no netHP despues CP/TP. No cambia mensajes estandar ni dano saliente2200-3.

Cliente SOLO E:\l2\system-hud\systemmsg-e.dat parche2087->2091, conserva
registrosanteriores y SafePackage. Codec413 roundtripPASS, archivosinstalados
hashcoincide. Script tools/Patch-PilotIncomingDamage.ps1 reproducible sobre
decodificado, rechaza IDsduplicados. PASS4 paquets IDs/string/int/longitud,
Java compila. Cliente cerrado/no7777establecido comprobado antes de copiar
y reiniciar; listener18872/pidactualizado. Core/personalizacionracial intactos,
DB/login/panel preservados. Backup pilot-hud-damage-2026-10-09.
Pendiente revision VISUAL en cliente de barra/iconos/numeros/colores; no afirmar
que Alt+F funciona ni efecto de sombreado. Docs PILOTOS-BARRA-EFECTOS-DANO.md,
source/dist/overlay/scripts/tests/docs sincronizados local, SINcommit/push.

Arranque HUD final: AI_SMOKE SUCCESS10/10 y check19/19+copias7/7PASS tras
limpieza. Check lanzado durante UD de la autoprueba dio diferencia temporal
PDef de Riven; al terminar y restaurar baseline vuelvePASS, no modificarstats.


## 2026-10-09 - Amber contrato implementado
Prototipo GM instalado: .amber y dialogo NPC902500; summon arquero902501 con fuego/lluvia carga3.5s/ruptura. 37 checks PASS, core e IA de otros conservados. Usar 2-JUGAR. Reproduccion visual pendiente de revision con usuario. Detalle: E:\l2-local\AMBER-CONTRATO-SUMMON.md; Nexus inbox 20261009-lineage2-amber-summon-implemented.md. Servidor activo, opt-in amber.verify=false; source/cloud espejados sin commit/push.

### Correccion posterior: boton Amber
El menu enviaba Quest AmberContract accept, bypass no registrado. Corregido a voice .amber firmar/romper; firmado valida NPC seleccionado/proximidad. Test ampliado usa BypassHandler + VoiceCommand: 40 checks PASS (verify-40-button-checks.log). Source/cloud actualizados, cliente cerrado verificado y servidor reiniciado. Nota: inbox/20261009-lineage2-amber-button-fix.md.

10/10/2026: combates disponibles otra vez,19/19 preparados. Corregida sub activa persistida del perfil ArenaMyrentha. Pruebas4vs4 y arena PASS. Cuenta del usuario ahora `hellkevin`, mismos personajes y progreso; detalles sin credenciales en inbox/20261010-lineage2-roster-account-fixed.md y continuidad27.

10/10/2026: catalogo nativoV3: franjas gruesas por clase en Alt+K, filtros corregidos en cliente/servidor y Siguiente clase solo slots poseidos. 1312 checks PASS, roster19/19. Continuidad28; inbox/20261010-lineage2-skill-groups-v3.md. Visual/clics in-game pendientes.

10/10/2026: buffs summons en Thiago: automatico segun summon y perfiles manuales. Amber fisica, buffs del amo conservados, 231 checks PASS, roster19/19. Continuidad29; inbox/20261010-lineage2-summon-buffs.md.

10/10/2026: correccionDDSemblemas a16x16/8x16, IDs nuevas,6crests/19rivales. Ver inbox/20261010-lineage2-crest-pow2.md y continuidad30.

10/10/2026: paneles .clanlab niveles/skills, HellkevinGMlider, gratuito. 342 checksPASS, clanes sin modificaciones hasta aplicar. Ver inbox/20261010-lineage2-clanlab.md, continuidad31.

10/10/2026 Giran NPC siege preparado .giran,5clanes x4 Fury/Waves nuevosconcrests,19pilotos. Ares/Nyx copias aisladas; IAespecial pendiente. Siege no iniciado, originalclanes/castillo/core/cliente conservados. Ver inbox/20261010-lineage2-giran-siege.md y continuidad32.

11/10 Giran V2: OOM pool32/heap4GB, agendas independientes, bandos nativos/19pilotos80. Prueba nativa PASS. Conquista246sinitem50MP3min. Continuidad33; ver inbox/20261011-giran-v2.md.

11/10 Giran V3: Amber puertas/perimetro, defensa competitiva4clanes/lideres246, guardianes actuales aliados/revival. 141checks nativosPASS; humano/propiedadHellconservados. Verinbox/20261011-giran-v3.md y continuidad34.

# Giran V4 completado — 11/10/2026
Proyecto E:\l2-local. Se instalaron bases HQ separadas Holly110000/142000, Fury111200/144100, Sacred110000/146200, Waves111700/147500 con geodata y rutas comprobadas. Salidas escalonadas5s. Escaramuzas entre atacantes en entrada/patio10s y retorno al avance20s; defensores/engravers prioritarios, PvP nativo. Respawn30s en HQ vivo/base de respaldo; rebuff después de resurrección externa. Construcción comprueba bandera real/reintenta respetando reutilización nativa30min. 347 checks nativos PASS: cuatro HQ construidos, ruta, selección respawn, revivalbuff, vuelta a puerta tras agresor; pruebas Amber/guardianes/Seal mantenidas. Humano/inventario,clanes/rep/blood/skills,Giran/fecha y382guardias idénticos;19pilotos offline80; Hellsing conservaGiran. Core/cliente sin cambios. Runtime/source/cloud y continuidad35 sincronizados; sin commit/push. GS libre y siege inactivo. Prueba completa de defensa/balance pendiente de Kevin. No reejecutar generadores V3 ni instaladores históricos.
Documento: E:\l2-local\GIRAN-CAMPAMENTOS-V4.md. Prueba/backups: research/giran-camps-v4, backups/giran-camps-v4-2026-10-11.
`n11/10/2026 Giran V5 PREPARADO, NO INSTALADO: E:\l2-local\research\giran-orders-v5. Scripts compilados: ordenes solo aliados/traer vivos mismo piso, puertas melee/magia. L2 17992 conectado a GS12376; esperar cierre antes de snapshot/install.ps1 -Verify. Runtime y source/cloud siguen V4. Wall: clic del mouse confirmado, coordenadas /loc pendientes; diagnostico preparado, no geodata cambiada. Compilacion PASS, prueba nativa pendiente. Ver inbox/20261011-giran-v5-in-progress.md y GIRAN-ORDENES-V5.md.

# Giran V5 completado — 11/10/2026
Proyecto E:\l2-local. Kevin cerró L2 y se instaló V5. Órdenes seguir/asalto/retirada evalúan clan, alianza y defensores actuales; los cuatro clanes rivales mantienen sus agendas. .giran traer teletraslada solo pilotos aliados vivos a celda conectada del mismo piso, sin revivir ni mover guardianes/humanos/enemigos. .giran diagnostico registra coordenadas cliente/servidor y estados IA. Ruptura de puerta no se interrumpe por distancia al capitán; magos usan nukes nativos y puerta requerida se prioriza antes que guardias en muralla. 389 checks nativos PASS: exclusión rivales/posición conservada, aliado misma altura, movimiento en capas -2448/-2144, daño melee y mágico real puerta, regresión HQ/revival/Amber/Seal/guardianes. Snapshot privado antes/después conserva Hellkevin/inventario, clanes/rep/blood/skills, Giran/fecha y382guardias;19pilotos offline80. Core/cliente sin cambios. Muro: Kevin usa clic; falta /loc exacto, no afirmar corregido por smoke tests. Memoria anterior OOM2GB por pool ThreadLocal caminos; V2 limita32buffers65MiB, GS actual4GB. Runtime/source/cloud y continuidad36 sincronizados; sin commit/push. Prueba completa de defensa pendiente de Kevin.
Documento: E:\l2-local\GIRAN-ORDENES-V5.md. Prueba y respaldo: research/giran-orders-v5, backups/giran-orders-v5-2026-10-11. No reejecutar instaladores/generadores históricos.

# Giran V6 completado — 11/10/2026
E:\l2-local. Kevin pidió escuadrones que avancen hasta conquista, líderes al artefacto y escoltas que limpien/protejan. Se instalaron etapas puerta exterior/patio/interior/sala/pasillo/artefacto; ningún objetivo secundario ausente detiene la ruta principal. Líder prioriza llegada y Seal nativo3min, escolta adquiere defensores1100 y protege canal; persecución10s/1600 desde adquisición, rival-attacker ventanas10s y retorno20s en todo castillo. Llegada final24 frente al antiguo100 y rango85 de Seal. Se corrigieron exactamente5bits E/W en5bytes de23_22, escalera norte y145064 x117528..117960; alturas/capas/otras colisiones conservadas, NPC artefacto original, sin bypass ni teleport de conquista. Original privado respaldado. 541 checks nativos PASS, incluyendo líder camina desde sala por pasillo/escalera hasta inicio real deSeal (sala despejada/salud restaurada para aislar navegación); escolta ataca agresor y mantiene defensor que se aleja másde400. Regresión órdenes aliadas/puertas/HQ/buffs/Amber/guardianes PASS. Snapshots conservan Hellkevin/inventario,clanes/rep/skills,Giran/fecha/owner y382guardias;19offline80. Core/cliente unchanged. Runtime/source/cloud/continuidad37 sincronizados,sincommit/push. Siege completo bajo combate/balance y muroexterior exacto(/loc) pendientes. No reejecutar instaladores históricos.
Documento E:\l2-local\GIRAN-ASALTO-POR-ETAPAS-V6.md; pruebas research/giran-assault-v6; backups/giran-assault-v6-2026-10-11.

# Giran V6 completado — 11/10/2026
E:\l2-local. Kevin pidió escuadrones que avancen hasta conquista, líderes al artefacto y escoltas que limpien/protejan. Se instalaron etapas puerta exterior/patio/interior/sala/pasillo/artefacto; ningún objetivo secundario ausente detiene la ruta principal. Líder prioriza llegada y Seal nativo3min, escolta adquiere defensores1100 y protege canal; persecución10s/1600 desde adquisición, rival-attacker ventanas10s y retorno20s en todo castillo. Llegada final24 frente al antiguo100 y rango85 de Seal. Se corrigieron exactamente5bits E/W en5bytes de23_22, escalera norte y145064 x117528..117960; alturas/capas/otras colisiones conservadas, NPC artefacto original, sin bypass ni teleport de conquista. Original privado respaldado. 543 checks nativos PASS, incluyendo líder camina desde sala por pasillo/escalera hasta inicio real deSeal (sala despejada/salud restaurada para aislar navegación); escolta ataca agresor y mantiene defensor que se aleja másde400. Regresión órdenes aliadas/puertas/HQ/buffs/Amber/guardianes PASS. Snapshots conservan Hellkevin/inventario,clanes/rep/skills,Giran/fecha/owner y382guardias;19offline80. Core/cliente unchanged. Runtime/source/cloud/continuidad37 sincronizados,sincommit/push. Siege completo bajo combate/balance y muroexterior exacto(/loc) pendientes. No reejecutar instaladores históricos.
Documento E:\l2-local\GIRAN-ASALTO-POR-ETAPAS-V6.md; pruebas research/giran-assault-v6; backups/giran-assault-v6-2026-10-11.

# Giran V7 completado — 11/10/2026
E:\l2-local. Ares y Nyx usaban SiegeGuardAI cuyo scan era alcance físico40 y sin Spawn no tenían retorno/patrulla. IA propia con eventos/formulas/casts/movimiento nativos: Ares patio/entradas, Nyx sala/pasillo/escalera norte/artefacto; patrulla en paz, escaneo1200 durante siege, prioridad Seal/agresor defensores, retención1600 y leash2000 del puesto. Dueño/defensores/neutrales protegidos, summons resuelven dueño, corpse60s/room10s. Sala superior aislada (BFS990 celdas, sin salida): transporte interno limitado a la resurrección hacia sala inferior, luego retorno caminando; Ares se queda en puesto interior cuando puertas cerradas, sin atravesarlas. 1909 comprobaciones PASS con ciclo completo ambas rutas, daño sin provocación/skills, dueño protegido, prioridad Seal, summon, límites y retorno sala; regresión V6 incluida. Snapshots preservan humano/inventario,clanes/rep/skills,castillo/owner/fecha,guardias;19pilotos offline80. Core/estadísticas/geo V6 unchanged. Runtime/source/cloud/continuidad38 W10/W11 sincronizados; no commit/push. Balance siege completo requiere juego. No reejecutar instaladores históricos.
Documento GIRAN-GUARDIANES-PATRULLA-V7.md; research/giran-guardians-v7 y backups/giran-guardians-v7-2026-10-11.

# Giran V8 completado — 11/10/2026
E:\l2-local. Los líderes antes iban al artefacto antes de evaluar amenazas y la escolta dejaba de pelear al superar formación. Cada piloto detecta defensores/guardias, agresores de party y conquistadores; combate/persecución local con límites/LOS/PvP nativos. Líder pelea ante amenaza inmediata y espera escolta en combate antes de conquistar; Seal nativo180s, no item,50MP. Treguas bilaterales20s entre atacantes bajo presión defensora; renovables, caducan sin presión, se rompen al iniciar conquista/agredir al socio con bloqueo15s. Clanes/alianzas/órdenes no cambian; los atacantes siguen enemigos legales, sin inmunidad. Evitan skills de área cerca de socios. Panel .giran muestra intención/treguas. Mirellas50010 y Thiago50008 adicionales en trono, menús nativos, suelo caminable, originales Coliseo preservados. 1439 comprobaciones nativas PASS: daño real de16 atacantes/4 captores y escoltas lejos del capitán, treguas/8roles/captura/traición/expiración20s real, espera escolta y Seal, servicios; regresión V6 (puertas,4HQ300gemas,recorrido hastaSeal,revive/buffs/Amber), guardianes V7/core/geo intactos. Fixtures aislados, sin cargar Hellkevin ni completar conquista; balance completo requiere jugar. Snapshot humano/inventario,clanes/skills/rep/blood,castillo/owner/fecha,382guardias idénticos;19pilotos offline80 y4rivales registrados. Runtime/source/cloud/continuidad39 W10/W11/Nexus guardados; sin commit/push. No reejecutar instaladores históricos.
Documento GIRAN-IA-TREGUAS-Y-SERVICIOS-V8.md; research/giran-tactics-v8 y backups/giran-tactics-v8-2026-10-11.

# GameServer: 8 GiB — 11/10/2026
E:\l2-local. Kevin autorizó subir límite a8GB. Start-L2Local.ps1 ahora usa8192MiB por defecto con al menos24GiB RAM total utilizable; equipos menores retienen2/3/4GiB automático; -GameHeapMb2048..8192 sigue disponible. Se conserva inicio512MiB/ZGC/pool32buffers; no cambia core/IA/cliente/19bots. Reiniciado sin L2 ni conexiones, arranque normal sin verificadores, jcmd confirma InitialHeapSize536870912 / MaxHeapSize8589934592; primer heap usado1076MiB. Puerto7777/login OK. No implica capacidad medida de más bots. Respaldo backups/game-heap8-2026-10-11, doc GAMESERVER-MEMORIA-8GB.md, cloud ops/windows y docs, continuidad40 W10/W11. Sin commit/push. No reejecutar instaladores históricos de heap4GB.
# Modelos L2: visor y catálogo base — 11/10/2026
E:\l2-local. Kevin quiere explorar apariencias nativas para bots/NPC. UE Viewer/UModel ya instalado en research/amber-l2/tools/umodel.exe. Nuevo VER-MODELOS-L2.cmd ofrece6 paquetes originalesNPC/monstruos y7 paquetes razas/equipo; research/model-catalog/Open-L2Models.ps1 resuelve ruta portátil ../l2, abre visor interactivo, sin tocar cliente/server ni reiniciar. Lectura nativa de una malla en cada uno de6 paquetesPASS; syntaxPSPASS, no se inspeccionó GUI. inventory.py genera modelos-npc.csv e inventory.json, base histórica npcgrp6519filas=>550mallas no vacías (incluye estructuras/objetos; excluye customs/razas). Paquetes actuales634 SkeletalMesh (239+85+74+179+30+27), no equivalen634especies únicas. XMLserver6590templates=6519base+71custom. Más de30mil unidades/spawns no significa30milcuerpos diferentes. Nombres/IDs/texturas/tipos asociados conservados en JSON/CSV. Visor gira/zoom/animaciones/capturas; algunos materiales/texturas npcgrp y piezasraciales requieren combinar/validar; galería de miniaturas todavía no generada. AparienciaNPC/summon reutilizable aparte stats/IA; botsPlayer necesitan comprobar capaapariencia/transformación/animaciones, no basta npcID. README, continuidadW10/W11, cloudresearch/opslocal y Nexusportable guardados. Sin commit/push. Fuente oficial https://www.gildor.org/en/projects/umodel.

# Galería L2 y visor reparado — 12/10/2026
Proyecto E:\l2-local. Kevin pidió generar galería y corregir el menú que se cerraba. Causa reproducida: SDL2.dll ausente; UModel podía listar/exportar pero fallaba al crear ventana. Se agregó DLL x86 del repo oficial gildor2/UEViewer/libs/SDL2/x86 (hash en research/model-catalog/verification.json). Open-L2Models.ps1 ahora comprueba dependencia, registra errores y verifica inicio; CMD conserva ventana/mensajes. Ventana UE Viewer build1590 abierta y respondiendo, también mediante API de galería.
GALERIA-MODELOS-L2.cmd abre app local en 127.0.0.1:32280, Node portable y Three.js r160 incluidos. Funciones: búsqueda por nombre/ID/malla, filtros, miniaturas, WebGL giratorio, abrir malla en visor con animaciones, favoritos/notas, exportar selección JSON, elegir/copy ID de referencia. Favoritos son del navegador; exportarlos para otra PC. Sin Internet/Blender para uso, rutas portátiles ../l2. No toca GameServer, cliente, stats ni IA; no hay reinicios.
641 referencias/objetos deduplicados: 640 glTF + PNG 384x420; enlaces de bin/texturas PASS, ninguna imagen uniforme vacía. LineageMonsters.alchemic_box_m00 solo está referenciado en catálogo base y falta en cliente; recurso marcado no disponible. 72 vistas con algún material sin textura (muchas mallas sin NPC asociado); fichas lo indican. Poses base/materiales representativos, sin partículas/reflejos ni animación en WebGL. NPC de referencia no cambia colores automáticamente. Shader alpha especular corrigió 129 cuerpos que aparecían recortados. Capturas de Chrome headless aislado validan grilla, WebGL Gremlin y búsqueda ID29020=>Baium. API origen inválido403/modelo inválido400/modelo válido200. UI native helper no disponible; validación de ventana por proceso, no captura nativa.
Código y todos los recursos para usar están en research/model-catalog del disco portátil; Blender3.5.1 D:/BlenderVersions solo generó miniaturas. Cloud-repo guarda código/metadata/vendor, sin commit/push; recursos generados y SDL binario permanecen en E, no subidos. Respaldos accesos anteriores en backups/model-gallery-2026-10-12. README y continuidad W10/W11, Nexus central y portable actualizados. Usar galería para elegir próximos NPC/summons; bots Player requieren revisar capa visual/animaciones.

# Amber: comparación visual — 12/10/2026
E:\l2-local. Usuario nota integración visual insuficiente (texturas/shaders/luz). Se descifró npcgrp actual solo para lectura:59001=>L2AmberNPCv5.AmberNPC (servidor902500),59002=>L2AmberArcherV2.AmberNPC (servidor902501). Ambos52153tri/76huesos,2atlas2048². Dump real: cuerpo/ropa Diffuse=SelfIllumination misma textura, máscaraNone, Specular/SpecularityMaskNone, maskedAlpha128/ZWrite/TwoSided. V4 había autoiluminado ambos para corregir ropa muy oscura. No cambia paquetes del cliente ni server.
Añadidas 2 entradas Personalizados: galería643 registros/642miniaturas. Comparar en http://127.0.0.1:32280/comparar.html desde GALERIA-MODELOS-L2.cmd. Tres vistas giratorias: actual aproximado unlit, prueba difusa o mezcla20% aproximada, NPC nativo seleccionable; luz estudio/oscura. Referencia Katerina1974tri/78huesos/texturas512²×2 y256²×2. Simulación no equivalencia exacta UE2; sin cambios ingame. Próximo ajuste sugerido: reducir/máscara selfillum, diferenciar superficies, luego tonos/detalles; LoD/compresión separado. Chrome headless propio con CDP esperó carga completa: estudio/oscuro/difusa-oscura PASS y capturas *-verified.png, sin JS excepciones. Capturas previas con tiempo virtual fueron prematuras/incompletas y no sirven como prueba.
Auditoría/hashes/dumps/prototipos/capturas en research/model-catalog/amber-comparison; AMBER-INTEGRACION-VISUAL-COMPARATIVA.md. HashUKXdespués=antes;642assets/thumbs/enlacesPASS. Builder preserva custom entries y soporta texturas de UKX además de UTX. Código/metadata en cloud local, recursos y continuidad W10/W11 en portátil, Nexus central y copia portable. Sin commit/push/reinicio GameServer. No ejecutar finalizadores históricos con conteos640 como si fueran el estado actual.

# Amber materiales V1 instalada — 12/10/2026

Proyecto E:\l2-local. Usuario autorizó retoques. Reducida autoiluminación con máscaras por superficie y reflejo nativo TexEnvMap en metal/pelo/ojos. Dos UKX actuales conservan nombre y solo cambian dos shaders cada uno; malla/texturas artísticas/animaciones idénticas. Nuevo AmberSurfaceV1.utx512²×4, wrapper121/CRC/nombre/roundtrip nativoPASS. Lectura nativa y export PSK exactoPASS; preview3casos navegadorPASS. Galería actual643/642. Instalado cliente cerrado, sin restart GS/IA/stats/DAT. Falta valoración ingame; no afirmar validación visual real UE2. Doc AMBER-INTEGRACION-VISUAL-V1.md y stage research/amber-l2/exports/surface-v1, backup E:\l2-local\backups\amber-surface-v1-20261012-024347 con Restore.ps1 protegido. Comparador localhost32280/comparar.html antes/V1/nativo; glTF no reproduce reflejos TexEnvMap. No ejecutar finalizadores/linkers históricos sobre estado actual. Continuidad portable W10/W11, central K y cloud local (sincommitpush).

## Cierre cámara y Nexus TV — 16/10/2026

Kevin pide guardar bitácora y continuar en otra sesión. Documento principal: `E:\l2-local\BITACORA-NEXUS-TV-Y-CAMARA-20261016.md`; guía `nexus-tv/GUIA-1080P-Y-CONTROL.md`. Cámara online con vuelo nativo confirmada; televisor3D de Giran con cámara/video local/YouTube confirmado por Kevin. Última ampliación instalada: controladorv3, receptor dinámico, modeloPanel4, perfil1080p preferido y4K experimental. Pruebas aisladas:1080p ~21–27FPS según fuente,4K real7.4FPS (no fluido). Nuevo `.tv`/`.televisor` solo GMlocal: compilado, API probada, carga al siguiente inicio de GameServer; pendiente confirmación visual del menú/modelo nuevo. Audio todavía Windows: OpenAL investigado, puente NO implementado. No reiniciar/abrir/cerrar clientes automáticamente; Kevin los prueba. Originalsystem-hud/cámara conservados; no commit/push. Estado detallado y respaldos en bitácora. Inbox complementario: `inbox/20261016-l2-tv-1080-remote.md`.

17/10/2026 Nexus TV v4 optimizada e instalada. Misma prueba aislada: local1080p30 23,13→28,59FPS/proceso37,48→20,56ms; YouTube16,8→22,2FPS salida/11,7→20 contenido (hd720). Todavía no30estables ni FPS de L2. BGRA/cadencia/auxiliares/status/backpressure mejorados, calidad conservada. Controles/equivalencia PASS, D3D9 patrón1080p180/180. Solo controlador reiniciado, clientes intactos. Finalcámara/fullhd/vol30/sinerror. Informe E:\l2-local\research\giran-screen\optimization-v4\INFORME.md; inbox/20261017-l2-tv-optimization-v4.md. Sincommit/push; pruebaGiran pendiente.


17/10/2026 Pantalla curva v5 construida/verificada y PREPARADA para próximo inicio. Cliente activo conserva plano; no se cerró/reabrió. Curva suave48/36.36grados y marco, mismo tamaño/raíz/posición,1392triángulos. Paquete UCC/UModel-game=l2 y checks PASS. Instalador conhash/respaldo/rollback/guardia abierto, aislado/idempotenciaPASS. Kevin debe cerrar solo Pantalla Giran y reabrir acceso para aplicar y confirmar visualmente. Informe E:\l2-local\research\giran-screen\curved-v5\README.md; inbox/20261017-l2-tv-curved-v5.md. Sincommit/push.


17/10 Curva v5 confirmada en captura por Kevin; pidió más. V6 preparada con avance72 (antes48), arco53.98, mismo tamaño/ubicación/1392triángulos. UCC/pose/UV/marker/UModel e instalación aisladaPASS. Staging actualizado; aplica al cerrar/reabrir Kevin Pantalla Giran. Clienteabierto conserva v5, no se cerró/abrió. Informe research/giran-screen/curved-v6/README.md; inbox/20261017-l2-tv-curved-v6.md. Sincommit/push.



# L2 Lab: cierre del editor y traslado W11 ? 17/10/2026

Origen `E:\l2-local` (letra puede cambiar en W11). Leer bit?cora ra?z `BITACORA-EDITOR-ESCENAS-20261017.md` y `CONTINUIDAD-W11/EDITOR-ESCENAS-20261017.md`. Editor visual glTF/JSON en research/scene-editor, lanzador 19. No exporta aún a .unr/juego. Paneles Chara Studio, jerarquías/piezas/grupos/fusión, texturas/capas, cámaras, panel ajustable y desbloquear selección/rama/todo implementados y probados.

Descargas p?blicas 2K pausadas: 2072/4724 indexadas; reanudar con 20, Python3.10+ y Pillow. Mantener mapas/archivos originales existentes. Respaldo código/proyectos: backups/editor-handoff-20261017-214227. Borrador del navegador NO guardado por agente: Kevin debe pulsar Guardar versión antes del traslado. No asumir que ?ltimos JSON QA son su escena. Servidor editor sigue abierto para ese guardado; cerrar después con 22. Juego/DB no detenidos autom?ticamente. Academy/Hellgames intactos. W11 Computer Use todavía pendiente de validar.

## 2026-10-28 - Bitacora consolidada de niebla del mapa
Kevin pidio guardar continuidad. Documento principal: E:\l2-local\BITACORA-NIEBLA-MAPA-20261028.md. Conserva diagnostico REA V7/V8, tirones CPU112-117ms, V9 circular con worker/actualizacion parcial, pruebas, respaldo/restore y pendientes. V9 instalada; SHA256 real verificado a93edc738847000f5eed39ab44fcba0ca2ab49fd36392efbbac64540fd524b4d. Falta confirmacion visual y medicion real V9; max3.388ms fue HAL aislado. Inbox: 20261028-l2-bitacora-niebla-mapa.md. Solo documentacion, sin cambios al juego.

## 28/10/2026 — Continuidad de diseño, comunidad y aventuras

Kevin cambiará de PC. Leer E:\l2-local\BITACORA-DISENO-COMUNIDAD-AVENTURAS-20261028.md (letra de unidad adaptable); copia completa en inbox/20261028-lineage2-comunidad-aventuras.md y CONTINUIDAD-W10/W11. Conversación 27–28/10: rendimiento real de bots vs humanos; Sudamérica y Ares (identidad Ares/GameAr pendiente, sin cifra verificada); coordinador custom no equivale a GameServer; escuadrones4 y concentración distribuida; estándar base+3 con salas/eventos clase única/base+1; aventuras y festivales ocasionales inspirados en video Project Gorgon y probable The Endless Forest; fortaleza caminante tripulable ExternalAssets.ext3_6b9626c3ec83bc; torretas; impuestos/estancias en adena y obras con tesorería. 55 paquetes nuevos (~2,52GiB) en descarga de assets comparados con inventario de Tanda3: no convertidos ni añadidos por esta sesión. Favoritos del visor son localStorage por PC, no exportados aquí. Todo el nuevo gameplay es propuesta, no instalado. Sin cambios de configuración, tests de carga, reinicios, commit/push ni backup de DB en esta sesión. No confundir cierre documental con migración completa. Archivos de video: research/video-project-gorgon-20261027 (metadata/transcripción, no análisis visual plano a plano).
