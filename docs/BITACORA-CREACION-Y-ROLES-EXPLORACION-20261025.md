# Bitácora: creación modular y roles de exploración

Fecha: 25/10/2026. Proyecto: `E:\l2-local`.
Estado: continuidad de diseño. Esta sesión no implementa mecánicas ni modifica cliente, servidor o personajes.

## 1. Creación del personaje y puntos de atributos

Kevin propone integrar la preparación de la build antes de terminar la creación del personaje, mediante interfaz propia, sin depender inicialmente de un NPC.

Recorrido deseado: apariencia/raza y sexo, cuerpo físico o mágico, origen de atributos, profesión y clase, distribución de puntos y revisión final. La modularidad VIP permitiría combinaciones avanzadas entre apariencia, atributos y ramas profesionales, incluso de razas distintas. Elegibilidad, precios y límites del VIP no están definidos.

La creación detallada debe ser opcional: un jugador puede crear un personaje para pasar objetos y completar la personalización después con un NPC. Se propone conservar los puntos no gastados para ese momento; la política exacta aún requiere definición.

El cuerpo y la variante masculino/femenino aportan ventajas y contrapartidas. La conversación anterior se recuperó en `BITACORA-CUERPO-SEXO-Y-CABELLOS-20261024.md`, que registra el módulo ya activado con servicio GM `.cuerpo`:

| Variante | STR | DEX | CON | INT | WIT | MEN |
|---|---:|---:|---:|---:|---:|---:|
| Masculino | +1 | −1 | +1 | +1 | −1 | −1 |
| Femenino | −1 | +1 | −1 | −1 | +1 | +1 |

No interpretar esto como nuevos porcentajes directos de ataque, velocidad, defensas o recursos. Los efectos derivados dependen de las fórmulas y de la build. El perfil corporal y el origen racial son capas distintas; evitar contabilizarlos dos veces.

Nueva capa solicitada: algunos puntos distribuibles manualmente dentro de lo permitido por la build. Se propone repartir sobre STR/DEX/CON/INT/WIT/MEN y mostrar sus efectos derivados. Presupuesto, límites, progresión, reinicios y costes no están decididos. No se aprobó un número concreto de puntos.

La interfaz debe separar base racial, ajustes de cuerpo/sexo y puntos asignados. Comparar con condiciones iguales de nivel/equipo/efectos. Elegir un camino profesional futuro no concede automáticamente nivel ni habilidades de tercera profesión.

Detalle previo: `research/CREACION-Y-PUNTOS-STATS-20261025.md`. La integración en la pantalla anterior a confirmar la creación todavía requiere investigación técnica; no sustituir silenciosamente ese objetivo por una ventana al ingresar al mundo.

## 2. Nueva idea del usuario: construir un rol más allá del PvP

Inspiración mencionada por Kevin: Baldur's Gate 3, el ladrón/Astarion y las distintas capacidades que permiten explorar, descubrir información y resolver situaciones de más de una manera. Registrar como inspiración, sin asumir una reproducción exacta de las reglas de ese juego.

Intención central: que preparar un personaje o un grupo también tenga sentido por sus capacidades de exploración, interacción y conversación, no solo por daño, defensa y rendimiento PvP.

### Ejemplos expresados por el usuario

- **Ganzúas y cerraduras:** abrir puertas, cofres o artefactos.
- **Desactivar trampas:** una utilidad distinta de abrir cerraduras, aunque puedan compartir especialización.
- **Hablar con animales:** obtener lore, curiosidades o pistas; posibles aliados o maneras de evitar que una criatura ataque. No todos los encuentros necesitan una recompensa material.
- **Religión/conocimiento:** reconocer ruinas, sitios u otros elementos del mundo y comprender su historia o significado.
- **Exploración/percepción:** notar detalles que otros personajes no perciben y descubrir cofres enterrados.
- **Excavación:** usar una pala tras descubrir un lugar; posibilidad de hallar algo interesante y distintos grados de valor o rareza del cofre. Probabilidades, estados y relación entre hallazgo y recompensa aún abiertos.
- **Formas alternativas de acceso:** abrir un cofre con ganzúa o intentar romperlo. No se definieron todavía consecuencias de romperlo.
- **Mentira y persuasión:** ampliar las opciones de diálogo y los resultados posibles de una conversación.
- **Composición del grupo:** preparar distintos personajes según las necesidades de una aventura; que los jugadores puedan asumir un rol útil fuera del PvP.

### Organización propuesta por el asistente, todavía no aprobada

Separar tres capas comprensibles:

1. **Build de combate:** atributos, cuerpo, profesión, clase y habilidades de combate.
2. **Competencias de aventura:** cerrajería, trampas, percepción/exploración, conocimientos, interacción con animales y habilidades sociales.
3. **Herramientas y condiciones:** ganzúa, pala, acceso a una conversación o conocimiento descubierto. Poseer una herramienta no implica dominar la competencia.

Esta separación permitiría que una profesión de combate no monopolice todas las utilidades. Relación con clase, atributos, entrenamiento y puntos de competencia pendiente de decidir. Un presupuesto independiente de aventura es una recomendación para que explorar no obligue a sacrificar toda la viabilidad en combate, no una regla autorizada.

Ejemplo de cadena de interacción, construido a partir de la idea del usuario:

`Notar indicio → descubrir escondite → excavar con pala → encontrar cofre → examinar cerradura/trampa → elegir cómo resolver → obtener contenido o nueva pista`.

Otro ejemplo propuesto: un animal revela un indicio, un personaje reconoce el significado religioso de las ruinas y otro abre el acceso. Son posibilidades de diseño, no contenido existente.

### Decisiones para una etapa posterior

- Qué competencias existen y cómo se aprenden o progresan.
- Qué acciones exigen una capacidad específica y cuáles permiten intentos básicos.
- Reparto individual/grupal de descubrimientos, información y recompensas.
- Qué se calcula por habilidad, por requisito fijo o por azar; consecuencias y reintentos.
- Diferencias entre descubrir, excavar, abrir, desarmar y romper.
- Cómo evitar que todo se resuelva cambiando de personaje repetidamente o repitiendo una tirada sin límite.
- Persistencia de cofres, trampas, puertas, animales aliados y decisiones conversacionales en un servidor multijugador.
- Cómo se conectan las competencias con la interfaz de creación y el servicio NPC posterior, sin volver obligatoria una preparación extensa.
- Si existe alguna relación con VIP. El usuario no asignó estas competencias al VIP; no asumir exclusividad.

## 3. Ampliación: competencias, familias y niveles

Actualización del 25/10/2026. Kevin solicita conservar también estos temas. Todo lo siguiente continúa en diseño; no hay habilidades, pasivas, NPC ni diálogos nuevos instalados.

### Propuestas del usuario sobre comunicación con criaturas

- La comunicación puede tener varios niveles. Cada criatura presente durante el juego puede exigir una competencia y nivel para permitir hablar.
- Ejemplo tentativo: Human Rogue con hablar con animales nivel 1; Treasure Hunter con nivel 2. No se trata todavía de una asignación definitiva ni de una modificación del árbol de clases.
- Alternativa más variada: elfos con comunicación con animales mágicos nivel 1; elfos oscuros (mencionados como «elfos de la noche») con animales espirituales o espectros.
- Pendiente decidir si esas afinidades dependen de raza visual, origen, cuerpo, profesión, clase o entrenamiento. En el sistema modular no deben confundirse esas dimensiones.
- Es necesario catalogar las criaturas que realmente vayan a estar presentes en el juego y sus diálogos, en lugar de asumir que todos los monstruos existentes deben conversar.

### Propuestas del usuario sobre religión

- Asociar inicialmente religión a profesiones de soporte, más que a magos de ataque: Bishop, Prophet, Swordsinger y Bladedancer son los ejemplos mencionados.
- Niveles, requisitos, progresión y reparto definitivo por profesión/clase no definidos.
- El usuario plantea la distinción entre habilidad activa y pasiva; menciona también detectar cofres enterrados, abrir cerraduras y desactivar trampas.

### Distinción conceptual propuesta por el asistente

La competencia representa lo que el personaje sabe hacer y su nivel de dominio. Activo/pasivo describe cómo se utiliza; una misma competencia puede admitir ambos usos. Es una propuesta de organización, no una mecánica ya implementada.

| Competencia | Ejemplo activo | Ejemplo pasivo |
|---|---|---|
| Comunicación con criaturas | Iniciar conversación | Comprender sonidos o frases al acercarse |
| Religión | Examinar altar o interpretar inscripción | Reconocer un símbolo o ruina |
| Percepción | Inspeccionar una zona | Advertir indicios de trampa o tesoro enterrado |
| Cerrajería | Intentar abrir una cerradura | Reconocer su dificultad |
| Desactivar trampas | Manipular una trampa descubierta | No se propuso un uso pasivo concreto |

Familias de comunicación propuestas: fauna común, criaturas mágicas, espíritus/espectros. Los niveles se compararían dentro de su familia: fauna común nivel 2 no implica entender espectros. Taxonomía final pendiente, especialmente porque un espectro no es necesariamente un animal.

Comprender a una criatura, poder iniciar diálogo y conseguir cooperación son condiciones distintas. Se propone que actitud, contexto, misiones y elecciones influyan en el resultado, sin convertir toda conversación en una recompensa material.

Para religión, el asistente propone información diferenciada según tradición o formación (por ejemplo, rituales, cantos o símbolos), sin dar automáticamente el mismo contenido a todas las clases citadas. No es un reparto aprobado.

### Catálogo de encuentros pendiente

Esquema mínimo propuesto: identificador/plantilla de criatura, familia de comunicación, competencia y nivel requeridos, actitud, diálogo y consecuencias posibles. Registrar también su presencia prevista en el mundo y qué determina el acceso del personaje.

Comenzar con un conjunto pequeño de encuentros diseñados a mano es una recomendación del asistente. Algunos podrían aportar una frase o curiosidad, otros pistas y unos pocos interacciones extensas. No se seleccionaron todavía criaturas ni se escribieron diálogos definitivos.

Mantener separados descubrir, excavar, detectar una trampa, desactivarla, abrir una cerradura y romper el contenedor. Esa separación permite cooperación entre personajes y distintas soluciones. Probabilidades, consecuencias y límites de reintento siguen pendientes.

## 4. Continuidad y pendientes conservados

- Interfaces y diálogo de Amber: referencias analizadas en `research/rpg-interface-review-20261024/ANALISIS.md`; demo existente en `research/npc-story-dialogue-v1`.
- Pasadizos físicos Rune–Pagan y acceso mencionado cerca de Ketra: pendientes por indicación del usuario.
- Próximo tema abierto: desarrollo de roles de aventura. No comenzar implementación ni imponer cifras de balance a partir de esta bitácora.
