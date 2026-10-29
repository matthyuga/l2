# Dion Hecatombe V3 · edificio pendiente y muros

26/10/2026. Kevin mostró un edificio con cubierta suspendida sobre muros intactos y pidió daño coherente, además de deterioro desigual en murallas. Se identificó Dion_NV_DE (StaticMeshActor1006_0) y Dion_NV_DE_Top (593_0), omitidos de las27 sustitucionesV2. No era una textura faltante: V1 deformó su cubierta sin sustituir su base.

Entrega separada: http://127.0.0.1:32290/?project=dion-hecatombe-v3.json; ABRIR-DION-HECATOMBE-V3.cmd. Selector Dion · Hecatombe V3 · Muros y edificio. Cámara4 enfoca el edificio corregido; cámara1 general. V2 permanece intacto.

El edificio DE se recuperó de la geometría original, se fragmentó y colapsó con Bullet, y recibió astillas/agujeros/escombros mediante el constructorV2.106 piezas estáticas (42 fragmentos del edificio y64 restos). Ambas piezas antiguas se retiraron del coreV3; no se dejó encima la cubierta aplastada de V1. El nuevo conjunto se ubicó usando el centro de la construcción original y su cota baja.

Siete actores Dion_NV_Wall01..05 fueron retirados del core y sustituidos por secciones dañadas nativas. Severidades por tramo:28%,75%,48%,90%,18%,65%,40% (parámetros artísticos, no porcentaje volumétrico medido). Alturas variables y brechas con recorte vertical por secciones; se eliminó el remate continuo sobre los huecos. Mampostería caída a los pies. No hay física en ejecución ni simulación estructural de muros. Daño estático, superficies interiores aproximadas.

La primera prueba con booleanas sobre los muros dejaba una tira de remate atravesando brechas. Se descartó ese resultado y se reemplazó por fix-dion-v3-walls.py con cortes por celdas y altura variable. Captura final revisada: sin esa tira. El centro de normalización del nuevo conjunto de muros se recalculó en el proyecto.

Archivos: build-dion-v3-damage.py (fuente reducida, edificio), fix-dion-v3-walls.py (muros definitivos), register-dion-v3.py (registro inicial). Proyecto projects/dion-hecatombe-v3.json. Exportaciones ../model-catalog/exports/dion-hecatombe-v3, con core.gltf que conserva dependenciasV1/V2, house11.glb y damaged-walls.glb. No mover el core aislado. register-dion-v3.py rechaza proyecto existente; antes de reutilizarlo incorporar el recálculo definitivo del centro de muros que se hizo tras fix-dion-v3-walls.py. No sustituir cambios futuros de Kevin.

Prueba verify-dion-v3.cjs pasó WebGL, ausencia de actoresDE antiguos, carga de muros y casa sin animación, cámara4 y guardado/reapertura.58objetos y28emisores; vista general1.161.001triángulos/2795draw calls. Resultado dion-v3-verification.json; capturas preview-dion-v3-general/edificio.png. Esos datos no garantizan FPS en la pestaña del usuario. No se modificó UNR,cliente ni servidor de juego.
