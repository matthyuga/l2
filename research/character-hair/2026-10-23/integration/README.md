# Cabellos instalados — 23/10/2026

Instalados 13 accesorios cosméticos de cabello en el cliente Interlude y en el servidor local. Están cargados también en el GameServer actual, sin reinicio.

## Cómo obtenerlos

- Mirella, NPC 50010: botón **Cabellos**, en la portada y en Hair. Cada accesorio cuesta **1 Adena** en el laboratorio.
- `//gmshop`: botón **Cabellos**, en la portada y en Hair. Entrega administrativa gratuita.
- IDs: **28000–28012**. Son accesorios equipables en el espacio de cabello; no agregan peinados al creador de personajes.

| ID | Accesorio |
|---|---|
| 28000 | Axe Dreads |
| 28001 | Baium Black Hair |
| 28002 | Baium Hair |
| 28003 | Beowulf Baium Hair |
| 28004 | Bio Plasma Dredy |
| 28005 | Blood Dreds |
| 28006 | Cabelo Baium Dreds |
| 28007 | Fire Dreds (19) |
| 28008 | Geffers Hair |
| 28009 | Gladiator Dreds Green |
| 28010 | Gladiator Dreds Orange |
| 28011 | Gladiator Dreds Magenta |
| 28012 | Gladiator Dreds Yellow |

Gladiator contiene cuatro colores; por eso los diez paquetes originales producen trece objetos.

## Cambios y comprobaciones

- Cliente activo: `E:/l2/system-hud/armorgrp.dat` y `itemname-e.dat`; se añadieron 13 registros conservando exactamente los bytes de todos los registros anteriores.
- Recursos: 20 paquetes UKX/UTX con nombres propios H0001…H0020 en Animations y SysTextures. No se sobrescribieron los baium.ukx de terceros ni recursos nativos.
- Corregida una definición de otra crónica al esquema de Interlude y varias referencias a grupos/mallas, incluida la enana de Baium Hair.
- Referencias de las 14 combinaciones de modelo/sexo de Interlude comprobadas contra objetos reales; 481 referencias del catálogo verificadas en total.
- Los 20 paquetes pudieron cargarse y exportarse mediante UModel. Sobres de cifrado y CRC comprobados, además de decodificación exacta del staging.
- Parser nativo y GameServer: 13 Armor en bodypart HAIR, cero funciones de estadísticas, cero skills, sin encantamiento ni cristalización. No se copiaron los bonos de combate de los proveedores.
- Tiendas nativas verificadas en vivo: buylist 28000 y multisell 50042800, con los 13 productos y precios indicados. Cuatro menús recargados.
- Datos persistentes en runtime, dist de source y overlay de cloud-repo. Se conservaron las plantillas anteriores del servidor y no se modificaron personajes ni inventarios reales.
- Verificación final: 43 archivos instalados con hashes correctos, sin IDs nuevos duplicados. No se reinició el servidor ni se abrió el juego.

**Pendiente:** revisar dentro de L2 el aspecto de los accesorios, su ajuste por raza/sexo y posibles cruces con el cabello base o cascos. La lectura/exportación de recursos no demuestra su apariencia final en el motor del juego. El pack de peinados base de Rolo sigue sin estar disponible (enlace 404); no forma parte de esta instalación.

## Respaldo y continuidad

Respaldo: `E:\l2-local\backups\hair-accessories-20261023-230455`.

Auditoría y scripts: `research/character-hair/2026-10-23/integration/`:

- `manifest.json`: modelos, materiales, reparación de referencias y hashes.
- `installation.json`: destinos, estado anterior y copias de respaldo.
- `verification.json`, `native-verification.txt`, `runtime-verification.txt`, `umodel-verification.json`: resultados.
- `verify.py`: comprobación de la instalación sin mutaciones.
- `rollback.py`: restauración con guardia de hashes; requiere cliente y servidor cerrados. Rechaza sobrescribir modificaciones posteriores.
- `build.py`, `install.py`, `HairLoad.java`: construcción, instalación y carga aditiva. No volver a ejecutarlos sobre la instalación actual; sus guardias impiden duplicarla.

No hubo commit ni push. El precio de 1 Adena corresponde al laboratorio; todavía no es una decisión para la economía del servidor público.
