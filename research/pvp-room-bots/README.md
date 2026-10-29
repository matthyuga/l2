# Bots de prueba para las cuatro salas PvP

15/10/2026. Integracion instalada en scripts runtime/source/overlay y comprobada en instancias de prueba. **No se reinicio el servidor ni se reemplazo el lobby activo durante la sesion de animaciones.** El control de bots estara disponible despues del proximo arranque normal que habilite las cuatro salas. Los bots siempre comienzan apagados.

## Uso con personaje GM

```
.salas bots iniciar libre 6 empate
.salas bots iniciar equipos 6 duplicado
.salas bots iniciar tres 6 parcial
.salas bots iniciar arena 4 tardio
.salas bots estado
.salas bots parar libre
.salas bots parar todas
```

Modos: `libre`, `equipos`, `tres`, `arena`. Entre 2 y 12 bots por modo (maximo 48). Solo un grupo por modo; detenerlo antes de iniciar otro perfil. No se exige cambiar la duracion de la ronda para usar bots. La votacion conserva sus 5 minutos de antelacion y ventana de 60 segundos.

Perfiles:

| Perfil | Comportamiento |
|---|---|
| `mayoria` | Todos votan por el siguiente mapa de la lista respecto al actual. |
| `empate` | Reparto igual entre los otros dos mapas; si son impares el ultimo se abstiene. |
| `parcial` | La mitad, redondeada hacia arriba, vota; el resto se abstiene. Es el valor predeterminado. |
| `abstencion` | Ninguno vota. Para observar el sorteo sin votos tampoco deben votar otros participantes. |
| `duplicado` | Cada bot emite un voto valido e intenta otro; el segundo debe rechazarse. |
| `tardio` | Esperan al cierre e intentan votar; deben ser rechazados. |

Si hay votos humanos, pueden cambiar el ganador o romper un empate preparado. Los contadores de `estado` muestran votos aceptados, rechazados, abstenciones, ordenes de ataque y reapariciones acumuladas del grupo. Retirar bots no borra sus votos ni sus bajas de la ronda, siguiendo las mismas reglas de salida de un participante normal.

## Combate y ciclo de vida

Son Player transitorios de laboratorio, identificados como HGTest..., nivel 80, humanos de combate cuerpo a cuerpo basico y sin equipamiento ni cuentas/personajes persistentes nuevos. No son una simulacion completa de clases, builds o toma de decisiones humana.

Entran por el mismo controlador que los jugadores, reciben equipo/flag y cambian de mapa con su sala. La IA solo elige bots propios vivos del mismo grupo e instancia y respeta RoomCombatRules: Libre/Arena contra todos, modos por equipo contra enemigos. **Los jugadores reales quedan fuera de la seleccion automatica de blancos de esta primera version.** Los bots no aparecen previamente en Giran ni recorren otras instancias.

Los votos pasan por `PvpRoundRooms.onCommand`, igual que la ventana del jugador; el modulo no escribe directamente el conteo ni el resultado. Los intentos se escalonan entre 2 y 41 segundos despues de la apertura. Cada nueva ronda renueva el token y permite un nuevo voto.

Solo los bots de este modulo reviven automaticamente diez segundos despues de detectar su muerte, recuperan sus propios recursos y vuelven a un spawn valido de su equipo. No se cura ni revive a personajes reales y no se concede inmunidad. `parar` cancela acciones y retira bots, listeners, visitas, membresia de combate y flag; si un bot abandona inesperadamente su sala, se retira su grupo en vez de permitirle recorrer otra instancia.

La instrumentacion habitual del servidor puede registrar combate/telemetria; no se afirma ausencia total de escrituras a DB. El modulo no crea cuentas, equipo, premios o personajes persistentes.

## Pruebas y limites

`verification.txt` contiene PASS para cuatro instancias distintas de las de clientes conectados, combate real mediante IA nativa y reduccion de HP/CP, empate 3/3, duplicados rechazados (6), abstenciones, tardios rechazados (4), sorteo sin votos, cambio de mapa, voto en ronda siguiente, respawn exclusivo de bots, mayoria/abstencion total, control GM y retirada completa.

Se uso un controlador aislado sin NPC, registro de comandos ni scheduler; el banco avanzo un reloj propio para comprobar ventanas sin esperar media hora. No cambio el reloj de las salas de produccion ni uso comandos de movimiento sobre personas conectadas. La copia del controlador del banco se cargo en un classloader separado de los scripts activos.

La primera prueba detecto que un Player nunca aparecido debia registrarse en World antes de su teleport; se corrigio el alta sin generar un spawn publico. Un ensayo de respawn no habia dejado pasar el tick de observacion de muerte; ese fallo del banco se conserva en `verification-respawn-fixture.txt`. La version final respeta primero ese tick y luego comprueba el plazo de diez segundos.

`final-runtime-audit.json`: cero bots residuales, cero propietarios de flag de bots, cero miembros residuales de combate y lobby anterior aun activo. `final-installation-audit.json`: hashes de seis archivos nuevos/modificados y del resto de la etapa anterior verificados. Compilacion de scripts del proximo arranque completada contra el core pendiente.

Quedan pendientes el arranque en frio y la revision visual junto con las cuatro salas. No se tocaron paquetes del cliente, animaciones ni core en esta etapa; no se inicio automaticamente ningun grupo en la sesion actual.

## Respaldo

`installation.json` registra los seis archivos y el respaldo `E:/l2-local/backups/pvp-room-bots-20261015-133147`.

Con GameServer detenido: `python E:/l2-local/research/pvp-room-bots/restore.py`. Verifica hashes y devuelve el controlador anterior de cuatro salas. Para deshacer mas etapas: bots, rondas, sincronizacion de posicion y auto-flag, en ese orden. El verificador original de rondas detectara deliberadamente que su host fue ampliado; el verificador de esta etapa reconoce esos tres reemplazos y comprueba los demas archivos.
