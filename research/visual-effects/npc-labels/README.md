# Base para etiquetas y efectos de NPCs — 14/10/2026

Actualización posterior: se instaló una primera prueba nativa dorada de EVENTO en el cliente y en un NPC del Coliseo. Ver `E:\l2-local\HELLGAMES-ETIQUETAS-NPC-V1.md` y `native-v1/installed.json`. El NPC activo está comprobado; la apariencia dentro de L2 todavía debe revisarse. Las notas siguientes describen las etapas anteriores de referencia y prototipo web.

## Mod solicitado

La referencia es el ejemplo de NevesOma publicado el 11/03/2022:

- https://maxcheaters.com/topic/243102-l2-client-dev-unique-examples-info/#comment-2795075
- https://www.youtube.com/watch?v=aJ8jLBBIPEs

Se revisaron los enlaces del comentario, la descripción real del video y búsquedas de la publicación. No se encontró una descarga pública del mod exacto. La descripción remite al autor y anuncia efectos/logos para NPCs estándar sin editar npcgrp.dat. No se confirmó que sea gratuito ni se contactó al autor, hizo una compra o abrió una cuenta.

## Alternativa ya descargada y preparada

Custom NPC With Logo [Interlude] está conservado en K. Se comprobó otra vez la integridad de su archivo 7z y se copiaron sus recursos de cliente a `native-reference/`, aislados del cliente del juego. No se copiaron ni ejecutaron los scripts de servidor del paquete.

La malla `athenas.logotipe` usa la cadena de material `athenas.fin → athenas.Lethal → athenas.logo`. La textura de referencia exportada es `reference-logo-athena.png`. Se puede ver el logo en la galería:

http://127.0.0.1:32280/?model=b2_cd52da7bdc5c5df45f&view=3d

Esta base corresponde a un NPC/efecto concreto; no se comprobó que implemente el mod que aplica etiquetas a todos los NPCs automáticamente. El visor glTF permite inspeccionar geometría y textura, pero no reproduce los emisores y animaciones de efecto originales.

## Diseño posible para HELLGAMES

Crear gráficos propios para etiquetas como Academia, Mercader, Capitán, Historia y Evento; ajustar tamaño, altura, transparencia, colores y animación de una base compatible. Mantener separadas las etiquetas de servicio fijas y los nombres individuales dinámicos: estos últimos requieren soporte adicional, no solo cambiar una imagen.

No se ha editado aún el logo original ni publicado una etiqueta HELLGAMES en el juego. El siguiente paso concreto sería preparar variantes visuales propias y ensayarlas en un único NPC de prueba antes de ampliar su uso. La funcionalidad de aplicación global del video sigue pendiente de conseguir o implementar por separado.

Procedencia y comprobaciones: `source-verification.json`. Cliente y GameServer sin cambios.


## Prototipo con part?culas ? 14/10/2026

Vista local: http://127.0.0.1:32280/npc-label-effects.html

Se prepar? una escena interactiva con un NPC de la biblioteca, una etiqueta HELLGAMES y part?culas suaves. Permite elegir Mercader, Academia, Historia, Evento o Capit?n; comparar oro discreto, azul arcano y brasas rojizas; ajustar de 0 a 80 part?culas y pausar la animaci?n. El valor inicial es 28.

Archivos: `research/model-catalog/npc-label-effects.html` y `npc-label-effects.js`. Las part?culas y la etiqueta son una simulaci?n Three.js, todav?a no recursos Unreal nativos. Se comprob? que la p?gina, m?dulos y dependencias del NPC se sirven por HTTP; falta comprobar visualmente la ejecuci?n WebGL.

Para integrarlo: preparar textura con transparencia y material compatible, configurar un emisor nativo y asociarlo a un NPC de prueba; comprobar altura, escala, visibilidad de nombres, animaci?n y rendimiento en el cliente Interlude. Despu?s probar varios NPCs en pantalla y decidir d?nde activar los efectos. Cliente y GameServer sin cambios en este paso.
