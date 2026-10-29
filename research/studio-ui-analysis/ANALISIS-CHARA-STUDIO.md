# Chara Studio como referencia del Taller de escenarios

17/10/2026 · referencia local Koikatsu RX22 · destino L2 Lab.

## Resultado

La interfaz se puede adaptar a nuestro editor con una base concreta: Chara Studio combina una barra permanente de categorías, paneles contextuales independientes, un árbol de escena y cámaras memorizadas. La vista 3D conserva el mayor espacio posible. Conviene reproducir esa organización y sus flujos con nuestros controles, manteniendo la preferencia de Kevin por las opciones a la izquierda y la escena a la derecha.

Este trabajo es **análisis y propuesta**. No cambia todavía la interfaz del Taller ni instala componentes en Chara Studio.

## Fuentes e identidad

- Captura de Chara Studio aportada por Kevin en este hilo: observación visual de la distribución y de una instalación con plugins. No es una captura runtime tomada por REA.
- `K:/JUEGOS/KOIKATSU 22/CharaStudio_Data/Managed/Assembly-CSharp.dll`: REA confirmó Unity Mono / CIL, metadatos completos, SHA-256 `361ee4c5a7dafbfa56845bb0a71a034ef388ce07663b7709b858136eb3486958`, MVID `cdaa1658-214e-4370-bd5b-16aee18cdad1`.
- REA inspeccionó 14 tipos de interfaz y control: 345 campos, 593 métodos y 3.458 aristas estáticas de llamada en esa selección. Una segunda selección añadió `Studio.CameraSelector` y `Studio.GuideInput`. No se ejecutó ni cargó el ensamblado en un CLR.
- `CharaStudio_Data/level1`, leído con UnityPy: 2.389 GameObjects y 2.376 RectTransforms; se resolvieron 13 identidades de controladores. La asociación de scripts usa sus cabeceras base; no decodifica todas las propiedades serializadas de los scripts.
- `research/scene-editor/app.js`, `index.html`, `style.css`: estado actual de nuestro Taller. La disposición se construye dinámicamente en app.js.

Evidencia persistida: [rea-selected-evidence.json](rea-selected-evidence.json), [rea-call-edges.json](rea-call-edges.json), [rea-camera-guide-evidence.json](rea-camera-guide-evidence.json), [unity-ui-layout.json](unity-ui-layout.json). Script de lectura reproducible: [inspect_ui_assets.py](inspect_ui_assets.py).

Identificadores principales REA:

| Evidencia | Alcance |
|---|---|
| `ev_57aeb5f6ff6b394d25f0c523e243d85ccc7b6098e4ca83418acea5123ec61dc4` | Identidad y clasificación del ensamblado |
| `ev_4533f1694573c21bce09730c23364c24f276a4305ea22f3268576d0f352b7914` | Controladores de menús, Workspace, árbol, objetos, cámaras y deshacer |
| `ev_c654ea105d7bfa49cbd4c47c2be6bb3ffeea0fe9a4fa33b1f893278e10e74e73` | Selector de cámara y entrada numérica de transformaciones |

Los tokens de métodos y campos del JSON solo son válidos para este hash/MVID. Las aristas CIL son referencias estáticas, no llamadas observadas en ejecución.

## Cómo está ubicado

| Zona | Observación de la captura | Verificación en archivos | Adaptación al Taller |
|---|---|---|---|
| Izquierda superior | Columna Add / Anim / Sound / System | `Canvas Main Menu/00_Command` contiene Add, Manipulate, Sound y System anclados arriba a la izquierda, separados verticalmente | Barra estrecha permanente: Añadir, Escena, Transformar, Cámara, Entorno y Proyecto |
| Panel junto a las categorías | Puede mostrar opciones sin ocupar toda la pantalla | `RootButtonCtrl` enlaza add/manipulate/sound/system; `AddButtonCtrl` controla la selección y un canvas | Un panel contextual semitransparente que puede plegarse; conservar búsqueda y selección al alternar secciones |
| Parte superior central | Diez botones numerados y Save; selector Set Camera | `Canvas System Menu/02_Camera` contiene slots `00` a `09`, cada uno con Button Save y Button Load. `SceneInfo.cameraSaveData`, `CameraControl.Export/Import` y `CameraSelector.SetCamera/NextCamera` respaldan el sistema de datos | Diez memorias de vista con guardar/recuperar, nombres opcionales y persistencia dentro del proyecto |
| Superior derecha | Accesos Menu / Work / Move / Color / Option / Camera | `00_Draw` contiene Button Menu, List, Input, Color, Manipulate y Camera List, anclados arriba a la derecha | Accesos compactos para mostrar/ocultar paneles; edición sin tapar innecesariamente la escena |
| Workspace a la derecha | Árbol desplazable, estados verdes y búsqueda visible | `WorkspaceCtrl` se asocia a `Canvas Object List`; `TreeNodeCtrl` a `Image Bar/Scroll View`. Métodos y campos de padres, hijos y selección múltiple verificados | Árbol de objetos con grupos, visibilidad por fila y búsqueda de objetos colocados; ubicación configurable, inicialmente en el panel izquierdo según la preferencia de Kevin |
| Pie del Workspace | Operaciones de objetos y botones de plugins | Campos buttonParent, buttonDelete, buttonCopy, buttonDuplicate, buttonFolder, buttonCamera y buttonRoute; OnClickParent llama a TreeNodeCtrl.SetParent | Agrupar, duplicar, quitar, renombrar y cambiar padre; incorporar solo operaciones que tengan soporte real |
| Izquierda inferior / edición numérica | Utilidades pequeñas, ejes y herramientas adicionales | `Canvas Guide Input/Guide Input` se ancla abajo a la izquierda. Contiene Pos/Rot/Scl con X/Y/Z y restauración por sección | Panel compacto de transformación que conserve siempre el objeto seleccionado; controles local/global y restaurar cada sección |
| Escenario | Fondo 3D dominante; ventanas discretas superpuestas | Distintos Canvas para menú principal, menú de sistema, Workspace y Guide Input | Vista 3D con opción de ocultar interfaz y paneles desacoplables o plegables |

Las posiciones de los RectTransforms son **coordenadas del canvas guardado**, no píxeles exactos de la captura de Kevin. El escalado de Unity, la resolución y los plugins pueden cambiar el resultado final.

## Estructura de comportamiento comprobada

**Menús y contexto.** `RootButtonCtrl` posee referencias add/manipulate/sound/system y selección. `ManipulatePanelCtrl` distingue charaPanelInfo, itemPanelInfo, lightPanelInfo, folderPanelInfo, routePanelInfo, cameraPanelInfo y routePointPanelInfo; maneja OnSelect, OnDeselect, SetActive y Deactivate. Esto respalda separar herramientas por tipo de objeto. Para L2 no necesitamos copiar todas las categorías de personajes.

**Árbol real.** `TreeNodeObject` posee parent, m_child, visible y permisos de añadir hijo/copiar/borrar. `TreeNodeCtrl` implementa SetParent, RefreshHierachy, SelectMultiple y SelectSingle. `WorkspaceCtrl.OnClickParent -> TreeNodeCtrl.SetParent` es una arista estática concreta. No es solamente una lista con nombres indentados.

**Herramientas de transformación.** `GuideObject` contiene modos de posición/rotación/escala y métodos MoveWorld/MoveLocal. `GuideObjectManager` mantiene objetos seleccionados y cambios de modo. `GuideInput` tiene inputPos/inputRot/inputScale y métodos OnEndEditPos/Rot/Scale y OnClickInitPos/Rot/Scale. Adaptación: gizmo, números y espacio local/global coordinados.

**Propiedades por objeto.** `MPItemCtrl` ofrece controles de color, alpha, emisión, patrones y otras capacidades específicas; `MPCameraCtrl` usa nombre y activo. En nuestro Taller, una pieza arquitectónica, un adorno y una aeronave pueden compartir transformaciones y mostrar solo propiedades compatibles. Editar materiales en el visor no equivale a convertirlos automáticamente a shaders de L2.

**Proyecto y cámaras.** `Studio` expone AddFolder, AddCamera, Duplicate, SaveScene, LoadScene e ImportScene. `SceneInfo` guarda dicObject, cameraSaveData y opciones ambientales. `UndoRedoManager` mantiene pilas undo/redo y notificaciones CanUndo/CanRedo. Podemos adoptar el modelo de escena persistente con vistas memorizadas y operaciones reversibles.

## Diferencias con nuestro editor actual

| Ya existe en el Taller | Falta para acercarlo al flujo de Studio |
|---|---|
| Panel izquierdo semitransparente y fondo negro | Barra de categorías más compacta, panel contextual plegable y ancho ajustable |
| Biblioteca con buscador, filtro y miniaturas | Separar búsqueda del catálogo y búsqueda de objetos de la escena |
| Lista plana de objetos y propiedades | Jerarquía con grupos/padres/hijos y selección múltiple |
| Mover, rotar, escalar y ajuste | Selector local/global y restaurar posición/rotación/escala por separado |
| Orbitar y encuadrar | Diez cámaras/vistas guardadas, FOV y estado persistente de cámara |
| JSON versionado, importación y borrador | Guardar cámaras, grupos y preferencias de disposición en un formato compatible |
| Una disposición fija a la izquierda | Plegado rápido de interfaz y Workspace opcional desacoplado |

## Propuesta de distribución

Configuración inicial: preservar opciones a la izquierda y vista a la derecha.

```text
┌──────────── Proyecto · Abrir · Guardar · Deshacer ────────────────────────┐
│ Categorías │ Panel contextual     │          Cámaras 1 … 10              │
│            │                      │                                      │
│ Añadir     │ Búsqueda / categorías │                                      │
│ Escena     │ o árbol de objetos   │             VISTA 3D                 │
│ Transformar│ o transformaciones   │                                      │
│ Cámara     │ o opciones de cámara │                                      │
│ Entorno    │                      │                                      │
│ Proyecto   │                      │                                      │
└────────────┴──────────────────────┴──────────────────────────────────────┘
```

La captura de Studio ubica Workspace a la derecha. Para imitarla más literalmente se puede permitir acoplar ese árbol a la derecha, sin obligar a abandonar la preferencia anterior. No conviene convertir todos los paneles en ventanas flotantes al mismo tiempo: en 1360×768 reduciría demasiado la superficie útil.

### Orden de adaptación

1. **Navegación y cámaras:** barra de categorías, panel contextual plegable, búsqueda separada de escena y diez memorias de vista. Es lo más útil para comparar antes/después del muelle desde el mismo encuadre.
2. **Organización de escenas:** grupos/carpetas, búsqueda del árbol, visibilidad por fila, selección múltiple y transformaciones local/global. Requiere actualizar modelo de proyecto, validación y deshacer; un cambio visual aislado no basta.
3. **Materiales y entorno:** propiedades compatibles por recurso, controles de luces/fondo y posteriores herramientas de materiales. El puente a paquetes L2 se mantiene separado y verificable.

## Límites y pendientes

- No se pudo corroborar una instancia CharaStudio.exe activa al inicio de esta inspección. No se lanzó una nueva, no se manipuló una escena y no se usó inyección runtime.
- No se probaron clicks, arrastre, teclas ni cambio de cámaras dentro de Chara Studio en esta sesión. Los flujos provienen de metadatos/CIL y archivos serializados, contrastados con la captura suministrada.
- No se atribuye cada botón de la captura a un plugin concreto. La búsqueda y varios accesos adicionales pueden depender del pack; su procedencia específica sigue abierta.
- Los scripts de inventario leen la instalación y escriben solo en esta carpeta de investigación. No se extrajeron iconos, texturas ni código de interfaz para insertarlos en nuestro editor.
- La adaptación será una implementación propia de patrones de interfaz, con recursos y funciones adecuados al editor de L2.

Checklist: distribución visual, módulos base, árbol, transformaciones y cámaras **analizados**; procedencia individual de plugins y conducta runtime **pendientes**; implementación de la nueva propuesta **posterior a este informe**.
