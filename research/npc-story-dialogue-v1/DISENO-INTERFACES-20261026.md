# Dirección de diseño: diálogos, historial y cartas

Fecha: 2026-10-26.
Estado: decisiones del usuario y propuesta de organización. No implementado por este documento. El estado técnico de la demo existente se consulta en README.md; INICIO.md describe el planteo inicial histórico.

## Decisiones del usuario

1. Fondo decorativo con elección del jugador: opaco, semitransparente o transparente.
2. Marcos o adornos para los nombres de los interlocutores.
3. Probar la forma angular del marco de Arcane como referencia para la interfaz.
4. Historial de una o varias conversaciones: retrato del personaje a la izquierda y lo que dijo a la derecha.
5. Cartas como medio de comunicación y soporte de encargos, misiones o interacciones.
6. Variante neón de la interfaz para una etapa posterior.

Referencias visuales: adjuntos del usuario y research/rpg-interface-review-20261024/inventory.json. Selecciones 1249 (ornamento dorado), 1209 (marco), 1288 (Arcane), 0271 (historial), 0709 (carta) y 0788 (neón).

## Propuesta de aplicación, pendiente de probar

- Separar fondo, marco, placa de nombre, retrato, texto y botones. Aplicar opacidad solo al fondo decorativo, conservando legibilidad del texto y controles.
- Probar marco angular inspirado en la geometría de la referencia Arcane, con área central despejada y ornamentos discretos. No incorporar su logo ni texto promocional.
- Historial cronológico con retrato, nombre y mensaje, incluyendo las respuestas del jugador. Prever consulta de conversación actual y anteriores. Persistencia, filtros y alcance entre sesiones aún no definidos.
- Carta: remitente, destinatario, cuerpo legible y presentación de papel/sello. Ejemplos posibles: invitación, pista, respuesta a un encargo. Aceptar, responder o entregar son acciones propuestas según el contenido, no requisitos ya cerrados. Cualquier efecto en misiones necesita validación de servidor.
- Neón: variante posterior que reutilice navegación y funciones, cambiando piezas visuales.

## Orden propuesto

1. Prueba visual de la ventana de diálogo y sus tres fondos.
2. Historial con retratos.
3. Carta de muestra y una interacción sencilla.
4. Variante neón.

Verificar lectura y áreas de clic a 1024x640 y 1280x720 antes de instalar. El usuario no pidió instalar cambios en este turno. Los túneles Rune-Pagan/Ketra siguen pendientes.
