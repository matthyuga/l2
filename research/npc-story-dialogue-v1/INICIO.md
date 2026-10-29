# Primera conversación de historia en L2

Estado: diseño inicial; sin cambios instalados en cliente ni servidor.

## Acuerdos

- Presentación tipo novela visual dentro de L2.
- Apariencia elegida: Grimdark Dialogue & NPC UI de ZSS Game Lab. El paquete comercial aún no fue localizado en las carpetas revisadas. Las imágenes de la página no sustituyen los archivos licenciados.
- Sprites originales generados con continuidad de personaje y expresiones, tomando como referencia el trabajo de El Último Bastión. Su estilo registrado es Clean Western Anime Cel; confirmar su aplicación al NPC elegido antes de producir el lote.
- Primer NPC: Amber, elegido por el usuario. El usuario no recuerda si adquirió el paquete; no se asume compra ni se usan previews como assets finales.
- Referencia visual localizada: research/amber-l2/reference-models/amber-web-2026-10-23/v14-full.png. Se prepara un retrato neutral con identidad y vestuario conservados para revisión antes de las demás expresiones.

## Alcance del primer prototipo

Una conversación de prueba de 4–6 intervenciones, tres expresiones (neutral, amable y seria), una decisión con dos respuestas y un cierre. Texto de prueba separado del canon. Sin recompensas ni cambios en quests existentes.

Retrato con transparencia a un lado, panel inferior de lectura, nombre, botones de respuesta/Continuar y cierre visible. Mantener el mundo detrás. Adaptar la composición al área visible del cliente y comprobarla a 1024×640 y 1280×720. Reservar espacio para el texto y evitar que el retrato lo tape.

Primera entrega: retrato base y composición para revisar. Después: expresiones, paquete de texturas y ventana nativa. Finalmente: enlazar un NPC de prueba con la conversación y verificar el recorrido dentro de L2.

## Separación de responsabilidades

Contenido: identificador de conversación, nodos, NPC hablante, expresión, texto, opciones y destinos. Diseñar esto para que futuras historias no requieran reconstruir la interfaz.

Servidor: sesión de conversación por jugador, NPC de origen, nodo válido y elecciones permitidas. Verificar distancia/estado y descartar respuestas repetidas o fuera de sesión. No aceptar decisiones narrativas calculadas únicamente por el cliente.

Cliente: presentar retrato, nombre, texto y botones; comunicar la respuesta. Reutilizar controles nativos y eventos. Determinar primero el transporte servidor→ventana disponible en este Interlude; no dar por existente un paquete de diálogo moderno.

La rueda de stickers demostró ventanas, texturas y botones personalizados; no demuestra por sí sola texto dinámico ni comunicación de conversación. Evitar temporizadores de sondeo. Texto progresivo, animaciones de boca, voz y transiciones quedan para una etapa posterior.

## Verificación

Abrir desde el NPC, continuar, recorrer ambas respuestas, cambiar expresión, cerrar y volver a abrir. Probar dos jugadores sin mezclar sus sesiones. Comprobar lectura/tamaño en las resoluciones de referencia y conservación de ventanas ajenas. La confirmación de un parser no equivale a validación visual en L2.

Recursos actuales: proyecto E:\l2-local; cliente E:\l2\system-hud. Memoria artística: K:\_CodexNexus\sessions\ultimo-bastion-imagenes.md. No instalar ni cerrar el cliente como parte de este diseño.
