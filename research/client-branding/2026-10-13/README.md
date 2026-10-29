# Splash Hell Games — 13/10/2026

Instalado el reemplazo solicitado por Kevin en `E:\l2\systextures`: once variantes `sp_32b_*.bmp` y once `sp_256_*.bmp`.

Fuente: `E:\l2-local\descarga de assets\hellgames.jpg`, 555 × 355. Imagen adaptada conservando proporciones: 640 × 409, centrada en un lienzo negro de 640 × 480, sin recorte. Se conserva la composición y el texto original. [Vista previa](preview.png).

Formato nativo conservado: BMP BI_RGB de 32 bits y BMP con paleta de 256 colores, envoltorio Lineage2Ver121 y cifrado específico del nombre final. Cada uno de los 22 archivos pasó decodificación de ida/vuelta y CRC; hashes instalados comprobados. Una decodificación del archivo instalado de 32 bits coincide píxel a píxel con la vista previa. La variante de 256 colores reduce la paleta según requiere el formato.

Respaldo completo: `E:\l2-local\backups\splash-hellgames-20261013-212713`. Detalle de rutas y hashes: [installation.json](installation.json). Original JPG copiado como `source-hellgames.jpg`; originales decodificados de referencia en `original-32.bmp` y `original-256.bmp`.

Pendiente confirmar visualmente al siguiente arranque del cliente. El cambio es el splash previo a abrir el juego, no el escenario de login. No se inició el cliente ni se cambió el servidor para esta tarea. El recurso es compartido por las carpetas system que usan este mismo cliente.

## Corrección tras aviso de imagen invisible

Kevin indicó que no veía nada. Se encontró que el primer BMP de 32 bits tenía todos los bytes alpha a cero. Aunque el encabezado es BI_RGB, el splash nativo utiliza ese cuarto byte como transparencia; los originales contienen valores distintos de cero. La conversión inicial verificó RGB y cifrado, pero omitió esa propiedad.

Corregido `install_splash.py`: píxeles negros transparentes y píxeles de la imagen opacos. Instalados nuevamente los 22 archivos con ida/vuelta, CRC y hashes comprobados; alpha verificado: 223430 píxeles opacos y 83770 transparentes. Respaldo de esta segunda intervención: `E:\l2-local\backups\splash-hellgames-20261013-214727` (contiene la primera versión fallida). Para recuperar el logo anterior usar el respaldo original `splash-hellgames-20261013-212713`.

El cliente estaba abierto durante esta corrección. La comprobación visible requiere el próximo arranque; no se cerró la partida del usuario.

## Corrección de huecos dentro de la imagen

La captura posterior de Kevin confirma que la imagen aparece, pero muestra huecos transparentes en sombras y letras. La versión anterior convirtió cada píxel negro en transparente. Se cambió la preparación: el contenido de la imagen usa RGB mínimo 1 y alpha 255; únicamente las franjas exteriores reservan negro puro y alpha cero. En el BMP de 8 bits se cuantiza la imagen separadamente a 255 colores y se reserva el índice 0 para las franjas, evitando que sombras compartan el color transparente.

Reinstaladas 22 variantes, con ida/vuelta, CRC y hashes verificados. Se comprobaron ambas profundidades: ningún píxel de la imagen central usa negro puro; los 261760 píxeles centrales de BMP32 son opacos y los 45440 de las franjas transparentes. Respaldo de esta intervención: `E:\l2-local\backups\splash-hellgames-20261013-230905` (versión anterior con huecos). Confirmación visible de esta última corrección pendiente del siguiente arranque. El respaldo original de 212713 sigue siendo el del logo anterior.
