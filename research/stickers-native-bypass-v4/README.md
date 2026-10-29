# Selección de la rueda — lista de acciones nativas V4

24/10/2026. Tras V3 el usuario informó que no aparecían ni el dibujo sobre el personaje ni el mensaje «Sticker enviado». Se encontró el bloqueo antes del handler: `RequestBypassToServer` exige caché HTML salvo las acciones declaradas por `SkillCatalogView.nativeWindowAction`. La rueda no tiene caché HTML y sus comandos no estaban declarados.

## Cambio aplicado

Se añadieron exclusivamente los literales `voice .sticker 1` hasta `voice .sticker 19` a las diez acciones previas. Se conserva la validación HTML para los demás comandos y los filtros de estado, límites de selección y espera de cinco segundos del handler.

El método se sustituyó en vivo con graft de `nativeWindowAction(String):boolean`. Antes de aplicar se comprobó en la JVM real que `voice .sticker 1` devolvía false. Después devolvieron true las19 acciones y las10 anteriores. Se probaron null, números fuera de rango, sufijos, ceros iniciales y acciones ajenas: todos siguieron rechazados. El graft comprueba que los cuerpos de todos los demás métodos quedan byte idénticos.

No se reiniciaron servidor ni clientes y no se alteraron las sesiones de jugadores.

## Persistencia y restauración

`server/agents/sticker-native-actions-v4.jar` aplica el mismo graft al cargar SkillCatalogView en el siguiente arranque. Se añadió `-javaagent` sólo al lanzamiento de GameServer en Start-L2Local.ps1; LoginServer conserva sus argumentos. La sintaxis de PowerShell se comprobó sin ejecutar el script. Una JVM nueva, usando el GameServer.jar real y el agente de arranque, verificó la aceptación exacta y el rechazo de entradas ajenas. GameServer.jar permanece sin modificar.

La fuente de SkillCatalogView se actualizó en source y overlay local para que una reconstrucción posterior contenga la misma lista.

El manifiesto maestro V1 incluye el agente, las fuentes y los scripts de arranque con sus respaldos/hashes. Su DeactivateStickers actualizado retira el transformer de arranque si existe y restaura únicamente el método nativo anterior mediante graft sobre la clase actual, conservando otros métodos. Después se retira el handler y se devuelven los archivos. La restauración completa sigue siendo `python research/stickers-radial-v1/rollback.py`, sin clientes conectados.

Respaldo: `E:\l2-local\backups\stickers-native-bypass-v4-20261024-171214`.

## Evidencia y pendiente

`live-verification.txt`: rechazo antes, aceptación exacta después y conservación de acciones anteriores. `cold-start-verification.txt`: agente de arranque verificado en otra JVM. `runtime-before.class`: método original para restauración; `runtime-patched.class`: clase aplicada.

Sigue pendiente un clic real que registre STICKER_REQUEST/STICKER_SENT y la confirmación del dibujo SOBRE LA CABEZA. La lista nativa arregla el acceso al handler; no demuestra por sí misma que el efecto se dibuje.
