# Taller L2: retorno a casa — 19/10/2026

Ruta real `E:\l2-local`. Estado detallado: `research/scene-editor/ESTADO-RETORNO-CASA-20261019.md`.

Giran ciudad sí quedó integrado y con piso texturado (189 pinceles BSP recuperados). La última importación web del 18/10 había quitado las referencias de mapas del catálogo, sin borrar archivos. Reparado `import-web-assets.cjs` para conservarlas y regenerado `data.json`. Verificación actual de carga de ciudad PASS: 1.938 objetos, 524.341 triángulos y sin errores JS. Regresión del importador PASS: cuatro escenas y 341 assets web registrados.

Biblioteca añadida: 172 recursos ambientales L2 (97 árboles/vegetación, 24 naturaleza/rocas, 11 estatuas, 24 ruinas y 16 decoración), más 329 Kenney Nature Kit y 12 Fantasy Ruins. Editor normal: lanzador 19, `http://127.0.0.1:32290`, selector Ciudad de Giran. Se inició el servidor del editor para verificar; no se abrió cliente L2 ni se tocaron sus mapas, base, Academy/Hellgames o proyectos guardados del usuario.

Respaldo de reparación `backups/scene-catalog-recovery-20261019`. Integración al taller visual; exportación nativa al juego sigue siendo otro pendiente.

También corregida pérdida de metadata `native/batch/sourcePackage` en los dos generadores de catálogo: restauradas 172 marcas nativas. Prueba actual de biblioteca L2 PASS (97 árboles/vegetación, miniaturas, selección); verificador espera `image.decode()` para evitar comprobar imágenes antes de cargar. Editor queda iniciado en puerto 32290.

Pedido posterior Kevin: visor a media altura. Corregida contradicción de CSS de dos/tres columnas: árbol vuelve a derecha y visor ocupa altura completa. Visor modular con ventana flotante arrastrable/redimensionable, ampliar/restaurar, pantalla completa real y acoplar. Prueba de todos los modos y tres resoluciones PASS, objetos intactos. Giran 1.938 objetos PASS y captura actual con suelo revisada. Detalles en documento local de retorno; backup `backups/viewport-layout-20261019`. Para recibir cambios guardar proyecto y recargar navegador.

Auditoría posterior de los 513 assets ambientales: `research/scene-editor/environment-assets-audit.json`, PASS; 172 L2 +329 Kenney +12 Fantasy Ruins, 1.526 archivos de modelo/miniatura/dependencias leídos y SHA256 registrados, cero problemas. Fuentes Kenney 329 GLB y Fantasy Ruins 12 DAE coinciden con importados; ZIP originales presentes en `research/web-assets/downloads`. Catálogo local en disco, no afirmar respaldo externo/nube: `git -C cloud-repo ls-files` no muestra estos recursos. Para ver todo usar filtro Todo el catálogo en biblioteca.
