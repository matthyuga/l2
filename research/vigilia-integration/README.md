# Vigilia del Dragón en L2 — 14/10/2026

Actualización del15/10/2026: V1 sustituida por la revisión de clan V2 a partir de capturas de Kevin. Dragón más detallado, habitación abierta/amueblada, puesto superior, escaleras nuevas y galería con NPC. Ver `../vigilia-clan-v2/README.md`. El rollback de V2 debe ejecutarse antes que este rollback histórico. Los apartados siguientes describen V1.

Instalación estacionada de la maqueta original `../airship-epic/Vigilia-del-Dragon-v1.blend`, autorizada por Kevin después de la integración de Aurelia. Se añade en una parcela propia, preservando Aurelia, la nave anterior, Dust2 y el muelle.

## Acceso dentro del juego

- `.muelle dragon` o `.muelle vigilia`: cubierta central.
- `.muelle dragon proa` o `.muelle vigilia proa`: cubierta cerca de la cabeza de dragón.
- `.muelle`: regresar al muelle habitual.
- `.muelle coliseo`: bajar al Coliseo desde esta nave.
- `.muelle aurelia` y `.muelle nave`: conservan los accesos anteriores.

Se mantienen las restricciones de viaje del handler GludioSky. Hay zona de paz y respawn al muelle. No cambian cuentas, inventarios ni nacimiento de personajes nuevos.

## Recursos instalados

- `E:/l2/StaticMeshes/HGVigilia.usx`: 23 piezas, atlas de 512² con 17 colores de material y mipmaps, FinalBlend de doble cara.
- `E:/l2/Maps/24_19.unr`: añade las piezas visuales y 274 actores ocultos de colisión nativa `deco01.Box02` (74 losetas de suelo y 200 barreras laterales).
- `server/game/data/geodata/24_19.l2j`: capas nuevas de la nave conservando todas las anteriores.
- Handler GludioSky actualizado y `vigilia_dragon.xml` nuevo en runtime, source/dist y cloud overlay. Se aplica el cambio sobre cada copia de su propio handler.

Modelo en 146500,52000,11600, escala 1 después de convertir el origen a 100 unidades por metro de diseño. Proa hacia +X. Envolvente nativa aproximada X144193–148840, Y51093–52907, Z11408–14506. No se solapa con la parcela de Aurelia ni con la de Dust2.

Respaldo de los nueve archivos: `E:/l2-local/backups/vigilia-integration-20261014-195245`. Manifest completo y hashes en `installation.json`. El GameServer anterior se apagó ordenadamente con cero clientes conectados; se inició con el lanzador habitual. LoginServer y base de datos no se reiniciaron.

## Pruebas completadas

- Compilación nativa sin errores. El importador emite avisos `BuildStripifyInfo` por aristas compartidas por más de dos triángulos. UModel vuelve a cargar las 23 mallas, el atlas y el material sin recursos ausentes.
- 40.699 triángulos exportados y 40.699 leídos para la geodata.
- `native-preview.png` inspeccionado: render reconstruido desde el paquete compilado mediante UModel/glTF. Ejes y orientación de UV comprobados. No es una captura del cliente L2.
- Preservados byte por byte los 51.570 payloads anteriores del mapa fuera de myLevel y las 5.044.468 capas anteriores de geodata.
- 7.782 capas alcanzables desde la cubierta/proa; 30.266 transiciones abiertas comprobadas contra las barreras, cero conflictos en esas líneas centrales. Las cajas siguen una cuadrícula de 16 unidades; no certifica holguras de cápsula en todo el recorrido.
- Paquetes Ver121 comprobados por payload íntegro y CRC; hashes de los nueve archivos instalados verificados.
- Compilación Java del handler y ensayo real en el GameServer activo: `server-smoke.txt` PASS. Llegadas efectivas 146500,52000,12061 y 147400,52000,12061. Ambos puntos permiten las cuatro direcciones cardinales y tienen paz/respawn. Se prueban 24 pasos abiertos, 16 bloqueados, regreso al muelle/Coliseo, nave anterior, acceso a Aurelia y sus pisos interiores. Player temporal, sin cuenta ni personaje guardados.

## Alcance y pendientes

Nave estacionada para exploración de la cubierta. No se implementaron vuelo, rutas, transporte móvil, NPCs, hélices animadas ni timón funcional. La cabina de capitán sigue siendo una estructura visual cerrada; no se añadió interior ni acceso nuevo al timón elevado. Las escaleras originales no tienen un recorrido completo validado en el cliente.

Se conservan los colores de madera, bronce, lona, faroles y ojos. El bump procedural de madera/lona y los shaders PBR no se trasladan al material nativo: el atlas contiene colores base. Los faroles/ojos no emiten luces dinámicas. La revisión visual y física dentro del cliente L2 sigue pendiente; las pruebas de servidor y el render convertido no la reemplazan.

## Reproducción y retirada

`export_source.py` se ejecuta con Blender. Luego `build_native.py`, `build_geodata.py`, `build_collision.py`, `prepare_server.py`, `verify_stage.py`, `install.py` y `prepare_smoke.py` preparan y comprueban cada etapa. Son adaptaciones aisladas del flujo validado para Aurelia; no se reejecutaron los instaladores históricos.

Para retirar: cerrar cliente y GameServer de forma sostenida y ejecutar `python research/vigilia-integration/install.py --restore`. Comprueba los hashes actuales antes de recuperar el respaldo. Retirar Vigilia antes de restaurar Aurelia, Dust2, la aeronave anterior o el muelle. No ejecutar constructores históricos sobre el mapa modificado.

Sin commit ni push.
