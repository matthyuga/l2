# Salas PvP, rondas y votacion

**ACTIVADAS 15/10/2026:** servidor reiniciado ordenadamente a pedido del usuario, sin clientes conectados. Lobby PvpRoundRooms registrado, dos NPC, tres mapas y cuatro instancias PvP separadas comprobados (300000 a 300003). Bots apagados; UI nueva cargada. Evidencia: `research/pvp-room-ui/activation-audit.json`. Los pendientes de arranque mencionados abajo corresponden al estado previo; la inspeccion visual sigue pendiente.

Actualizacion UI: salida con dialogo nativo temporizado y votacion con barra grafica y confirmacion nativa del mapa elegido. Cancelar en el dialogo de salida devuelve al ultimo punto interior, por instruccion posterior del usuario. Reemplaza los segmentos de texto de esta version inicial; activacion al proximo arranque de las cuatro salas, sin tocar el cliente. Detalle y limitaciones visuales: `research/pvp-room-ui/README.md`.

Actualizacion: bots opcionales con combate y seis perfiles de votacion integrados. Control GM, apagados por defecto y disponibles al proximo arranque normal de las cuatro salas; sesion de animaciones preservada sin reinicio. Uso y evidencia en `research/pvp-room-bots/README.md`. Restaurar bots antes de restaurar esta etapa.

15/10/2026. Implementacion preparada y probada en instancias aisladas del servidor. **Las cuatro salas se habilitan en el proximo arranque normal con Start-L2Local.ps1.** No se reinicio la sesion abierta del usuario. El lobby activo sigue siendo el de Elven anterior hasta ese arranque.

## Modos independientes

Cada modo dispone de su propia instancia, reloj, votacion y puntaje. El NPC de Giran/muelle de Gludio mostrara Libre, Rojos vs Azules, Rojos vs Azules vs Verdes y Arena - Top 10.

- Libre: todos son oponentes, aun cuando compartan clan o party. Se conservan las parties y sus servicios normales.
- Dos equipos: asignacion al equipo menos numeroso; bajas de enemigos suman al equipo. Ataques, daño y efectos hostiles entre compañeros bloqueados, tambien con Ctrl y daño dirigido al summon. Los buffs y ayudas normales siguen sus reglas habituales.
- Tres equipos: mismas reglas, con verde como tercer equipo. Interlude solo ofrece identificadores nativos rojo/azul; verde usa titulo visible VERDES y colores de nombre/titulo, sujetos a confirmacion visual. No se agrego un identificador de equipo nativo inexistente.
- Arena: todos contra todos, sin limite de diez participantes. El cuadro muestra los mejores diez de la ronda por bajas, luego menos muertes y finalmente ID para un orden estable. No hay premios ni resets de habilidad añadidos.

El marcador superior informa modo, resultado y tiempo restante. `.salas top` abre el cuadro. La salida conserva sus cuatro segundos vulnerables, cancelacion al volver dentro y regreso a Giran. Cambiar de mapa no cura, limpia efectos ni revive. Un muerto permanece muerto y se traslada al nuevo mapa despues de su revival normal.

## Votacion

La ronda dura provisionalmente 30 minutos, configurable. Cuando faltan cinco minutos se abre un panel HTML para los participantes de esa sala. La votacion dura 60 segundos, con barra segmentada decreciente y segundos restantes. Despues quedan cuatro minutos de ronda con resultado visible. Se muestran los votos por mapa, tambien a quien no voto.

Un voto por personaje y ronda; no se cambia el voto emitido. Se rechazan votos de personas fuera de la sala, mapas inexistentes, paneles de una ronda anterior y votos tardios o duplicados/concurrentes. Desconectarse no permite votar nuevamente. No se implemento bloqueo de multicuenta por persona.

Gana el mapa con mas votos; los empates se sortean solo entre los empatados. Sin votos, se sortea entre los tres mapas habilitados. El mapa actual tambien puede ganar: no se pidio prohibir repeticiones. Cada modo vota por separado y conserva su modalidad.

El panel se puede cerrar y reabrir con `.salas votar`. La version inicial actualiza el HTML y marcador cada segundo; aspecto, suavidad de barra, colores y convivencia con otras ventanas siguen pendientes de inspeccion en el cliente. No se modificaron paquetes del cliente.

## Mapas y perimetros iniciales

Limites abiertos: una coordenada exactamente sobre el limite cuenta como exterior. Unidades del mundo L2; no equivalen a metros comprobados.

| Mapa | Limites X | Limites Y | Limites Z | Tamaño XY |
|---|---|---|---|---|
| Elven | 42000 a 49200 | 46600 a 54000 | -3800 a -2000 | 7200 x 7400 |
| Primeval Isle, sector costero | 4352 a 8448 | -22064 a -17968 | -3750 a -2700 | 4096 x 4096 |
| Valley of Saints | 83216 a 87312 | -85952 a -81856 | -4200 a -2200 | 4096 x 4096 |

Se instalaron las regiones de geodata 20_17 y 22_15, ausentes antes, desde una revision fija del [repositorio Orion](https://github.com/naustagic/L2JOrion_Interlude/tree/98e351766c569504210a24d96a9f39262f19b397/L2jOrion_Geodata/geodata). URLs, tamaños y hashes en `research/pvp-rounds/geodata-sources.json`.

La muestra a intervalos de 256 unidades encontro 221 puntos interiores conectados de 222 validos en Primeval y 225 de 225 en Saints; todos los puntos de aparicion elegidos pertenecen al componente conectado. Esto no certifica cada celda ni la apariencia de playa. Los limites y cuatro spawns de cada mapa son configurables y requieren recorrido visual posterior.

## Evidencia y operacion

`research/pvp-rounds/state-verification.txt`: tiempos, votos invalidos/duplicados/concurrentes, resultado, sorteo sin votos, balance de equipos, reingreso, puntaje, muertes duplicadas, Top 10 y estados independientes.

`research/pvp-rounds/server-verification-v4.txt`: clases reales en el servidor, instancias de prueba sin NPC y reloj acelerado. Daño real a enemigos y bloqueo a compañeros; debuffs; cambios Elven/Primeval/Saints; muerte y puntaje; salida/cancelacion; ataques de party y area en Libre; equipo verde; Arena aislada; cambio de mapa con personaje muerto sin resurreccion; cleanup offline. Hellkevin no fue desplazado por estas pruebas. No hubo pulsaciones automatizadas ni validacion del renderizado del cliente.

Regresion de Elven anterior: `research/elven-autoflag/verification.txt` PASS. Auditoria final de esta etapa: cero probes, cero propietarios de flag offline y cero miembros residuales de las reglas nuevas.

Configuracion: `server/game/config/Custom/PvpRooms.properties`. Las fuentes y los scripts estan sincronizados en source y overlay local, sin commit/push. El core nuevo queda en `server/pending-core-patches/20261015-pvp-rounds` para que el arranque normal aplique sus siete clases despues de la correccion de sincronizacion de posicion. No arrancar directamente GameServer.jar omitiendo ese paso.

Respaldo: `backups/pvp-rounds-20261015-115354`. Manifiesto con hashes: `research/pvp-rounds/installation.json`. Rollback con GameServer detenido: `python research/pvp-rounds/restore.py`; comprueba cambios posteriores y conserva la correccion de posicion anterior. Retiene la geodata para otros usos. Orden de restauracion completa: rondas, sincronizacion de posicion, auto-flag.
