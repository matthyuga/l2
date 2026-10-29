# Investigacion de cerebros de bots L2

Actualizacion de la revision completa: [ADAPTACION.md](ADAPTACION.md), [PERFILES.md](PERFILES.md), inventario de236archivos y prototipo Java de decisiones/preview compilado. Treinta escenarios de politica aprobados; no se activo este prototipo en la pelea. Las limitaciones y la secuencia exacta de integracion estan en ADAPTACION.md. El resto de este README conserva el relevamiento inicial.

15/10/2026. Analisis estatico de tres repositorios publicos descargados en esta carpeta. No se ejecutaron builds, SQL, parches ni bots de terceros; servidor, cliente y partidas intactos. No implica prueba de rendimiento ni de funcionamiento en nuestro core.

## Veredicto

La referencia mas util para enriquecer PvpSiegeBrain es L2Autobots: separar perfiles por rol/clase y habilidades con condiciones, soporte propio, control de distancia, consumibles y mascotas. Portar selectivamente esas decisiones a Java/Mobius, conservando nuestros Player, RoomCombatRules, instancias, snapshots, tandas y sistema de votos. No sustituir todo el servidor ni instalar patch.diff directamente. No se encontro en esta muestra un cerebro aprendido que ya juegue PvP Interlude humano de forma completa.

Un LLM puede servir en una etapa posterior para dialogo o decisiones generales espaciadas. Los proyectos revisados no demuestran que un LLM elija cada skill de combate de manera competitiva. Recomendacion propia: combate rapido con reglas/estados locales; modelo opcional fuera del tick, ordenes limitadas y validacion nativa. Sin promesa de autoaprendizaje.

## Fuentes inspeccionadas

### L2Autobots, Elfocrash

https://github.com/Elfocrash/L2Autobots

Snapshot master f990c61df25e94c08ea6c36c5e230928a36ce0fc, commit2020-09-27. Kotlin para aCis382, GPL-3.0 segun LICENSE/README. No compatible directo con nuestros paquetes org.l2jmobius ni APIs Skill/Player. build.gradle usa Kotlin1.3.70, Gradle6, jcenter, coroutines y dependencias antiguas. No se intento construirlo.

Archivos y evidencia concreta:

- behaviors/CombatBehavior.kt: ciclo de actualizacion, seleccion de objetivo, soporte propio y listas de skills; preferencia de ataque/skills. Tiene logica de retorno/revive propia que no corresponde importar a nuestras salas.
- behaviors/classes/AdventurerBehavior.kt: Backstab condicionado a estar detras; Bluff/Trick/Switch, blows, Dash/UE/Mirage y toggles. Esa condicion no prueba que el bot sepa caminar para buscar la espalda.
- attributes/Kiter.kt: alejamiento del blanco cuando entra en radio configurado, verifica movimiento con geodata. Es un desplazamiento simple, no un planificador tactico completo; adaptar al perimetro de sala y alturas reales.
- classes/SoultakerBehavior.kt: debuffs Gloom/Anchor/Abyss/Doom/Silence si faltan, ataque magico, summon1129 condicionado a cadaver, TP condicionado a servitor. Util para dejar de intentar invocar sobre el propio bot vivo.
- classes/PhoenixKnightBehavior.kt: ShieldSlam/Stun/Shackle segun estado del objetivo; defensas/autosoporte condicionales.
- classes/CardinalBehavior.kt y attributes/Healer.kt: seleccion de aliado herido, curas. Hay puntos que requieren revision: las condiciones1218/1217 miran HP del caster en lugar de HP del target; Healer.kt contiene un TODO explicito sobre comportamiento defectuoso. No copiarlo sin corregir/probar.
- attributes/SecretManaRegen.kt: implementa recarga directa a maxMP por debajo20%; el ciclo la usa para comportamientos que implementen ese atributo. No corresponde a nuestras potas y consumo real; excluir. README tambien ofrece reposicion infinita de buffs/consumibles.
- CombatBehavior.kt trata clan/party como aliados. Nuestras reglas de sala pueden permitir combate dentro del mismo clan/party: usar RoomCombatRules y el equipo/instancia, no importar esa amistad por defecto.

### L2jRoboto, Elfocrash

https://github.com/Elfocrash/L2jRoboto

Snapshot master9ebda43140ceafe7339c2f446fcf054789a5a308, commit2018-10-16. GitHub muestra archivado19/01/2019. Java/aCis372; MIT segun LICENSE. README lo declara WIP y desaconseja servidor live. Base de referencia mas simple, no mejor mantenida por estar escrita en Java.

`ai/CombatAI.java`, `model/BotSkill.java`, `HealingSpell.java`, `OffensiveSpell.java`, `SupportSpell.java`: separacion de decisiones ofensivas/curas/soporte y seleccion de spells. Gestion de shots por nivel en lugar del grado real del arma: nuestra implementacion por grado es preferible. Tiene reposicion automatica de consumibles y ciclo de muerte propios, incompatibles con reglas de prueba si se copian literalmente. Importa net.sf.l2j y FakePlayer propio: necesita port.

### l2-smartbot, PlayerExplains

https://github.com/PlayerExplains/l2-smartbot

Snapshot main f65cb3acc526ffc8f29a76a492ad109375895d39, commit2026-05-03. L2J C4/Scions of Destiny, GPL-3.0 segun LICENSE. README explica limitaciones de IDs/API por core. Mas reciente en este snapshot, pero pocos commits no certifican madurez.

`smartbot/SmartBotController.java`: actualizacion periodica de un segundo; roles MAGE/ARCHER/HEALER/BUFFER/DAGGER/TANK, seguir/asistir, curar, resucitar y detectar buffs faltantes, skills candidatas fijas. Importa L2PcInstance/L2Skill/ThreadPoolManager de otro core. No es compatible directo con Mobius Interlude.

`BotLlmService.java`, `model/BotMemory.java`, `SmartBotKnowledge.java`: conversacion via HTTP a Ollama, memoria corta, hechos de archivos de texto y comandos como follow/assist/attack/buff. Los casteos por tick estan en SmartBotController y no los decide Ollama. Hay llamadas HTTP sincronas dentro de los metodos de generacion; revisar su ejecucion/colas antes de integrar. El README distingue LLM opcional y conocimiento simple, no embeddings/aprendizaje de PvP.

## Candidato no confirmado

El buscador mostro Teravibes/L2-Living-Worlds como fork de Mobius Interlude, pero abrir directamente el repositorio devolvio404. No se descargo ni se usa como base de recomendacion: disponibilidad y codigo sin verificar.

## Integracion propuesta para nuestros bots

1. Perfil de combate explicito por funcion y arma, resuelto con habilidades realmente disponibles. Los personajes del laboratorio son hibridos: clase activa sola no basta; no conceder skills nuevas como atajo.
2. Evaluar supervivencia/autosoporte, curar aliados legales y recuperar MP; luego control/debuff, ataque y posicionamiento. Mantener cooldown, MP, item consume, LOS y comprobacion de condiciones nativas.
3. Healer que prioriza cura/cleanse/revive valido, mago con debuffs pertinentes y rango, arquero que mantiene distancia, daguero con condiciones posicionales, tanque con control/defensa, summoner con target de invocacion valido y asistencia. Implementar por etapas y probar skills concretas, no asumir todas cubiertas.
4. Compartir objetivo/enemigos solo dentro de instancia y equipo; configuracion de salas decide amistades. No usar clan como sustituto del equipo.
5. Mantener todos los movimientos dentro de arena; no usar teleport para simular kite; cancelar objetivos muertos/invalidos y evitar spam de ordenes.
6. Medir ejecuciones reales, curacion/control efectivos, consumo, muertes/objetivos y carga del servidor. Las metricas de orden aceptada actuales no son prueba suficiente por si solas.
7. Al ampliar, verificar que los perfiles no queden sobrecargados por stock y que pool DB/telemetria soporten la carga. No cambiar recursos para que ganen artificialmente.

La igualdad de cantidades/sorteo de equipos implementada no asegura equilibrio de roles. Separar la mejora de IA de una eventual distribucion equilibrada de healers/tanques/dano; conservar aleatoriedad dentro de esas restricciones si el usuario lo pide.

## Alcance

Solo investigacion y copias de referencia. No se instalaron motores de terceros ni se modificaron los bots activos. Para reutilizar codigo conservar las licencias/atribucion correspondientes y revisar compatibilidad de la distribucion; esa revision no constituye asesoramiento legal.
