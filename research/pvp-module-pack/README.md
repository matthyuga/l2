# HELLGAMES — selección de módulos PvP

Preparado el 15/10/2026. Recursos de código para revisión/adaptación; NO es un pack listo para instalar. No se modificó runtime, core, configuración, cliente o base de datos en esta preparación. No se ejecutó código descargado.

## Base local comprobada

`local-base/` contiene copias de referencia del estado actual:

| Componente | Función comprobada en código | Estado |
|---|---|---|
| FlagPvPZone.java | Activa flag al entrar; lo pone a cero al salir; trata muerte como salida y revive como ingreso | Ya existe en nuestro source; no se configuró una zona nueva |
| ArenaZone.java | Zona de combate mediante ZoneId.PVP | Ya existe en nuestro source |
| ZoneNPoly.java | Contorno poligonal | Ya existe en nuestro source |
| PvpFlagTaskManager.java | Expiración normal del flag de jugadores | Ya existe; debe coordinarse con un flag forzado por sala |
| elven/PvpRooms.java | Lobby, perímetro, salida vulnerable de 4 s, retorno interior y salida a Giran | Implementado en la sesión anterior |
| elven/PvpFlaggingStopTask.java | Tarea de flag de NPCs FakePlayers | Ya incorporada; NO es auto-flag para jugadores |
| elven/ElvenPvpRoom.java | IA de los nueve combatientes existentes | Ya activo; sin curación al entrar/observar revive |

**Distinción clave:** el flag violeta del jugador y la condición de zona PvP son mecanismos diferentes. La instancia 3051 ya permite PvP; esto no demuestra que se haya activado flag violeta permanente en todos los jugadores ni que el conteo/recompensas de kills tengan el comportamiento deseado.

## Módulo externo adquirido como referencia

Proyecto: L2jOrion Interlude C6.

Repositorio: https://github.com/Hl4p3x/L2jOrion_Interlude_C6

Árbol fijado: `0daf83956edc9402dda235cd69f97d1d13cb82a7`.

Se descargaron seis archivos fuente/configuración/documentación públicos (47.508 bytes). Las URLs exactas y hashes están en `downloads.json`; `external/orion/` conserva sus rutas. Encabezados de licencia preservados. No se adquirió el pack completo ni se validó su compilación/ejecución.

- `RandomZoneTaskManager.java`: reloj, avisos, selección aleatoria de zona, traslado de participantes y soporte opcional de vallas.
- `L2RandomZone.java`: flag automático y estado de zona; contornos y puntos de aparición configurables.
- `randomPvpZone.ini`: activación, restricciones de clases y aislamiento.
- `RandomZone.xml`: siete zonas de ejemplo: Hot Springs, Castle, Lake, Valley Lords, Talking Harbor, Frozen Land y Sea of Spores. Sus tiempos de ejemplo son 2700 s (45 min).
- `PvPZone.xml`: otras delimitaciones de ejemplo.
- `README.md`: documentación del proyecto.

**No incluye votación del próximo mapa** en los dos controladores revisados. La selección llama a Rnd y es aleatoria. Tampoco confirma qué pack utilizó L2Damage. Los ejemplos RandomZone.xml descargados no contienen Elven ni la playa de Primeval; sus límites tendrán que prepararse y comprobarse en nuestro mapa.

## Otra fuente localizada

Publicación para Mobius Interlude: https://l2jmobius.org/forum/index.php?topic=11872.0 — “Pvp Flag Zone”, 19/03/2024.

El índice de búsqueda muestra un parche con FlagZone, zonas XML y ejemplo Primeval. La apertura directa devolvió 403; NO se descargó o auditó el parche completo. El fragmento indexado aplica Noblesse al entrar y limpia el flag al salir; por eso no debe importarse tal cual para HELLGAMES. Nuestro core ya tiene FlagPvPZone, con nombres de paquetes modernos `entity` en lugar de los `model` de ese parche.

## Selección para adaptación

1. Usar la infraestructura Mobius ya presente para flag, geometría e instancias.
2. Tomar el módulo Orion como referencia para configuración de mapas, reloj y anuncios. No copiar las dependencias l2jorion.* ni reemplazar el core.
3. Añadir el módulo de votación de mapa al finalizar el tiempo, siguiendo la intención del usuario. No confundirlo con votereward de tops externos. Aún no se identificó un módulo de votación descargable y compatible verificado.
4. Mantener la franja de salida vulnerable durante cuatro segundos, sin curaciones ni limpieza de efectos.
5. Preparar Elven y la playa de Primeval con polígonos, suelo y apariciones verificados. No usar el XML de isla entera como si fuera la playa.

Puntos de compatibilidad que deben resolverse al implementar: el flag nativo se limpia inmediatamente al salir de FlagPvPZone; el reloj normal puede expirar mientras el jugador permanece en zona; la franja debe conservar las reglas PvP hasta terminar la salida; salir no debe borrar un flag de combate previo; un cambio de mapa no debe curar o resetear cooldowns. Revisar además conteo de kills de arena versus kills PvP, si se desean recompensas.

## Alcance actual

Completado: inventario local, descarga fijada de módulo Orion y selección técnica de componentes. Pendiente: adaptación/compilación de módulos externos, auto-flag específico de salas, reloj de partida, votación, segundo mapa y pruebas ingame. No se presenta este dossier como integración funcional de esos pendientes.
