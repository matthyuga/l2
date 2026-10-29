# Dust2: caída al aparecer y primera corrección de cliente

Kevin informó que alcanza a ver el suelo pero cae al vacío inmediatamente al usar .dust2. La prueba anterior del servidor no detectaba colisión/física de cliente. No considerar aquella integración como aterrizaje validado.

Proyecto E:/l2-local/research/dust2-integration/floor-fix. Geodata cargada; se corrigió paquete de cliente al formato nativo Interlude123/license28, añadiendo realmente los datos/offsets L2 requeridos (no solo cabecera). 37 meshes con geometría idéntica, 9932 caras/10191 nodos de colisión, metadatos y mip offsets rebasados. Actores con colisión poligonal/world explícita. Instalados solo HGDust2Arena.usx y24_19.unr, cliente cerrado. Respaldo E:/l2-local/backups/dust2-collision-fix-20261014-133504. Rollback principal mantiene hashes actualizados. GameServer21308 sigue activo.

Lectura nativa completa con L2unreal,68 materiales/imágenes con UModel y40 consultas de soporte vertical PASS; **física real del cliente aún NO confirmada**. Se preguntó a Kevin que vuelva a abrir L2 y pruebe .dust2. Falta su resultado; no dar por resuelto ni asegurar causa única todavía. README de floor-fix detalla comprobaciones y límites.
