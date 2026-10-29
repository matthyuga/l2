# Stickers de la lámina Maggie Fess — V2

24/10/2026. Instalados en el Lab `E:\l2-local`, cliente `E:\l2\system-hud`. Imagen aportada por el usuario: `E:\l2-local\descarga de assets\maggie-fess-2xj1f66khj0.jpg`. El archivo original se conserva intacto.

Se extrajeron 19 PNG separados con transparencia exterior y se revisó `contact-sheet.png`. Los blancos interiores, textos y globos se conservaron mediante eliminación del fondo conectada al exterior. Los halos de la ilustración original pueden seguir siendo visibles, especialmente sobre fondos oscuros: no son recortes vectoriales ni una fuente con alpha original.

## Probar

Entrar al juego y escribir `.sticker 1`. El botón de stickers junto al minimapa abre la rueda con los primeros ocho dibujos. El botón central cierra la rueda. Se puede enviar cualquiera de los 19 por número o nombre.

**Alt+E y el sondeo periódico están desactivados.** Los dos intentos anteriores cerraron el cliente en `StickerRadialUI.OnTimer`. Se retiraron SetUITimer/KillUITimer, se dejó OnTimer con un único Return y se comprobó el paquete con un parser nuevo. El cliente fue reabierto, pero ingresar al mundo y usar el botón todavía requiere prueba del usuario. No presentar la apertura del proceso como validación del ingreso.

Duración configurada: 3 segundos, emisor máximo 3,1 s. Espera compartida: 5 segundos, validada en servidor. El mismo recurso se usa para el dibujo sobre el personaje y su miniatura del catálogo. Tamaño del sprite: 34 unidades por semieje para que la ilustración se pueda distinguir.

| Comando | Nombre |
|---|---|
| `.sticker 1` | tesoro |
| `.sticker 2` | ataco |
| `.sticker 3` | duelo |
| `.sticker 4` | pergamino |
| `.sticker 5` | curame |
| `.sticker 6` | escondite |
| `.sticker 7` | elfa |
| `.sticker 8` | abrazo |
| `.sticker 9` | paladin |
| `.sticker 10` | gato |
| `.sticker 11` | magia |
| `.sticker 12` | asesino |
| `.sticker 13` | cocina |
| `.sticker 14` | orco |
| `.sticker 15` | arbol |
| `.sticker 16` | unicornio |
| `.sticker 17` | amor |
| `.sticker 18` | castillo |
| `.sticker 19` | furia |

## Archivos y comprobaciones

- `cutouts/`: PNG individuales. `cutouts.json`: cajas exactas y hash del original. `contact-sheet.png`: revisión de los 19.
- `NexusStickersV2.u`: arte, texturas de rueda y 19 emisores temporales. Wrapper121 con CRC y roundtrip exactos.
- `NexusStickerEffectsV2.usk`: 19 acciones nativas con EAM_Trail y física PHYS_Trailer.
- IDs cosméticos19720..19738; se reemplazaron los ocho stickers de prueba y se añadieron once. Los 30.289 registros ajenos de cada catálogo y sus trailers se conservaron byte a byte.
- XDAT: se actualizaron sólo las dos ventanas de stickers. Las 140 ventanas ajenas permanecen byte idénticas. Se retiraron los rótulos de Alt+E y se diferenciaron el botón de apertura y el central de cierre.
- La primera recarga usó la clase anterior ya cargada en JVM. La verificación detectó el catálogo de ocho y restauró los archivos. La instalación definitiva usa `custom.StickerEmotes.MaggieStickerEmotes`, con la entrada anterior convertida en un shim sin registro para próximos arranques.
- Script y shim sincronizados en runtime, dist y overlay local. No se modificó GameServer.jar ni se publicó nada a servicios externos.
- `live-verification.txt`: confirma por reflexión las 19 selecciones numéricas y por nombre en el handler activo y rechaza entradas inválidas. `client-verification.txt`: 19 emisores, acciones, callbacks, límites VM y ausencia de temporizador. Ninguna de esas pruebas valida el dibujo real, el clic, el seguimiento al correr o la vista desde otro cliente.

## Respaldo

Actualización V2: `E:\l2-local\backups\stickers-maggie-v2-20261024-164145`.

El manifiesto maestro `research/stickers-radial-v1/installation.json` fue actualizado con los hashes y archivos nuevos. La restauración completa al estado previo al sistema sigue disponible con `python research/stickers-radial-v1/rollback.py`, cerrando antes L2 y las conexiones de jugadores. Retira también el handler V2 y verifica hashes para no pisar cambios posteriores.


Confirmaci?n del usuario (24/10/2026): ?Entr? y aparece el sticker?. Ingreso al mundo y dibujo del sticker confirmados con el temporizador retirado. Bot?n/rueda, seguimiento, duraci?n y segundo cliente siguen sin confirmaci?n expl?cita.


ACLARACION DEL USUARIO: el sticker se ve en el menu, pero NO aparece sobre el personaje al elegirlo. La confirmacion previa fue mal interpretada: ingreso/rueda visibles, render en mundo NO confirmado y actualmente reportado ausente. La rueda tambien recorta las texturas. Investigar callback/paquete/attachment y corregir UV/tamano de controles.
