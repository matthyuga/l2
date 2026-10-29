# Dion Hecatombe V2 · Escombros integrados

26/10/2026. Kevin aprobó el aspecto de los escombros irregulares y pidió aplicarlos al mapa devastado. Variante separada lista en http://127.0.0.1:32290/?project=dion-hecatombe-v2.json. Lanzador ABRIR-DION-HECATOMBE-V2.cmd. Selector Dion · Hecatombe V2 · Escombros. Cámara1 general,2 acercamiento,3 calle.

Se sustituyeron los27 edificios residenciales/comerciales que V1 había recortado, con sus28 techos asociados. Diez tipos nativos H01,H02,H03_A,H03_B,H04,Agit01,BS,WH,WG,SH01, incluyendo las construcciones de las afueras. No se intercambiaron diseños por una plantilla genérica: se generaron también los7 tipos que faltaban. Iglesia, murallas, terreno y entorno permanecen en el core; no afirmar que se destruyeron todos los edificios de cualquier clase del mapa.

Cada tipo procede de su casa original, fragmentada y colapsada en Blender, luego astillada/perforada con el procedimiento V2. Escombros,tejas,ladrillos,madera y puertas rotas conservados. Se retiraron los cubos/vigas genéricos de V1 y props interiores/signos dentro de las huellas arrasadas que podían quedar flotando.

Posición: se recuperaron las coordenadas nativas y se compensó la normalización del editor por centro de bounding box. En V1 el root había quedado con posición0 después de normalizarlo, desplazando el conjunto respecto de efectos definidos en coordenadas nativas; V2 compensa ese centro. Cada ruina conserva orientación relativa a su prototipo; altura del terreno muestreada bilinealmente por fragmento antes de agrupar materiales. Esto es ajuste aproximado al heightfield, no una nueva simulación conjunta de todos los edificios: pueden persistir intersecciones de restos entre edificios cercanos.

Se agruparon las geometrías por material dentro de cada casa:637 primitivas para27 ruinas. Cada ruina es un conjunto editable; los bloques detallados siguen en sus archivos/fuentes de escombros (tipos1..3 dion-rubble-v2,4..10 dion-city-rubble-v2). Se conservan las colecciones anteriores. Nuevo mapa sin física ni clips de derrumbe ejecutándose;28 emisores fuego/humo más cenizas ambientales. Fuego/humo reducidos para dejar leer los restos.

Archivos: projects/dion-hecatombe-v2.json; ../model-catalog/exports/dion-hecatombe-v2/core.gltf, StaticMeshActor*.gltf/.bin, type*.bin y placement-audit.json. Esos glTF dependen de los bin compartidos y el core de las exportaciones originales: no moverlos aislados. FuenteV1 hash comprobado sin cambios.

Construcción: build-dion-city-extra.py genera fuente Blender reducida para los7 tipos adicionales y reutiliza build-dion-collapse.py --static --source y build-dion-rubble-v2.py con parámetros de directorio/tipos. apply-dion-city-rubble-v2.py prepara el mapa/terreno y registra assets/proyecto; rechaza sustituir un proyecto existente. Preservar cambios posteriores de Kevin. Copia de data previa en backups/dion-hecatombe-v2.

Verificación: verify-dion-city-v2.cjs, dion-city-v2-verification.json; carga WebGL sin errores,56 objetos (core+27ruinas+28efectos),27 edificios/10tipos, recuperación de cámara, guardado y reapertura. Prueba aislada1600×1000:60FPS,2112 llamadas,1.117.418 triángulos visibles. No es una garantía para otra pestaña/hardware. Capturas preview-dion-hecatombe-v2-general/calle.png revisadas. Sin modificación de mapasUNR,cliente ni servidor de juego.
