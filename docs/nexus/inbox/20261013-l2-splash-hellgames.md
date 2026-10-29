# Lineage II — splash actualizado

13/10/2026, sesión de experiencia de jugadores. Ruta real: E:\l2-local.

Por pedido de Kevin se reemplazó el splash del cliente E:\l2 usando descarga de assets\hellgames.jpg (bosque, criatura y texto Hell Games). Instaladas 22 variantes BMP nativas cifradas en systextures; proporción conservada en 640x480 con franjas negras. Respaldo: E:\l2-local\backups\splash-hellgames-20261013-212713.

Documentación, script y manifest: research/client-branding/2026-10-13. Integridad y decodificación comprobadas; vista en próximo arranque pendiente. No se modificó servidor ni pantalla/escenario de login. Esta nota evita que otra sesión revierta el splash nuevo al mantener assets.

Corrección posterior: el primer splash era invisible por alpha cero en el BMP32. Corregido a alpha opaco para imagen/no negro y transparente para negro; reinstaladas 22 variantes verificadas. Manifest apunta al respaldo de segunda intervención 20261013-214727, que contiene la versión fallida; el respaldo original 20261013-212713 conserva el logo anterior. Pendiente ver en próximo arranque; cliente del usuario no se cerró.

Captura posterior mostró huecos en sombras/texto. Última corrección instalada: RGB mínimo 1 y alpha opaco en toda la imagen central; negro transparente solo en franjas. BMP8 cuantizado separadamente con índice 0 reservado a franjas. Validado contenido central sin color transparente en ambas variantes y hashes/cifrado de 22 archivos. Nuevo respaldo 20261013-230905 conserva la versión con huecos; manifest actualizado. Pendiente vista al reiniciar cliente.
