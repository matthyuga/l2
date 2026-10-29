# Assets externos · Tanda 5 — 28/10/2026

[Abrir catálogo](http://127.0.0.1:32280/?batch=Assets%20externos%20%C2%B7%20Tanda%205)

8 modelos. 8 con huesos; 287 clips exportados.

| Modelo | Huesos | Clips | Materiales | Texturas |
|---|---:|---:|---:|---|
| [Achates (Lost Ark)](http://127.0.0.1:32280/?model=ext3_2493ca25e8066e) | 72 | 122 | 3 | complete |
| [HIT2 - Hundra (High Poly)](http://127.0.0.1:32280/?model=ext3_0c60d736139fdf) | 123 | 17 | 7 | complete |
| [Humanity Reconstructed (Mir4)](http://127.0.0.1:32280/?model=ext3_2ed12f43dd59c1) | 38 | 37 | 1 | complete |
| [Infinian (Lineage Series)](http://127.0.0.1:32280/?model=ext3_60384c71864db0) | 190 | 14 | 3 | complete |
| [Morgan (Raven 2)](http://127.0.0.1:32280/?model=ext3_0422c3747f25e5) | 116 | 17 | 4 | complete |
| [Silver Dragonkin (Mir4)](http://127.0.0.1:32280/?model=ext3_3f0f0a7612b4d2) | 58 | 37 | 2 | complete |
| [Tarisland - Dragon (High Poly)](http://127.0.0.1:32280/?model=ext3_f645befc212d2d) | 155 | 27 | 2 | complete |
| [WoP - Octopus Pirate King (High Poly)](http://127.0.0.1:32280/?model=ext3_40050f05d42b4b) | 184 | 16 | 3 | complete |

[Auditoría y reparaciones de texturas](../texture-audit-20261028/REVISION.md)

No se modificó el cliente, el servidor ni la base del juego. Favoritos y anotaciones se conservan en el navegador del usuario.

## Verificacion adicional

- Ocho ZIP originales sin cambios y CRC validos.
- 287 clips: nombres y duraciones individuales comparados con las tomas FBX originales, error inferior a 0.0001 s.
- Imagenes vinculadas en los ocho FBX presentes y legibles.
- 74 modelos tecnicos y 149791 canales conservados en SQLite, con hashes de sus datos descomprimidos comprobados.
- Achates: muestreo limitado a cada toma en una sesion aislada de Blender; no se cambian claves ni tiempos. 11 clips / 2376 canales coinciden byte por byte con la exportacion normal, al igual que geometria, rig y materiales. Ver sampling-verification.json.
- Captura de los ocho modelos: [contacto.jpg](contacto.jpg).
