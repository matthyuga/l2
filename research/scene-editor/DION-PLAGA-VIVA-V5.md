# Dion V5 · plaga viva

26/10/2026. Kevin propuso formas espinosas emergiendo de la tierra y tejido vivo, como referencia de infestación orgánica. Se crearon geometrías originales en Blender, sin importar assets de otro juego.

Abrir http://127.0.0.1:32290/?project=dion-hecatombe-v5.json o ABRIR-DION-HECATOMBE-V5.cmd. Selector Dion · Hecatombe V5 · Plaga viva. Cámara6 detalle de una colonia;1 general. V4 conservado.

Ocho colonias en sectores abiertos y un grupo pequeño entre ruinas. Cada una tiene membrana lobulada apoyada en el terreno,7raíces sinuosas,5espinas curvas de quitina y5nódulos. Total40espinas/56raíces. Suelo muestreado bilinealmente desde el heightfield nativo; membranas y raíces siguen su relieve. Alturas/curvaturas variables con semilla271029. Material granate oscuro y quitina gris-púrpura, vetas/manchas/fibras mediante shader estático. No es animación biológica ni física activa; no se añadieron partículas.

Constructor build-dion-living-v5.py, salida model-catalog/exports/dion-living-v5/colonies.glb y organic-audit.json. Protección de salida existente; --refine se usó solo durante preparación antes de entregar. living-material.js añade variación superficial en el Taller; app.js lo aplica exclusivamente al asset custom_dion_living_v5. Shader no horneado al GLB para otros visores. SueloV4 conserva su módulo y escenas anteriores conservan materiales.

Registro register-dion-living-v5.py; proyecto projects/dion-hecatombe-v5.json.59objetos en mapa. Expandir Plaga viva en el árbol para seleccionar componentes; movimiento del conjunto conserva posiciones relativas. Copia data previa en backups/dion-living-v5. Fuentes y V4 no sustituidas.

Verificación verify-dion-v5.cjs pasó carga WebGL/shaders sin errores,59objetos,cámara6,guardado/reapertura. Capturas preview-dion-v5-general/tejido.png revisadas; se corrigieron normales de la membrana y material demasiado plano antes de entregar. Resultado dion-v5-verification.json. Vista general2937draw calls/1.195.537triángulos. No se midió FPS en la pestaña de Kevin. Sin instalación de cambios en clienteUNR/juego.
