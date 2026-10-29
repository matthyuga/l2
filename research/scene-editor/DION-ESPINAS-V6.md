# Dion V6 · variantes según bocetos de Kevin

26/10/2026. Petición: tres espinas separadas en fila por una calle, arqueadas hacia la misma dirección; además una grande solitaria y dos grupos combinados, siguiendo dibujos adjuntos. Se construyeron cuatro recursos originales: single.glb,giant.glb,interlaced.glb,branched.glb.

Proyecto http://127.0.0.1:32290/?project=dion-hecatombe-v6.json; ABRIR-DION-HECATOMBE-V6.cmd. Selector Dion · Hecatombe V6 · Espinas variadas. Abre directamente la calle. Cámara7: fila de tres;8:espina gigante;9:arcos entrelazados;10:ramificada. Cámaras1..6 y mapa/coloniasV5 conservados.

Las tres espinas de calle son objetos independientes, escalas1/1,1/1,23, ubicación aproximada nativa(18,-20),(18,8,-26),(19,6,-32), mismo giro. No tienen membrana estrellada grande: solo collar pequeño de enraizamiento. Perfil tipo hoja/colmillo aplanado, base ancha, punta curvada, sección asimétrica, acanaladuras leves. Las combinadas se construyeron como arcos opuestos y tronco con ramas laterales. Gigante1,75veces el modelo simple. Variantes adicionales en exteriores, con altura de terreno muestreada; algunas intersecciones menores con escombros/vegetación pueden ajustarse desde el Taller.

Todos disponibles desde Añadir, nombres Plaga · Espina arqueada individual / Espina gigante solitaria / Arcos orgánicos entrelazados / Espina ramificada. Los6objetos añadidos pueden moverse/rotarse/escalarse sin modificarV5. Geometría estática, cero física/partículas/animación nuevas. Material vivoV5 aplicado por prefijo custom_dion_spine_v6_ en app.js. Shader de fibras/vetas propio del Taller, no horneado a GLB externo.

Constructor build-dion-spines-v6.py,registro register-dion-spines-v6.py; ambos protegen versiones previas. Exportaciones model-catalog/exports/dion-spines-v6; audit y placements. Proyecto projects/dion-hecatombe-v6.json. Backup data en backups/dion-spines-v6. No regenerar encima de ediciones futuras de Kevin.

Pruebas verify-dion-v6.cjs:65objetos,6nuevas colocaciones,3espinas simples con mismo giro, cuatro cámaras nuevas, carga/shaders sin errores, guardado/reapertura. Resultado dion-v6-verification.json; capturas preview-dion-v6-calle/gigante/entrelazadas/ramificada.png revisadas. V5 y clienteUNR/juego no modificados.
