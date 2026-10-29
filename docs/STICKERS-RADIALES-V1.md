Estado vigente ? 24/10/2026: el usuario confirm? ?quedo perfecto? despu?s de instalar V5 y reiniciar L2. Sticker visible y colocado sobre la cabeza. Las 19 acciones usan Bip01_head y bAbsolute=true. REA identific? que Bip01 Neck1 fallaba en AttachToBone y el motor eliminaba el emisor; el hueso correcto permite crearlo, y la orientaci?n absoluta corrige el desplazamiento lateral. Sin sondeo de teclado; apertura por bot?n. Duraci?n configurada: 3 segundos; espera entre env?os: 5 segundos. Seguimiento en movimiento, tiempo exacto y vista desde otro cliente no se comprobaron por separado. Respaldo V5: E:\l2-local\backups\stickers-rea-v5-20261024-175600. Rollback maestro actualizado.

# Stickers sobre el personaje y rueda radial V1

Implementado e instalado el 24/10/2026 en el laboratorio `E:\l2-local` y su cliente habitual `E:\l2\system-hud`. No está instalado en Academy ni Hellgames.

**Estado vigente:** sustituido el arte de prueba por 19 recortes de la lámina `maggie-fess-2xj1f66khj0.jpg`, con ocho en la rueda y todos disponibles por comando. Ver `research/stickers-maggie-v2/README.md`. Alt+E y Esc mediante sondeo están desactivados tras dos cierres del cliente. Se retiró por completo el registro del temporizador; OnTimer sólo retorna. Acceso por botón y cierre por botón central. Recuperación del ingreso y presentación gráfica pendientes de nueva prueba en juego.

**Última revisión V3:** el usuario confirmó el ingreso y la rueda, pero aclaró que el sticker NO se dibujaba sobre el personaje. Se instaló unión al cuello en vez de trailer, texturas ajustadas para evitar el recorte de botones y confirmación/log de envío. Prueba de dibujo sobre la cabeza aún pendiente. Ver `research/stickers-overhead-v3/README.md`.

**Bloqueo de envío corregido V4:** se comprobó en la JVM activa que la lista nativa rechazaba `voice .sticker 1`. Se agregaron las19 acciones exactas al método nativeWindowAction y se verificaron en vivo y en una JVM nueva. Sin reiniciar L2 ni GameServer; jar del juego intacto, agente de arranque para persistencia. Nuevo clic/render pendientes de confirmación. Ver `research/stickers-native-bypass-v4/README.md`.

## Uso

- Abrir la rueda con **Alt+E** o el botón de stickers cerca del minimapa.
- Elegir una de las ocho reacciones con un clic. La rueda se cierra al enviarla.
- Cerrar sin enviar con **Esc**, **Alt+E** o el botón central.
- Alternativa por chat: `.sticker 1` hasta `.sticker 8`, o `.sticker risa`, `gg`, `corazon`, `enojo`, `llanto`, `sorpresa`, `duda`, `saludo`.

El efecto dura tres segundos, con entrada y salida suaves. La espera compartida es de cinco segundos y la valida el servidor. No consume MP, concede habilidades, hace daño ni cambia estadísticas. Esta versión abre/cierra con la combinación y selecciona con clic; no implementa mantener la tecla y soltar para seleccionar.

## Implementación

- Nueva clase de interfaz `StickerRadialUI` en `Interface.u`, dos ventanas nuevas en `Interface.xdat`. Todos los exports previos de scripts y las 140 ventanas previas se conservaron byte a byte.
- Temporizador de 60 ms activo durante GamingState, lectura nativa de Alt/E, detección del flanco de pulsación y cancelación con Esc. El temporizador se retira al salir del estado de juego.
- `NexusStickersV1.u`: ocho reacciones originales y texturas para la rueda; ocho emisores de una partícula, sin regeneración, vida de partícula de 3 s y vida máxima del emisor de 3,1 s. Propiedades heredadas de partículas verificadas contra Engine.u del cliente.
- `NexusStickerEffectsV1.usk`: acciones nativas `SkillAction_LocateEffect`, `AttachOn=EAM_Trail`, física `PHYS_Trailer` resuelta con el enum del cliente, destino igual al emisor del sticker. Sigue al actor sin depender de un hueso específico.
- Ocho filas cosméticas 19720..19727 en skillgrp/skillname. Los 30.289 registros previos de cada catálogo y sus trailers se conservaron byte a byte; recifrado 413 verificado. Paquete gráfico/script con wrapper 121, nombre exacto, CRC32 y roundtrip verificados.
- Script Java `custom.StickerEmotes.StickerEmotes`, sin cambios al core. Se transmite `MagicSkillUse` cosmético a través del broadcast nativo del personaje. La intención es que los clientes cercanos con los recursos instalados vean el sticker.
- Reserva atómica de recarga por objectId, reloj monótono, retirada de entradas al expirar. Se rechazan selecciones fuera del catálogo y estados muerto, teleport, observador e invisible.
- Carga en vivo mediante el ScriptEngine normal; carpeta añadida a la lista de scripts permitidos para el siguiente arranque. Sin reiniciar GameServer ni modificar GameServer.jar.
- Script y configuración sincronizados con dist y overlay local. Sin publicación remota.

## Verificación y límites

### Corrección del cierre en OnTimer (24/10)

El primer ingreso del usuario produjo un General Protection Fault con `Interface.StickerRadialUI.OnTimer` en el historial. La apertura del proceso L2 no validaba el ingreso al mundo y el estado inicial se considera fallido.

Se encontró una incompatibilidad de tipos en las tres llamadas nativas a `IsKeyDown`: el parámetro `EInputKey` es `Core.ByteProperty`, pero se había emitido `EX_IntConstByte`, que devuelve un entero de 32 bits. Se reemplazó por `EX_ByteConst`. La reparación altera exactamente tres bytes de opcode (`0x2c` a `0x24`); conserva tamaños, saltos VM y todos los demás exports. El paquete que falló se conserva en `research/stickers-radial-v1/timer-crash-v1/Interface.u`.

La verificación ahora exige los tipos de los tres argumentos y la firma nativa. Corrección instalada, manifiesto de respaldo actualizado y cliente reabierto. **Pendiente de confirmar mediante un nuevo ingreso si esta corrección elimina el cierre.** No atribuir al análisis estático una prueba de estabilidad en juego.

Resultado del segundo intento: el usuario confirmó el mismo cierre en OnTimer; la corrección de los argumentos no bastó. Se retiraron SetUITimer/KillUITimer y el cuerpo de OnTimer. La versión con esa retirada se conserva en el cliente con el arte V2. Sigue pendiente confirmar la estabilidad entrando al mundo y usando el botón.

`research/stickers-radial-v1/client-verification.txt` registra lectura nueva de los paquetes, cadena de campos de la clase, límites válidos de todos los saltos VM, los ocho bypass exactos y los valores de emisores/acciones nativas. `catalog-verification.json` registra la preservación de filas. `live-verification.txt` confirma la carga real del handler, las ocho selecciones numéricas y por nombre, mayúsculas/espacios, entradas inválidas y el límite exacto de la espera de cinco segundos.

**Pendiente de comprobar visualmente dentro de L2:** posición de la rueda y el botón, apertura por teclado y clics, tamaño/orientación del sticker, que siga al jugador al correr y girar la cámara, desaparición a los tres segundos y visibilidad desde un segundo cliente. Las verificaciones de archivos y servidor no demuestran ese resultado gráfico.

## Respaldo y restauración

Respaldo: `E:\l2-local\backups\stickers-radial-v1-20261024-162504`.

Manifiesto de instalación: `research/stickers-radial-v1/installation.json`.

Para restaurar, cerrar L2 y los clientes conectados y ejecutar `python research/stickers-radial-v1/rollback.py` o `Restore.cmd` dentro del respaldo. Comprueba hashes para no sobrescribir cambios posteriores, retira el handler activo y devuelve únicamente los archivos registrados. Los scripts de construcción trabajan sobre el snapshot `current`; no deben reinstalarse ciegamente después de otros cambios del cliente.


Confirmaci?n del usuario (24/10/2026): ?Entr? y aparece el sticker?. Ingreso al mundo y dibujo del sticker confirmados con el temporizador retirado. Bot?n/rueda, seguimiento, duraci?n y segundo cliente siguen sin confirmaci?n expl?cita.


ACLARACION DEL USUARIO: el sticker se ve en el menu, pero NO aparece sobre el personaje al elegirlo. La confirmacion previa fue mal interpretada: ingreso/rueda visibles, render en mundo NO confirmado y actualmente reportado ausente. La rueda tambien recorta las texturas. Investigar callback/paquete/attachment y corregir UV/tamano de controles.
