# Giran renovada — 19/10/2026

Kevin autorizó decorar Giran libremente con los recursos existentes porque su conexión remota no permite trabajar cómodamente. Base aceptada `giranmodificado1`; se preservó intacta.

Entrega `E:\l2-local\mapas editados\giranrenovada1\giranrenovada1.json`, copia idéntica en `research/scene-editor/projects`. Enlace directo `http://127.0.0.1:32290/?project=giranrenovada1.json` carga la copia usando borrador independiente; no toca el borrador general del usuario. Lectura de proyectos locales permitida sólo por nombre JSON seguro; ruta inválida rechazada. Pruebas de enlace/recarga/aislamiento PASS.

2.234 entradas, 289 añadidas, ocho ramas: plaza, avenida, mercado, monumento norte, catedral, río, artesanos y jardín de la Memoria. Piedra clara, 55 materiales de techos en pizarra, agua azul, follaje, fuente, bancos, jardineras, urnas, faroles y estandartes. Diez cámaras guardadas/capturas. Dos piezas de estatua antigua siguen ocultas. Nuevos props editables.

Recursos `research/model-catalog/exports/giran-renovada` (base de ciudad copiada + mobiliario propio con texturas existentes), registrados en galería/data. No se cambiaron cliente, .unr, DB o Academy/Hellgames. Materiales estáticos, no simulación/luces dinámicas. Originales Giran GLTF y proyecto base mantienen hash.

Verificación de carga/guardadoAPI/recarga 2.234 objetos PASS; sin errores JS/HTTP. Auditoría de triángulos: 101 props de mobiliario, cero intersecciones arquitectónicas detectadas tras corrección. Informes `research/scene-editor/giran-renovada-verification.json`, `giran-placement-audit.json`, `project-link-verification.json`. Límite de objetos aumentado a 4.000 en schema y servidor; límite de archivo 3MB se mantiene. Backup `backups/giran-renovacion-20261019`. README junto a entrega explica dependencias, cámaras y alcance. No reejecutar generador sobre ediciones del usuario; ahora exige --rebuild.
