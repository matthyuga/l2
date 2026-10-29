# Casas de Dion destruidas en bloques — 26/10/2026

Entrega: tres modelos de casa real de Dion Classic IL divididos en 132 fragmentos, fijados en el estado final de sus simulaciones. No es todavía la sustitución de todas las casas del mapa de Dion.

Abrir http://127.0.0.1:32290/?project=dion-casas-destruidas-bloques-v1.json o ABRIR-CASAS-DESTRUIDAS-DION.cmd. Selector: Dion · Casas destruidas en bloques. Las tres ruinas también están registradas en Añadir como recursos reutilizables.

Cada raíz Casa 1/2/3 contiene bloques independientes: expandir la flecha del árbol derecho y seleccionar una pieza Techo/Pared, o usar modo Piezas en el visor. Las casas están desbloqueadas; el suelo de exposición está protegido. Se puede mover la ruina completa o transformar/ocultar sus fragmentos internos. Sus cambios se conservan como parts en el proyecto JSON. Guardar como conserva una copia propia.

Casa H01: 47 bloques (congelados desde la prueba inicial, sin volver a simular); H02: 44; H03_A: 41. Estas dos últimas se fragmentaron y simularon con el mismo constructor parametrizado build-dion-collapse.py --static. Actores H02: StaticMeshActor322_0/795_0; H03_A: StaticMeshActor89_0/134_0. 132 piezas reales; no son 132 ladrillos individuales. Grosor aproximado de 10 cm para las superficies originales. Texturas de fachada y tejas conservadas; las caras interiores de corte usan material liso.

Salidas finales ../model-catalog/exports/dion-ruins-blocks-v1: house1.glb, house2.glb, house3.glb y suelo separado floor.glb. Cada GLB de casa contiene sus nodos de fragmentos, materiales/texturas embebidos y cero clips de animación. Ya no necesita ejecutar simulación. Piso de exposición independiente, no se incluye en las casas reutilizables.

register-dion-ruins.py registra assets y escena base; captura del proyecto desde navegador aislado con verify-dion-ruins.cjs. No reejecutar el registro para sobrescribir futuras ediciones del proyecto del usuario. El constructor original de derrumbe mantiene parámetros por defecto y rechaza sobrescribir salidas existentes. Las simulaciones y Hecatombe V1 originales se conservaron.

Verificación: dion-ruins-verification.json. Carga WebGL, 132 fragmentos, texturas presentes, ausencia de animaciones, selección de pieza editable, cambio de posición de un bloque sin alterar otras casas y guardado/reapertura de esa transformación. Captura preview-dion-casas-destruidas.png. Pruebas en navegador aislado; JSON del usuario sin modificar. Registro conserva backups previos de data.json. Sin instalación en cliente L2/servidor.
