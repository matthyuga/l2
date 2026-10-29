# Stickers: compensación local de gamma V6

Instalada con cliente cerrado el 24/10/2026. Falta confirmación visual del usuario. Respaldo: E:\l2-local\backups\stickers-gamma-v6-20261024-203027.

La misma LUT inversa que funcionó para Amber se aplica a los19 dibujos que aparecen sobre el personaje, Reaction0..Reaction18 de NexusStickersV3.u. Los emisores existentes usan mezcla alfa; no se aplican otras curvas de color explícitas en sus propiedades. Se mantiene la unión Bip01_head/bAbsolute corregida en V5, duración configurada3s y espera5s.

Sólo se modifican bytes RGB de las19 imágenes RGBA256×256. Se conservan todos los bytes alfa, cabeceras de mip, offsets, tamaños, clases, código, propiedades de emisores, tablas e imágenes de la rueda. La comparación global del paquete descifrado permite cambios únicamente en esos intervalos RGB. Se validó además con parser independiente, formato nativo5, un mip, wrapper121, CRC y roundtrip exactos.

Las imágenes originales están en current/NexusStickersV3.u y en el respaldo. No se recompilaron ni sustituyeron las clases. NexusStickerEffectsV3.usk, Interface.u/xdat, la compensación de Amber, Option.ini y l2.ini se comprobaron sin cambios. No hay cambio de servidor, comandos, stats ni gamma global.

Cómo probar: entrar y enviar `.sticker 1`, esperar5s y enviar `.sticker 2`; probar también `.sticker 3` u otros claros. Evaluar si se recupera el detalle de blancos/caras, sin alterar su posición o desaparición. No hay selector Original/Compensar para stickers en esta revisión: se cambia el recurso del efecto. Para comparación con el original se puede restaurar este único paquete con cliente cerrado.

expected-comparison.png es una simulación de referencia, no una captura del juego. La LUT procede de la curva real capturada por REA y tiene el mismo límite que Amber: el negro levantado por la gamma global no se corrige completamente, y la transparencia/fades pueden introducir diferencias. Si cambian las opciones de gamma del juego, recalcular o retirar esta compensación.

Restaurar únicamente esta compensación: cerrar L2 y ejecutar `python E:\l2-local\research\stickers-gamma-v6\restore.py`. Verifica hashes y conserva las demás correcciones. Retirar V6 antes del rollback completo de stickers; sus guardas detectan el paquete posterior. La demo de Amber es otra capa independiente y tiene sus propios restore-gamma-demo.py / restore-demo.py.

Nota de verificación: el serializer por defecto resolvía el paquete por nombre en el cliente instalado al leer el archivo staged renombrado. Se corrigió el verificador para leer explícitamente los ExportEntry del paquete objetivo; una segunda comparación byte a byte del archivo completo confirma los cambios permitidos. Los dos primeros intentos de staging fallaron esa verificación y nunca fueron instalados.
