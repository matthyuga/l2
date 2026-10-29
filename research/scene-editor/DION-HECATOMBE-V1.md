# Dion · Hecatombe V1

## Rendimiento — 26/10/2026

Tras observar pausas, fuego/humo cambiaron de un Sprite por partícula a geometría instanciada: un draw call por emisor, sin reducir el número de partículas. El resaltado de raíces con más de 128 mallas o 200.000 triángulos usa su caja envolvente; las piezas pequeñas mantienen resaltado geométrico. Desactivar resaltado evita generar sus geometrías.

Prueba aislada Chrome headless, 1600×1000: escena completa pasó de 40 a 60 FPS y 3.451 a 2.903 draw calls; efectos solos de 577 a 29 llamadas incluyendo ambiente. Son mediciones de esa prueba, no garantizan igual resultado en la pestaña del usuario. Datos dion-performance-before.json / dion-performance-after.json, script measure-dion-performance.cjs. Verificación dedicada de Dion pasa, incluidos guardado/reapertura, selector y presupuesto de resaltado. Regresión histórica verify-piece-picking.cjs pasó selección/materiales/resaltado pero agotó espera al guardar: espera texto antiguo «Versión guardada», mientras la aplicación actual usa «Proyecto guardado».

Abrir http://127.0.0.1:32290/?project=dion-hecatombe-v1.json o ABRIR-DION-HECATOMBE.cmd en la raíz del laboratorio. También aparece en el selector del Taller. Tres cámaras en botones 1, 2 y 3.

Base: Dion Classic maps IL, 20_22, importado previamente con 2.087 actores y terreno nativo de diez capas. No es una modificación instalada en el cliente Interlude. La variante conserva la distribución y añade 28 techos colapsados, 27 edificios con roturas, escombros, vigas, terreno quemado, once ramificaciones de fisuras, cenizas y 14 incendios con humo (28 emisores animados).

Primera aproximación geométrica: las roturas no reconstruyen interiores ni cierran superficies de corte. Sin NPCs, BSP original ni colisiones nuevas. El archivo original no se alteró; SHA-256 conservado en ../model-catalog/exports/dion-hecatombe-v1/audit.json.

Proyecto: projects/dion-hecatombe-v1.json. Recurso: ../model-catalog/exports/dion-hecatombe-v1/scene.gltf; depende de imágenes/buffer en la exportación original scene-batch1-library_fe488fdfccee. No moverlo aislado. Constructor build-dion-hecatombe.py rechaza sobrescrituras por defecto; --rebuild únicamente para reconstrucción explícita antes de cambios del usuario.

Fuego/humo implementados en scene-effects.js y effect-schema.js. app.js carga proyectos iniciales definidos por escenario. build_data.py conserva escenas personalizadas al regenerar datos. Pruebas verify-dion-hecatombe.cjs: WebGL real, animación, guardado validado por servidor, reapertura y cambio mediante selector. Resultado dion-hecatombe-verification.json; captura preview-dion-hecatombe-v1.png. Pruebas en navegador aislado, sin modificar borradores del usuario.
