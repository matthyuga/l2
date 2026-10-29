# Retorno a casa — 19/10/2026

Ruta operativa: `E:\l2-local`. Revisión de los trabajos del 18/10 en W11.

- Ciudad de Giran (`22_22.unr`) integrada al selector del taller normal (lanzador 19). Los informes y capturas del 18/10 muestran 1.938 objetos, 524.341 triángulos y suelo visible/texturado. Se recuperaron 189 pinceles BSP aditivos para plazas, calles e interiores; auditoría: 22 materiales texturados, sin texturas faltantes. Castillo/territorio (`23_22`) es otra escena.
- Ambientación L2: 172 recursos importados, incluidos 97 árboles/vegetación, 24 naturaleza/rocas, 11 estatuas, 24 ruinas y 16 decoración/estructuras.
- Recursos web: 329 Kenney Nature Kit y 12 Fantasy Ruins importados en el catálogo. Son modelos añadibles al taller. El log de conversión fallida de Collada corresponde a un intento previo; existen las 12 conversiones finales y su manifiesto.
- Se detectó una regresión posterior a las pruebas de Giran: `import-web-assets.cjs` reemplazaba la lista de assets desde la galería, que no contiene los mapas especiales. El JSON conservaba las escenas pero perdía `scene_giran` y `scene_giran_city`.
- Corregido el importador para conservar los assets de las escenas; regenerado `data.json` con `build_data.py`: 2.801 assets. `verify-web-catalog.cjs` verifica conservación, cuatro escenas con archivo existente y los 341 modelos web. PASS.
- Respaldo anterior a la reparación: `backups/scene-catalog-recovery-20261019`.
- Prueba actual `verify-giran-city.cjs` PASS: 1.938 objetos, 524.341 triángulos, BSP incluido y sin errores JavaScript. Editor iniciado en `http://127.0.0.1:32290`.
- La importación también descartaba `native`, `batch` y `sourcePackage`, ocultando recursos L2 en el filtro normal. Ambos generadores ahora conservan esos campos y se restauraron las 172 marcas nativas en el catálogo. Prueba actual `verify-l2-environment.cjs` PASS: 97 recursos de vegetación, miniaturas y selección para colocar. Se corrigió la espera de carga de imagen del verificador con `decode()`.

La integración es del editor visual. No significa exportación de modificaciones al cliente L2 ni edición de sus mapas nativos. No se modificaron proyectos guardados del usuario, base de juego, Academy ni Hellgames.

## Visor modular y distribución corregida

La captura de Kevin confirmó que el visor ocupaba sólo la mitad superior: `panel-layout.css` imponía dos columnas sobre las tres definidas por `workspace.css`. El árbol se colocaba automáticamente en una segunda fila. Eliminada esa contradicción y fijadas las tres columnas en una fila de altura completa.

Barra nueva sobre el mapa: Ventana flotante (arrastrar cabecera, redimensionar esquina inferior derecha), Ampliar/Restaurar, Pantalla completa/Salir y Acoplar. Conserva escena y cámara. Ampliar ocupa el navegador; Pantalla completa usa la API del navegador y permite salir con Escape. Al acoplar se retira el tamaño de la ventana flotante y se recupera la distribución normal.

`verify-viewport-window.cjs` PASS en 1314×622, 1600×1000 y 900×650: altura completa, árbol a la derecha, arrastre, cambio de tamaño y canvas, ampliar/restaurar, fullscreen/salida, acoplar, paneles plegados y objetos conservados, sin errores JS. Capturas `preview-visor-completo.png`, `preview-visor-maximizado.png`. Giran volvió a pasar con 1.938 objetos; captura actual revisada visualmente, suelo visible. Su verificador ahora cuenta geometría fuente por separado: los triángulos visibles cambian legítimamente por la proporción del visor y el frustum culling. Respaldo `backups/viewport-layout-20261019`.
