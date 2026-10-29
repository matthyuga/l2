# Agite grupal 4vs4 — Hellsing / Holly / Sacred

Modulo nuevo `custom/GroupAgite`, separado de Amber, .ia y .arena.
No cambia core, cliente, armas, clases, dyes ni reglas raciales.

## Equipos

| Clan | Lider | Reclutas |
|---|---|---|
| Hellsing | Hellkevin | Vaelkor, Noctis, Selene |
| Holly | Kaelis | Gorvak, Myrentha, Ignara |
| Sacred | Caelan | Arden, Zhurak, Morvain |

Los once bots son Players reales cargados desde los perfiles reservados
`ArenaNombre` de nivel80 y tres subs. Los perfiles NPC proxy se conservan;
desde el ajuste del 10/10 aparecen solo en su duelo .arena. El evento usa una instancia
privada del mismo mapa. Los siete pilotos originales tampoco se modifican.
La autoprueba reemplaza al usuario por ArenaAelira; no carga a Hellkevin.

## Creacion y uso

Con Hellkevin GM, entrar al suelo PvP del Coliseo, sin party/combate y sin
invulnerabilidad. Ejecutar:

```
.agite preparar
.agite iniciar
.agite estado
.agite cancelar
```

`preparar` crea los tres clanes mediante ClanTable del motor y asigna sus
integrantes, solo si el nombre/lider/membresias son compatibles. NO reemplaza
clanes ajenos ni retira personajes de otros clanes. No aumenta el nivel de clan
ni concede skills de clan. Clanes/membresias persisten; las parties son del evento.
Si se produce un fallo parcial de creacion, no se borran automaticamente clanes
ya creados; corregir la causa y volver a preparar. Comando solo Hellkevin GM.

## Rondas

- Hellsing vs Holly; Sacred espera tras la entrada norte en una instancia de
  espera separada. No puede participar ni recibir dano de la ronda activa.
- Veinte segundos de preparacion; luego se quita la invulnerabilidad de combate.
- Una ronda termina al morir simultaneamente los cuatro integrantes de un equipo.
  Summons no cuentan como jugadores. Mientras quede alguien vivo, puede revivir.
- Ganador suma1, permanece y enfrenta al que esperaba; perdedor pasa a esperar.
- Diez segundos de intermedio, seguido de nueva preparacion20s.
- Primer equipo con3puntos gana; hasta7rondas decisivas.
- DobleKO/limite6min son empate, sin puntos y mismo enfrentamiento. Tras tres
  empates se cancela por estancamiento; nunca se inventa un ganador.
- Limite de seguridad1hora; preparacion inicial sin iniciar caduca a5min.
- Desconexion/salida de instancia del usuario cancela y limpia el evento.

Entre rondas se reviven/restauran HP/CP/MP, buff externo del laboratorio y
reuse de skills para TODOS, incluido Hellkevin. Los bots reponen por ronda
50CP,30MP,10HP, shots/flechas/reactivos; usan handlers y condiciones reales.
No se equipa ni cambia la build de Hellkevin: si usa arma+16 contra bots+4,
eso sigue siendo una diferencia real; no se afirma balance competitivo.

## Ordenes y decisiones

```
.agite cubrir
.agite seguir
.agite asalto
.agite senuelo
```

Ordenes aplicadas a Hellsing; rivales usan cubrir. Seguir interrumpe ataques
previos y reagrupa; asalto prioriza ofensiva sin rutinas de apoyo a aliados;
senuelo hace avanzar/frontales con Aggression si la tienen y retirarse con HPbajo.
No fuerza a un jugador humano a cambiar target ni inventa Hate para PvP.

Formacion base: frente150unidades, soporte/healer180atras, separacion lateral.
Noctis pasa a mando si Hellkevin muere, luego Vaelkor y Selene. Rivales usan
el primer integrante vivo como reemplazo del lider.

Amenaza pondera distancia, impactos recientes contra el lider, casteo, HPbajo
y target del lider. Preocupacion por aliados pondera HP, dano recibido, lider
y healer; una vida critica puede superar la prioridad del lider.

Curas HP/CP, curas a summon, UD, control, cubics, resurreccion individual,
resurreccion masiva y ataques se solicitan SOLO si el Player conoce la skill,
hay MP/HP/reactivos, reuse, rango/LOS y condiciones normales. Masiva1254 se dirige
a un cadaver del clan, no a self: dos o mas muertos con cobertura, o tres muertos
y casterHP<30% amenazado. Casteo largo sigue siendo interrumpible.
Bots confirman la solicitud de resurreccion del motor; Hellkevin conserva su
confirmacion normal. No se reviven por codigo durante una ronda de combate.

Sacrificio tactico inicial significa intentar control/cobertura de un aliado
critico y exponerse al hacerlo, NO suicidarse a proposito ni transferir dano
artificial. Daguero intenta Mirage/Bluff/blows/destarget segun skills disponibles;
magos/control y otros frentes tienen listas iniciales ampliables, no todo su kit.
Summon enemigo se prioriza si bajoHP o TP, siempre que el lider no este critico
y no tenga dos enemigos cerca. Invocaciones limitadas a2 solicitudes por ronda.

## Observacion y limites

SQL: `lab_group_runs`, `lab_group_events`. Guarda ordenes, rondas/puntos, casts
aceptados/rechazados, items consumidos, dano real del evento y estado cada2s
de12Players: recursos/posicion/target/efectos/casteo/root/stun/silence, mas summon.
REQUEST_ACCEPTED no demuestra que la skill haya impactado. No causa exacta de
resist/cancel ni efectos mas breves que el muestreo. Cola4096, batches512,
perdidas reportadas; no prometer telemetria perfecta ni una vista nueva del panel.
Reutiliza mensajes de dano enemigo2204-2207 ya existentes; barra de target Player
por HUD del laboratorio y ventana de party normal. Sin parche nuevo del cliente.

Cancelacion/final limpia parties y bots, retira summons de bots, quita invul,
restaura ubicacion original y estado offline de los perfiles. Clanes se conservan.
Party no se restaura porque preparar exige que el usuario no tenga party previa.
Los buffs/reuse/recursos del usuario se resetearon para las rondas: no se promete
restaurar su estado de combate anterior, solo posicion y salida segura.

## Pruebas

Compilacion Java contra core instalado y GroupPolicyCheck:291checks PASS,
incluye todas ramas de rotacion, campeon3puntos y cota7rondas decisivas.
GroupGeoCheck:12 comprobaciones de suelo/NSWE PASS (ocho puestos de combate
y cuatro de espera). Las primeras posiciones de combate demasiado alejadas
caian sobre una estructura elevada; se corrigieron a separacion900 unidades
entre lideres dentro del suelo verificado. No equivale a validar LOS/puertas
en vivo ni a verificar las cuatro rutas de espera completas.
Autoprueba aislada opt-in `-Dlab.agite.smoke=true`: 12Players, parties4,
combate normal, exige dano real, mas de10 solicitudes de skills y summon.
NO crea clanes ni modifica al usuario. Validacion de clanes/CP clan/resurreccion
masiva y conducta PvP completa requiere ensayo manual posterior.

Backup/compilacion: E:\l2-local\backups\group-agite-2026-10-09.
No commit/push automatico. No modificar ni reiniciar simultaneamente con
otra sesion que este probando Amber o el personaje.

Estado de entrega: modulo v1.1 compilado y sincronizado en runtime/source/overlay.
Autoprueba live del 09/10/2026: `GROUP_SMOKE PASS hits=188 casts=245 summon=true`.
Run1 finalizado SMOKE_PASS, dropped=0; los 19 perfiles Arena quedaron offline.
Se registraron 113 consumos de pociones, invocaciones y posiciones reales de
summons, y solicitudes de curacion y UD. Esto NO demuestra que cada skill
solicitada haya impactado ni valida aun todas las decisiones tacticas.
Los impactos reales se distinguen de solicitudes de ataque en event_name=DAMAGE
por detail_text con `:skill=`; las solicitudes contienen REQUEST_ACCEPTED.
Se corrigio la reserva de perfiles: estan repartidos entre telemetryarena1/2/3,
no exclusivamente en telemetryarena2. Log archivado en backup/smoke-pass.log.
Arranque normal posterior verificado: modulo v1.1 cargado, roster completo y
verify-arena-roster.js PASS19/19, copias7/7. Sin autoprueba activa.
Los tres clanes todavia NO se crearon: se crean con .agite preparar del usuario.
