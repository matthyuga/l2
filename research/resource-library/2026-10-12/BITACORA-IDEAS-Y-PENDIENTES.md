# Bitácora de ideas y temas — 12/10/2026

Proyecto: laboratorio Lineage II Mobius CT_0 Interlude, E:/l2-local. Recoge la exploración y las capturas antiguas compartidas por el usuario. Es un mapa de trabajo futuro, no una orden de instalar todos los candidatos.

## Criterios y estado general

- Organizar recursos por capas: guías, experiencias, equipo, interfaces, eventos y demás contenido útil.
- Distinguir publicaciones de descargas recuperables, archivos auditados e integración probada.
- Las capturas aportan referencias visuales; no se copiaron como archivos a esta bitácora. Se conservan en la conversación.
- No se instalaron los mods investigados ni se modificaron cliente o servidor por esta exploración.
- Consultar también RECURSOS-POR-CAPAS.md, BOSSES-IMPORTABLES.md y el manifiesto de descargas de esta carpeta.

## 1. Biblioteca de recursos, guías y herramientas

Buscar y clasificar materiales para editar cliente, modelos, texturas, efectos, DAT, mapas y geodata. Herramientas ya identificadas: UModel, L2ClientDat, l2tool, Blender/PSK-PSA y L2Editor/UCC. Conservar procedencia, licencias y compatibilidad por crónica. La primera selección extensa está en RECURSOS-POR-CAPAS.md.

## 2. Experiencias de jugadores y administradores

Investigar mantenimiento, rendimiento, equilibrio, economía, facciones y experiencias con mundos simulados/bots. Separar testimonios y cifras declaradas de mediciones propias. No extrapolar capacidad de otros proyectos a nuestro servidor.

## 3. Equipo y apariencias custom

Armaduras, armas, accesorios y apariencias de otras crónicas. Captura antigua de un set oscuro con detalles celestes recordado como «Dark Water», aproximadamente 2017: identificación pendiente. Se encontró Water Armor, pero NO se confirmó coincidencia:
https://play4fan.ru/load/doplonenija_tekstury/bronja/armor_water_armor/14-1-0-674
El usuario decidió seguir con otros temas; no insistir en identificarlo salvo que se retome.

## 4. Bosses importados y encuentros con utilidad

Octavis como referencia inicial. Candidatos investigados: Istina, Tauti, Metucellar y Balrogs; detalles y enlaces en BOSSES-IMPORTABLES.md. Explorar también modelos de otros juegos con adaptación real, sin dar por supuesta compatibilidad directa.
Separar apariencia/animaciones, plantilla y conducta de NPC, y encuentro completo. Importar un boss no importa automáticamente sus fases, carro, arena o cinemáticas. Ideas: expediciones, arena, oleadas y combates con aliados/bots.

## 5. Monstruos, NPC y cobertura de la galería

Raider of Pastureland de la captura: confirmado en el catálogo local como variante de LineageMonsters.kel_mahum_m00. IDs 21443, 21444, 21446, 21447, 21448 y 21449; texturas LineageMonstersTex.dark_mahum_t00/t01. La ficha m0098 muestra otra variante, titulada Platinum Tribe Soldier. No falta necesariamente el recurso: la galería deduplica por malla y usa una miniatura representativa.
Mejora propuesta: explorar/mostrar variantes de texturas, nombres e IDs; aclarar que partículas y reflejos no están representados en miniaturas.
Dos NPC femeninos de capturas, «Alexia / Cambio de Clase» y «L2 Zybox / Trainer»: modelos originales sin identificar. Nombres y funciones custom no prueban origen. Pendiente buscar coincidencias visuales y archivos.

## 6. Iconos de habilidades sobre la cabeza

Capturas de iconos circulares flotantes al activar habilidades. Coinciden con la familia Overhead Skill Icons; versión exacta sin confirmar. Neophron publicó Symbols Buffs Over the Head con temporizador para Interlude en 2016, republicado en 2017:
https://maxcheaters.com/topic/206809-neophron-symbols-buffs-over-the-head-with-a-timer/
https://maxcheaters.com/topic/212056-re-share-neophron-symbols-buffs-over-the-head/
Incluye Frenzy, Guts, Zealot, defensas, barreras y otras habilidades. Integración documentada mediante efectos del cliente y skillgrp.dat. Pendiente recuperar/auditar archivos y comprobar objetivo, cancelación y duración real, especialmente con skills custom.

## 7. Interfaces y comodidad de uso

Investigar interfaces modernas compatibles con IL: inventario, minimapas, party, resaltado de aliados, avisos y legibilidad. Abstract: publicación de diciembre 2025, actualización septiembre 2026; modifica engine.dll/nwindow.dll y requiere prueba aislada:
https://mmo-dev.info/resources/abstract-interface-for-interlude.3866/
L2Eirin documenta resaltado de party, advertencia de enchant y agathions en IL. Es evidencia de funciones declaradas por ese servidor, no un pack público verificado:
https://forum.l2eirin.com/topic/4055-update-%E2%84%9647-interlude-x1x30x300/

## 8. Renovación visual y clientes alternativos

Fermata declara lectura de assets originales IL y render moderno: iluminación, sombras, relieve en algunas superficies, reflejos, clima, niebla y ajustes de efectos.
https://fermata.gg/docs/features/rendering/
https://fermata.gg/docs/admins/compatibility/
https://fermata.gg/docs/features/status/
No probado localmente. Su documentación consultada indica que NO carga custom data packs; faltan funciones como enchant de skills y cristalización. Investigar como laboratorio separado; no asumir sustitución viable para nuestro cliente custom.
Funciones adicionales declaradas con soporte de servidor: pings, marcadores y registros de daño/curación/muerte; interesantes para coordinación y evaluación de bots/bosses.

## 9. Materiales, partículas, efectos y sonido

Explorar auras, efectos de habilidades, fuego, nieve y ambientación, buscando claridad además de espectacularidad. Herramientas y packs en la selección por capas. Effekseer sirve como fuente de texturas/frames; no se ha integrado su runtime en IL.
Ya descargados y auditados: Kenney UI RPG Expansion y Interface Sounds CC0, con hashes/licencias en download-manifest.json. No integrados; sonido no audicionado.
Steam Audio experimental para L2: autor declara pruebas con IL/Kamael, HRTF para auriculares; distancia sin terminar de ajustar y oclusión por paredes no funcional. No probado por nosotros:
https://github.com/guglovich/Steam-Audio-Lineage-2

## 10. Barco y base flotante de Gracia — pendiente explícito

Capturas antiguas: escenario probablemente Keucereus Alliance Base y muelles, más nave pequeña; identificación de modelo exacto no cerrada. Dos capturas parecen de editor. No prueban navegación ni colisiones.
Publicación localizada después: adaptación de deMEV para IL, 24/02/2016, incluye Keucereus, Gludio Airship Field, Aerial Cleft y Seeds:
https://maxcheaters.com/topic/200222-keucereus-alliance-base-gludio-airship-field-aerial-cleft-seed-of-destructioninfinity-for-interlude/
Página consultada sin enlace de archivo recuperable visible. NO hay descarga verificada, ni confirmación de que contenga el barco exacto. Autor menciona ampliar regiones del mundo y datos de puertas HF P5; adaptar instrucciones al core Mobius, no copiarlas ciegamente.
Usuario pidió dejarlo pendiente. Posibles usos: base de expediciones, barco fijo explorable, defensa por oleadas; transporte móvil exige sincronización adicional.

## 11. Edición de escenarios y ambientación

Capturas muestran Unreal Level Editor bajo UnrealEngine2Runtime, mapas giran.unr y 21_19.unr; una fecha visible es 21/03/2018. Usuario recuerda modificar agua por lava/nieve, quitarla, cambiar suelos/superficies, estructuras y adornos.
Referencias: plaza con materiales celestes/oscuros, altar y partículas, árboles, columnas y cambios alrededor del templo. Verde intenso en torre/cartel parece selección del editor, no color final confirmado. Magenta de partículas: origen/color final sin confirmar.
Recuperar flujo de edición de mapas, materiales/shaders, static meshes, partículas y distribución. Diferenciar cambio visual de colisión/geodata y lógica: lava visual no causa daño por sí sola, nieve no crea suelo transitable. Bots necesitan navegación coherente.
Idea inicial: pequeña plaza de pruebas con variantes de ambientación; después escenarios de evento y zonas de expediciones.

## 12. Cámaras y cinemáticas

Comprobado en nuestro source: serverpackets/SpecialCamera.java y CameraMode.java; Quest.java expone helpers. Scripts Valakas y Sailren usan secuencias SpecialCamera; Sailren.java desde línea 227 encadena planos.
Permite plantear primeros planos, giros, cambios de distancia y tiempos, coordinados por script con animaciones/efectos/mensajes. No se probó una nueva cinemática en juego ni un editor visual de recorridos compatible.
Idea: plano general de plaza → altar → aparición del boss → giro → devolver control y comenzar encuentro. Asegurar restauración de cámara/control y alcance de espectadores.

## 13. Eventos y sistemas jugables

Revisar los scripts existentes antes de importar sistemas externos: Christmas, HeavyMedal, L2Day; CaptureTheFlag, Deathmatch, Elpies, Race, TeamVsTeam, Wedding y clan halls. Diseñar recompensas y progresión junto con los assets. Conectar escenarios, NPC, bosses y cinemáticas a actividades concretas.

## 14. Fafurion Weapons y sockets — 12/10/2026

Primer pack integrado: siete armas IL, IDs54130–54136, base S. Cliente/servidor y GS abierto verificados; revisión visual ingame pendiente. Singer usa M.Atk193 acorde a Imperial Staff. Sin SA/procs custom; Stormer conserva su multiataque normal. Detalles en FAFURION-ARMAS-INTEGRACION.md.

Idea explícita del usuario: sockets para gemas/engranajes con atributos; combinaciones y buffs/skills por bajas PvP/PvE, daño o HP/CP restaurados. Viable con desarrollo propio, todavía NO implementado. Propuesta, ejemplos y puntos de persistencia/UI/balance en FAFURION-SOCKETS-PROPUESTA.md. No dar por activa esta mecánica ni importar sistemas de otra crónica sin adaptar.

## Orden de trabajo orientativo, sin compromiso de implementación

Kevin eligió Veilmar Fortress/Sanctuary of the Dawn Monarch y propuso excursiones al estilo Point Lookout: embarcar, salir narrativamente del mapa general y entrar en otro entorno. RAR verificado y dos vistas 3D preparadas: superficie (941 actores y terreno) e interiores (466). Mapa único 17_24. Por pedido posterior de jugar un agite, se instalaron los cinco paquetes en E:/l2 con respaldo, se generó geodata local y se importaron 26 puertas. .veilmar abre una sala PvP compartida bajo demanda (3052); .veilmar agite invoca nueve combatientes del tipo usado en Elven, .veilmar calma los elimina y la sala vacía también los retira. Accesos a ambos interiores, retorno al origen y revivir. El duelo .ia mago/fisico sigue disponible. Verificación del servidor: pisos, PvP, daño nativo, puertas, obstáculos y spawn/limpieza. Entrada visual con cliente y navegación completa pendientes; campaña/barco no implementados. [Guía](../../../VEILMAR-PVP.md), [detalle técnico](../../veilmar/README.md).

Nueva búsqueda de escenarios poco comunes: jardines de Eva, World Tree Village, Crow Island, templos de Octavis/Orbis, Fantasy Island/Kratei, Naia, catedrales y nuevos packs de mapas. Lista con fuentes y estado de verificación: [Escenarios exóticos en la web](ESCENARIOS-EXOTICOS-WEB.md). No se consideran ya descargados o integrados en nuestro visor.

Avance en barcos y escenarios aéreos: se descargaron mapas y dependencias de Gracia y mallas/texturas de Superion. En el visor hay cuatro escenas con posiciones originales y 164 componentes de Superion. Superion se ensambló desde 643 actores del mapa 22_22 de Helios. No se considera adaptado al cliente Interlude ni instalado en el servidor. Chaos' Air Fortress queda pendiente de una extracción selectiva de Sakura. Detalles: [Escenarios y Superion](../../airships/ESCENARIOS-Y-SUPERION.md).

1. Completar catálogo y variantes; identificar NPC pendientes cuando se retome.
2. Elegir mejoras de interfaz/claridad y probar iconos de habilidades.
3. Recuperar un entorno aislado de edición de mapas y hacer una plaza de prueba.
4. Prototipar un encuentro con un boss, efectos y cinemática.
5. Evaluar sonido espacial y renovación gráfica por separado.
6. Retomar barco/Gracia cuando haya archivos recuperables.

Los temas se elegirán con el usuario. Mantener disponibles las otras capas: equipo, recursos, experiencias y eventos.


## Precarga y pantalla de carga personalizada

12/10/2026: generados e instalados un panel transparente Lineage II / Interlude y un fondo epico de llegada (fortaleza en nubes, airships, aventureros). Se reemplazaron 22 BMP codificados del splash y se agrego un UTX separado con cambio exclusivo de English_LoadingTexture en system-hud/Localization.ini. Fuentes/EXE/DLL/servidor intactos. Verificados roundtrips, alpha, lectura nativa y hashes; primer arranque visual pendiente. Respaldos y restore protegido. Otras propuestas aun sin generar: asedio, santuario azul/dorado y marca del server. [Detalle](../../../PRECARGA-Y-FONDO-EPICO-V1.md).


Marca confirmada: **HELLGAMES**. Referencia aportada: HELL / GAMES en letras serif plateadas. Precarga actualizada e instalada como V2, conservando guerrero, fortaleza y barco. Master startup-hellgames-v2.png; 22 BMP verificados, V1 respaldada. Fondo epico permanece sin texto. Primera inspeccion desde cliente pendiente.
