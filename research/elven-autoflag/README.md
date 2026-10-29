# Elven auto-flag: integración sobre Mobius

Etapa autorizada 15/10/2026: integrar flag de sala y coordinar temporizador normal; conservar salida vulnerable de cuatro segundos. No incluye reloj de ronda, voto ni segundo mapa.

## Implementación

- PvpFlagTaskManager conserva propietarios independientes, identificados por clave. Adquirir dos veces la misma clave no duplica el registro. No modifica el plazo de flag de combate.
- Player.updatePvPFlag protege el flag violeta mientras exista al menos un propietario. Esto evita que un vencimiento concurrente o una salida de zona lo borre durante la visita.
- La tarea normal ignora la expiración mientras el flag sea forzado; al liberar el último propietario reanuda el plazo de combate restante, o limpia el flag si ya venció. No llama a updatePvPStatus porque cambia el plazo y puede ignorar zonas PvP.
- FlagPvPZone nativo usa la misma API, de modo que superponer zonas o una zona con la sala no produce limpiezas cruzadas.
- PvpRooms mantiene su propietario durante entrada, visita, salida de cuatro segundos, cancelación, muerte y revive observado. Lo libera después de llegar a Giran, o al detectar salida externa/desconexión. La tarea de flag también limpia propietarios offline como respaldo.
- Ninguna ruta nueva restaura HP/CP/MP, buffs, debuffs ni cooldowns; tampoco aplica Noblesse, restricciones de clase o protección de teleport.

## Archivos y recuperación

baseline.json contiene la copia previa de diez archivos (JAR, tres fuentes de core y sus copias overlay, y tres copias del script). installation.json registra hashes instalados. Se reemplazaron cinco entradas .class del JAR y se verificó igualdad de las otras 2100 entradas.

Restauración: con GameServer detenido, ejecutar `python research/elven-autoflag/restore.py`. Rechaza cambios posteriores para no pisar trabajo nuevo. Cargar de nuevo el servidor para aplicar la restauración.

## Verificación

compile.txt: compilación contra las bibliotecas desplegadas. VerifyElvenFlagV2.java verifica handlers activos, personajes temporales sin cuentas persistentes, flag, propietarios, plazos, frontera y conservación de estado. verification.txt: PASS en el servidor activo, incluyendo buff, debuff, cooldown y concurrencia. No sustituye una prueba visual en cliente.

Repetición con el usuario conectado: V2 falló al comprobar el debuff porque applyEffects también ejecuta la probabilidad de éxito del efecto y el verificador no validaba esa precondición. V3 instala el efecto continuo de Weakness de forma determinista solo en el personaje transitorio y comprueba su presencia antes de entrar. La repetición V3 pasó. El código de sala/core no cambió por esta corrección del verificador. Fallo previo conservado en verification-fixture-failure.txt.

RoomClientProbe usa el handler normal de salas para Hellkevin, identificado por ID y nombre observados en el servidor y cliente conectado. La entrada real se confirmó con instancia300000 y flag1; la apariencia visual queda sujeta a la observación del usuario. No usa captura ni entrada de teclado alternativa.

La primera versión del agente quedó cargada y Windows mantuvo abierto su JAR; intentar reemplazar ese archivo falló. La ampliación de pruebas se empaquetó con clase y JAR nuevos (VerifyElvenFlagV2 / verify-state-v2.jar) y se ejecutó correctamente. No se modificó el runtime para resolver ese bloqueo del archivo de pruebas.
