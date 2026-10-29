# Prueba de derrumbe de una casa de Dion

Fecha: 26/10/2026. Primera demostración visible, separada de Dion Hecatombe V1.

Abrir http://127.0.0.1:32290/assets/exports/dion-collapse-demo-v1/demo.html o ABRIR-PRUEBA-DERRUMBE-DION.cmd. Botones Ver derrumbe/Pausar, Casa intacta, Ver restos, Encuadrar; cámara lenta y barra temporal. Cámara orbital, zoom y desplazamiento. La página explica sus límites.

También se registró el escenario Dion · Prueba de física en el Taller. Proyecto projects/dion-collapse-demo-v1.json. Abrir http://127.0.0.1:32290/?project=dion-collapse-demo-v1.json, seleccionar la casa en el árbol y reproducir el clip en el panel de animación. El clip se detiene al terminar.

Fuente: casa real Dion Classic IL, StaticMeshActor34_0 (Dion_NV_H01) y StaticMeshActor129_0 (Dion_NV_H01_Top), extraída de scenario-batches/library_fe488fdfccee/scene-with-terrain.blend. Texturas originales de la casa conservadas. Suelo de prueba con textura de losas de Giran. Fuente y proyecto Hecatombe V1 sin sobrescribir.

Preparación: corte de la geometría en celdas, conservación de UV y materiales, grosor de 0,10 m para las superficies arquitectónicas. Resultado: 47 fragmentos, 12 de techo y 35 de paredes. Colisionadores convexos, suelo pasivo, gravedad de -9,81 m/s², 8 subpasos y 30 iteraciones de resolución por frame en Bullet/Blender 5.0.1. 216 frames a 24 FPS. Piezas sujetas mediante estado cinemático hasta frame 30 y liberadas en frame 31. El movimiento posterior resulta de gravedad y contactos, no de keyframes dibujados a mano.

Límite importante: la liberación está programada; NO calcula resistencia, conexiones estructurales ni decide qué apoyo falla. NO hay fractura dinámica de edificios arbitrarios ni física en vivo en el navegador. Tampoco representa cada ladrillo. Es una prueba de caída y colisión de fragmentos preparados, grabada para reproducción ligera. Las colisiones convexas aproximan la forma, y las roturas en cuadrícula son deliberadamente sencillas.

Blender: build-dion-collapse.py, salida ../model-catalog/exports/dion-collapse-demo-v1/simulation.blend, collapse.glb y simulation-audit.json. register-dion-collapse.py combina 47 clips simultáneos en uno, registra el asset/escenario y conserva un backup de data.json. El constructor rechaza sobrescribir una salida existente. No ejecutarlo para modificar cambios del usuario.

Verificación: verify-dion-collapse.cjs y dion-collapse-verification.json. Comprobados carga WebGL sin errores, 47 transformaciones, 40 piezas desplazadas más de 0,3 m, reproducción, resultado final, retorno de todas las piezas a su pose inicial, barra temporal, repetición tras acabar e integración con la animación del Taller. Vista aislada: unos 60 FPS, 183 llamadas de dibujo, unas 6.500 caras/triángulos visibles (varían por encuadre). Capturas preview-dion-collapse-before/falling/after/editor.png. No se midió la pestaña del usuario.

model-motion.js local se usa ahora desde app.js en vez de la copia dentro del Behemoth; el clip de derrumbe usa LoopOnce y clampWhenFinished. Los clips normales conservan su bucle. El lanzador del Taller admite -CollapseDemo. No se instaló software ni se modificó el cliente L2/servidor de juego.
