# Ideas de actividades sociales y vínculos con animales

Fecha: 2026-10-21.
Proyecto: Lineage II, `E:\l2-local`.
Estado: registro conceptual para continuar en otra sesión. No implementado ni validado técnicamente. Las propuestas del asistente no equivalen a decisiones aprobadas.

## 1. Limpiar el cielo para un festival

### Idea del usuario

Actividad recreativa y sociable para cuando haya jugadores en el servidor. Conseguir una aeronave o varias y limpiar un cielo cubierto de nubes que anuncian una tormenta, para que el festival pueda celebrarse con el cielo despejado.

Los jugadores usan un extractor para absorber las nubes. Algunas forman criaturas que pueden atacar a los participantes. El objetivo principal es limpiar el cielo, con combate como parte de la actividad.

### Apariencia de las criaturas

Propuesta del usuario: partir de un monstruo existente y cubrirlo o rellenarlo visualmente con material esponjoso, tipo nube o algodón, hasta que parezca una criatura hecha de nube. Conservar sus movimientos y acciones bajo la nueva apariencia.

Posible camino técnico, pendiente de comprobar en el cliente: conservar esqueleto y animaciones, modificar materiales y añadir volúmenes de nube ligados a los huesos. Una textura sola podría no cambiar suficientemente la silueta. Verificar articulaciones y animaciones antes de extender el concepto.

### Sugerencias abiertas del asistente

- Nombre provisional: «Un cielo para el festival».
- Preparativos en tierra, extracción a bordo, defensa y mantenimiento para repartir tareas.
- Mostrar visualmente el progreso con claros y luz en las zonas despejadas.
- Enemigos conceptuales: nimbos escurridizos, chispas que interrumpen extractores y nubarrones que exigen cooperación.
- Ojos visibles y señales eléctricas para comunicar ataques.
- Absorción por capas hasta revelar un núcleo, como mecánica adicional a implementar.
- Celebración posterior y reconocimiento de distintas contribuciones.
- Posible festival con llovizna si la limpieza queda incompleta; no definido.

### Continuación pendiente

Elegir una criatura base por silueta y movimiento; comprobar assets, materiales, aeronaves, cielo y representación del extractor. Empezar por una prueba visual de una sola criatura. No hay monstruo ni recurso concreto seleccionado.

## 2. Rescate de animales y vínculo persistente

### Origen e intención del usuario

Inspiración: el impacto emocional de ver un rescate de perritos abandonados. Llevar al juego un encuentro que invite a una decisión personal, con consecuencias, sin puntos de karma ni clasificación moral.

### Encuentro y urgencia

- Un jugador encuentra un animal en muy mal estado en un rincón del mapa.
- El evento se activa cuando el jugador se acerca lo suficiente.
- Desde esa activación comienza una cuenta regresiva: necesita ayuda o muere.
- El jugador puede rescatarlo o ignorarlo.
- No se asignan puntos de karma por esa decisión.

### Vida después del rescate

Posibilidades planteadas por el usuario, aún por concretar:

- Llevarlo a una posada propia, dormitorio o habitación alquilada para que descanse.
- Darle un nombre.
- Que pueda servir como pet, atacar si se vuelve más fuerte o recolectar recursos.
- Tener su propia quest o historia.
- Poder liberarlo, devolverlo a su entorno o reunirlo con su familia o manada, si la tiene.
- Admitir también destinos trágicos.

### Relación con el alojamiento

El usuario plantea un sistema de puntos de dormitorio: pintar paredes, cambiar el piso y añadir adornos aumentaría esos puntos, que podrían intercambiarse por premios. Una mascota alojada también podría contribuir al sistema.

No están definidos la fórmula, los premios, la permanencia de puntos ni cómo se relacionan con el bienestar del animal. Mantener esta idea vinculada al futuro diseño de alojamientos.

### Referencia emocional narrada por el usuario

El usuario recuerda una experiencia personal en Baldur's Gate 3: entregó el silbato de su perro a una mujer que mantenía perros en jaulas; el perro apareció encerrado y, al poder hablar con animales, expresó que se sentía abandonado. Después el usuario liberó a los perros, el suyo huyó y más tarde pudo recuperarlo. Le habría gustado que el perro recordase lo ocurrido, en lugar de limitarse a alegrarse al volver a verlo.

Registrar como recuerdo del usuario, sin verificar aquí los detalles del juego. La intención de diseño que comunica es que las experiencias compartidas dejen huella en el vínculo y en las respuestas posteriores de la mascota.

### Líneas de diseño para explorar, no decisiones cerradas

- Memoria de acontecimientos concretos y cambios de confianza; evitar reducir el vínculo a una puntuación de karma.
- Distinguir recuperación física, confianza y capacidades de la mascota.
- Que sus reacciones posteriores reconozcan rescate, cuidado, separación, abandono o reencuentro.
- Evitar que la utilidad o los puntos de habitación desplacen el sentido emocional del rescate.

### Preguntas pendientes para continuar

- Cómo comunicar la emergencia y permitir ayuda sin exigir objetos que un jugador nuevo no podría conseguir a tiempo.
- A quién pertenece el evento si se acercan varios jugadores y qué ocurre con desconexiones o salidas de zona.
- Cómo se rescata y cómo transcurre la recuperación.
- Qué recuerda el animal y cómo lo expresa mediante conducta, animaciones o diálogos apropiados.
- Qué consecuencias persisten al liberar, perder o reencontrar una mascota.
- Cómo se conectan alojamiento, puntos, bienestar y recompensas.

## 3. Ampliación: encuentro sorpresa dentro de una misión instanciada

Fecha: 2026-10-21, continuación de la conversación.

### Propuesta del usuario

Tomar como referencia la entrada a misiones que describe de Guild Wars 2: desde el mundo compartido, acercarse a un acceso y aceptar viajar a un espacio separado con NPCs. Durante una misión cuyo objetivo inicial es otro, encontrar por sorpresa una cría vulnerable. Si el jugador la rescata, salir de la instancia con ella como pet persistente.

La especie queda abierta: cachorro de perro u otro animal que encaje con L2; también una cría de dragón, considerando el Strider y la quest clásica como antecedentes. Se busca una situación inesperada que despierte emoción, no simplemente repetir una quest conocida para obtener una mascota.

Esta variante permite plantear el rescate como una experiencia personal dentro de la misión. Queda por decidir si sustituye al encuentro en mundo abierto o si ambos formatos coexistirán. La instancia real y su aislamiento en este servidor aún no fueron verificados.

### Candidatos encontrados en los datos locales

Inspección de `server/game/data/stats/npcs` (definiciones del servidor; no prueba visual del cliente):

- Wolf: pet 12077, archivo `12000-12099.xml`.
- Hatchling of the Wind / Stars / Twilight: pets 12311, 12312 y 12313, archivo `12300-12399.xml`.
- Baby Buffalo: BabyPet 12780.
- Baby Kookaburra: BabyPet 12781.
- Baby Cougar: BabyPet 12782.
- Los tres BabyPet figuran en `12700-12799.xml`.

Esto ofrece candidatos existentes sin elegir todavía uno. Verificar apariencia, tamaño, sonidos y animaciones en el cliente; no se confirmó un modelo específico de perro doméstico ni de lobezno herido.

### Sugerencias de puesta en escena, pendientes de elección

- Mantener el rescate fuera del anuncio inicial de la misión para preservar el descubrimiento.
- Dar señales perceptibles: un ruido débil, movimiento o rastro que invite a acercarse, sin depender de que el jugador encuentre un punto invisible.
- Tras ayudarlo, mostrar una primera respuesta pequeña (aceptar agua, dejar de retroceder, intentar seguir al jugador).
- Al salir, conservar al mismo individuo y su estado de recuperación. La transición de NPC de escena a pet debe preservar identidad y evitar duplicados.
- Presentar la salida como llevarlo a un lugar seguro; sus funciones de combate o recolección pueden llegar después de recuperarse.

### Pendientes técnicos y narrativos

Comprobar soporte de instancias/aislamiento; definir persistencia del rescate y de la mascota; resolver desconexiones, reintentos y abandono de misión sin reiniciar arbitrariamente su historia ni duplicarla. Elegir especie después de comparar candidatos en pantalla.

## Punto de reanudación

Ambas ideas quedan en fase conceptual. Retomar primero la que el usuario elija, sin implementar ni convertir las sugerencias en requisitos automáticamente.

