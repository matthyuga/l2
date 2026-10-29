# Vigilia ? cabeza original Red Dragon ? 20/10/2026

Estado: COMPLETADO EN EL TALLER. Kevin descarg? el ZIP oficial en `descarga de assets/red-dragon.zip` y autoriz? adaptar este modelo a la aeronave tras rechazar la recreaci?n anterior.

## Abrir y revisar

- Proyecto: http://127.0.0.1:32290/?project=vigiliareddragon1.json
- Vista sin globo, con referencias de personaje: http://127.0.0.1:32290/?project=vigiliareddragon1-escala.json
- Toma 9: detalle de la cabeza original en la proa.
- Capturas: `mapas editados/vigiliareddragon1/general.jpg`, `dragon-integrado.jpg`, `dragon-diseno.jpg`, `cubierta-conservada.jpg`.

## Modelo y modificaciones

Se import? el FBX original de GadgetHamster, con dise?o de Alexander Ostrowski, desde el archivo proporcionado por Kevin. Se conservaron la malla de cabeza/cuello, los dientes, ojos, UV y los mapas originales de color, normal OpenGL, rugosidad y emisi?n de 4096?4096. No se recre? ni sustituy? la anatom?a con primitivas.

Se aislaron cabeza y cuello mediante los pesos del esqueleto; se retiraron cuerpo, extremidades y alas. Corte de cuello en Y3,75 del FBX original, cerrado con una cara de tapa. Se fij? la pose de reposo, con boca abierta; la versi?n instalada en el proyecto es est?tica, sin armature ni animaciones de vuelo. Se orient? hacia proa (+X de Blender), con inclinaci?n de 29 grados y escala1,85. El acabado rojo/negro original se mantiene para comparar su encaje en la nave. La cabeza conserva 26.428 tri?ngulos; el export con casco suma41.948.

El m?ster parte de `research/vigilia-clan-renovada2/Vigilia-renovada2.blend`. Se retiraron solo las piezas del mascar?n anterior en la copia y se verificaron sin cambios las otras1.467 mallas. Las otras15zonas del JSON conservan recursos, IDs, transformaciones y visibilidad. El nuevo proyecto tiene17objetos y la cabeza independiente `VIG_16_RedDragon`.

Vigiliarenovada2, vigiliadragon1 y sus borradores no se modificaron. El ZIP y FBX originales se conservan; hashes en `archive-sha256.txt` y `adaptation-audit.json`. Gludio, Academy/Hellgames y el cliente nativo se conservan. Esto es una prueba visual en el taller; no una instalaci?n de mapa/colisi?n/geodata en L2.

## Archivos

- `source/`: ZIP extra?do; FBX y mapas originales.
- `RedDragon-source-import.blend`: importaci?n completa original, con esqueleto y poses.
- `RedDragon-head-adapted.blend`: cabeza y cuello aislados.
- `Vigilia-RedDragon.blend`: nave completa con cabeza original adaptada.
- `adapt_head.py`: adaptaci?n reproducible; no reejecutar sobre ediciones manuales sin respaldo.
- `register-project.cjs`: registro de cat?logos y creaci?n de las dos variantes. Rechaza sobrescribir el JSON sin --rebuild.
- `research/model-catalog/exports/vigilia-red-dragon/red-dragon-head.gltf`: casco sin mascar?n viejo y cabeza original con materiales; dependencias en la misma carpeta.
- `research/scene-editor/projects/vigiliareddragon1.json`, copia id?ntica en `mapas editados/vigiliareddragon1`.
- `adaptation-audit.json`, `import-inventory.json`, `project-registration.json`, `verification.json`.
- Respaldo de cat?logos anterior al registro: `backups/vigilia-red-dragon-20261020`.

## Validaci?n

`verify-adaptation.cjs` PASS: carga WebGL real de17objetos, conservaci?n exacta de15zonas ajenas al mascar?n/casco, exportaci?n JSON, guardado API, recarga, variante de escala, Blender/JSON/export de vigiliarenovada2 sin modificar y sin errores JavaScript/HTTP. Vista general: aproximadamente138miltri?ngulos y77llamadas de dibujo. Se revisaron im?genes del detalle aislado, integraci?n y conjunto.

## Atribuci?n

Red Dragon ? GadgetHamster. Dise?o del personaje: Alexander Ostrowski.
Fuente: https://sketchfab.com/3d-models/red-dragon-77e89ab9b88a444cb51339c2ed3959a3
Autor: https://sketchfab.com/GadgetHamster
Licencia: Creative Commons Attribution4.0, https://creativecommons.org/licenses/by/4.0/
Cambios: aislamiento de cabeza/cuello, cierre del corte, pose est?tica, orientaci?n/escala y adaptaci?n a la proa. Cr?dito conservado en este documento, en ambos proyectos, en los cat?logos y en asset.copyright del glTF.
