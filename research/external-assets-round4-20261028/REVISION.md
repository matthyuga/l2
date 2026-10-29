# Assets externos · Tanda 4 — 28/10/2026

Importación incremental de las nuevas descargas de `E:\l2-local\descarga de assets`.

[Abrir Tanda 4 en el catálogo](http://127.0.0.1:32280/?batch=Assets%20externos%20%C2%B7%20Tanda%204)

## Resultado

- 55 modelos con miniatura y vista 3D; 0 pendientes de esta tanda.
- 37 modelos nuevos con esqueleto.
- 19 modelos nuevos con clips; 285 clips exportados en total.
- 66 modelos en el índice técnico acumulado de huesos y animaciones.
- 3057 fichas previas conservadas exactamente, incluidas sus referencias técnicas.
- 55 archivos ZIP originales comprobados por SHA-256 antes y después.

## Categorías

- NPC: 32
- Objetos: 17
- Monstruos: 6

## Animaciones

- Alastor: 1 clips.
- Apex Legends CAR SMG Mythic Allfather's Fury: 1 clips.
- Arachnida: 24 clips.
- Beyond Resurreccion Grimmjow: 20 clips.
- Deep monstrosity: 43 clips.
- Empire Flamethrower Energy Cannon: 2 clips.
- Kurosaki Ichigo: 34 clips.
- Leocetus Leader: 1 clips.
- Lizard Man Warrior: 1 clips.
- Lust: 1 clips.
- Maw: 83 clips.
- Mugetsu Ichigo: 21 clips.
- Quincy Ichigo: 23 clips.
- Serephina: 8 clips.
- Ulquiorra Cifer: 1 clips.
- Ultron Cannon: 1 clips.
- Valak: 1 clips.
- Zaraki Kenpachi: 18 clips.
- Zeromus: 1 clips.

Los nombres de movimientos se conservan tal como aparecen en el archivo; no certifican daño, alcance, IA ni equivalencia con una habilidad de L2. La reproducción desplaza cada clip a cero sobre una copia en memoria, para evitar esperas cuando el original usa tiempos absolutos tardíos. No se modifican los tiempos de los GLB ni los datos almacenados en SQLite.

## Materiales y calidad

- 47 vistas con mapas y sin referencias ausentes detectadas; 8 con revisión de materiales pendiente; 0 sin mapas de imagen.
- El estado de textura no garantiza equivalencia de todos los shaders con el programa de origen. Las observaciones visuales particulares se incorporan a la ficha.
- Las vistas del catálogo no equivalen a una adaptación UKX/UTX para Interlude.

## Observaciones visuales

- Beyond Resurreccion Grimmjow: Revisar la orientación de la pose base; sus clips se conservan sin certificar el resultado en otro esqueleto.
- Reaper AA Gun: Los componentes y las transparencias requieren revisión visual; la vista actual no representa un arma ensamblada validada.
- Serephina: La pose importada presenta deformaciones y una vista base poco visible. El rig y sus componentes requieren revisión antes de reutilizarlo.
- Ulquiorra Cifer: Revisar la orientación de la pose base antes de usarlo como personaje.

## Archivos

- [Inventario CSV](INVENTARIO.csv).
- [Métricas](summary.json).
- [Integridad de las descargas](source-integrity.json).
- [Prueba del navegador](browser-verification.json).
- [Contacto visual 1](contacto-1.jpg)
- [Contacto visual 2](contacto-2.jpg)
- [Contacto visual 3](contacto-3.jpg)

Base técnica acumulada: `E:\l2-local\research\rig-database-20261028\rig-catalog.sqlite`. Se conservó una revisión SQLite coherente antes de ampliarla. Los originales y los favoritos del navegador real no fueron alterados. Respaldo de catálogo y visor en `E:\l2-local\backups\external-assets-round4-20261028`.
