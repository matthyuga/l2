# Estructura jugable del servidor

Fecha: 13/10/2026.
Estado: borrador de diseño para conversar, ampliado el 14/10/2026. No aprueba rates, recompensas ni cambios del servidor. La orientación más reciente del prelanzamiento está registrada al final y precisa las alternativas iniciales.

## Motivo y prioridad

Kevin señala que la exploración de recursos de Internet está desplazando decisiones fundamentales: llegada del jugador, equipo, adena, EXP, party, materiales, zonas de farmeo y nivel inicial. Diseñar estos sistemas como un recorrido conectado antes de seguir ampliando capas de contenido.

Este documento complementa `research/player-experience/2026-10-13/`; no reemplaza sus análisis ni convierte propuestas anteriores en decisiones aprobadas. Las facilidades, personajes y recompensas del laboratorio no son automáticamente reglas del servidor público.

## La primera decisión: qué recorrido queremos

| Modelo | Qué sostiene el progreso | Qué hay que diseñar |
|---|---|---|
| Nivel 1 con progresión extensa | Aprender, subir, cambiar de profesión y de equipo | Utilidad de cada tramo, compañeros disponibles, ruta de retorno y acceso tardío |
| Nivel 1 con progresión breve | Introducción y transición al juego compartido | Duración objetivo, primeras recompensas y continuidad entre introducción y actividades avanzadas |
| Nivel máximo desde el inicio | Equipo, dominio de la clase, builds y objetivos sociales | Equipo base competitivo, aprendizaje opcional, economía y objetivos posteriores al nivel |

Ningún modelo está elegido. Nivel máximo inmediato no exige regalar equipo final; empezar en nivel 1 no obliga a un recorrido largo. Si se ofrece un salto opcional, hay que resolver por qué alguien elegiría el recorrido completo y evitar recompensas iniciales explotables mediante personajes alternativos.

Elegir primero qué debe poder hacer una persona durante su primera sesión y cuándo debe poder jugar con un veterano. Después calibrar EXP y demás rates.

## Recorrido que debemos poder explicar

Entrada → orientación y recursos básicos → primera actividad → primera mejora útil → elección de ruta solo/party → objetivo compartido → siguiente meta visible.

Para cada paso registrar: requisitos, lugar, tiempo objetivo, recompensa, coste y alternativa si no hay compañeros. Los tiempos son metas de diseño pendientes, no resultados medidos.

## Decisiones conectadas

| Sistema | Decisión pendiente | Dependencia y criterio de prueba |
|---|---|---|
| Llegada | Aldea o hub; nivel; profesiones; guía; equipo y consumibles iniciales | El jugador entiende qué hacer y puede completar una primera actividad sin asistencia del GM |
| EXP y SP | Duración del recorrido; ritmo por tramo; aprendizaje de skills | Diseñar por tiempo hasta actividades concretas; comprobar clases y rutas diferentes antes de fijar multiplicadores |
| Equipo | Base inicial, primera mejora, techo de poder y vías de obtención | Cada mejora tiene una utilidad; definir también enchant, SA, dyes, subs y sockets antes de acumular ventajas |
| Adena | Fuentes, gastos recurrentes, compras y comercio | Comparar ingreso neto por sesión; transporte y consumibles no deben bloquear la ruta inicial |
| Materiales | Qué se farmea, para qué receta y qué se puede comerciar | Cada material tiene demanda explicable; revisar funciones de crafters y spoilers si se usan sistemas nativos |
| Party | Reparto de EXP, adena y drops; ventajas por cooperación; acceso de soportes | Medir ganancia por participante y tiempo de organización; una recompensa total mayor no garantiza que convenga agruparse |
| Zonas | Entrada, solo, grupos pequeños y conflicto/élite | Cada zona tiene función y alternativa; habilitar suficiente espacio sin dispersar toda la población |
| PvP y clanes | Cuándo se puede participar; riesgo; pérdidas; recompensas | Evitar que perder el acceso a una zona corte toda la progresión; revisar monopolios y victorias acordadas |
| Servicios | Buffs, curación, mana, teleports y asistencia de IA | Las facilidades cambian costes y valor de los roles; decidir antes de calibrar party y economía |
| Continuidad | Entrada tardía, regreso, permanencia del equipo y actualizaciones | Poder incorporarse sin anular logros anteriores; distinguir poder, variantes y apariencias |

## Ficha mínima de una zona de farmeo

- Público: nivel, equipo y tamaño de grupo requerido.
- Propósito: EXP, adena, materiales, preparación de equipo u objetivo colectivo.
- Encuentro: enemigos, dificultad y comportamiento que exige del jugador.
- Economía: botín comerciable o ligado; ingreso bruto y gastos por sesión.
- Destino de las recompensas: recetas o compras concretas.
- Riesgo: muerte, PvP, pérdida de acceso y posibilidad de monopolio.
- Alternativa: dónde avanzar si está ocupada o faltan jugadores.

No elegir todavía mapas ni IDs de materiales: primero definir sus funciones.

## Propuesta para la primera prueba

Construir un recorrido pequeño: bienvenida, actividad solo, actividad de grupo y primera mejora. Probar también una clase de soporte y una entrada con poca concurrencia. Comparar tiempos, gastos, utilidad de la recompensa y siguiente objetivo entendido por el jugador.

La primera hipótesis sugerida para discutir es una introducción breve seguida de progresión de equipo y objetivos compartidos. Sigue pendiente decidir si empieza en nivel 1 o en nivel máximo. No implementar esta hipótesis como configuración sin resolver esa elección.

## Orden para cerrar decisiones

1. Promesa del servidor y experiencia de la primera sesión.
2. Nivel inicial y duración hasta participar con otros.
3. Equipo base, primera mejora y techo de poder.
4. Adena, materiales y gastos que sostienen ese recorrido.
5. Party, servicios y funciones de las zonas.
6. PvP, clanes, entrada tardía y continuidad.
7. Rates y cantidades, calibrados con recorridos reales.

## Orientación de Kevin para el prelanzamiento — 14/10/2026

Registro de intención, no configuración implementada:

- Comenzar con un prelanzamiento para probar sistemas, quests personalizadas y preferencias de los participantes, buscando compatibilidad con la visión del proyecto.
- Facilitar mediante un NPC la adquisición de las demás subclases al nivel máximo y la preparación de builds. El nivel exacto de creación del personaje sigue sin especificarse.
- Considerar acceso a equipo y hasta joyería única sin enchants para probar. El catálogo, costes y alcance de «sin enchants» quedan por definir.
- Proponer salas inspiradas en CS 1.6 con capacidad objetivo de 32 jugadores; habilitar después otros eventos progresivamente. Es un objetivo de diseño, no capacidad técnica verificada ni necesidad de reunir 32 para comenzar.
- Diseñar joyería personalizada y drops de bosses. Kevin indica que ya tenemos sets; esto no acredita su balance o validación para lanzamiento público.
- Renovar la experiencia de L2 y permitir disfrutar del PvP sin exigir previamente años de farmeo.
- Explorar expediciones, lugares con lore, campañas y misiones con sentido, con Baldur's Gate y Fallout como referencias de experiencia narrativa.
- Considerar una versión single player separada de la online, donde se concentraría la acción. No hay alcance técnico ni implementación elegidos.
- Captar atención progresivamente y considerar premios por tiempo de permanencia. No hay sistema de recompensas aprobado.

Kevin recuerda haber pasado voluntariamente de un servidor PvP a otro más hardcore cuando quiso una experiencia diferente. Es una experiencia personal que inspira la posibilidad de recorridos alternativos; no demuestra que todos los participantes vayan a desear leveleo tras jugar PvP.

### Consecuencias propuestas para organizar las pruebas

Estas son propuestas del asistente, pendientes de acuerdo:

1. Separar las condiciones del test de la economía definitiva. Acceso libre permite probar combate; para probar obtención de equipo hace falta una prueba específica con condiciones controladas.
2. Definir antes de invitar jugadores qué progreso de pruebas podría reiniciarse y qué reconocimiento se conservaría. No prometer persistencia ni borrar nada por este documento.
3. Empezar por una modalidad y un recorrido narrativo breve. Para las salas, fijar mínimo de participantes y comportamiento con poca concurrencia antes de habilitar colas distintas.
4. Probar joyería nueva como opciones con ventajas y costes explícitos. Evaluar combinaciones con subs y sets; disponer de una pieza no debe convertirse automáticamente en superioridad en toda situación.
5. Distinguir permanencia conectada de participación y regreso voluntario. Considerar reconocimiento cosmético o de contribución; evitar que acumular horas otorgue una ventaja creciente de combate. No imponer rachas ni usar número de bajas como única medida de aporte.
6. Medir por prueba: comprensión del objetivo, acceso efectivo, builds utilizadas, dificultades, participación por rol, deseo expresado de repetir y retorno observado. No inferir disfrute únicamente de horas conectadas.

Próximas definiciones concretas: contrato del prelanzamiento (acceso, catálogo, enchants, subs, persistencia), primera modalidad jugable y primera expedición corta. Rates y economía definitiva siguen abiertos.
