# Integracion de equipamiento - 2026-10-13

Estado: instalacion local verificada. **543 piezas y variantes integradas; 49 entradas pendientes** de las 592 definiciones distintas encontradas en 37 packs. No son 543 sets completos: se cuentan armas, piezas, joyas, escudos, accesorios y variantes visuales.

Acceso: **GM Shop del Laboratorio (Mirella, NPC 50010) -> Equipo custom - 3 tandas -> Tanda 1, 2 o 3 -> pack**. Las listas con mas de 40 productos usan la paginacion normal del multisell. El servidor y el cliente quedaron cerrados; los datos se cargan al iniciarlos. No se agregaron NPCs, bots ni personajes, ni se modificaron inventarios o la base de datos.

## Instalacion y respaldo

- Cliente: `E:\l2`, sistema activo `system-hud`. Se ampliaron weapongrp.dat, armorgrp.dat e itemname-e.dat.
- Nuevos IDs de items: **25000-25542**, por debajo de 32768 para mostrarse correctamente en el multisell de Interlude.
- Modelos y texturas propios con prefijos EB01..EB37: conviven con los originales y con el Fafurion previamente integrado.
- Servidor: XMLs equipment-*.xml, multisells 50037001..50037037 (36 listas activas), menus 50010-80..83.
- Los datos del servidor se sincronizaron al source local y al overlay de cloud-repo. No se publicaron ni subieron los binarios descargados.
- Respaldo: `E:\l2-local\backups\equipment-batches-20261013-160432`. El manifiesto files.json registra archivos anteriores y nuevos.
- Reversion: `python research\equipment-batches\rollback.py`, con cliente y servidor cerrados. Rechaza revertir si un archivo fue modificado despues.

## Estadisticas y funcionamiento

- **275 Weapon y 268 Armor**, incluyendo 19 escudos en weapongrp del cliente y joyeria/accesorios dentro de Armor del servidor.
- Armas: base S nativa por tipo. Espada/maza de una mano fisica 281/132; daga 246/132; arco 581/132; dos manos/duales/punos 342/132; lanza 281/132. Magicas: staff Imperial 274/193 o Arcana Mace de una mano 225/175, segun la configuracion visual. Los XML y catalogos contienen las cifras exactas.
- Se conserva el indicador de arma magica en los modelos adaptados como magicos. El color o efecto visual de fuego/hielo no agrega dano elemental.
- Armaduras y joyas: referencias S de Interlude. Las piezas separadas de cuero/tela reparten los valores de su base de cuerpo completo; una armadura pesada de cuerpo completo suma pecho y piernas.
- Alas y accesorios de pelo: cosmeticos, base sin grado. Los cascos reales usan el slot head; no todos los adornos llamados helmet ocupan el mismo slot.
- No se importaron SA, bonos de set del proveedor, poderes PvP, skills especiales, sockets, gemas ni procs. Solo se conserva el comportamiento nativo de golpe multiple en lanzas. Las variantes visuales pueden compartir estadisticas.
- Las dagas dobles sin tipo propio en Interlude se adaptaron al tipo DUALFIST. Queda decidir su comportamiento definitivo antes de balancear o publicar.
- Precio de laboratorio: 48.800.000 Adena por arma; 1.000.000 por armadura, escudo, joya o accesorio.
- Se corrigieron referencias de grupo de Unreal, nombres de paquetes y dependencias entre packs cuando el objeto correspondiente estaba disponible.
- Algunos iconos ausentes usan el icono de su base nativa. Algunos modelos/texturas de objeto tirado al suelo ausentes usan la representacion nativa de la base. Esto no sustituye los modelos equipados faltantes: esas entradas quedaron pendientes.

## Comprobaciones

PASS: 2.272 archivos instalados verificados por SHA-256; los registros preexistentes de los tres catalogos conservan sus bytes, incluido Fafurion y sus aliases. PASS: 543 templates aceptados por DocumentItem y registrados por ItemData nativos en un proceso de validacion aislado. PASS: 36 listas multisell, sus 543 productos y acceso del NPC 50010. Sin IDs duplicados de estas incorporaciones. Los catalogos recompilados se descifraron de nuevo y coinciden byte por byte con los esperados.

La validacion no es una prueba visual dentro del juego. Queda revisar apariencia, escala, animaciones, efectos y compatibilidad en cada raza/sexo. El servidor no se inicio y no se abrieron conexiones a la base de datos para verificar. Los reportes historicos de Fafurion tienen hashes de catalogos anteriores: ahora los catalogos agregados se verifican con research/equipment-batches/verify.py.

## Catalogo por pack

| Tanda | Pack | Integradas | Pendientes |
|---|---|---:|---:|
| 1 | Icarus Weapons Retail | 37 | 0 |
| 1 | Ice Invoke Weapons + Effect | 21 | 0 |
| 1 | Fafurion Weapons With Effects Level 3 | 7 | 0 |
| 1 | Bow Zariche | 1 | 0 |
| 1 | Draconic Bow Gold | 1 | 0 |
| 1 | Leviathan | 15 | 0 |
| 1 | Gold Dragon Uniform | 1 | 0 |
| 1 | Elegia | 15 | 0 |
| 1 | Vorpal | 3 | 12 |
| 1 | Water Core | 15 | 0 |
| 1 | Sealed Vesper Jewels | 6 | 0 |
| 1 | Freya Shield | 1 | 0 |
| 1 | Angry Wings | 1 | 0 |
| 1 | Astral Helmet | 1 | 0 |
| 2 | Black Antharas Weapons | 10 | 0 |
| 2 | Dragon Weapon Fire & Water | 18 | 0 |
| 2 | Dynasty Weapons | 51 | 0 |
| 2 | Blaze Pack: armor, weapon, helmet, wings | 29 | 0 |
| 2 | Vesper Red: armor, weapon, helmet, wings | 26 | 1 |
| 2 | Pandorium: Blue, Green, Red | 43 | 0 |
| 2 | Dynasty Armor With Shoulders V1.5 | 3 | 22 |
| 2 | Epic Dark Knight Armor | 13 | 0 |
| 2 | Anakim & Lilith Wings | 0 | 2 |
| 2 | 19 Helmet Pack | 16 | 1 |
| 2 | Animated Shield | 4 | 0 |
| 3 | Lindvior Weapons | 5 | 0 |
| 3 | Valakas + Red and Blue Effect | 20 | 3 |
| 3 | R110 Krishna | 37 | 0 |
| 3 | Vesper Weapons Retail | 37 | 1 |
| 3 | Moirai Armor | 16 | 0 |
| 3 | Ixion Titanium Armor & Weapons | 25 | 0 |
| 3 | Iron Hell Armor + Jewels | 20 | 0 |
| 3 | Saint Seiya Armor | 23 | 3 |
| 3 | Halloween Armor & Weapons | 8 | 4 |
| 3 | Moirai, Vorpal y Elegia Jewels | 9 | 0 |
| 3 | Moirai, Vorpal y Elegia Shields | 3 | 0 |
| 3 | School Uniform | 2 | 0 |

## Pendientes concretos

Las 49 entradas no se instalaron ni se pusieron a la venta. Hay versiones protegidas de Vorpal (Lineage2Ver811/821), el paquete Dynasty con shoulders tiene una cabecera modificada, y faltan archivos/referencias en algunos accesorios, Saint Seiya, Halloween, Valakas y una variante de Vesper. Hace falta conseguir versiones compatibles/completas o reparar su recurso exacto. No se sustituyo entry.dll ni se ejecutaron binarios incluidos en los packs.

| Pack | ID del proveedor | Nombre | Recurso faltante (muestra) |
|---|---:|---|---|
| b1-09-vorpal | 14501 | Vorpal Breastplate | `EB09_FMagic-v1.FMagic_m015_t3110_u` |
| b1-09-vorpal | 14502 | Vorpal Gaiters | `EB09_FDarkelf-v1.FDarkElf_m012_t2110_l` |
| b1-09-vorpal | 14503 | Vorpal Gauntlets | `EB09_FDarkelf-v1.FDarkElf_m012_t2110_g` |
| b1-09-vorpal | 14504 | Vorpal Boots | `EB09_FDarkelf-v1.FDarkElf_m012_t2110_b` |
| b1-09-vorpal | 14506 | Vorpal Leather Armor | `EB09_FMagic-v1.FMagic_m015_t3110_u` |
| b1-09-vorpal | 14507 | Vorpal Leather Leggings | `EB09_FDarkelf-v1.FDarkElf_m013_t1110_l` |
| b1-09-vorpal | 14508 | Vorpal Leather Gloves | `EB09_FDarkelf-v1.FDarkElf_m013_t1110_g` |
| b1-09-vorpal | 14509 | Vorpal Leather Shoes | `EB09_Dwarf-v.Cleo_Chaos_Master_FDwarf_m013_b` |
| b1-09-vorpal | 14511 | Vorpal Tunic | `EB09_FDarkelf-v1.FDarkElf_m008_t3110_u` |
| b1-09-vorpal | 14512 | Vorpal Stockings | `EB09_FDarkelf-v1.FDarkElf_m009_t3110_l` |
| b1-09-vorpal | 14513 | Vorpal Mitters | `EB09_FDarkelf-v1.FDarkElf_m008_t3110_g` |
| b1-09-vorpal | 14514 | Vorpal Slippers | `EB09_FDarkelf-v1.FDarkElf_m004_t3110_b` |
| b2-05-vesper-red-armor-weapon-helmet-wings | 22996 | Heart Wings | `ArgonitePandurusWingsTex.ArgonitePandurus01` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9733 | Dynasty Breast Plate | `EB21_SHEV_Dynasty_00.04FDarkElf_m006_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9734 | Dynasty Breast Plate | `EB21_SHEV_Dynasty_00.05FDarkElf_m006_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9735 | Dynasty Breast Plate | `EB21_SHEV_Dynasty_00.02FDarkElf_m006_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9736 | Dynasty Breast Plate | `EB21_SHEV_Dynasty_00.03FDarkElf_m006_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9737 | Dynasty Breast Plate | `EB21_SHEV_Dynasty_00.FDarkElf_m006_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9738 | Dynasty Gauntlet | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_g` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9739 | Dynasty Gaiters | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_l` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9740 | Dynasty Boots | `EB21_SHEV_Dynasty_00.FDarkElf_m010_b` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9741 | Dynasty Leather Armor | `EB21_SHEV_Dynasty_00.01FDarkElf_m003_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9742 | Dynasty Leather Armor | `EB21_SHEV_Dynasty_00.FDarkElf_m003_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9743 | Dynasty Leather Armor | `EB21_SHEV_Dynasty_00.02FDarkElf_m003_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9744 | Dynasty Leather Leggings | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_l` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9745 | Dynasty Leather Gloves | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_g` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9746 | Dynasty Leather Boots | `EB21_SHEV_Dynasty_00.FDarkElf_m004_b` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9747 | Dynasty Tunic | `EB21_SHEV_Dynasty_00.FDarkElf_m008_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9748 | Dynasty Tunic | `EB21_SHEV_Dynasty_00.FDarkElf_m208_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9749 | Dynasty Tunic | `EB21_SHEV_Dynasty_00.FDarkElf_m108_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9750 | Dynasty Tunic | `EB21_SHEV_Dynasty_00.FDarkElf_m408_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9751 | Dynasty Tunic | `EB21_SHEV_Dynasty_00.FDarkElf_m308_u` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9752 | Dynasty Stockings | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_l` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9753 | Dynasty Gloves | `EB21_SHEV_Dynasty_00.FDwarf.FDwarf_m008_t201_g` |
| b2-07-dynasty-armor-with-shoulders-v1-5 | 9754 | Dynasty Shoes | `EB21_SHEV_Dynasty_00.FDarkElf_m006_b` |
| b2-09-anakim-lilith-wings | 9897 | Anakin Wing | `sixplan.Mfighter_raid_master_m001_a` |
| b2-09-anakim-lilith-wings | 9898 | Lilith Wing   | `sixplan.Mfighter_raid_master_m001_a` |
| b2-10-19-helmet-pack | 10009 | Helmet | `FDarkelf_real_pvp_by_a6y_guard_m003_a.FDarkelf_real_pvp_by_a6y_guard_m003_a` |
| b3-02-valakas-red-and-blue-effect | 9517 | Valakas + Red and Blue Effect 9517 | `L2CreedWeapons_tex.LightFusion_DerThrodBow_t00_fb` |
| b3-02-valakas-red-and-blue-effect | 9522 | Valakas + Red and Blue Effect 9522 | `Orange_Weapons.caster` |
| b3-02-valakas-red-and-blue-effect | 9521 | Valakas + Red and Blue Effect 9521 | `L2CreedWeapons_tex.LightFusion_DerThrodHammer_t00_fb` |
| b3-04-vesper-weapons-retail | 9447 | Vesper Shield | `EB29_LineageWeaponsTex-v.vesper_verteidiger_t01_wp` |
| b3-08-saint-seiya-armor | 30000 | Saint Seiya Armor 30000 | `EB33_SaintSeiyaHelmet.fshaman_Aquarius_Helmet_m001` |
| b3-08-saint-seiya-armor | 30012 | Saint Seiya Armor 30012 | `EB33_zodiacarmor.FDarkElf_m004_t1004_g` |
| b3-08-saint-seiya-armor | 30013 | Saint Seiya Armor 30013 | `EB33_zodiacarmor.FDarkElf_m010_t1004_b` |
| b3-09-halloween-armor-weapons | 20092 | Halloween Armor & Weapons 20092 | `EB34_LineageCustom3_ByLucifer.FDarkElf_asn_t00` |
| b3-09-halloween-armor-weapons | 50044 | Halloween Armor & Weapons 50044 | `lineage2Effecs.envariation17_009t` |
| b3-09-halloween-armor-weapons | 50049 | Halloween Armor & Weapons 50049 | `lineage2Effecs.envariation17_009t` |
| b3-09-halloween-armor-weapons | 50050 | Halloween Armor & Weapons 50050 | `lineage2Effecs.weapon_lind_thrower` |

Detalle completo: research/equipment-batches/installation.json y stage/manifest.json. IDs disponibles para el proximo turno: research/equipment-batches/CATALOGO.csv. No crear equipamiento de exhibicion usando los IDs originales de los proveedores: usar los nuevos IDs del catalogo.

## Correccion del empaquetado del cliente - 2026-10-13

El cliente mostro `Files are corrupted` para `../SysTextures/EB05_Renato.utx`. Las texturas/modelos renombrados se habian instalado como paquetes Unreal sin cifrar; la inspeccion de tablas y la validacion del servidor no detectaban esa incompatibilidad con el cliente.

Se reemplazaron 505 paquetes propios EB*.utx/ukx/usx: UTX con Lineage2Ver121 y clave derivada del nombre FINAL; UKX/USX con Lineage2Ver111. Los archivos .u conservan su formato anterior. Todas las cargas utiles descifradas coinciden byte por byte con las preparadas, y se verificaron cabeceras, CRC32 y hashes instalados. UModel abre la textura EB05_Renato instalada y reconoce sus dos texturas y shader. El instalador queda corregido para futuras instalaciones y verify.py exige esas cabeceras y CRC.

Respaldo: `E:\l2-local\backups\equipment-asset-envelope-20261013-165057`. Manifiesto: research/equipment-batches/asset-envelope-fix/installation.json. Catalogos, estadisticas, inventarios y maniquies conservados. El servidor sigue activo; falta repetir el arranque y la inspeccion visual en el cliente. Esta comprobacion no afirma que se haya abierto el cliente sin errores.
