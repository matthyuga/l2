# Sticker sobre el personaje — revisión V3

24/10/2026. El usuario aclaró que «aparece el sticker» se refería al dibujo dentro de la rueda. **La imagen no aparecía sobre el personaje al seleccionarla.** Se corrigió la memoria y los manifiestos para no atribuir a esa confirmación una prueba de render en el mundo.

## Revisión instalada

- Paquetes nuevos `NexusStickersV3.u` y `NexusStickerEffectsV3.usk`.
- Se sustituyó EAM_Trail/PHYS_Trailer por `EAM_BoneSpecified=3`, `AttachBoneName=Bip01 Neck1`, unión equivalente a la usada por la prueba visual del NPC. Emisor finito de 3 s, máximo 3,1 s, desplazamiento de partícula35 y tamaño34 por semieje. El posicionamiento final sobre cada raza/cuerpo requiere comprobación visual.
- Los 19 IDs19720..19738 apuntan a V3. `cast_range=0xffffffff`, igual que los efectos cosméticos de referencia. Las 30.289 filas ajenas y el trailer siguen idénticos; skillname no cambió.
- La captura mostró botones y rueda recortados: los dibujos128/512 se estaban muestreando sin la reducción esperada. El arte ahora se coloca en el rectángulo superior izquierdo del tamaño que dibuja el control:84 por botón,98 centro,48 apertura y384 rueda. Los contenedores de textura mantienen tamaños potencia de dos. La rueda declara UV384×384 y modo Normal. Sin cambiar las 140 ventanas ajenas.
- El script confirma `Sticker enviado: <nombre>.` tras aceptar y emitir el paquete. El log registra `STICKER_REQUEST` y `STICKER_SENT`, para distinguir un callback que no llega al servidor de un recurso que no se dibuja.
- GM invisible: recibe el efecto sólo en su propio cliente; no se revela a terceros. No se cambia el estado invisible ni ninguna estadística.
- El handler conserva su identidad; se redefinió solamente la clase de script existente, sin modificar el core ni reiniciar GameServer. Fuente sincronizada en runtime, dist y overlay local.
- Alt+E sigue desactivado. No se reintrodujo el temporizador de teclado.

## Prueba pendiente

El cliente fue reabierto. Al elegir «tesoro» o escribir `.sticker 1`, comprobar separadamente:

1. La rueda se cierra y el chat confirma «Sticker enviado: tesoro».
2. El dibujo aparece SOBRE LA CABEZA del personaje, y no sólo dentro del menú.
3. Desaparece a los tres segundos y acompaña al personaje al moverse.
4. Otro cliente con los recursos instalados también lo ve.

El parser verifica las clases, propiedades nativas, referencias de hueso, límites VM, ausencia de timer y duraciones, pero no valida la presentación en el juego.

Seguimiento V4: el usuario no recibió ni la confirmación de envío. Se descubrió que la validación de bypass rechazaba los comandos de la rueda antes de llegar al handler. Se habilitaron en vivo exclusivamente las19 acciones nativas. Ver `../stickers-native-bypass-v4/README.md`. Se espera una nueva selección real y comprobación visual.

Respaldo de esta revisión: `E:\l2-local\backups\stickers-overhead-v3-20261024-170339`. El manifiesto maestro V1 se actualizó para que la restauración completa con `research/stickers-radial-v1/rollback.py` incluya los paquetes nuevos y los cambios del script. Los dos paquetes anteriores se conservan sin uso para el historial y la restauración.
