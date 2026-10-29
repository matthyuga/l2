# Explorador de modelos de Lineage II

## Fichas provisionales para personajes - 27/10/2026

La ficha de cada modelo incorpora nombre elegido o sugerido, territorio propuesto, facción/bando, nivel propuesto, IP propuesto y etiquetas libres. Se guardan con el botón de favoritos junto a la nota anterior; no sustituyen los datos de referencia, niveles ni apariciones del catálogo. Los campos de nivel e IP admiten texto y rangos para no exigir una definición final.

Los nombres propuestos y etiquetas aparecen en las tarjetas. La búsqueda incluye también propuestas y notas, con coincidencia sin distinguir acentos; los filtros de territorio propuesto y etiqueta permiten organizar los elegidos. Las etiquetas se añaden con Enter, coma o el botón Añadir, y se quitan con ×. El territorio admite nuevas entradas y sugiere los ya guardados.

Se conserva la clave localStorage `l2-model-choices`, las notas, NPC seleccionados y propiedades desconocidas de los favoritos antiguos. También se conservan para exportación las referencias guardadas que ya no aparecen en el catálogo. Los nuevos campos se almacenan en `planning`; la exportación conserva `selections` e incorpora `schema_version: 2`. Se siguen guardando por modelo, en el navegador de cada PC.

Comprobado en Chrome aislado: favoritos antiguos y notas, campos desconocidos, referencia fuera del catálogo, edición, recarga, búsqueda por nombre/etiqueta/IP/facción/nota, filtros, deduplicación y eliminación de etiquetas, exportación, recurso sin NPC, referencia nativa y disposición de 390 px. No se usó ni modificó el perfil del navegador del usuario. Evidencias en `tmp/gallery-planning-20261027`; script reproducible `research/gallery-planning-20261027/verify.cjs`. Respaldo de HTML/JS/CSS en `backups/gallery-planning-20261027`. No se cambiaron modelos, stats, spawns ni GameServer. Para cargar los nuevos controles, guardar cualquier edición pendiente y recargar la galería.

## Auditoría completa de texturas - 23/10/2026

Se revisaron las 2.647 vistas únicas del catálogo de 2.955 entradas. Se recuperaron materiales en 105 vistas (229 slots): 100 completas y cinco parciales. Se verificaron geometría y claves intactas, se regeneraron miniaturas y se recorrieron en Chrome las 59 páginas con las 2.809 miniaturas disponibles. Las vistas 3D de muestras reparadas también cargaron.

La interfaz incorpora filtro «Texturas» y estado de materiales en fichas. Permanecen 350 vistas con materiales pendientes, separadas de 329 vistas de colores planos intencionales. No se afirma que todos los shaders del juego estén reproducidos. Se corrigió además el servidor de archivos para JPG/JPEG/WebP y GLB, que antes rechazaba recursos existentes.

Detalle, fuentes, límites y lista completa: [recuperación de texturas](../gallery-texture-repair-20261023/README.md). Respaldo en `backups/gallery-textures-20261023`. Cliente, stats, apariciones y GameServer no modificados.

## Nivel y marco por tipo - 23/10/2026

Las tarjetas incorporan una franja superior con tipo y nivel, marco de color y leyenda. NPC azul; monstruo rojo; criatura/mascota verde; raid dorado; épico violeta; objeto o sin clasificar gris. Las mallas con varios tipos muestran todas las etiquetas y un marco mixto. Criatura/mascota reúne Pet, BabyPet, Servitor, TamedBeast, FeedableBeast y FriendlyMob; es una agrupación funcional, no una clasificación biológica.

`build_npc_facts.py` extrae nivel, tipo y raza de las plantillas activas en `server/game/data/stats/npcs`, sin alterar el servidor ni gallery.json. Genera `npc-facts.json`: 6.753 plantillas, 6.738 con nivel explícito. Los recursos sin plantilla se muestran como «Nivel sin datos». Los niveles pertenecen a esta copia local, no se afirman como balance oficial.

Una tarjeta compartida muestra mínimo-máximo de sus referencias. Al filtrar por lugar se usan sólo las referencias coincidentes. La ficha y el selector de NPC muestran el nivel exacto y se actualizan al cambiar de referencia. Las referencias con nivel ausente producen el aviso «parcial» en el rango.

Pruebas en Chrome: Baium GrandBoss nivel 75, Gremlin Monster nivel 1, Sylvain NPC nivel 70; Death Lord compartido nivel 60-83 y referencia ID20862 nivel75; rangos específicos de habitantes de Dion; filtros de zonas y visualización móvil sin desbordamiento. Evidencia en `tmp/gallery-level-types-20261023`, script `tmp/verify_gallery_level_types.py`; respaldo en `backups/gallery-level-types-20261023`.

## Territorios y lugares - 23/10/2026

La galería incluye filtros «Territorio» y «Zona o lugar». Las tarjetas muestran los nombres e IDs que aparecen en el lugar elegido; al abrir una ficha se selecciona una referencia coincidente. Cambiar «NPC de referencia» actualiza su nombre y sus ubicaciones, con fuentes y un ejemplo de coordenadas. Una malla compartida no implica que todos sus NPC habiten el mismo lugar.

El índice `habitats.json` se genera con `python research/model-catalog/build_habitats.py`, leyendo 183 archivos habilitados de la copia de Mobius en `source/L2J_Mobius_CT_0_Interlude/dist/game/data/spawns`. Registra 3.042 IDs y 185 grupos o sectores. No se modifican stats, cliente, apariciones ni gallery.json. No se declara que la copia local sea una versión oficial intacta. No cubre todas las apariciones creadas desde scripts. Los modelos sin información conservan la opción «Sin ubicación registrada».

Los archivos con nombre aportan una clasificación nominal; los archivos por cuadrícula conservan esa cuadrícula sin inventar un nombre. Los entornos de Ruins of Despair y Ruins of Agony se seleccionan por proximidad a sus destinos administrativos, con radios editoriales de 8.000 y 7.500 unidades y altura entre -5.000 y 0. Ambos están marcados como aproximados: incluyen alrededores, no límites oficiales ni un bestiario exhaustivo. Las fuentes, radios, métodos y hashes se conservan en el índice. Los IDs >=40000 y grupos explícitos de laboratorio se excluyen como evidencia de hábitat clásico.

Verificación: Dion habitantes, Gludin habitantes, entorno de Ruins of Despair, referencia seleccionada coherente, fuentes en ficha, combinación con categoría NPC, ausencia de ubicación para ID custom 62000 y exclusión de Death Knight subterráneo 20136 de los dos entornos superficiales. Pruebas y capturas en `tmp/gallery-habitats-20261023`, script `tmp/verify_gallery_habitats.py`; respaldo en `backups/gallery-zones-20261023`.

## Navegación y zoom - 23/10/2026

Se añadieron controles de página arriba y abajo del catálogo: números cercanos, primera y última página, anterior/siguiente y campo «Ir a página». Los controles se sincronizan, validan el rango y se ajustan cuando cambian los filtros.

El salto de zoom se debía a que OrbitControls truncaba `devicePixelRatio` con una operación de bits: una escala fraccionaria menor a 1 se convertía en cero. Ahora se conserva su valor decimal, se normalizan eventos de rueda en píxeles/líneas/páginas y se limita la magnitud de cada evento para evitar saltos extremos. La corrección está en el control compartido del visor.

Verificado en Chrome aislado: salto por botón a página 3, por campo a 10, última página, rechazo de 9999 y reinicio al filtrar por Baium. Con DPR 0,8, tres pasos de rueda acercaron la cámara gradualmente de distancia 10 a 9,38, 8,80 y 8,25; el paso inverso volvió a 8,80. También se comprobaron eventos grandes, unidades de línea/página, carga 3D de Baium y disposición a 390 px sin desbordamiento horizontal. Evidencia en `tmp/gallery-navigation-zoom-20261023`; script en `tmp/verify_gallery_navigation_zoom.py`; respaldo en `backups/gallery-navigation-zoom-20261023`.

## Corrección de carga - 23/10/2026

El catálogo actual contiene 2.955 registros. Algunos objetos de entorno no incluyen `npcs` y un objeto personalizado no incluye `names`. La interfaz asumía que ambas listas siempre existían y abortaba la carga completa, aunque `/api/catalog` respondía correctamente.

`gallery.js` normaliza esas listas y los campos de presentación antes de construir búsquedas y fichas. Se añadió el título al texto de búsqueda, un mensaje de error más preciso y una versión en la URL del módulo para evitar la copia anterior en caché. No se modificó gallery.json ni se eliminaron modelos.

Verificación con Chrome aislado: 48 tarjetas iniciales y 2.195 resultados visibles con los filtros predeterminados; búsqueda por ID 29020 encuentra Baium; ficha de Baium y WebGL cargados, sin mensaje pendiente y botón «Ver imagen». Evidencia en `tmp/gallery-load-20261023`; respaldo en `backups/model-gallery-load-20261023`.

Actualización: 843 registros, 842 miniaturas. Se añadieron dos vistas de Veilmar (superficie e interiores), con 1.407 actores estáticos y el relieve original. Buscar «Veilmar». [Archivos, territorio y límites](../veilmar/README.md).

Estructuras aéreas: cuatro escenarios reconstruidos desde actores de mapas originales (Gludio, Keucereus, zona aérea 13_25 y Superion), más 164 componentes de Superion. Buscar «Estructuras aéreas» o «Superion». [Procedencia, límites y enlaces 3D](../airships/ESCENARIOS-Y-SUPERION.md). Los conteos siguientes corresponden al historial anterior.

12/10/2026 — Hay 20 vistas de Gracia (piezas de nave, muelle y montaje), 663 registros y 662 miniaturas en total. Buscar «Gracia». Montaje corregido según VehiclePartsGrp, con materiales opacos reparados y offsets de las piezas. El montaje y las nuevas piezas skeletal se ven en WebGL; las piezas estáticas originales también se abren en UModel desde paquetes aislados. Procedencia y límites en [Estructuras aéreas](../airships/README.md).

Actualizado12/10/2026. Abrir `GALERIA-MODELOS-L2.cmd` en la raíz de l2-local. Inicia una galería local en el navegador con640 miniaturas y vistas3D. También se conserva `VER-MODELOS-L2.cmd` para abrir directamente los paquetes en UModel. Se completó la instalación existente con SDL2.dll x86, obtenida del repositorio oficial de Gildor: faltaba esa dependencia y el visor fallaba al crear la ventana3D.

La galería usa Node portable incluido, en127.0.0.1:32280, y Three.js r160 incluido localmente. No requiere Internet, Blender, instalaciones globales ni cambios al GameServer para usarla. Blender3.5.1 de D:/BlenderVersions se utilizó solo para generar las imágenes; imágenes/modelos/texturas y programas de uso están en el discoE portátil. Las rutas se resuelven respecto de l2-local y el cliente hermano ../l2.

Funciones: búsqueda por nombre/ID/malla, filtro por categoría y paquete, favoritos con notas, exportación de selección JSON, imagen y vista3D giratoria, elección de NPC de referencia y copia de ID. El botón «Abrir con animaciones» abre esa malla en UModel. Los favoritos se guardan en el navegador de cada PC; exportarlos permite llevar la selección y entregarla para el trabajo de NPC/bots. Seleccionar un NPC de referencia no cambia automáticamente los colores del modelo: se muestra una apariencia representativa.

Amber NPC y summon se añadieron desde el npcgrp instalado actual, en «Personalizados». Ahora hay643 registros y642 miniaturas:640 originales más2 de Amber. `comparar.html` ofrece una comparación giratoria con luz de estudio/ambiente oscuro, material actual aproximado, prueba difusa o mezcla20% y referencia nativa elegible. Las pruebas son simulaciones de estudio; no se instalan en el juego. Ver AMBER-INTEGRACION-VISUAL-COMPARATIVA.md y amber-comparison/audit.json. `build_gallery.py` conserva las entradas personalizadas al regenerar el catálogo base.

El catálogo contiene641 referencias/objetos deduplicados (mallas del catálogoNPC más las mallas de seis paquetes originales). Hay640 recursos leídos y renderizados; LineageMonsters.alchemic_box_m00 figura en el catálogo base pero no está en los paquetes de este cliente. Se muestra como no disponible al activar «Mostrar recursos sin imagen». En72 modelos hay algún material sin textura representativa; la ficha lo indica. Muchos de ellos no tienen NPC asociado. Las vistas no incluyen partículas/reflejos/animaciones especiales del juego.

Validación:640 glTF/bin/miniaturas legibles, todos los enlaces de texturas presentes, PNG384x420 sin candidatos uniformes vacíos. SDL y UModel tienen arquitectura x86 compatible. Ventana nativa «UE Viewer build1590» abierta y respondiendo; API de apertura probada con Gremlin. Galería y WebGL texturizado comprobados mediante capturas de Chrome headless aislado. El control de UI nativa no estuvo disponible; no se inspeccionó visualmente su ventana. Solicitudes de origen ajeno o modelo inexistente rechazadas403/400. `verification.json` guarda resultados y hashes. No se modifican cliente ni stats/IA/servidor, y no hace falta reiniciarlos.

Seleccionar uno de los tres paquetes de monstruos, los tres de NPC o una raza jugable. El visor muestra la malla en3D; ratón izquierdo rota, derecho acerca, central desplaza. PgUp/PgDown cambia objeto; [ / ] cambia animación; X reproduce en bucle, F centra y H muestra ayuda. Ctrl+S toma captura. En paquetes de razas hay piezas de cuerpos/armaduras, no siempre un personaje completo; Ctrl+T permite marcar mallas para vista multipartes.

## Inventario comprobado

- Servidor actual:6590 plantillas XML (6519 base y71 custom según inicio). Las unidades repetidas del mundo no son modelos independientes.
- Catálogo original de NPC conservado del trabajo de Amber:6519 filas,550 referencias de malla no vacías distintas. Incluye algunos objetos/estructuras, no550 personajes completos. No incorpora nuevas filas de Amber ni paquetes jugables de razas/armaduras.
- Seis paquetes originales del cliente:634 objetos SkeletalMesh: LineageMonsters239, LineageMonsters2 85, LineageMonsters3 74, LineageNpcs179, LineageNPCs2 30, lineagenpcsev27. Un objeto malla puede ser variante/pieza, y no necesariamente una especie independiente.

`modelos-npc.csv` agrupa por malla y muestra nombres/IDs de NPC, cantidad de plantillas, variantes de texturas y tipos del servidor. `inventory.json` conserva todos los IDs asociados y los objetos enumerados en cada paquete; los `.list.txt` son las salidas reales de UModel. `inventory.py` puede regenerarlos sin alterar archivos del juego.

La apariencia final puede depender de sustituciones de texturas del npcgrp, piezas adicionales y materiales del cliente. El visor de una malla no garantiza que todas las variantes tengan exactamente el aspecto final ingame. Algunos materiales pueden requerir ajustes de visualización.

## Uso en nuestro proyecto

Un NPC/monster/servitor puede reutilizar una apariencia nativa mediante su ID visual de cliente; estadísticas y conducta se configuran aparte. Un NPC con aspecto de boss no adquiere automáticamente sus estadísticas ni poderes. Para nuestros bots Player hay que comprobar un mecanismo de apariencia/transformación y compatibilidad de animaciones: no basta con sustituir el ID de NPC en sus datos de clase.

La galería está generada en `gallery.json`, `thumbs/` y `exports/`, con nombres/IDs asociados y aviso de materiales incompletos. Las imágenes muestran una pose base; los efectos y la animación real se revisan con el visor nativo. Los paquetes de razas jugables contienen piezas de armaduras/cuerpos y se exploran desde el menú de UModel, sin confundirlas con personajes completos del catálogoNPC.

Para regenerar: Python3.10 con Pillow ejecuta `build_gallery.py`; Blender compatible ejecuta `render_gallery.py` en modo `--factory-startup -b --python`. El primer script conserva recursos preparados; el segundo actualiza miniaturas cuando cambian los glTF. `fix_alpha.py` corrige el caso de texturas especulares con alpha usado por el shader, para no recortar cuerpos opacos. `verify_gallery.py` comprueba el catálogo y los enlaces. Respaldo del acceso anterior: backups/model-gallery-2026-10-12. Sin commit ni push.

Herramienta y controles: https://www.gildor.org/en/projects/umodel
