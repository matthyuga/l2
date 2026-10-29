# Revisión de texturas — 28/10/2026

25 modelos reparados o mejorados, con 267 conexiones de mapas registradas. 1865 imágenes externas verificadas; 0 inválidas después de la reparación de extracción.

[Comparación antes/después](before-after.jpg) · [Todos los modelos reparados](repaired-contact.jpg)

## Qué se corrigió

- BodyHighJacker: Windows tar no soportaba filtros RAR y había creado cuatro imágenes llenas de ceros. Reextraído con UnRAR; nueve archivos comprobados contra el CRC original. La ficha muestra model1; model2 sigue disponible en el paquete, sin ensamblar.
- Cinco Volt de Apex: recuperados color, normales y AO donde existe. No se reinterpretaron sus mapas especulares/gloss/ILM como metálico o emisión sin prueba.
- Bloody Rose: el GLB no tenía ningún material. Se conectó su atlas y mapas PBR a la malla con UV existente.
- Crimson Cup Plants: reparadas las equivalencias BaseColor/albedo, Alpha/opacity y Emission/emissive.
- Abomination: recuperadas referencias de cuerpo, ojos, cabello y bastón, además de normales. Su pose importada sigue requiriendo revisión.
- Hologram Police: recuperadas referencias rusas y extensiones `.tga.png`; falta el normal de la base.
- Old house: recuperadas tablas, puertas, ventanas, ladrillos, tejado y vigas por nombres de piezas; otros materiales siguen pendientes.
- Zeromus: se asignó el único atlas del paquete a las siete piezas como candidato. Sus rutas originales no permiten demostrar la asignación: sigue marcado para revisión UV.
- CATTO: atlas de cuerpo y cabello asignados por contenido visual; auxiliares/transparencias pendientes.

## Conservación de datos

Cada cambio conserva los bytes originales de geometría, pesos, huesos, matrices y animaciones. Se conservan los bufferViews originales y el BIN completo como prefijo idéntico. Solo se agregan imágenes y se modifican materiales; Bloody Rose recibe índices de material. Evidencia por revisión en `revisions.json`, originales en `before/`, hashes anteriores/nuevos y respaldo SQLite coherente en `rig-database-20261028/database-revisions`. Las revisiones materiales tienen su propia tabla `material_revisions`; la protección contra otros cambios de artefacto sigue activa.

Los originales descargados no se modifican. Las miniaturas se renderizan desde el GLB reparado. La prueba del navegador decodifica las imágenes y comprueba el SHA del visor técnico. Esto no certifica un retarget ni la adaptación a Interlude. Los nombres de mapas no demuestran por sí solos la convención DirectX/OpenGL de cada normal.

## Modelos modificados

| Modelo | Conexiones registradas | Estado actual |
|---|---:|---|
| [Abomination - DOOM : The Dark Ages - Rigged](http://127.0.0.1:32280/?model=ext3_02ca3c6c038ee4) | 64 | complete |
| [ANGEL OF DEATH from Hellboy 2 statue scan](http://127.0.0.1:32280/?model=ext3_9da6c9d3b86fa7) | 1 | complete |
| [Bloody Rose Sword / FREE](http://127.0.0.1:32280/?model=ext3_d346aea0f43e05) | 5 | complete |
| [FREE/ Wild Sword](http://127.0.0.1:32280/?model=ext3_35215022f8d13b) | 15 | pending |
| [Hologram Police Robots](http://127.0.0.1:32280/?model=ext3_94be31d26c08d8) | 16 | pending |
| [Robotic Eye](http://127.0.0.1:32280/?model=ext3_6d97524f4de6d2) | 2 | complete |
| [SCI FI SPIDER ROBOT](http://127.0.0.1:32280/?model=ext3_6b9626c3ec83bc) | 29 | complete |
| [Sentinel Ship - DOOM : The Dark Ages](http://127.0.0.1:32280/?model=ext3_5d5474a67d0505) | 30 | complete |
| [Shrine](http://127.0.0.1:32280/?model=ext3_ccce33233c3db8) | 7 | complete |
| [World's End Inn](http://127.0.0.1:32280/?model=ext3_fbc518ec419534) | 2 | complete |
| [Apex Legends CAR SMG Mythic Allfather's Fury](http://127.0.0.1:32280/?model=ext3_df579a9fd3034f) | 10 | pending |
| [Apex Legends Volt SMG Cyber Gradient](http://127.0.0.1:32280/?model=ext3_9f92daf26cdb3b) | 2 | complete |
| [Apex Legends Volt SMG Graduate Thesis](http://127.0.0.1:32280/?model=ext3_169be7ef066246) | 3 | complete |
| [Apex Legends Volt SMG High Dosage](http://127.0.0.1:32280/?model=ext3_de63ca20a00c50) | 3 | complete |
| [Apex Legends Volt SMG Neutralizer](http://127.0.0.1:32280/?model=ext3_dc828cfb8e8fb2) | 3 | complete |
| [Apex Legends Volt SMG Void Touched](http://127.0.0.1:32280/?model=ext3_942242061f8a05) | 3 | complete |
| [Lizard Man Warrior](http://127.0.0.1:32280/?model=ext3_f475e21537c5d4) | 4 | complete |
| [𝙐тѕм [Concept]](http://127.0.0.1:32280/?model=ext3_a84166ef58d205) | 4 | complete |
| [Wᴀᴛᴄʜᴍᴀɴ Oꜰ Dᴏᴏᴍ (reworkig)](http://127.0.0.1:32280/?model=ext3_f9874e82eaadc5) | 2 | complete |
| [Watchman Of Doom](http://127.0.0.1:32280/?model=ext3_667b352a7c772f) | 8 | complete |
| [Zeromus](http://127.0.0.1:32280/?model=ext3_d2e535fbed12ff) | 21 | pending |
| [CATTO](http://127.0.0.1:32280/?model=ext3_1b503079fd52f4) | 2 | pending |
| [The BodyHighJacker](http://127.0.0.1:32280/?model=ext3_e101d68bf367ad) | 1 | complete |
| [Crimson Cup Plants](http://127.0.0.1:32280/?model=ext3_cdaea01fbc1830) | 9 | complete |
| [Old house](http://127.0.0.1:32280/?model=ext3_b531b47f902dcf) | 21 | pending |

## Casos pendientes

| Modelo | Qué queda |
|---|---|
| Airship02Fbx | Hay referencias de texturas pendientes de reparar. Referencias: rope_texture2093.jpg |
| CATTO | Texturas reconectadas; quedan referencias ausentes o ambiguas. Referencias: asignación/materiales auxiliares |
| Despair - Darksiders 2 - Rigged | Hay referencias de texturas pendientes de reparar. Referencias: material_3 |
| FREE/ Wild Sword | Texturas reconectadas; quedan referencias ausentes o ambiguas. Referencias: LeafSet024_4K-JPG_Color.jpg, LeafSet024_4K-JPG_NormalGL.jpg, LeafSet024_4K-JPG_Opacity.jpg, LeafSet024_4K-JPG_Roughness.jpg, leafRouhgness.png |
| Hologram Police Robots | Texturas reconectadas; quedan referencias ausentes o ambiguas. Referencias: Основа_Normal.tga |
| medieval town (no textures) | Hay referencias de texturas pendientes de reparar. Referencias: 212_DefaultMaterial_BaseColor.png, 212_DefaultMaterial_Emissive.png, 212_DefaultMaterial_Metallic.png, 212_DefaultMaterial_Normal.png, 212_DefaultMaterial_Roughness.png, 2x_DefaultMaterial_BaseColor.png, 2x_DefaultMaterial_Emissive.png, 2x_DefaultMaterial_Metallic.png… |
| Old house | Texturas reconectadas; quedan referencias ausentes o ambiguas. Referencias: Deep_Metal.png, lod_3.png, wind_1.png |
| Robot | Faltan los mapas externos usados por los materiales met?licos; el paquete no los incluye. Referencias: TexturesCom_Metal_AluminumBrushed_1K_albedo.tif, TexturesCom_Metal_AluminumBrushed_1K_metallic.tif, TexturesCom_Metal_AluminumBrushed_1K_normal.tif, TexturesCom_Metal_AluminumBrushed_1K_roughness.tif, TexturesCom_Metal_PaintedGun_1K_albedo.tif, TexturesCom_Metal_PaintedGun_1K_metallic.tif, TexturesCom_Metal_PaintedGun_1K_normal.tif, TexturesCom_Metal_PaintedGun_1K_roughness.tif |
| Apex Legends CAR SMG Mythic Allfather's Fury | Texturas reconectadas; quedan referencias ausentes o ambiguas. Referencias: skydive_trail_energy_01_1_msk.png, skydive_trail_energy_01_2_nml.png |
| Zeromus | Atlas recuperado; asignaci?n UV pendiente de confirmar porque las rutas originales son ambiguas. Referencias: asignación/materiales auxiliares |

Airship y Robot no traen las imágenes externas que requieren algunos materiales. Medieval town se publicó expresamente sin texturas. Armor Cat es STL sin mapas/UV; no se presenta como reparación pendiente.

## Evidencia

- `inventory.json`: auditoría inicial de materiales GLB y archivos disponibles.
- `sources/*.json`: lectura de materiales, imágenes y conexiones FBX; incluye SHA del archivo fuente.
- `revisions.json`: cambios por material/slot, archivos fuente y SHA, prueba de conservación y respaldo.
- `image-validation.json`: integridad de formato de las imágenes extraídas.
- `body-rar-crc.json`: CRC de todos los archivos del RAR recuperado.
- `browser-verification.json`: carga real con Three.js, texturas decodificadas y acceso al índice técnico.

## Nuevas descargas

[Tanda 5 en el catálogo](http://127.0.0.1:32280/?batch=Assets%20externos%20%C2%B7%20Tanda%205)

8 modelos nuevos publicados; se conservan autor, licencia y enlace de procedencia.
