# R4 Arena: terreno recuperado ? 13/10/2026

Corregida la conversi?n incompleta se?alada por el usuario. El paquete original s? trae suelo: TerrainInfo1, altura16 R4_Arena_T.01.16_14, siete capas de textura, QuadVisibilityBitmap y EdgeTurnBitmap. Recuperados del mapa 16_14 con coordenadas nativas, escala128/128/76 y ubicaci?n Z original. UTexture versi?n123/license0 usa mipmaps directamente despu?s de propiedades (no cabecera extendida de Veilmar license30).

Agregado terreno con 65536 v?rtices al glTF existente de R4, manteniendo668actores est?ticos. Capas compuestas a2048px usando matrices y m?scaras originales. Miniatura revisada: terreno visible bajo edificios y vegetaci?n. Dependencias y miniatura verificadas; API devuelve terrain_included=true. Sin cliente ni servidor modificados. Se conservan scene.blend sin terreno y scene-with-terrain.blend actualizado.

A?n sin BSP, agua, part?culas ni iluminaci?n original. No atribuir suelo ausente anterior a descarga da?ada. Abrir enlace habitual y Ctrl+F5 para descartar cach? de glTF/miniatura.

Scripts terrain.py/add_terrain.py, terrain-audit.json/audit-with-terrain.json en research/scenario-batches/r4_arena y carpeta padre. Los dem?s escenarios necesitan revisi?n de terreno individual antes de declarar completa su vista.
