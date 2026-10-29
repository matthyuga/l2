# Tanda 5 y texturas completadas - 28/10/2026

E:\l2-local\research\external-assets-round5-20261028\REVISION.md
E:\l2-local\research\texture-audit-20261028\REVISION.md

8 nuevos / 287 clips publicados en Tanda 5. 25 GLB reparados o mejorados; 1865 imagenes verificadas. 10 casos pendientes de materiales/UV, mas un STL plano sin mapas.
BodyHighJacker: tar no soportaba filtros RAR, creo cuatro imagenes llenas de ceros. Recuperadas con UnRAR instalado; CRC de los nueve archivos verificado. Unpack_rars.py ahora usa UnRAR y no marca como listo un paquete con error de extraccion.
74 modelos en rig-catalog.sqlite / 149791 canales verificados. Revisiones de materiales preservan BIN original y JSON de geometria/rig/animacion; historial material_revisions, snapshots en texture-audit-20261028/before, respaldo SQLite coherente. Sett no se modifico.
Achates: el exportador Blender muestrea union global de tiempos para cada toma y tardaba mas de 35 min. Opcion aislada narrow_animation_sampling limita al rango de cada toma para una unica armadura sin otros objetos animados/drivers/shapekeys. No modifica fcurves ni tiempos. 122 clips completos en ~130 s; 11 clips y 2376 canales exactos contra exportacion sin parche, geometria/rig/materiales identicos. Datos en sampling-verification.json. No modificar globalmente el addon.
Todos los ocho ZIP originales conservan SHA; prueba de carga final en browser-verification.json. No se toco cliente/servidor/DB del juego ni favoritos del usuario.
