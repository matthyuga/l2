# Bots de salas con perfiles nativos del siege

15/10/2026. Instalados y activos: seis bots por cada una de las cuatro salas (24). Se reemplazo el controlador basico en caliente y se sincronizaron nueve fuentes/scripts en runtime, source y overlay. No se modificaron cliente, animaciones ni core. El servidor estaba detenido al comenzar y se inicio con el lanzador normal; PID observado 27412.

## Perfiles

Se reservan temporalmente personajes de laboratorio verificados y desconectados del roster NormalNpcRoster/RealHumanPilots. No se crean clones ni se trasladan actores que otro laboratorio ya tenga cargados. Se excluyen clientes reales y perfiles sin nivel80, tres subclases o acceso normal. Reserva SQL online=2 y comprobacion World antes de cargarlos.

Se conservan las clases activas guardadas, habilidades, equipo y clan nativos. La seleccion mezcla perfiles con clan y sin clan cuando hay disponibilidad; la muestra activa contiene 17 con clan, 7 sin clan y 17 clases distintas. No se modifica la pertenencia a los clanes. Mientras estan reservados no estan disponibles para iniciar simultaneamente otra prueba del siege con esos mismos personajes.

`PvpSiegeBrain` adapta el acercamiento por etapas, recuperacion de atasco y casteo del controlador SiegeSquadBrain a las salas. No importa objetivos de castillo, banderas ni conquista. Usa habilidades conocidas, MP, cooldowns, condiciones y geodata; no aplica daño artificial ni teletransporta para simular movimiento. Mantiene ataques nativos sin reiniciar la intencion continuamente. Los ataques automaticos siguen dirigidos solo a otros bots propios de la misma sala, respetando equipos. No elige jugadores reales como blancos.

Se forman parties aleatorias de 2 a 4 entre bots del mismo equipo; puede quedar un bot solo si el numero no alcanza. En Libre/Arena se priorizan rivales fuera de la party, aunque las reglas siguen permitiendo atacar a sus miembros. Al cambiar de ronda se reagrupan segun los equipos nuevos. El filtro de pertenencia impide quitar o modificar la party de jugadores reales.

Los bots conservan los seis perfiles de votacion y comandos anteriores. Los actuales usan `parcial`: mitad vota, mitad se abstiene. Reaparicion de bots a los10segundos, con sus propios recursos y buffs; no cura/revive personas reales.

## Uso y retirada

```
.salas bots estado
.salas bots parar equipos
.salas bots parar todas
.salas bots iniciar equipos 6 parcial
```

Modos: libre/equipos/tres/arena. Perfiles: mayoria/empate/parcial/abstencion/duplicado/tardio. Los mismos permisos GM y limite2..12 por sala. El arranque normal no inicia bots automaticamente; los24 actuales se iniciaron expresamente en esta sesion.

**Detener los bots antes de cerrar el servidor o iniciar una prueba del siege.** La retirada devuelve los personajes a su posicion/instancia y titulo previos, experiencia, nivel, conteos PvP/PK/karma, recursos, cooldowns y cantidades de items registrados al reservarlos. Restaura efectos anteriores que aun no vencieron; esta reconstruccion no certifica identica procedencia/caster ni todos los detalles internos de cada efecto. El uso de municion/consumibles queda compensado por cantidad. Las clases/subclases/habilidades aprendidas y clanes no se editan.

Un cierre forzado impide esa restauracion normal; no se incorporo un mecanismo persistente de recuperacion tras crash. No usar estos perfiles prestados como bots permanentes sin esa siguiente mejora. El combate genera telemetria normal y escrituras de laboratorio.

## Evidencia

- `verification.txt`:6/6 actores de prueba caminaron mas100unidades bajo movimiento nativo; tres subclases, mas80habilidades y arma cargados; mezcla clan/sin clan, variedad de clases y parties del mismo equipo. Al retirarlos, fingerprint SQL de clases, subclases, habilidades, clan y cantidades de equipo identico al inicial.
- `vote-verification.txt`: empate2/2, duplicados/tardios rechazados, abstenciones, cambio mapa, voto siguiente ronda y parties compatibles tras rebalanceo. Actores del banco liberados.
- `live-audit.json`:24bots,4salas,17conclan/7sinclan,17clases,9parties. Primera muestra6movieron/17HP-CPcambiaron en6s; muestra posterior2movieron/15HP-CPcambiaron, con los demas atacando/casteando/muertos o parados. No se afirma que todos caminen continuamente.
- `live-status.txt`:ordenes de combate y reapariciones reales en las cuatro salas.
- `lobby-registry-audit.txt`:se restauro el registro del lobby real y sus callbacks NPC despues de detectar que el constructor Script del banco sustituia el registro por nombre aun con live=false. El handler activo y ScriptManager vuelven a apuntar al mismo lobby. No repetir ese banco sin preservar/restaurar el registro.

El test de votos adicional tardo varios minutos mientras se cargaban otros16perfiles y competia con la telemetria de24bots. Se guardo diagnostico de threads/DB; no se altero el pool ni se silencio telemetria. Evitar pruebas adicionales masivas mientras se usa el cliente.

No se establecio la causa exacta del estancamiento visual de los bots basicos iniciales; la prueba anterior solo demostraba daño a distancia cercana. Esta etapa incorpora verificacion expresa de desplazamiento y perfiles completos, sin afirmar una causa no probada.

## Archivos y respaldo

`installation.json`:nueve archivos, respaldo `E:/l2-local/backups/pvp-siege-bots-20261015-145524`. Helpers nuevos PvpSiegeRoster/PvpSiegeBrain; PvpRoomBots conserva su estructura para redefinicion en vivo. Compilacion del conjunto de scripts aprobada.

Rollback: primero `.salas bots parar todas`, luego detener GameServer y ejecutar `python E:/l2-local/research/pvp-siege-bots/restore.py`. Verifica hashes y restaura el controlador basico anterior. Orden completo: siege-bots, UI, bots basicos, rondas, sincronizacion, auto-flag.
