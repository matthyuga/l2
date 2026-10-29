# Huecos entre capas de cabello: ajuste de materiales

El usuario muestra partes del escenario a través de peinados extra: humano Fighter F, humana Fighter H, humana Mystic I, elfo masculino I en modo Clásico y otros en negro. Que uno de los ejemplos sea Clásico indica que no basta con atribuirlo al tinte HSL. Las capturas por sí solas no demuestran que cada hueco tenga la misma causa.

## Hallazgo

Los 112 materiales de tanda 1 usan FB_AlphaBlend (2), AlphaTest=True, ZWrite=True, TwoSided=True y AlphaRef=5. Los 28 materiales de tanda 2 en NexusHairT2M11 repiten esa configuración. Los cuatro del arreglo Dark Elf G conservan FB_AlphaBlend y usan AlphaRef160. La orca J ya tiene FB_Overwrite y no se modifica aquí.

Cuando un plano semitransparente escribe profundidad, puede impedir dibujar las capas que están detrás, aunque su propio color siga mezclándose con el escenario. Es una causa plausible de los huecos en capas superpuestas; la confirmación de los casos visuales requiere probarlos en el cliente.

REA, evidencia ev_1e9712328319542f9aeec56117c642c88103fcb74fbfb093d3cc21fe86f277e5 (`rea-finalblend.json`), confirma campos independientes en el material nativo: referencia al material en +0x578, modo de mezcla en +0x57c, bits de estado en +0x580 y referencia alfa en +0x584. La ruta HSL v2 clona ese material antes de sustituir su textura, por lo que conserva el modo de mezcla original. El ajuste del paquete también se hereda en modo Libre tras reiniciar el cliente.

## Cambio preparado

Solo FB_AlphaBlend (2) → FB_Overwrite (0) en 144 materiales. Mantiene AlphaTest y su umbral original, TwoSided, ZWrite, ZTest, referencias e índices. Los píxeles descartados siguen descartados; los visibles se dibujan opacos. No se rellenan texturas ni se añade geometría. Un hueco real de malla podría permanecer y requerir un arreglo específico.

No cambia colores, mallas, rostros, conteos, letras, DLL HSL v2 ni servidor. No afecta materiales del juego original. Archivos compartidos por ambos perfiles: NexusHairMaterialsV2.utx, NexusHairT2M11.utx y NexusHairGRepairV12.utx.

## Validación

- Un byte de propiedad cambiado por cada exportación; todos los demás bytes de cada material coinciden.
- Referencias y tabla de importaciones conservadas.
- Codificación nativa121, CRC y decodificación exacta verificadas.
- UCC cargó y exportó los 144 materiales: cero errores y cero advertencias. 395 comprobaciones de propiedades y modelo de cobertura alfa/profundidad.
- Pendiente revisión visual en los ángulos de las capturas, en Clásico y Libre. Los resultados anteriores no prueban por sí solos que todos los huecos desaparezcan.

Instalación: `install.py` exige cliente cerrado, respalda archivos y actualiza hashes de los manifiestos afectados. `rollback.py` restaura únicamente este arreglo, conservando HSL v2.
