# Fondo ornamental oscuro — V4

Instalado el 26/10/2026. Se recreó con ImageGen el patrón oscuro de rosetas y arabescos adjuntado por Kevin y se adaptó al panel angular existente. Falta valoración dentro de L2.

## Prueba

Abrir L2, entrar al mundo y pulsar AMBER. Elegir Opaco para ver mejor el motivo; Semi para verlo integrado con el escenario; Transparente para ocultar el relleno. Los controles Original/Compensar siguen siendo independientes.

## Alcance y verificación

Se modificaron exclusivamente los píxeles de BackgroundOpaque y BackgroundSemi dentro de NexusAmberAngularV3.u. La máscara alfa anterior se conserva exactamente. BackgroundClear y los otros 35 exports del paquete conservan sus bytes; tablas de nombres/importaciones e inventario de 35 texturas idénticos. Interface.u, Interface.xdat, retrato, botones, marco y servidor no se modificaron.

Los píxeles originales se localizaron mediante coincidencia exacta BGRA de 1024×512 en el export nativo, offset 66. Se sustituyó únicamente ese bloque, sin cambiar sus metadatos. Se comprobó el paquete con lectura nativa fresca, wrapper121, CRC y roundtrip exacto; también hashes instalados y del respaldo. La comprobación de restauración pasó con --check.

Previsualizaciones inspeccionadas a 1024×640 y 1280×720; son composiciones previstas, NO capturas del juego.

## Arte y trazabilidad

- [Textura generada original](ornamental-generated.png), copiada al proyecto desde la salida de ImageGen.
- [Relleno adaptado al panel](ornamental-fill-610x280.png).
- [Prompt y método de generación](PROMPT.md).
- [Previsualización opaca](preview-opaque-1024.png).
- [Comparación de fondos](comparacion-fondos.jpg).
- native-verification.log, verification.json y native-inventory-before.tsv: evidencia del cambio limitado.
- input-hashes.json, output-hashes.json e installation.json: hashes y estado.

La preparación para el motor solo encuadra/redimensiona la textura y aplica la máscara alfa preexistente; no redibuja el patrón generado.

## Restauración

Con L2 cerrado:

`python E:\l2-local\research\npc-story-dialogue-v1\install-ornamental-demo.py --restore`

Respaldo: `E:\l2-local\backups\npc-story-ornamental-v4-20261026-140259`.

Esto restaura el fondo geométrico V3. Si se desea retirar también la interfaz angular, restaurar primero V4 y después V3. Los instaladores históricos rechazan cambios posteriores por hash.
