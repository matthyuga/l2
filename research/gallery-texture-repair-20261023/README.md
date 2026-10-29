# Recuperación de texturas de la galería L2

Fecha: 23/10/2026.
Solicitud: revisar todas las páginas y recuperar texturas de NPC, monstruos y variantes de jefes usando los recursos disponibles.

## Resultado comprobado

- Catálogo conservado: 2.955 entradas y 2.647 vistas 3D únicas.
- 105 vistas mejoradas, con 229 asignaciones de material recuperadas. Cien quedaron completas en sus materiales usados; cinco mejoraron parcialmente.
- Las claves, asociaciones de NPC, ubicaciones y geometría se conservaron.
- Se regeneraron las 105 miniaturas y se revisaron visualmente en hojas de contacto.
- Comprobación en Chrome aislado: 59 páginas y 2.809 miniaturas disponibles cargadas sin errores. Se incluyeron las mallas sin NPC asociado.
- Tres vistas reparadas verificadas en WebGL: Feline King del paquete Scarlet, Dark Horror y una pieza de vestimenta orca. También se comprobó un GLB de la biblioteca de ruinas.
- No se cambiaron paquetes originales, cliente L2, stats, spawns ni GameServer.

Las entradas son vistas, variantes y piezas, no especies ni personajes únicos. Una textura representativa recuperada no reproduce necesariamente todos los efectos, animaciones o variantes de color del cliente Unreal.

## Causas y métodos

1. El paquete Scarlet Van Halisha incluía un LineageMonsters3 completo sin su dependencia LineageMonstersTex3. Se recuperaron 72 vistas de ese paquete en las distintas pasadas. La comparación de posiciones, coordenadas UV e índices de las piezas verificó coincidencia con modelos existentes. El título del archivo de descarga no significa que todas esas piezas sean variantes de Halisha.
2. Algunos materiales tenían el mismo nombre dentro del mismo espacio de paquete y una sola textura inequívoca en el catálogo. Se reutilizaron esas referencias, sin búsqueda por parecido.
3. UModel no soporta GlowModifier de varios recursos clásicos. El lector local de paquetes UE2 siguió las propiedades Material/Diffuse hasta el objeto Texture. Se recuperaron 42 slots por esta vía. No se recreó el efecto animado de GlowModifier.
4. Algunos recursos renombrados tenían cuerpo, UV y topología idénticos. Se usaron como vistas representativas de materiales compatibles. Incluye piezas de vestimenta orca, Orfen y un tigre; no equivale a certificar los colores autorales del paquete externo.
5. Se revisaron las referencias npcgrp de los paquetes, incluyendo nombres con guiones. No aportaron recuperaciones adicionales en la segunda pasada. Las piezas auxiliares sin referencia no recibieron texturas elegidas al azar.
6. El servidor de galería no permitía JPG ni GLB, aunque existían en disco. Se añadieron MIME para JPG/JPEG/WebP y GLB. Se reinició solamente el servidor de la galería, después de verificar el proceso que escuchaba en 32280. JPG y GLB pasaron HTTP 200; GLB también cargó en WebGL.

## Lo que sigue pendiente

Quedan 350 vistas únicas con materiales usados sin textura, representadas en 360 tarjetas. Incluyen dependencias ausentes como EXS_MonstersTex y Wog_buildingtex, recursos auxiliares sin referencia identificable, materiales de escenarios parcialmente resueltos y algunas texturas que UModel no puede exportar. Es una lista de pendientes, no la afirmación de que todos esos recursos estén dañados o sean imposibles de recuperar.

Se mantienen aparte 329 vistas únicas de bibliotecas que usan colores planos de forma intencional, representadas en 341 tarjetas. No se pintaron con texturas inventadas. Las 131 entradas sin vista disponible conservan su estado; corregir una textura no recupera geometría vacía o no exportable.

Ejemplos de límites confirmados:

- EXS_MonstersTex: no está en el paquete local revisado; las criaturas lo solicitan explícitamente.
- Wog_buildingtex: el paquete incluye Wog_Uniq_Building_Tex, pero éste no contiene los objetos solicitados como di_door03, di_door_deco y elf_vi_137. Cambiar sólo el nombre no resolvería esas referencias.
- Algunas texturas de efectos declaran RGBA8RawData pero UModel informa que no tienen mipmaps válidos. No se convirtió ese valor de propiedad en píxeles supuestos.
- LineageMonsters71.kd falla en UModel al leer un índice de nombre; se conserva el original.
- Varias mallas de prueba o antiguas no tienen materiales declarados o referencias de NPC identificadas. No se dedujo una textura sólo por el nombre o silueta.

## Uso en la galería

Actualizar con Ctrl+F5. El filtro **Texturas** permite elegir completas, pendientes o colores planos del recurso. Las tarjetas pendientes muestran cuántos materiales usados faltan y la ficha conserva las notas de procedencia.

Estos estados describen materiales del visor, no la integridad total de shaders y efectos del juego. Un material con imagen difusa puede seguir requiriendo un shader especial para verse exactamente como en L2.

## Evidencia y reproducción

- `audit-before.json` y `audit-after.json`: censo de todas las vistas, materiales usados e imágenes externas; también leen el contenedor GLB.
- `summary.json`: diferencias y validaciones; sin enlaces a imágenes rotos ni cambios de geometría.
- `pending-models.json`: listado completo de tarjetas pendientes.
- `repair-matches.json`: coincidencias de malla o material, donante y firma de geometría.
- `native-evidence-retraced.json`: 42 cadenas nativas verificadas, con paquete, objeto, clase, offsets y propiedades.
- `npcgrp-resolution.json`: segunda revisión de referencias de los paquetes.
- `body-matches.json`: coincidencias exactas de cuerpos renombrados.
- `qa-fixed-1.jpg` a `qa-fixed-5.jpg`: revisión de las 105 miniaturas cambiadas.
- `tmp/gallery-textures-20261023/verification.json`: 59 páginas, decodificación de miniaturas, filtro y apertura de tres modelos 3D.
- `tmp/verify_gallery_textures.py` y `tmp/verify_gallery_glb.py`: pruebas de navegador.

Scripts de recuperación en esta carpeta. No ejecutar los finalizadores históricos de la galería para regenerar todo: pueden reemplazar metadatos añadidos después.

## Respaldo

`E:/l2-local/backups/gallery-textures-20261023` conserva gallery.json previo, glTF anteriores y los archivos de interfaz/servidor. Los buffers y fuentes originales no se modificaron. Para revertir miniaturas habría que restaurar los glTF y renderizarlos de nuevo; no se conserva una copia de cada PNG anterior.
