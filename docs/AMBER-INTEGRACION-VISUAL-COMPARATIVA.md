# Amber: comparación de materiales e integración visual

12/10/2026. Amber NPC y summon añadidas a la galería. Abrir `GALERIA-MODELOS-L2.cmd` y seleccionar «Comparar Amber con los modelos de L2», o visitar http://127.0.0.1:32280/comparar.html mientras la galería está activa.

Se leyó el npcgrp actual de system-hud, sin modificarlo. Referencias observadas:

| Variante | ID servidor | Display cliente | Malla instalada |
|---|---:|---:|---|
| Amber NPC | 902500 | 59001 | L2AmberNPCv5.AmberNPC |
| Amber summon | 902501 | 59002 | L2AmberArcherV2.AmberNPC |

Ambas tienen 52.153 triángulos, 76 huesos y dos atlas de 2048×2048. Los shaders de cuerpo y ropa tienen Diffuse y SelfIllumination apuntando a la misma textura, SelfIlluminationMask=None, Specular=None y SpecularityMask=None; alpha masked, AlphaRef128, TwoSided y ZWrite activos. Auditoría del paquete instalado en `research/model-catalog/amber-comparison/audit.json`, con dumps completos de materiales y hashes.

Esto señala una causa de la separación visual: el aporte propio de color puede dominar la respuesta a la luz del entorno. La v4 lo añadió a ambos atlas para resolver la ropa excesivamente oscura de v3. La ropa, el pelo, la piel y los accesorios comparten dos shaders sin respuestas especulares diferenciadas. Las texturas conservan el tratamiento toon del personaje original. Estos hechos no demuestran por sí solos todo el comportamiento del renderer de L2; la comparación es una herramienta para elegir una dirección y después validarla ingame.

La referencia inicial es Katerina, `LineageNPCs.a_traderB_FHuman_m00`: 1.974 triángulos, 78 huesos y cuatro texturas (dos512×512 y dos256×256). El visor permite elegir otros NPC nativos. Esa diferencia de resolución y geometría no explica automáticamente el problema de iluminación; también importa cómo se usan los materiales y la información pintada en las texturas.

El comparador muestra tres vistas giratorias y dos ambientes: estudio y oscuro. A la izquierda aproxima el material actual mediante unlit; en el centro permite una prueba difusa sin autoiluminación o una mezcla aproximada con20% de aporte propio; a la derecha aparece la referencia nativa. Se mantienen geometría y texturas de Amber. Son glTF de estudio, sin equivalencia exacta con UE2, sin sus partículas/reflejos/sombras del cliente. No se instaló ninguna prueba en L2 ni se modificaron sus paquetes o estadísticas.

Orden propuesto para una revisión futura: ajustar la autoiluminación, mantener un aporte suave si hace falta evitar que la cara/ropa se apaguen, separar respuestas de piel/tela/cuero/pelo/ojos/metal mediante materiales o máscaras, y retocar tonos/gradientes/detalles del atlas según la referencia. Preparar LOD y compresión de recursos en un trabajo posterior si se amplía el uso a muchos personajes.

Validación: galería643 registros/642 miniaturas, enlaces de buffers/texturas completos. Chrome headless aislado esperó la carga real de las tres vistas; capturas de estudio, oscuro y prueba difusa oscura PASS, sin excepciones JS. La prueba oscura deja evidente la diferencia de respuesta en esta simulación. Los hashes de los dos UKX instalados permanecen idénticos a los registrados al iniciar la auditoría. Capturas verificadas: `amber-comparison/day-verified.png`, `night-verified.png`, `diffuse-night-verified.png`; los otros PNG de intentos anteriores son diagnósticos de capturas prematuras.

Código/metadata sincronizados con cloud-repo local; recursos generados y documentación están en el disco portátil, con copia de memoria en Nexus. Sin commit/push ni reinicio de GameServer.


Actualización 12/10/2026: se instaló la integración de materiales V1; ver AMBER-INTEGRACION-VISUAL-V1.md. Este documento describe la auditoría anterior. El comparador ahora muestra antes/V1/nativo.
