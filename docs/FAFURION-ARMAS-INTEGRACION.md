# Fafurion Weapons: integración inicial

Fecha: 12/10/2026. Estado: instaladas en cliente activo y servidor, con siete templates registrados también en el GameServer que está corriendo. No se reinició el servidor. Revisión visual dentro del juego pendiente.

## Armas y estadísticas

Valores base a +0, antes de atributos del personaje, buffs, pasivas, shots y fórmulas de combate. Todas grado S. Los IDs son objetos nuevos, no reemplazos de las armas originales.

| ID | Arma | Tipo | P.Atk | M.Atk | Velocidad base | Equivalente de estadísticas |
|---|---|---|---:|---:|---:|---|
| 54130 | Fafurion Avenger | Maza de una mano | 281 | 132 | 379 | Basalt Battlehammer, 6365 |
| 54131 | Fafurion Cutter | Espada de una mano | 281 | 132 | 379 | Forgotten Blade, 6364 |
| 54132 | Fafurion Fighter | Puños duales | 342 | 132 | 325 | Demon Splinter, 6371 |
| 54133 | Fafurion Singer | Bastón mágico de dos manos | 274 | 193 | 325 | Imperial Staff, 6366 |
| 54134 | Fafurion Shaper | Daga de una mano | 246 | 132 | 433 | Angel Slayer, 6367 |
| 54135 | Fafurion Stormer | Lanza de dos manos | 281 | 132 | 325 | Saint Spear, 6370 |
| 54136 | Fafurion Dual Sword | Espadas duales | 342 | 132 | 325 | Base física de Tallum Blade*Dark Legion's Edge, 6580 |

Singer conserva el nombre del pack IL, aunque su malla se llama Retributer. El texto original anunciaba M.Atk 175; se ajustó a 193 para coincidir con Imperial Staff y se corrigió también el DAT visible. Las duales usan dos instancias del modelo Cutter. Este archivo trae siete entradas IL y seis mallas diferentes; no se declara integrada toda la familia Fafurion de otras crónicas.

P.Atk contribuye a golpes físicos y habilidades que lo usan; M.Atk a ataques mágicos y determinadas curas. Tener M.Atk no convierte automáticamente el arma en mágica. Singer tiene `is_magic_weapon=true`; las otras seis, clasificación física. El tipo SWORD/BLUNT/DAGGER/DUALFIST/POLE/DUAL permite aplicar las condiciones y maestrías normales de cada tipo. P.Atk no es velocidad de ataque y M.Atk no es velocidad de casteo. Algunas curas son fijas o porcentuales; CP no obtiene una bonificación universal por M.Atk.

## Especialidades actuales

- Apariencia, materiales, iconos y partículas originales del pack.
- Stormer conserva exclusivamente la habilidad normal `3599/1`, Polearm Multi-attack, de Saint Spear.
- Las otras seis no tienen habilidades propias. No se añadieron SA, buffs, procs, daño elemental de agua ni sockets.
- Dual Sword no hereda el bonus PvP `3552` ni la habilidad especial de +4 `3570` de su referencia. Es una base para nuestro sistema futuro.
- Se conservan peso, grado, precio de referencia, cristalización, consumo de shots y funciones de enchant de sus bases. Enchant usa reglas S existentes; no se cambiaron tasas, límites ni tablas de SA. No existe todavía una ruta nueva de inserción de SA para estos IDs.
- El material de cliente del pack (47) se corrigió a ADAMANTAITE (8) y se retiró su marca de arma heroica. Esto acompaña las definiciones reales del servidor.

## Cómo probarlas

Abrir el cliente habitual mediante `2-JUGAR.cmd`. Con un personaje GM autorizado, usar un comando por arma:

```text
//create_item 54130 1
//create_item 54131 1
//create_item 54132 1
//create_item 54133 1
//create_item 54134 1
//create_item 54135 1
//create_item 54136 1
```

También se pueden obtener desde el botón **Fafurion** en Mirella / GM Shop del Laboratorio (48.800.000 Adena por arma), o desde **//gmshop → Fafurion** (gratuitas como los otros artículos administrativos). Las siete salen a +0. Ambas listas y los cuatro menús están cargados en el servidor abierto, sin reiniciarlo.

No se entregaron automáticamente a personajes ni se añadieron a drops, crafts o recompensas. Los comandos anteriores sí crearán objetos persistentes en el inventario del GM que los ejecute.

Revisar: icono, tooltip, arma en ambas manos cuando corresponde, ataque, casteo con Singer, brillo y partículas con distintos enchants. La comprobación de lectura/exportación nativa no equivale a una inspección visual real en UE2.

## Instalación y comprobaciones

Cliente activo: `E:\l2\system-hud`. Su `l2.ini` incluye `Paths=../system-hud/*.u`; los tres paquetes nuevos pueden resolverse desde esa carpeta.

- `weapongrp.dat`: conserva los 1313 registros anteriores byte por byte y añade siete armas más siete alias visuales compatibles con multisell.
- `itemname-e.dat`: conserva los 9208 registros anteriores byte por byte y añade los nombres de las siete armas y sus siete alias visuales. Descripciones corregidas en V2 con terminador NUL.
- Nuevos paquetes: `LineageWeapons_fafurion.u`, `LineageEffect_fafurion.u`, `LineageEffects_fafurion.u`.
- XML: `server/game/data/stats/items/54100-54199.xml`, copia en source/dist y overlay de cloud-repo local.
- Codificación 413 comprobada por descifrado posterior y comparación exacta del contenido.
- Todas las referencias nuevas a modelos/materiales/iconos/clases de efectos existen en los paquetes instalados. UModel exportó las seis mallas y sus materiales sin errores.
- El parser nativo del GameServer aceptó los siete objetos. Sus funciones estadísticas coinciden con sus bases S, el flag mágico es correcto y las habilidades coinciden con lo descrito arriba.
- Se añadieron únicamente siete templates a la instancia actual mediante una herramienta temporal de laboratorio. Se conservaron las identidades de todos los templates existentes y se agregó el XML a la lista de recarga actual. En un arranque normal el archivo se descubre desde disco; no hace falta volver a ejecutar el agente.
- No hubo cambios de métodos del core, personajes, inventarios o base de datos. No se modificaron archivos HUD/Amber ajenos a estas dos adiciones de catálogos.

Respaldo: `backups/fafurion-weapons-20261012-202625`, con DAT originales y `files.json` que registra archivos nuevos, hashes y destinos. Detalle: `research/fafurion-weapons/installation.json`.

Herramientas y resultados: `research/fafurion-weapons/build_integration.py`, `install.py`, `verify_installation.py`, `manifest.json`, `verification.json`, `runtime-verification.txt`. Build/install son de primera instalación y rechazan IDs o archivos ya presentes; **no reejecutarlos como actualizadores**. La verificación es de solo lectura respecto al cliente y servidor.

El original recibido se conserva en `descarga de assets/Fafurion_Weapons_H5_IL.rar`; SHA256 `176bae09025d96eeda562e6d32f96d342647500ad7f24c22952b9ad53f511f04`. CRC del archivo comprimido correcto. Esto no es una certificación antimalware ni de derechos de redistribución. Paquetes y catálogos binarios permanecen locales; no se publicaron.

Para mover a otra PC, conservar el servidor y el cliente activo completos, con este XML y los tres paquetes. No sustituir DAT por respaldos anteriores ni por versiones del pack que omitan los otros customs.

Para deshacer, coordinar primero el apagado del cliente/servidor y revisar si ya se crearon objetos 54130–54136 en inventarios. No quitar templates que aún tengan instancias persistidas. Restaurar los DAT únicamente si sus hashes siguen siendo los de esta instalación, para no perder futuras adiciones. El respaldo no desregistra por sí solo los templates de un proceso que siga corriendo.

Propuesta de sockets, aún sin implementar: [FAFURION-SOCKETS-PROPUESTA.md](FAFURION-SOCKETS-PROPUESTA.md).

## GM Shop añadido — 12/10/2026

Multisell NPC `50035413`, limitado a Mirella 50010; buylist administrativa `54130`, sin NPC autorizado y con precio 0, usando la ruta administrativa existente. Se añaden accesos Fafurion a las portadas y secciones Weapons de ambas tiendas. No se cambian los catálogos anteriores de venta.

XML de compras y HTML sincronizados en runtime, source y cloud local. `research/fafurion-weapons/shop-verification.txt` comprueba con el parser nativo los siete productos, precios, restricción a Mirella y cuatro accesos en la caché HTML activa. No se simuló una compra sobre un personaje del usuario. Respaldo `backups/fafurion-shop-20261012-204201`; manifiesto `shop-installation.json`. No reejecutar `add_shop.py` ni el agente de carga sobre una lista ya instalada.

## Corrección de tienda y tooltip V2 — 12/10/2026

Kevin proporcionó capturas reales: Avenger comprado/equipado con P.Atk281/M.Atk132 e imagen visible en inventario, pero multisell mostraba iconos vacíos, `(null)` y estadísticas0. El tooltip concatenaba texto de una SA ajena. La primera verificación de parser/datos no cubrió estos problemas de representación en cliente.

Se corrigieron dos causas:

- MultiSellList transmite el display ID como short de16bits. Los IDs54130–54136 salen negativos al interpretarlos con signo (−11406 a−11400); el inventario usa un campo de32bits. Se reservaron alias de cliente24130–24136 y se agregó `displayId` a los templates originales. Los IDs persistentes siguen54130–54136: no se cambian ni migran los objetos comprados. DAT conserva también las entradas de IDs altos para la buylist administrativa que transmite el ID original de32bits. Sin cambios al formato de paquetes del core.
- La descripción añadida inicialmente no terminaba en NUL. Se reemplazó por `Arma de grado S.` con terminador explícito en las catorce entradas de nombres. No hay ninguna SA/poder activado por ese texto espurio.

Instalado con L2 cerrado. GameServer conserva los mismos objetos ItemTemplate, sus stats y listas; solo se actualizaron sus siete campos displayId. Precios de Mirella48.800.000 y GM0 conservados. No hay updates de DB, recreación ni pérdida de instancias.

Verificación V2: comparación de bytes de todos los registros ajenos a Fafurion; alias de armas idénticos salvo ID; descripciones terminadas; codec413 roundtrip; XML/hash; paquete MultiSellList real serializado antes/después, decodificación positiva de los siete IDs visuales, precios y IDs de productos originales conservados. Resultado `research/fafurion-weapons/client-fix-v2/runtime-verification.txt` y `verification.json` PASS. Espera confirmación visual del usuario tras reabrir el cliente; no declarar comprobado el shop en pantalla solo por serialización.

Respaldo `backups/fafurion-client-fix-v2-20261012-205047`; contiene DAT/XML anteriores, manifiestos iniciales y hashes. Preparador/instalador `fix_client_v2.py`, agente de una sola ejecución `FafurionDisplayFixV2.java`; no reejecutar sobre el estado instalado. `verify_installation.py` sí acepta el estado V2. Continuidad debe conservar tanto el cliente con alias como el XML con displayId; una mitad aislada produce referencias sin imagen.
