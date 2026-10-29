# Taller de escenarios — L2 Lab

## Cielos, clima, partículas y audio — 21/10/2026

El selector de escenarios incluye **Gludio · Jardín de las Brisas (animado)**: el muelle aéreo con jardín, dos árboles, flores, pérgolas, bancos, fuentes y nueve emisores animados. Abrirlo carga `gludiobrisas1-animado.json`, conserva un borrador separado y abre la biblioteca de ambientes. Acceso directo: http://127.0.0.1:32290/?project=gludiobrisas1-animado.json&ambientes=1 . Lanzador dedicado: `E:\l2-local\ABRIR-MUELLE-JARDIN.cmd`. El proyecto original permanece intacto; los cambios se guardan desde el Taller. Verificación: garden-atmosphere-verification.json; captura preview-muelle-jardin-ambientes.png.

Sobre el visor está el botón **☁ Ambientes**. Abre una biblioteca con búsqueda y páginas: **Cielos**, **Partículas** y **Audio**. Elegir un cielo lo aplica a la escena; elegir una partícula usa esa imagen en un emisor de prueba. Audio reproduce fragmentos de hasta 12 segundos con controles de reproducción y volumen; cerrar la biblioteca detiene el sonido.

En **Vista → Ambiente** se elige lluvia, tormenta con destellos, nieve, tormenta de arena, viento/polvo, cenizas o niebla. También se ajustan giro del cielo, luz, cantidad de partículas, viento y niebla. **Restaurar ambiente de estudio** recupera el fondo negro y la luz original. El interruptor de animación de Vista pausa también el clima.

Cielo y configuración de clima se conservan en borrador, proyecto JSON y Deshacer/Rehacer. Los proyectos anteriores, sin ambiente, siguen abriendo con el entorno de estudio. El audio es una escucha previa: no se guarda ni se reproduce automáticamente al abrir un proyecto.

Catálogo inicial: 89 cielos (59 Poly Haven, 25 Screaming Brain Studios y 5 Kenney) y 182 texturas de partículas. Las vistas previas están en `../atmosphere-library/preview`, sin modificar originales. **Actualizar descargas** prepara nuevas vistas de los ZIP de Sonniss terminados y actualiza la biblioteca; los formatos de audio no compatibles se registran en `preview-catalog.json`. Freesound sigue pendiente de login. Los originales de Sonniss permanecen en sus ZIP.

Acceso directo con la biblioteca abierta: http://127.0.0.1:32290/?ambientes=1 . Implementación: atmosphere.js/css, atmosphere-schema.js, atmosphere-catalog.cjs y `../atmosphere-library/build-preview.py`. Verificación en Chrome con WebGL: verify-atmosphere.cjs, atmosphere-verification.json y capturas preview-biblioteca-ambientes.png / preview-ambiente-arena.png.

El clima es una simulación visual del Taller. Su configuración todavía requiere una integración separada en el cliente Interlude.

## Desbloquear para editar

Al seleccionar un elemento, encima de las herramientas del panel izquierdo aparece su estado: **Bloqueado para editar** o **Editable**. El botón visible **Desbloquear para editar** habilita la selección y sus piezas. Si el bloqueo viene de un padre se muestra su nombre; al abrir esa ruta se protegen explícitamente las ramas hermanas para no habilitarlas accidentalmente. El candado del árbol ahora refleja también el bloqueo heredado o parcial y permite desbloquearlo directamente.

En el panel derecho están **Desbloquear grupo/rama** y **Desbloquear todo**, cada uno con su acción inversa de bloqueo. Grupo/rama usa el grupo de escena más cercano o, si se seleccionó una pieza sin grupo, su objeto completo; el tooltip indica el nombre del destino. Desbloquear una rama limpia los candados internos de esa rama, conservando los de las demás. Desbloquear todo limpia los bloqueos de objetos, grupos y piezas internas de toda la escena. Los contenedores con piezas protegidas también quedan protegidos contra movimientos o edición global hasta desbloquear su rama.

Los cambios de bloqueo se guardan con el proyecto, entran en deshacer/rehacer y no modifican geometría ni texturas. No se desbloquea nada automáticamente al aplicar una textura. Implementación en lock-controls.js y app.js, con validación de alcance en verify-lock-controls.cjs (incluye grupos anidados y preservación de ramas externas). Captura preview-desbloqueo-visible.png.

## Panel izquierdo compacto y ajustable

La barra de secciones y las acciones del panel usan iconos con nombre accesible y ayuda al pasar el cursor. Terreno conserva el nombre de la textura y la miniatura, con **Aplicar textura** a su derecha. Debajo hay iconos para abrir la biblioteca, restaurar material, reemplazar o superponer una capa. Repetición y opacidad tienen iconos, valores editables y porcentaje visible; la opacidad se habilita en modo capa.

El borde derecho del panel izquierdo es un separador arrastrable con cursor ↔ (`ew-resize`). Admite ancho210–520px, limitado por el espacio disponible para el visor. Recuerda el ancho en el navegador al recargar y al ocultar/reabrir el panel. Doble clic restaura el ancho inicial adaptable. Con el separador enfocado, flechas izquierda/derecha ajustan10px (Shift30px), Home restaura y Escape cancela un arrastre. Redimensionar actualiza el visor sin mover la cámara ni alterar el proyecto. `sidebar-ui.js` concentra estas funciones; `verify-sidebar.cjs` y preview-sidebar-compacta.png verifican uso y distribución a1360x768.

## Ventana de escena y detalles

### Seleccionar piezas desde la vista 3D

El selector sobre el visor permite elegir **Objeto**, **Piezas** o **Material**. Objeto mantiene la selección de objetos completos. Piezas elige la malla interna bajo el cursor; Alt + clic lo hace temporalmente desde cualquier modo. Material elige la pieza y el material de la cara pulsada, dejando seleccionado ese material en Terreno. El árbol abre la ruta correspondiente y desplaza su fila a la vista, conservando los iconos y bloqueos.

El cursor anticipa en celeste la geometría seleccionable; la selección se remarca en dorado con relleno tenue y bordes de la geometría real. Elegir un material desde Terreno también remarca únicamente las caras que lo usan en la pieza seleccionada. **Resaltar** permite ocultar estos auxiliares para apreciar el color de la textura. Los auxiliares no cambian materiales ni se guardan/exportan o interfieren con la colocación y los rayos de selección.

Las piezas son los nodos y mallas que conserva el recurso glTF. Un material puede cubrir varias zonas de una misma malla; elegirlo no crea módulos geométricos nuevos ni permite cortar una región arbitraria. Implementación: selection-highlights.js e integración en app.js/scene-tree.js. verify-piece-picking.cjs verifica selección por cursor, revelado del árbol, Alt+clic, material de cara, resaltado parcial, protección por bloqueo y guardado/reapertura de la textura editada.

El árbol de **Escena** está a la derecha de la vista 3D. Las flechas abren grupos y piezas internas reales del glTF. Cada fila tiene iconos de ojo y candado; ocultar un padre oculta su rama y bloquearlo protege a sus hijos. Seleccionar una fila o un objeto en el visor actualiza los detalles de la izquierda.

La barra izquierda contiene Añadir, Detalles, Posición, Material, Vista y **Terreno** (debajo de Vista). Detalles muestra nombre, origen y acciones; Posición reúne ubicación, rotación y escala; Material muestra miniaturas de los materiales y abre su edición en Terreno. Terreno contiene las herramientas de textura y capas, antes llamadas Superficies. El panel izquierdo se reduce a una barra de 44px con Mostrar panel; el árbol derecho permanece disponible.

Ctrl + clic permite seleccionar varios objetos completos de la misma rama. **Agrupar** conserva las piezas independientes bajo un padre transformable; **Desagrupar** devuelve los hijos a la rama anterior conservando sus transformaciones mundiales. Se admiten grupos anidados y duplicar/quitar una rama completa. Las piezas internas permiten editar sus parámetros, materiales, nombre, visibilidad y bloqueo dentro de su objeto.

**Fusionar** combina los objetos seleccionados, o las piezas de un grupo seleccionado, en una malla estática con sus materiales. Requiere objetos visibles y desbloqueados, admite hasta tres millones de vértices y excluye esqueletos, morphs e instancias. Se conserva una receta de sus componentes en el JSON para reconstruirla; Deshacer recupera los objetos independientes. No realiza operaciones booleanas ni soldadura de vértices. Las combinaciones de escala/rotación que introducen cizalla se rechazan al reorganizar objetos para preservar las posiciones.

Jerarquía, modificaciones de piezas internas, materiales y recetas de fusión se conservan en borrador, JSON y deshacer/rehacer. La lectura sigue admitiendo proyectos antiguos sin estos campos. Una importación con referencias internas inválidas conserva la escena abierta. Implementación en scene-tree.js, workspace.css, merge-meshes.js y structure-schema.js, integrada con app.js y el servidor. Pruebas: verify-hierarchy.cjs y verify-nested-groups.cjs; capturas preview-hierarchy-workspace.png.

## Biblioteca modular y nombres en español

El icono Añadir abre una ventana de catálogo independiente: arrastrar su cabecera mueve la ventana; el botón de expandir alterna pantalla amplia y tamaño normal; la esquina inferior derecha permite cambiar su tamaño. Cerrar o Escape devuelve el espacio de trabajo. Seleccionar una miniatura cierra la biblioteca e inicia la colocación sobre una superficie.

El catálogo muestra miniaturas en cuadrícula, búsqueda, filtro de estructuras/todo y categorías. Se puede alternar Nombres en español / Nombres originales. La búsqueda consulta ambos. Los originales se conservan debajo de cada nombre y los identificadores de recursos no cambian. Las traducciones son parciales: algunos nombres comunes tienen equivalencia revisada; otros usan términos orientativos señalados; nombres propios y códigos desconocidos siguen originales. No se tradujo el cliente de Lineage2 ni se promete una localización completa del catálogo.

Implementación: asset-library.js/css. Pruebas de ventana, expansión, arrastre, idioma, búsqueda, categorías y colocación: verify-library.cjs y library-verification.json. Captura preview-biblioteca.png.

## Controles Studio, nodos y cámaras

Actualización del17/10: panel izquierdo de detalles con iconos; desmarcar **Mostrar panel** lo reduce a44px. Cualquier icono abre su sección. La vista3D ocupa el centro y el árbol de escena el costado derecho.

Navegación adaptada tras lectura estática de Chara y KKUS: izquierdo arrastrado orbita; derecho horizontal cambia distancia y vertical cambia altura; central desplaza en pantalla; izquierdo+derecho mueve en profundidad. Shift acelera4x, Ctrl reduce a0,6x (Ctrl tiene prioridad si se pulsan ambos). W/E/R seleccionan mover/rotar/escalar. F lleva la vista al pivote seleccionado manteniendo ángulo/distancia. C trae el objeto al punto de enfoque de la cámara (requiere desbloquearlo). Q alterna pivotes de objetos seleccionables, no vértices ni huesos. Las teclas no actúan mientras se escribe en campos.

Diez memorias de cámara sobre la vista: **Save** captura ubicación, ángulo mediante punto de enfoque y FOV; el número recupera esa toma. Se conservan en borrador y JSON; usar Guardar versión para crear una copia de disco. Los proyectos antiguos siguen admitidos sin estos campos. Hay buscador de objetos colocados independiente de la biblioteca.

Evidencia del comportamiento original y diferencias: ../studio-ui-analysis/NAVEGACION-CHARA-STUDIO.md. Pruebas específicas: verify-studio-controls.cjs / studio-controls-verification.json. La actualización no instala decoraciones en el cliente ni cambia mapas originales.

Primera version local, 17/10/2026. Prioridad aprobada por Kevin: **muelle y aeronaves, empezando por el muelle**.

## Abrir

Ejecutar `E:\l2-local\19-EDITOR-ESCENAS-L2.cmd` o visitar http://127.0.0.1:32290 mientras el servidor este activo. El lanzador usa el Node portable existente y abre el navegador predeterminado. No requiere Computer Use ni Internet para funcionar. No inicia GameServer ni modifica clientes.

## Empezar

1. El muelle abre con ocho piezas arquitectonicas, bloqueadas para evitar movimientos accidentales.
2. Orbitar arrastrando con el boton izquierdo; acercar con la rueda; desplazar con el derecho.
3. Buscar un recurso a la izquierda, seleccionarlo y pulsar una superficie visible para colocarlo. Esc cancela.
4. Seleccionar un objeto en la vista o en el árbol derecho. Editar posicion, rotacion y escala con los ejes del visor o desde Posición. Para editar una pieza base, desbloquear su candado en el árbol.
5. W mueve, E rota, R escala, F encuadra, Supr quita el objeto desbloqueado. Ctrl+Z deshace, Ctrl+Y rehace, Ctrl+S guarda una version.
6. Guardar version escribe un JSON nuevo en `research/scene-editor/projects/`, sin sobrescribir versiones previas. Exportar JSON descarga una copia. Abrir proyecto permite seleccionar un JSON exportado o guardado. Cambiar de escena o abrir otro proyecto guarda primero los cambios pendientes en una version independiente.
7. El selector superior permite pasar a la aeronave Gracia: casco, velamen, cola y mando editables por separado. No es la nave externa instalada, Aurelia ni Vigilia; es una referencia del catalogo para iniciar el trabajo con aeronaves.

El borrador del navegador ofrece recuperacion al volver a abrir. Las versiones en disco y el JSON exportado son las copias recomendadas para conservar el trabajo.

## Alcance y limites

### Superficies del piso

Seleccionar una pieza en el árbol derecho y desbloquearla con su candado. Abrir **Terreno** desde la barra izquierda: elegir el material del piso (por ejemplo `G_kserth_tmfloor`), una textura y aplicar como reemplazo o capa. La capa permite ajustar opacidad; Restaurar material recupera el material heredado. Los cambios específicos de una pieza interna tienen prioridad sobre los materiales de su padre. Se guardan en JSON, borrador y deshacer/rehacer, sin alterar el mapa original.

La proyeccion es horizontal, pensada para pisos, con repeticion por cada cuatro metros del visor. Afecta todas las caras de la pieza que comparten el material elegido. No hay pincel por zonas, escultura del terreno ni exportacion automatica al juego. `surfaces.js/css` implementan la herramienta y `verify-surfaces.cjs` verifica bloqueo, aislamiento entre objetos, reemplazo, capa, guardado, recarga, restauracion, deshacer y rechazo de texturas no permitidas.

La biblioteca CC0 descargada se administra en `../texture-library/`. El boton Explorar texturas abre una galeria ampliable con busqueda, miniaturas y categorias en español. `/api/textures` devuelve los materiales terminados de `catalog.json`; `texture-catalog.cjs` mantiene permitidos sus identificadores para guardar proyectos. Recargar incorpora nuevas descargas. El visor utiliza el color 2K y conserva los demas mapas y los ZIP originales para futuras mejoras. `verify-cc0-textures.cjs` verifica imagen real de 2048x2048, filtros, seleccion, render WebGL, guardado y recarga.

- Editor de **composicion de escenas**: seleccionar, mover, rotar, escalar, duplicar, ocultar, bloquear y colocar recursos. No edita vertices, UV, esqueletos ni animaciones.
- Reutiliza catalogo/glTF/texturas locales de research/model-catalog. Se indexaron 2.286 recursos preparados; el filtro inicial muestra estructuras y objetos. Las referencias de modelos y superficies no acreditan que todos sean colocables como StaticMesh en Interlude sin conversion adicional.
- Materiales, iluminacion, cielo, nubes y efectos son una aproximacion. La escena del muelle contiene su arquitectura; no representa todo el mapa vivo ni sus otras instalaciones.
- Los campos muestran **metros del visor glTF**, con Y como altura. No son las coordenadas nativas X/Y/Z del juego. Se guarda la huella SHA-256 del mapa de Lab y su marco de referencia en data.json/proyectos para un futuro puente validado.
- No abre ni guarda `.unr` completos. Los proyectos se guardan en formato `l2-scene-editor-v1`; **todavia no existe un instalador de estos proyectos en el juego**. Incorporar la decoracion aprobada requerira un paso separado que preserve paquetes/actores originales y gestione geodata si cambia el recorrido.
- No hay cambios a E:/l2, E:/l2-hellgames ni E:/l2-academy. No se cambio el editor Unreal existente.

## Estructura y verificacion

`server.js`: servidor HTTP local en 127.0.0.1:32290, recursos del catalogo en lectura y guardado limitado a JSON nuevos de projects/. No expone los proyectos por HTTP; para abrirlos se usa el selector de archivos. El POST valida formato, recursos, IDs y transformaciones y exige origen local.

`app.js`, `index.html`, `style.css`: interfaz Three.js r160 con OrbitControls, TransformControls y SkeletonUtils. Los dos ultimos se obtuvieron del repositorio oficial mrdoob/three.js, tag r160; MIT (licencia en ../model-catalog/vendor/THREE-LICENSE.txt).

`build_data.py`: constructor de referencias al catalogo y metadatos; lee el mapa para su SHA-256, sin escribir en el cliente. No hace falta ejecutarlo para usar el editor.

`verify.cjs`: pruebas funcionales en Chrome headless aislado mediante Playwright ya disponible. Render WebGL real de muelle y nave, colocacion de objeto en superficie, transformacion numerica, deshacer/rehacer, duplicacion, ocultar/mostrar, guardado versionado, eliminacion/reapertura y validaciones HTTP. Resultado verification.json; imagenes preview-muelle.png, preview-decoracion.png y preview-aeronave.png. Los JSON creados por QA se identifican en el informe.

No commit ni push. El proyecto de trabajo actual es exclusivamente L2 Lab.

## Interfaz Studio
Kevin prefiere flujo tipo Chara Studio: fondo negro, paneles semitransparentes, detalles a la izquierda, vista3D central y árbol de escena a la derecha. Herramientas Mover/Rotar/Escalar y encuadre en la parte superior izquierda. Rail de aspectos: Añadir, Detalles, Posición, Material, Vista y Terreno. Opacidad inicial78%; cuadrícula inicialmente oculta. El borrador anterior se restaura automáticamente al recargar. Pruebas a1360x768 sin desbordamiento horizontal. Distribución inspirada en el flujo Studio, sin replicar todas las funciones de Chara Studio.

