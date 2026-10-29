# Evento de rondas inspirado en Counter-Strike 1.6

Idea de Kevin, 13/10/2026. Estado: propuesta y viabilidad inicial; no implementado ni probado en juego. Se revisó código local y documentación de herramientas. Los tiempos siguientes son candidatos de diseño, no parámetros definitivos.

## Experiencia buscada

Entrar a una partida breve, jugar objetivos por equipos y salir conservando el personaje original. Azul representa CT y rojo T. El equipo de la partida pertenece al evento: no sale al mundo persistente. Esto abre una vía competitiva que no exige adquirir previamente el mejor set.

Sería combate y controles de L2 con reglas de objetivos inspiradas en CS. Importar arquitectura no convierte selección de objetivos, casteo y habilidades en disparos de un FPS. Granadas, headshots, retroceso, salto/agachado y compra de CS no se obtienen al convertir un mapa.

## Modos

| Modo | Objetivo | Reglas candidatas | Trabajo especial |
|---|---|---|---|
| C4 | Rojo planta; azul impide o desactiva | Rondas sin respawn, sitios A/B, un portador, cambio de lados | Objeto de bomba, progreso, interrupciones y reloj posterior a plantado |
| Rehenes | Azul habla con NPCs y los escolta a una zona segura | Reservar cada rehén a un guía; punto por rescate, victoria por umbral | Seguimiento, caminos, atascos y reglas si muere/desconecta el guía |
| VIP | Azul escolta a un integrante hasta extracción; rojo lo detiene | Rotar VIP; victoria por escape, muerte del VIP o tiempo agotado | Perfil del VIP, límites de velocidad/teleport y rutas alternativas |
| Iceworld/Poolday | Tomar armas disponibles y combatir | Rondas por eliminación o una variante con respawn y puntuación | Armas temporales, recogida controlada y reposición |

## Ronda C4: reglas que no pueden quedar ambiguas

Ejemplo inicial: preparación de 10–15 segundos, ronda de 2–3 minutos, plantado de 5 segundos, desactivación de 7 segundos y detonación a los 35–45 segundos. Ajustar después de medir desplazamientos y combate. Primera prueba posible con un sitio; segundo sitio cuando las rotaciones sean viables.

- Un único portador autorizado. Al morir, deja un objeto de objetivo recogible por su equipo. No depender de soltar una bomba comercializable desde inventario normal.
- Plantado y desactivación requieren proximidad y posición válida, sin permitir interacción a través de paredes. El servidor valida la acción; la barra únicamente informa.
- Definir interrupciones por movimiento, daño, stun, muerte, desconexión y salida de zona. No considerar solo pérdida de HP: CP puede absorber el golpe.
- Tras plantar, el reloj de bomba reemplaza la condición de tiempo normal. Si mueren todos los rojos, azul todavía tiene que desactivar; si azul no puede desactivar, se puede cerrar como victoria roja según la regla publicada. Antes del plantado, eliminar a todo un equipo resuelve la ronda.
- Resolver una sola vez el resultado aunque expiración y desactivación coincidan. Precisar qué marca temporal determina prioridad.
- Bomba con modelo propio, señal roja A/B, efectos y sonidos: requieren assets compatibles y su instalación en cliente. Primero se puede usar un objeto/NPC y mensajes existentes.

## Rehenes y VIP

Hay intención FOLLOW y un controlador local de escuadras que la utiliza. Eso es una pieza reutilizable, no un sistema de rehenes terminado. Probar navegación en esquinas, puertas, desniveles y túneles; no teletransportar rutinariamente al rehén como sustituto de escoltarlo. Si se atasca, aplicar una regla visible de recuperación o retorno.

Definir si rehenes son invulnerables o si se penaliza herirlos, si se permiten curas y cuántos puede guiar una persona. Para empezar conviene un rehén y una ruta fiable. En VIP, limitar movilidad y protecciones dentro del modo: skills de L2 pueden permitir atravesar o trivializar la ruta. El VIP rota para que el mismo jugador no cargue siempre con el rol.

## Equipo temporal y conservación del personaje

Elegir entre dos diseños: arquetipos del evento con atributos y habilidades acotados, o clases originales con perfiles de equipo normalizados. Igualar armas por sí solo no iguala nivel, buffs, skills acumuladas ni builds del laboratorio. Mantener roles útiles sin permitir que una clase invalide los objetivos.

Registrar al entrar ubicación, equipo original, perfil y estados que se vayan a cambiar; restaurar al salir. Evitar modificar experiencia, subclases y posesiones persistentes si el modo no lo necesita.

Crear IDs exclusivos y asociar objetos reales concedidos a jugador y partida. Bloquear comercio, correo/transferencias disponibles, almacén, venta, cristalización, enchant y mejoras fuera de las reglas. El arma visible en el suelo puede ser un punto de recogida controlado que otorga la copia autorizada; no tiene que ser un drop libre del mundo.

Limpieza al terminar, salir, morir según modo, desconectar, reconectar y reiniciar servidor; reconciliación persistente antes de devolver acceso al mundo. Revisar también objetos en suelo y huérfanos. Una duración de shadow item, por sí sola, no garantiza ese ciclo. Nunca borrar equipo legítimo basándose en coincidencia de nombre.

Recompensas candidatas: cosméticos, títulos o registro de partidas. Si se incorpora dinero/materiales persistentes, estudiar inflación, victorias pactadas y multicuentas. Ganar no debería introducir inmediatamente otra obligación de farmeo para ser competitivo en este mismo modo.

## Qué está confirmado en nuestro código

Rutas relativas a E:\l2-local\source\L2J_Mobius_CT_0_Interlude:

- `dist/game/data/scripts/custom/events/TeamVsTeam/TvT.java`: creación de instancia dinámica, separación en equipos, teleports y asignación BLUE/RED. Es referencia de infraestructura, no lógica de rondas CS.
- `java/org/l2jmobius/gameserver/entity/actor/enums/creature/Team.java`: NONE, BLUE, RED. No prueba uniformes CT/T personalizados.
- `java/org/l2jmobius/gameserver/network/serverpackets/SetupGauge.java`: barra con tiempos y color. Validar su comportamiento con nuestro cliente durante acciones del evento.
- `java/org/l2jmobius/gameserver/network/serverpackets/PlaySound.java`: mensaje para reproducir un recurso de sonido. El recurso tiene que existir en cliente; no envía un WAV nuevo.
- `dist/game/data/scripts/handlers/chat/commands/voiced/SquadCommand.java`: uso de intención FOLLOW.
- `java/org/l2jmobius/gameserver/entity/item/ItemTemplate.java` y `item/instance/Item.java`: restricciones de intercambio, depósito y drop. Falta un ciclo de propiedad y recuperación específico del evento.

Solo lectura: no se compiló, ejecutó ni instaló un evento durante esta investigación.

## Importar mapas de CS 1.6

No son compatibles directamente. GoldSrc utiliza BSP con geometría, texturas y entidades; nuestro cliente necesita paquetes y escenarios compatibles con su versión de Unreal. La conversión de representación visual no importa automáticamente reglas, colisiones del servidor, caminos o spawns.

Ruta candidata, todavía no demostrada con un mapa CS en nuestro cliente:

1. Elegir un escenario pequeño y reunir archivo de mapa, texturas/dependencias y, si existe, fuente editable.
2. Extraer o reconstruir geometría y UVs en una representación intermedia. Comparar dimensiones; no asumir una escala universal.
3. Preparar mallas por sectores y texturas para el editor compatible con Interlude. La documentación histórica de UnrealEd describe importación ASE/LWO, pero queda por validar nuestra cadena exacta de creación y empaquetado.
4. Colocar arquitectura y preparar colisión del cliente, geodata del servidor, alturas, línea de visión y navegación. Son responsabilidades distintas.
5. Recrear zonas de objetivo, puertas necesarias, puntos iniciales y límites del evento.
6. Probar caminar, perseguir, atacar sin atravesar paredes y seguir rutas con NPCs; después medir rendimiento y jugabilidad con varios participantes.

Los espacios de CS se diseñaron para otro movimiento y cámara. Pasillos, cobertura y alturas pueden necesitar adaptación al alcance de magos/arqueros y a la movilidad de L2. Ver un mapa en un visor no demuestra que sea jugable. Los escenarios locales en `research/scenario-batches` también distinguen visualización e instalación.

En esta búsqueda no se encontró un port de CS 1.6 a Interlude verificado. MaxCheaters tiene una sección específica de CS: encontrar allí un mapa CS no significa que haya sido convertido para L2.

Alternativa: reconstruir una arena propia con distribución inspirada en Iceworld/Poolday y materiales de L2. Permite probar el modo sin depender de toda una conversión. Para redistribuir assets de un mapa concreto, identificar autor y condiciones de uso; un archivo descargable no acredita permiso de redistribución.

## Fuentes técnicas consultadas el 13/10/2026

- [Decay-Library: documentación BSP GoldSrc](https://github.com/AbitTheGray/Decay-Library/blob/master/docs/GoldSrc/BSP.md?plain=1): descripción del formato por sus implementadores. Apoya la distinción de geometría, texturas y entidades, no un conversor a L2.
- [GoldSrc Map2Prop, documentación del autor](https://github.com/erty-gamedev/GoldSrc-Map2Prop): convierte fuentes de mapas/OBJ a SMD de GoldSrc; no es un importador de mapas Interlude. Repositorio archivado que indica traslado a Map2Prop. No descargado ni ejecutado.
- [Unreal Wiki: Static Mesh Browser Menu](https://wiki.beyondunreal.com/index.php/Legacy%3AStatic_Mesh_Browser_Menu): referencia histórica de importación ASE/LWO; contenido consultado mediante resultado indexado, apertura directa fallida. No demuestra compatibilidad exacta de nuestro editor.
- [Dave Johnston: The Making Of Dust](https://www.johnsto.co.uk/design/making-dust/): relato del creador sobre diseño del mapa y cambios de distribución. Útil para estudiar rutas y sitios, no para afirmar equivalencia de combate entre CS y L2.

## Primer prototipo propuesto

Partida 3 contra 3, C4 en una arena ya jugable de L2, perfiles normalizados, un sitio y seis rondas con cambio de lado a mitad. Modelo provisional y barra existente. Validar rondas, objetivos, conservación de personaje y limpieza antes de assets finales. Después una arena pequeña estilo Iceworld para probar la cadena de mapas; rehenes cuando haya navegación fiable. Todos estos números y pasos quedan como propuesta para el siguiente trabajo.
