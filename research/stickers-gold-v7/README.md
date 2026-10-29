# Rueda de stickers dorada — V7

Instalada el 26/10/2026 con L2 cerrado. Falta validación visual y de clics dentro del juego.

## Cómo probar

Abrir L2 y pulsar el lanzador habitual del menú de stickers. Aparece la rueda con aro de hojas doradas, medallones, placas de nombre, cabecera STICKERS y cierre central CERRAR. La barra azul de las dos ventanas de stickers se desactivó con los mismos campos de chrome ya usados en el diálogo de Amber.

Probar hover, pulsado y envío desde los ocho stickers; comprobar cierre central y reapertura. No se añadieron atajos nuevos: se conserva la apertura por botón y la lógica existente.

## Alcance

- Conservados los ocho dibujos originales: TESORO, ATACO, DUELO, PERGAMINO, CURAME, ESCONDITE, ELFA y ABRAZO. Los PNG originales no se modificaron; solo se adaptaron para los medallones.
- Conservados código, acciones, efectos sobre la cabeza, compensación de stickers y gamma global. Interface.u y NexusStickersV3.u permanecen idénticos.
- Nuevo NexusStickerGoldV7.u con 33 texturas: fondo/aro, cabecera, placa inferior, ocho botones × tres estados, cierre × tres y lanzador × tres.
- Solo se modifican StickerRadialWnd y StickerLauncherWnd en Interface.xdat; las otras 145 ventanas quedan byte a byte iguales, incluidas todas las páginas de Amber.
- Se mantienen el orden y las zonas de clic originales de 84×84; cierre de 98×98 y lanzador de 48×48. Para alojar la cabecera, la ventana crece de 414 a 438 de alto y se compensa su ancla: los centros y tamaños nominales de las nueve zonas de clic en pantalla se conservan matemáticamente. Ninguna superposición entre botones.

## Arte

Aro y marcos de medallón generados con ImageGen integrado. Originales y [prompts](PROMPTS.md) guardados en este proyecto. Las placas reutilizan el arte D Oro ya aprobado; el fondo reutiliza la textura floral V4. No se usó el mockup como atlas ni se regeneraron los personajes.

[Previsualización al tamaño previsto](preview-native.png): composición de referencia, NO captura del juego. Se inspeccionó para comprobar que cabecera, personajes, nombres y pie no se recortan. La apariencia real y el comportamiento nativo aún deben comprobarse en L2.

## Verificación

UCC; paquete con wrapper121, CRC y roundtrip exactos. Lectura nativa e inventario completo de 33 texturas, sin funciones ni emisores nuevos. XDAT exacto, preservación de 145 ventanas ajenas, controles dentro del contenedor, sin solapamientos y anclas/tamaños de clic conservados. Hashes de archivos instalados y de dependencias, originales de dibujos y respaldos; restauración comprobada con --check.

No se modificó servidor, quests, habilidades ni código de envío. No se abrió, cerró o reinició L2 como parte de la instalación.

## Restauración

Respaldo: `E:\l2-local\backups\stickers-gold-v7-20261026-152100`.

Con L2 cerrado:

`python E:\l2-local\research\stickers-gold-v7\install.py --restore`

Agregar `--check` para verificar sin modificar. Vuelve a la rueda anterior con barra azul y conserva el diálogo V5. Como esta capa modifica el XDAT compartido, retirar V7 antes de restaurar capas anteriores que también lo cambien, como los botones de Amber V5. Sus guardas de hash rechazan el orden incorrecto.

Los constructores e instaladores históricos no deben ejecutarse sobre el estado actualizado.
