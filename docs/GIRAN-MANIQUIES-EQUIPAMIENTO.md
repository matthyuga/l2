# Maniquies de equipamiento en Giran - 2026-10-13

**157 NPCs pasivos instalados y activos**, IDs 62000-62156. Acceso GM: `.galeria` (fuera de combate e instancias). El comando lleva al corredor norte de la plaza. Servidor local iniciado y verificado en 127.0.0.1:7777.

Cuatro anillos de radio 460, 635, 810 y 985 alrededor de 81920,148608,-3400. Miran hacia el centro y dejan corredores cardinales. Separacion minima entre maniquies: 89,7 unidades. Los interiores muestran combinaciones de armaduras; los siguientes muestran armas, cascos y accesorios.

- 51 combinaciones con pecho/cuerpo completo (incluyen uniformes y variantes de color).
- 157 modelos/variantes visuales de armas distribuidos entre los mismos 157 NPCs.
- 18 escudos visuales, emparejados con armas de una mano; sin incompatibilidades de dos manos.
- 31 cascos/accesorios adicionales en expositores de armas.
- 404 items custom distintos representados. Las variantes identicas comparten expositor. Cobertura de todas las entradas instaladas con apariencia visible; 0 entradas visuales sin representar. Las joyas no alteran el modelo del personaje.
- Las piezas no disponibles en la integracion anterior no se inventan. En ranuras sin pieza propia puede usarse equipo S nativo como base de exposicion; el CSV enumera los IDs custom de cada maniqui.

Implementacion: NPC tipo Folk con fakePlayer nativo, nombres E001..E157, sin inventario, cuenta ni personaje jugable; inmoviles, invulnerables, no atacables, sin paseo, chat, comercio, drops ni recompensas. Enchant visual 0 para ver el recurso original. El script EquipmentShowcase aplica proteccion al aparecer y registra el comando GM de acceso. No cambia el comportamiento de otros NPCs.

Archivos instalados en runtime, source y overlay local:
- data/stats/npcs/custom/equipment_showcase.xml
- data/lab/world-spawns/EquipmentShowcase.xml (directorio de spawns realmente activo del proyecto)
- data/scripts/custom/EquipmentShowcase/EquipmentShowcase.java
- config/Custom/WorldContent.ini: agrega unicamente EquipmentShowcase a CustomScriptFolders.

Respaldo: E:\l2-local\backups\equipment-showcase-20261013-162525. Manifiesto de cambios: research/equipment-batches/showcase/installation.json.

Verificaciones PASS: esquemas NPC/spawn, IDs de equipo resueltos por el parser nativo, 157 NPCs vivos sin duplicados, inmovilidad/invulnerabilidad, ubicacion prevista y 157 paquetes CHAR_INFO serializados con todas las ranuras correctas. Reportes native-verification.txt, runtime-verification.txt y coverage.json.

La apariencia final, escala y altura deben revisarse desde el cliente. No hay geodata 22_22 de Giran instalada; se uso el mapa local y el nivel conocido de la plaza (-3400) para la distribucion. No se afirma haber realizado una inspeccion visual dentro del juego.

El arranque normal aplico la correccion pendiente preexistente 20261012-lab-service-repair; los maniquies no necesitaron modificaciones del core.

Catalogo con nombres, IDs, coordenadas y equipo: research/equipment-batches/showcase/CATALOGO-MANIQUIES.csv. No borrar los templates de equipo mientras sus maniquies esten activos.

## Correccion del empaquetado del cliente - 2026-10-13

El cliente mostro `Files are corrupted` para `../SysTextures/EB05_Renato.utx`. Las texturas/modelos renombrados se habian instalado como paquetes Unreal sin cifrar; la inspeccion de tablas y la validacion del servidor no detectaban esa incompatibilidad con el cliente.

Se reemplazaron 505 paquetes propios EB*.utx/ukx/usx: UTX con Lineage2Ver121 y clave derivada del nombre FINAL; UKX/USX con Lineage2Ver111. Los archivos .u conservan su formato anterior. Todas las cargas utiles descifradas coinciden byte por byte con las preparadas, y se verificaron cabeceras, CRC32 y hashes instalados. UModel abre la textura EB05_Renato instalada y reconoce sus dos texturas y shader. El instalador queda corregido para futuras instalaciones y verify.py exige esas cabeceras y CRC.

Respaldo: `E:\l2-local\backups\equipment-asset-envelope-20261013-165057`. Manifiesto: research/equipment-batches/asset-envelope-fix/installation.json. Catalogos, estadisticas, inventarios y maniquies conservados. El servidor sigue activo; falta repetir el arranque y la inspeccion visual en el cliente. Esta comprobacion no afirma que se haya abierto el cliente sin errores.
