# Elven: auto-flag integrado

Actualizacion con cliente conectado: corregido el regreso involuntario a Giran causado por paquetes de posicion anteriores al teleport. El usuario confirma permanencia en Elven con nombre violeta. Cruce del borde/cancelacion y salida a Giran en unos cuatro segundos comprobados con Hellkevin conectado; regresion de daño y conservacion de estado aprobada. La confirmacion visual del indicador sigue pendiente. Detalle y persistencia de la correccion: `research/elven-position-sync/README.md`. Restaurar esta nueva etapa antes de ejecutar la restauracion de auto-flag.

15/10/2026. Primera etapa instalada y comprobada en el servidor local activo.

Al entrar en Elven se activa el flag violeta. Se mantiene durante la visita, al cruzar el borde, durante los cuatro segundos de salida y al cancelar el retorno. La muerte cancela la salida como antes; la sala no revive ni cura al personaje. El controlador conserva el flag durante la visita y al observar el revive.

El regreso a Giran libera el flag de la sala. Si aún existe un plazo de combate previo vigente, se conserva hasta su vencimiento normal; no se reinicia ni se borra por salir. Las zonas nativas con flag y la sala tienen propietarios independientes para que una salida no borre la obligación de otra.

No se aplican Noblesse, curaciones, limpieza de efectos o resets de habilidades. No se adoptaron las restricciones de healers de Orion. Se conserva el menú de Giran/muelle de Gludio, el mapa Elven, su perímetro y la salida vulnerable ya implementados. El reloj de ronda, votos y nuevos mapas quedan para otra etapa.

## Comprobaciones ejecutadas

Compilación contra el JAR del proyecto: PASS. Arranque del servidor y registro del controlador actualizado: PASS.

Pruebas sobre los handlers activos y Player reales transitorios (sin crear cuentas ni personajes persistentes): PASS.

- Flag inmediato al entrar y conservación frente a vencimiento del temporizador, intento de limpieza y estado intermitente.
- Daño efectivo durante la cuenta de salida y después de cancelar; sin protección de teleport añadida.
- Sin salida a 3,8 segundos; regreso a Giran después de cuatro segundos; reingreso en la última posición interior.
- Conservación de HP/CP/MP, Wind Walk, Curse: Weakness y el timestamp de reutilización de prueba en las transiciones comprobadas.
- Plazo de combate previo conservado al entrar/salir; expiración normal fuera de la sala.
- Propietarios independientes e idempotentes, superposición de zonas nativas y sala/zona; 200 cambios concurrentes de propietario frente a 200 intentos de limpieza del flag.
- Cancelación por muerte, observación de revive sin curación, salida externa y liberación offline.

Los cuatro bordes conservan cruces transitables en la muestra de geodata: 29/42/9/82. Esto no certifica todos los caminos ni sustituye la prueba visual. Queda pendiente ver el color del nombre, indicador y movimiento desde el cliente con el usuario.

## Archivos y respaldo

Core: Player.java, PvpFlagTaskManager.java y FlagPvPZone.java. Sala: PvpRooms.java. Fuentes sincronizadas con el runtime y el overlay local; sin commit/push.

Se guardó el JAR anterior y las copias fuente/script antes de modificar. Se sustituyeron cinco entradas .class y se comprobó que las otras 2100 entradas del JAR permanecen iguales.

Respaldo y hashes: `research/elven-autoflag/baseline.json` e `installation.json`. Restauración con GameServer detenido: `python research/elven-autoflag/restore.py`; rechaza modificaciones posteriores. Evidencia de comportamiento: `research/elven-autoflag/verification.txt`; banco/compilación y detalle en su README.md.
