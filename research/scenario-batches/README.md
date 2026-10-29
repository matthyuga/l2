# Escenarios: primera tanda ? 13/10/2026

Agregados R4 Arena (16_14) y Canon Cathedral Interlude (17_17) al visor, filtro Escenarios, etiqueta Tanda 2. No instalados en cliente ni servidor.

R4: 668 actores, 151 referencias est?ticas exportadas, cero actores omitidos en montaje. Canon: 1377 actores, 62 referencias, cero omitidos. Materiales del glTF ensamblado y dependencias comprobados; miniaturas revisadas visualmente. Las escenas conservan posiciones, rotaciones y escalas originales. Encuadre centrado en zona principal: Canon comparte archivo con otras salas.

Son vistas de arquitectura: a?n sin terreno heightmap/BSP/agua/part?culas/iluminaci?n original/NPCs. No llamarlas mapas completos jugables. Algunas texturas especiales de R4 no se recuperaron ?ntegramente; referencia en manifiestos y notas. No se inspeccion? WebGL vivo durante este paso, solo miniaturas renderizadas y respuesta HTTP.

http://127.0.0.1:32280/?model=scenario_batch1_r4_arena&view=3d
http://127.0.0.1:32280/?model=scenario_batch1_canon_cathedral&view=3d

Fuentes originales en K, SHA256 en manifest.json/audit.json por escena. Backup de cat?logo: gallery-before-first-scenarios.json. Scripts prepare.py/assemble.py/focus.py preservan originales; no ejecutar el main hist?rico build_gallery.py.

Siguiente tanda pendiente: Heart of Steel Fortress y Crow Island Village, luego World Tree Village y jardines. Evitar duplicar variantes HF/IL y paquetes de territorios ya existentes sin comparar. Todas las dem?s descargas de K siguen pendientes de preparaci?n para visor.


# R4 Arena: terreno recuperado ? 13/10/2026

Corregida la conversi?n incompleta se?alada por el usuario. El paquete original s? trae suelo: TerrainInfo1, altura16 R4_Arena_T.01.16_14, siete capas de textura, QuadVisibilityBitmap y EdgeTurnBitmap. Recuperados del mapa 16_14 con coordenadas nativas, escala128/128/76 y ubicaci?n Z original. UTexture versi?n123/license0 usa mipmaps directamente despu?s de propiedades (no cabecera extendida de Veilmar license30).

Agregado terreno con 65536 v?rtices al glTF existente de R4, manteniendo668actores est?ticos. Capas compuestas a2048px usando matrices y m?scaras originales. Miniatura revisada: terreno visible bajo edificios y vegetaci?n. Dependencias y miniatura verificadas; API devuelve terrain_included=true. Sin cliente ni servidor modificados. Se conservan scene.blend sin terreno y scene-with-terrain.blend actualizado.

A?n sin BSP, agua, part?culas ni iluminaci?n original. No atribuir suelo ausente anterior a descarga da?ada. Abrir enlace habitual y Ctrl+F5 para descartar cach? de glTF/miniatura.

Scripts terrain.py/add_terrain.py, terrain-audit.json/audit-with-terrain.json en research/scenario-batches/r4_arena y carpeta padre. Los dem?s escenarios necesitan revisi?n de terreno individual antes de declarar completa su vista.
