# Bosses de otras crónicas y juegos: candidatos

12/10/2026. Kevin compartió una captura antigua que identifica como Octavis y preguntó por bosses importables para darles utilidad en nuestro Mobius Interlude. La captura muestra apariencia, no permite comprobar archivos ni funcionamiento.

## Qué significa compatible

1. Cliente: malla, materiales, animaciones, sonidos y referencias DAT que nuestro Interlude pueda cargar.
2. Servidor: plantilla de NPC propia en la revisión Mobius actual, con display, colisión, stats y skills definidos.
3. Encuentro: IA, fases, objetivos, spawns, condiciones de victoria y recompensas. No vienen automáticamente con una malla.

Un SQL de un pack antiguo no se debe aplicar directamente a nuestra base: puede corresponder a otro core/esquema. Un FBX/glTF/PSK es material para convertir, no un NPC ya instalable.

## Candidatos encontrados

| Candidato | Evidencia | Estado |
|---|---|---|
| Octavis C6 | [Publicación L2JBrasil de 2022](https://www.l2jbrasil.com/topic/144999-npc-octavis-c6/). El resultado indexado declara Interlude y muestra enlace de pack. Comentarios preguntan por sonidos/animaciones. | Pista concreta; apertura directa no disponible con la herramienta. No descargado; integridad, animaciones y funcionamiento pendientes. |
| Istina IL | [Recursos del publicador Vikos](https://mmo-dev.info/resources/authors/vikos.23560/), entrada de septiembre de 2023; también [share L2JBrasil](https://www.l2jbrasil.com/topic/146619-boss-istina-interlude/). | Entrada confirmada en la página del publicador; pack no inspeccionado. Share de Brasil solo localizado por índice. |
| Tauti IL | [Ficha de adaptación TheVainglorious](https://l2rr.ucoz.ru/load/npc_for_interlude/npc_tauti_for_interlude/8-1-0-1692). Declara animaciones para mob/boss. | Página consultada; afirmación del adaptador, sin prueba local. |
| Metucellar Final Form IL | [Ficha de adaptación TheVainglorious](https://l2rr.ucoz.ru/load/npc_for_interlude/npc_metucellar_final_form_for_interlude/8-1-0-1698). | Página consultada; candidato de criatura, pack pendiente. |
| Boss Balrogs IL | [Índice del publicador Vikos](https://mmo-dev.info/resources/authors/vikos.23560/), entrada de septiembre de 2023. | Referencia localizada; no se estableció el juego de origen del modelo. No atribuirlo a otra franquicia solo por el nombre. |
| Personajes de otras franquicias | [Publicaciones de Xtellia](https://maxcheaters.com/profile/225965-xtellia/content/page/3/?type=forums_topic_post): YoRHa 2B y Kalifa para IL; en Kalifa declara animaciones y sonidos ajustados. | Ejemplos publicados de adaptación, no prueba de que cualquier boss de otro juego sea convertible. No se descargaron ni probaron. |

## Utilidad propuesta por nosotros

- Octavis: campeón de arena contra jugador y aliados; escalado para nuestras builds. Una segunda etapa podría incorporar escoltas y fases. No se afirma que carro, arena o cinemática estén en el pack.
- Istina: encuentro de presión por oleadas, con zonas peligrosas y objetivos secundarios.
- Tauti: jefe de asalto con ataques anunciados y ventanas de castigo; animaciones necesarias por verificar.
- Criatura ajena a L2: jefe opcional de evento o invocación; revisar que estética, escala y lectura de ataques encajen.

Las propuestas son diseños propios, no descripciones de las mecánicas retail de esos bosses.

## Primera comprobación cuando seleccionemos uno

Inventariar paquete y procedencia/permisos; abrir malla y animaciones en UModel; verificar reposo, movimiento, ataque, cast, impacto y muerte; revisar shaders, alpha, escala y colisión. Preparar una referencia DAT y un NPC aislados con IDs libres, sin importar SQL ajeno. Probar primero carga y movimiento, luego daño/IA, y finalmente el encuentro. Las animaciones de otros juegos pueden requerir conservar su propio esqueleto o trabajo de adaptación; no asumir retarget automático.

Estado de esta investigación: fuentes y candidatos registrados. Ningún boss descargado o instalado. Prioridad sugerida: Octavis por la referencia aportada por Kevin, seguido de Istina/Tauti si sus packs resultan completos.
