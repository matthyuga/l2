# Reparaciones de apariencia v12

Instaladas el 26/10/2026 tras el diagnóstico con REA y la autorización del usuario. Pendiente comprobar el resultado dentro del juego, especialmente la orca J, donde el análisis no pudo descartar por completo falta de cobertura geométrica.

Se cambió únicamente lo siguiente:

- **Elfo oscuro masculino, G:** los cuatro colores apuntan a materiales nuevos con AlphaRef=160, como el material donante. Mezcla alfa, prueba alfa, dibujo por ambas caras y escritura de profundidad se conservan. No se cambia su malla, su textura ni los otros peinados de Tanda 1.
- **Orca Fighter, J:** los cuatro colores apuntan a un material de recorte opaco: FB_Overwrite, AlphaTest=true, AlphaRef=128, TwoSided=true y ZWrite/ZTest=true. Se conserva el atlas, sus colores y la malla. Los píxeles aceptados ya no se mezclan parcialmente con el fondo. Es una corrección localizada del tratamiento de transparencia; si queda un agujero por falta de geometría, habrá que ajustar esa superficie después de la prueba nativa.
- **Orco Fighter masculino, D/E/F:** se carga una cabeza nueva, MOrc_m001_f del donante, adaptada al esqueleto y transformaciones nativos. Se conservan sus UV, correspondientes a las texturas de cara completa ya instaladas. A/B/C continúan con la cabeza original. Las caras del orco místico y de otros modelos no cambian.

Paquetes nuevos: Animations/NexusOrcFaceV12.ukx, SysTextures/NexusHairGRepairV12.utx y SysTextures/NexusOrcaJRepairV12.utx. Engine actualizado en system-hud y system-camera-online. Formato 121 ligado al nombre de cada archivo, CRC independiente y descifrado idéntico al original. No se modificaron las texturas existentes, NWindow, el servidor, cuentas ni personajes.

Pruebas: geometría orientada, UV y esqueleto de la cabeza compilada; ocho materiales cargados y exportados por UCC nativo con cero errores/advertencias; 2303 casos de regresión de recursos/ABI/selector; 15486 casos de Tanda 2; 5824 casos de conteo y 112 replays del bucle nativo de materiales. La base de reversión tiene 2314 comprobaciones, mantiene las reparaciones independientes y no contiene rutas de Tanda 2. Estas pruebas no equivalen a una comprobación visual dentro del cliente.

Fuentes del diagnóstico: ../2026-10-26-rea-appearance-audit/README.md y rea-live-hooks.txt. El valor 160 del elfo oscuro está verificado contra el material de origen; el material opaco de la orca es una adaptación para eliminar la mezcla semitransparente observada, no una afirmación de que se haya demostrado ausencia de huecos en toda su geometría.

Reversión de estas reparaciones: ejecutar rollback.py con el cliente cerrado; valida hashes y restaura los archivos anteriores a v12, incluidos los manifiestos. No se ha ejecutado esa reversión sobre la instalación exitosa. La reversión global de Tanda 2, en v9/rollback.py, se ha actualizado con bases que conservan el cabello G reparado y las caras D/E/F del orco, junto con sus dos recursos independientes. Las copias históricas no se sobrescriben. Ver installation.json para las rutas de backup.
