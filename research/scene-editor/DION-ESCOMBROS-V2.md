# Dion · Escombros irregulares V2

26/10/2026. Variante separada pedida por Kevin para eliminar el aspecto de bloques cortados rectos. La colección V1 de 132 fragmentos y la simulación original se conservaron.

Abrir http://127.0.0.1:32290/?project=dion-escombros-v2.json o ABRIR-ESCOMBROS-DION-V2.cmd. Selector: Dion · Escombros irregulares V2. Cámara1 detalle central, 2 vista general, 3 casa izquierda. Cada raíz de casa está desbloqueada; expandir árbol o modo Piezas para modificar sus fragmentos. Suelo de exposición independiente y protegido.

Cambios: subdivisión de bordes de corte, mellas geométricas deterministas, bisel leve y cortes booleanos sobre caras seleccionadas. 132 fragmentos originales modificados y 34 operaciones booleanas que alteraron la geometría. Las operaciones incluyen huecos y mordidas: no cada operación implica necesariamente un agujero pasante visible desde todos los ángulos. Nuevos restos por casa: 24 ladrillos, 14 astillas/vigas, 18 tejas y 8 piezas de puerta (6 tablas y 2 travesaños). Total: 324 piezas, agrupadas en tres casas.

Materiales: texturas originales exteriores conservadas; material liso interior sustituido por mampostería o madera con UV proyectadas. Texturas CC0 existentes ambientCG Bricks001 y Planks001, imágenes de 512px embebidas; terracota para tejas desprendidas. Agujeros, bordes y astillas son geometría, no solo manchas de textura. No se instalaron herramientas ni se modificó el cliente de juego.

Importante: esta pasada es daño artístico aplicado después de congelar el derrumbe; no se recalcularon los contactos tras las pequeñas modificaciones. El resultado sigue siendo estático, sin clips ni física ejecutándose. Algunas piezas conservan superficies planas y cortes interiores aproximados; no constituye una simulación de rotura de cada ladrillo.

Constructor build-dion-rubble-v2.py; salidas ../model-catalog/exports/dion-rubble-v2/house1..3.glb y damage-audit.json. Semilla271026. Fuentes V1 comprobadas sin cambios mediante SHA-256. Salida existente protegida contra reconstrucción. Blender terminó los tres exports; PowerShell reportó salida1 al capturar avisos de deprecación de Material.use_nodes, sin traceback/errores de construcción; GLB y audit producidos y verificados.

Registro register-dion-rubble-v2.py, backup de data.json antes del alta. No reejecutar para sustituir ediciones futuras de Kevin. Proyecto projects/dion-escombros-v2.json, recursos disponibles en Añadir.

Pruebas verify-dion-rubble-v2.cjs: carga WebGL sin errores, 111/108/105 nodos editables, cero animaciones, 8 piezas de puerta/24 ladrillos/14 astillas/18 tejas por casa, movimiento de fragmento y persistencia al guardar/reabrir. Resultado dion-rubble-v2-verification.json. Vista de detalle:67.964 triángulos y460 llamadas de dibujo, según encuadre. Captura preview-dion-escombros-v2-detalle.png revisada visualmente. No se garantiza rendimiento de una ciudad completa con estos recursos.
