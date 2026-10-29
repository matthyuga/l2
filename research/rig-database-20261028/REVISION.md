# Base fiable de rigs y animaciones — Sett

Revisión del 28/10/2026. Objetivo: conservar mediciones verificables para comparar esqueletos y preparar experimentos, sin confundir coincidencias con compatibilidad demostrada.

[Abrir ficha técnica interactiva](http://127.0.0.1:32280/rig-inspector.html?model=ext3_02b86c82826120)

## Resultado de Sett

| Dato | Medición y alcance |
|---|---|
| Huesos | 144 joints en el GLB; 144 bones tras importar el FBX |
| Con pesos | 132 joints con influencias positivas en las primitivas exportadas |
| Animaciones | 1 clip, sin segmentación semántica |
| Tiempo del GLB | 0.016666668 a 90.916664124 segundos |
| Duración del clip | 90.899997456 segundos |
| Importación FBX | 60.0 FPS; acción entre frames 1.0 y 5455.0 |
| Curvas FBX importadas | 1440 curvas escalares; 8,104,930 puntos observados por Blender |
| Pistas GLB | 432 canales vectoriales TRS; 300 con variación por encima de 1e-6 |
| Nombres y padres | Sin huesos perdidos/añadidos y sin discrepancias de parentesco entre ambos formatos |
| Poses muestreadas | 1584 posiciones de joints en 11 instantes; error máximo 0.000007787541 unidades globales |

Las curvas escalares y los canales vectoriales no son la misma unidad: una rotación quaternion ocupa cuatro curvas escalares y una pista vectorial. Los 60 FPS corresponden a la escena importada; glTF almacena tiempos en segundos y no exige una frecuencia global fija.

## Base de datos

Archivo: [rig-catalog.sqlite](rig-catalog.sqlite). Versión de esquema 1.

- models: 29
- nodes: 5375
- joints: 5028
- clips: 52
- channels: 18010
- source_bones: 144
- source_actions: 1
- segments: 0
- experiments: 0

La base contiene matrices locales/globales de referencia, matrices inversas de enlace, orden de joints por skin, parentesco, incidencias de pesos, canales, interpolación, tiempos y valores. Las muestras de los canales glTF se guardan completas como bytes compactos comprimidos con zlib, con tipo de componente, tamaño y SHA-256. No se almacenan solamente estadísticas o capturas de pantalla.

Las incidencias de pesos corresponden a vértices de primitivas exportadas: pueden incluir duplicados por UV/material e instancias. No equivalen a un recuento de vértices únicos del FBX.

El contraste directo FBX/GLB está realizado para Sett. Los otros 28 modelos tienen una medición del GLB, sin afirmar una validación equivalente de sus originales.

## Evidencia y versiones

- REA inspeccionó `sett.zip`: inventario de 22 entradas del directorio central, sin contradicciones de integridad reportadas.
- Evidencia de inspección: `ev_1a4509f2d15947a6818745a03365c1b51eb72b6691e7c446a631405625ffc18e`.
- Inventario: `ev_dcba1f8726194379f1b2050da224b8e088ace1200000b5c6846a94f988867a80`.
- [Bundle REA completo](rea-sett-evidence.json). REA no interpretó los huesos ni ejecutó el modelo; esa parte procede de Blender y de la decodificación de glTF.
- [Observación FBX](sett-fbx-observation.json), [correlación](sett-correlation.json) y [prueba de poses](sett-pose-verification.json).
- `snapshots/` conserva copias del ZIP, FBX y GLB de Sett bajo sus SHA-256. La copia FBX coincide con el miembro original del ZIP.
- La ficha verifica el SHA-256 del GLB antes de mostrarlo. Un cambio bloquea su presentación como la revisión anterior.
- `build_database.py` rechaza sustituir silenciosamente una malla de otro hash bajo la misma clave. Antes de una nueva pasada conserva una copia SQLite coherente en `database-revisions/`.

## Comparación preliminar

- Sett → Blood Queen | Rigged | Lost Ark: 143 candidatos por nombre normalizado; 142 con nombre de padre coincidente. Transferencia sin probar.
- Sett → rigged elf woman: 57 candidatos por nombre normalizado; 50 con nombre de padre coincidente. Transferencia sin probar.

No hay un porcentaje de compatibilidad inventado. La comparación no prueba igualdad de proporciones, ejes locales, matrices de enlace, contactos de pies/manos, movimiento de raíz ni función de los apéndices.

## Qué queda sin establecer

- Los ataques, reposos, poses y muertes aún no tienen etiquetas ni cortes confirmados. La tabla `segments` está vacía.
- No se trasladó ninguna animación a otro modelo. La tabla `experiments` está vacía.
- Las etiquetas anatómicas son hipótesis basadas en nombres y están marcadas `unverified`.
- La prueba FBX/GLB cubre posiciones de joints en 11 instantes; no demuestra equivalencia en todos los frames, orientaciones o deformaciones de malla.
- No se validó ni instaló una adaptación UKX/UTX para Interlude.

## Uso para experimentar con control

1. Elegir un intervalo temporal y confirmar visualmente qué movimiento contiene. Guardar sus límites como segmento, conservando el clip completo.
2. Elegir esqueleto destinatario y revisar una correspondencia explícita de huesos, con especial atención a apéndices y padres diferentes.
3. Generar el resultado en un archivo nuevo. Conservar huellas de origen, parámetros, versión de herramientas y resultado de la prueba.
4. Comparar pose, proporciones y contactos antes de adaptar al cliente. Un resultado fallido también debe conservar su registro.

## Verificación

- [Prueba de SQLite y blobs](database-verification.json): integridad, claves foráneas, tamaño y hash de todos los canales descomprimidos, y hashes de las tres copias de Sett.
- [Prueba del navegador](browser-verification.json): jerarquía 3D, búsqueda y selección de huesos, pistas, comparación, reproducción/pausa, cambio de modelo y acceso desde la galería.
- [Jerarquía completa en texto](sett-hierarchy.txt).

Los originales y los favoritos del navegador real no se modificaron. Respaldo de la integración del catálogo en `E:\l2-local\backups\rig-database-20261028`.

La prueba del navegador tambi?n simula bytes de otra versi?n mediante interceptaci?n en un contexto aislado: el SHA discrepante bloquea el visor. No se alter? ning?n archivo real para esta prueba. Regresi?n de favoritos, etiquetas, exportaci?n y m?vil completada.

## Ampliaci?n con Tanda 4 ? 28/10/2026

La base acumulada ahora contiene 66 modelos y 71.227 canales verificados. Las cifras previas de esta revisi?n describen la primera entrega. Ver `E:\l2-local\research\external-assets-round4-20261028\REVISION.md` para las 55 nuevas incorporaciones y sus l?mites visuales. La reproducci?n normaliza tiempos solo sobre copias en memoria; el GLB y SQLite conservan tiempos originales.
