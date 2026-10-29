# Bitácora y traslado del editor L2 Lab — 17/10/2026

Cierre preparado: 2026-10-17T21:42:27.751614-03:00. Ruta de origen W10: `E:\l2-local`.
Proyecto de trabajo: **L2 Lab**. Academy y Hellgames no se modificaron.

## Antes de retirar el disco

1. **Pulsar Guardar versión en el editor abierto** (o Exportar JSON). El borrador local del navegador NO viaja con el disco. Esta sesión no tiene navegador conectado y no pudo guardar ese borrador por Kevin. Los JSON ya guardados están en `research/scene-editor/projects`; hay 74 versiones, incluidas pruebas automáticas. No asumir que la más reciente es la escena del usuario.
2. Las descargas se pausaron para el traslado. `21-PAUSAR-DESCARGA-TEXTURAS-L2.cmd` permite volver a pausarlas si se reanudan.
3. Tras guardar, ejecutar `22-CERRAR-EDITOR-ESCENAS-L2.cmd`. Se dejó el servidor del editor abierto para permitir el guardado. El cierre no guarda la escena ni cierra el navegador.
4. Cerrar el cliente L2 y, si el servidor de juego está activo, usar `5-DETENER-SERVIDOR.cmd`. No se detuvieron juego ni base de datos desde esta tarea.
5. Cerrar programas que usen el disco y expulsarlo de forma segura desde Windows.

## Continuar en Windows 11

- Localizar la letra REAL del Seagate. En el traslado anterior fue D:, en esta PC es E:. Conservar `l2-local` y `l2` como carpetas hermanas. No reemplazar rutas masivamente.
- Abrir `19-EDITOR-ESCENAS-L2.cmd` desde esa copia. Usa Node portable incluido y rutas relativas; dirección `http://127.0.0.1:32290`. No requiere iniciar MariaDB, GameServer ni UnrealEd.
- Abrir proyecto desde el editor y elegir el JSON que Kevin haya guardado. El navegador de W11 puede empezar sin borrador, ancho de panel ni preferencias de W10. Las cámaras guardadas en el proyecto sí viajan.
- Para texturas: ejecutar `20-DESCARGAR-TEXTURAS-L2.cmd`. Requiere **Python 3.10+ y Pillow** en W11; el lanzador comprueba `python` y luego `py -3`. Si falta Pillow: `python -m pip install Pillow` usando el intérprete instalado (o `py -3 -m pip install Pillow`). No se incluyó Python portable. El editor funciona sin Python.
- El descargador conserva catálogos, ZIP completos y mapas ya extraídos. Al reanudar omite materiales terminados y reintenta pendientes; un archivo `.part` puede descargarse nuevamente. No borrar archivos parciales ni `source.json` para el traslado.
- Probar Computer Use sobre Explorador y luego UnrealEd en W11. **Pendiente de validar**: W10 tenía errores de captura 0x80004002/IsBorderRequired. No afirmar que W11 ya lo resolvió ni instalar plugins de terceros como supuesto requisito.
- No restaurar SQL, reinstalar el servidor ni ejecutar instaladores históricos para abrir este editor. Los documentos antiguos de continuidad de juego conservan su valor histórico.

## Estado de los tres catálogos de texturas

Descargas **pausadas**, catálogos completos todavía NO descargados. Se solicitó cubrir materiales públicos de ambientCG, Poly Haven y ShareTextures, con conjuntos 2K; no todos los formatos/resoluciones repetidos ni modelos/HDRI/productos pagos.

| Proveedor | Materiales indexados | Objetivo descargable | Fallos registrados en esta pasada |
|---|---:|---:|---:|
| ambientCG | 1497 | 2018 | 32 |
| Poly Haven | 140 | 869 | 4 |
| ShareTextures | 435 | 1837 | 14 |

Total indexado: **2072 / 4724**. Es una foto del catálogo publicado al detener los procesos; algún material recién terminado puede incorporarse al reanudar. Fallos de conexión/DNS/timeout son reintentables; algunos recursos no ofrecen mapa Diffuse 2K. Los 2 materiales ambientCG sin paquete público no entraron al plan de 2018. No se promete que todos los pendientes sean descargables.

Archivos de control: `research/texture-library/run.json`, `progress.json`, `polyhaven/progress.json`, `sharetextures/progress.json`. Gestor `run_all.py`, descargadores `download.py` y `download_providers.py`. Catálogos originales y sitemap conservados. API local `/api/textures` publica terminados; `/api/texture-progress` informa avance.
Mapas y procedencia/licencias/checksums: `research/model-catalog/exports/cc0-textures`. Archivos originales: `research/texture-library/archives` y `research/texture-library/sharetextures/archives`.

## Funciones implementadas

- Fondo negro, paneles semitransparentes. Escena 3D central, árbol jerárquico a la derecha y detalles a la izquierda.
- Barra de iconos Añadir, Detalles, Posición, Material, Vista y Terreno. Panel izquierdo ajustable por borde ↔ (210–520px) y ocultable.
- Biblioteca de modelos modular, ampliable, galería/búsqueda/categor?as y traducciones parciales conservando nombres originales.
- Jerarquía con piezas reales de glTF, grupos anidados, agrupar/desagrupar y fusionar mallas estáticas conservando materiales. Fusión no hace booleanas ni suelda vértices.
- Visibilidad y candado por fila. Desbloquear para editar junto a texturas; desbloquear grupo/rama o todo desde Escena. Bloqueos heredados y protección de ramas externas, con deshacer y guardado.
- Selección Objeto/Piezas/Material, Alt+clic temporal en pieza, resaltado dorado y anticipación celeste. Selección desde árbol y desde visor sincronizadas.
- Terreno aplica textura por material (reemplazar/superponer capa, repetición, opacidad). Aplicar junto a miniatura. No hay escultura de terreno ni pincel por zonas arbitrarias.
- W mover, E girar, R escalar; C trae selección al foco de cámara, F va a selección, Q nodos. Izquierdo orbita, derecho altura/distancia, central desplaza; Shift acelera x4 y Ctrl reduce x0,6. Diez tomas de cámara guardables/recuperables.
- JSON con grupos, piezas, materiales, cámaras y recetas de fusión; borrador del navegador y deshacer/rehacer.
- Para restaurar la composición base, cambiar a otra escena en el selector superior y volver al muelle; se guarda versión de los cambios pendientes antes del cambio. Recargar recupera el borrador, no restaura el mapa.

## Alcance y pendientes

Este es un editor visual local basado en exportaciones glTF y proyectos JSON. **No instala los cambios en el cliente ni reescribe `.unr`**. El mapa nativo `l2/Maps/24_19.unr` no se modificó en esta sesión. La exportación nativa, colisiones, geodata y movimiento funcional de aeronaves siguen pendientes de un flujo específico compatible con el cliente.
Continuar primero comprobando en W11 el proyecto guardado, miniaturas/texturas y controles. Luego reanudar los tres catálogos y revisar recursos fallidos. No tocar Academy/Hellgames. Mantener original y copia de trabajo separados.

## Verificación y respaldo

Los informes existentes del editor registran pruebas de biblioteca, controles/cámaras, superficies, proveedores CC0, jerarquías/grupos, selección de piezas, panel ajustable y desbloqueos. Última verificación de candados: `lock-controls-verification.json`, passed=true, sin errores; regresiones de jerarquía, selección y panel también pasaron. W11 y exportación al juego aún no validados.

Respaldo de esta entrega: `backups/editor-handoff-20261017-214227/editor-source-and-projects.zip`, con código, proyectos JSON existentes al cierre, informes, documentación y scripts de descarga. `files-sha256.json` registra hashes de cada archivo incluido; ZIP comprobado por CRC al crearse. El ZIP **no contiene** los grandes glTF, texturas, ZIP originales, cliente, bases de datos, Node ni el borrador privado del navegador. El conjunto completo viaja en el disco, manteniendo especialmente `research/model-catalog/exports`, `thumbs`, `vendor` y `research/texture-library`.
Cualquier versión guardada por Kevin después de este respaldo queda en la carpeta projects del disco, pero no en este ZIP previo.

Estado consolidado y copia de los catálogos/avance: `backups/editor-handoff-20261017-214227/state.json` y `texture-status/`. No se hizo commit ni push. Nexus central y copias portables incluyen nota de continuidad.

## Mensaje para la siguiente sesión

Estamos en Windows 11 con el disco de L2 Lab. Leer primero `BITACORA-EDITOR-ESCENAS-20261017.md` y `CONTINUIDAD-W11/LEER-PRIMERO.md` desde la letra actual del disco. Continuar el taller visual `research/scene-editor`, abrir con 19, recuperar el JSON guardado por Kevin y reanudar texturas con 20 tras comprobar Python/Pillow. No confundir proyectos QA con la escena del usuario ni dar por completados los tres catálogos. Verificar Computer Use por separado. Mantener el mapa nativo y Academy/Hellgames intactos.
