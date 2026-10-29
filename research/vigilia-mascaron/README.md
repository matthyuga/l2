# Vigilia · mascarón naval propio — 20/10/2026

El usuario rechazó el encaje del Red Dragon original: la criatura roja parecía de otro universo que el barco. Autorizó usarlo como guía para un diseño propio acorde con la aeronave.

Abrir: http://127.0.0.1:32290/?project=vigiliamascaron1.json

Variante de escala: http://127.0.0.1:32290/?project=vigiliamascaron1-escala.json

Toma 9: detalle del mascarón. Capturas en `mapas editados/vigiliamascaron1`: `general.jpg`, `dragon-integrado.jpg`, `dragon-diseno.jpg`, `cubierta-conservada.jpg`.

## Diseño

Geometría original, sin utilizar la malla del Red Dragon. Conserva como guía su perfil alargado, cuernos barridos, cresta nasal y aletas de mejilla. Se interpreta como una pieza fabricada por los constructores del barco:

- Roble con la misma textura y acabado del casco, nogal y el mismo bronce envejecido de la nave.
- Boca estrecha sin lengua ni encías, dientes fundidos de bronce e incrustaciones pequeñas de ámbar relacionadas con los faroles.
- Escamas como bajorrelieves de madera y volutas de bronce, reducidas para conservar la lectura del conjunto.
- Collar y tirantes de anclaje visibles en la unión al casco.

## Archivos

- Máster: `Vigilia-mascaron.blend`, 113 piezas nuevas independientes.
- Generador: `build_figurehead.py`. Utiliza los ayudantes geométricos y la selección de piezas antiguas definidos al inicio de `research/vigilia-dragon-sculpt-20261020/recreate_dragon.py`; no ejecuta el diseño rechazado. No reejecutar generadores sobre ediciones manuales sin respaldo.
- Export: `research/model-catalog/exports/vigilia-mascaron/mascaron.gltf`, casco sin mascarón anterior y nuevo `VIG_16_Mascaron`.
- Recurso: `custom_vigilia_mascaron`, registrado en data/gallery/custom-assets.
- Proyecto y copia idéntica: `research/scene-editor/projects/vigiliamascaron1.json`, `mapas editados/vigiliamascaron1/vigiliamascaron1.json`.
- Auditoría: `design-audit.json`; prueba: `verification.json`; registro: `project-registration.json`.
- Respaldo de catálogos: `backups/vigilia-mascaron-20261020`.

## Conservación y pruebas

La geometría y materiales de 1.467 mallas ajenas al mascarón anterior se conservan por firmas, así como el hash del Blender de vigiliarenovada2. Las otras quince zonas del JSON mantienen IDs, recursos, transformaciones y visibilidad. Las versiones anteriores, el FBX original y los borradores se conservan. El nuevo proyecto tiene 17 objetos.

`verify-figurehead.cjs` PASS: carga WebGL real, exportación, guardado API, recarga, variante con referencias de escala, originales Blender/JSON/export intactos y sin errores HTTP/JavaScript. Aproximadamente 145.000 triángulos y 79 llamadas de dibujo en la vista general. Export de reemplazo: 49.036 triángulos, incluyendo casco.

Prueba visual del taller, sin instalación de cliente L2 ni cambios de colisión/geodata. Gludio, Academy y Hellgames no se modificaron.

Referencia visual: Red Dragon de GadgetHamster, diseño de Alexander Ostrowski, CC BY 4.0: https://sketchfab.com/3d-models/red-dragon-77e89ab9b88a444cb51339c2ed3959a3. No se usa su malla ni sus texturas en esta variante.
