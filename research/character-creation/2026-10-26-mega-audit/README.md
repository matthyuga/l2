# Revisi?n del cliente MEGA ? 26/10/2026

Estado: descarga completa; prueba de integridad de todas las entradas RAR PASS. Auditor?a est?tica, sin instalar ni ejecutar el cliente descargado.

- Contiene 1615 entradas. Se extrajeron paquetes de animaci?n y texturas de razas a una carpeta de investigaci?n.
- Las tablas chargrp.dat y hair.int recuperadas previamente son iguales a las nativas. No se encontr? una ampliaci?n del n?mero de opciones del creador.
- Los siete paquetes Fighter, Magic, Elf, DarkElf, Orc, Shaman y Dwarf tienen cambios de serializaci?n en los recursos de cabello/cabeza. Esos cambios de bytes por s? solos no prueban cambios geom?tricos.
- Confirmaci?n geom?trica: el objeto de cabello MElf_m003_m00_ah conserva su nombre original, pero el exportador UModel obtiene 399 puntos y 586 tri?ngulos del donante, frente a 60 puntos y 86 tri?ngulos del cliente nativo. Por tanto, hay al menos un peinado realmente distinto que reemplaza una opci?n original, sin ser un objeto de inventario.
- Se compararon las exportaciones con nombres terminados en _ah, _bh y _f de doce paquetes de texturas: no hay cambios respecto a los nativos. En particular, no hay nuevas exportaciones de caras en esos paquetes.
- La cabeza de ejemplo FElf_m000_f conserva 197 puntos y 360 tri?ngulos en ambos clientes. La igualdad por secci?n est? registrada en face-sample-comparison.json.
- No se identific? un pack de rostros adicionales. No afirmar que todos los peinados sean distintos: el n?mero exacto de dise?os ?nicos requiere exportarlos y compararlos uno a uno.

Conclusi?n: recurso donante ?til para rescatar peinados como opciones adicionales mediante adaptaci?n. Copiar estos paquetes completos reemplazar?a modelos existentes y otros recursos de las razas. No instalado; la integraci?n actual sigue intacta.

Evidencias: inventory.json, appearance-comparison.json, sample-geometry.json, face-sample-comparison.json y registros de exportaci?n. Los avisos Unknown class Texture/MeshAnimation de las exportaciones corresponden a haber desactivado expresamente texturas/animaciones en UModel; las cuatro exportaciones de mallas terminaron con c?digo 0.


Galer?a 26/10/2026: generadas 84 opciones (5 masculinas y 7 femeninas para cada uno de los siete modelos base), 168 vistas y siete l?minas por raza/arquetipo. Archivos galeria/index.html y Galeria-peinados-MEGA.zip. Renders est?ticos con UModel y Blender, usando texturas embebidas del donante y las texturas nativas cuando el material se resuelve en el motor; no prueban integraci?n. No todos son dise?os nuevos. En la opci?n A de Orc/Shaman, ambos sexos, se omiti? en la vista la pieza AH auxiliar flotante y se conserv? la malla BH. Revisadas visualmente las siete l?minas. No se modific? el cliente ni servidor.


Comparaci?n visual 26/10/2026: creada comparison/index.html con selector de modelo/sexo, columnas Original instalado + Tanda 1 instalada + Tanda 2 sin instalar. 84 originales y 28 extras actuales, frente a 84 opciones MEGA, 392 vistas y 14 l?minas. Fuentes actuales exportadas de E:/l2 y registradas con hashes en comparison/live-sources.json. Enlace a?adido al index.html de galer?a previo. Sin cambios al cliente/servidor. QA visual de las 14 l?minas mediante hoja de contacto.
