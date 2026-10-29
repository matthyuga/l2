# Aurelia integrada en L2 — 14/10/2026

Estado posterior del 14/10/2026: Vigilia del Dragón fue añadida al mismo mapa conservando los recursos de Aurelia. Antes de restaurar Aurelia hay que retirar Vigilia con su propio restore y verificar hashes; ver `../vigilia-integration/README.md`.

Modelo de `../airship-resort-v1`, creado desde cero a partir de la referencia de Kevin. Se añade a la región actual `24_19`, en una parcela separada de la aeronave anterior y Dust2. No se sustituyen esas atracciones.

## Acceso

- `.muelle aurelia` o `.muelle aurelia cubierta`: terraza junto a la piscina.
- `.muelle aurelia a`: pasillo de la cubierta interior A.
- `.muelle aurelia b`: pasillo de la cubierta interior B.
- `.muelle aurelia puente`: puente de navegación.
- `.muelle`: regreso al muelle habitual.
- `.muelle coliseo`: regreso al Coliseo, también desde Aurelia.
- `.muelle nave`: conserva el acceso a la aeronave anterior.

Mismas restricciones de viaje del muelle: vivo, fuera de combate/PvP/karma, sin vuelo, instancia, Olimpiadas ni teleport pendiente. La parcela es zona de paz y respawn al muelle. No cambian el spawn de personajes nuevos, inventarios ni cuentas.

## Instalación

- Cliente: `E:/l2/StaticMeshes/HGAurelia.usx`, 28 piezas de malla, atlas de colores de 256² con mipmaps y material FinalBlend de doble cara.
- Cliente: `E:/l2/Maps/24_19.unr`, añade esas piezas y los soportes de colisión nativos.
- Servidor: `server/game/data/geodata/24_19.l2j`, conserva todas las capas anteriores y añade las de Aurelia.
- Handler GludioSky y archivo nuevo `aurelia_resort.xml`, tanto en runtime como source/dist y cloud overlay. Cada copia del handler se modifica sobre su propio contenido.
- Posición del modelo: 156000,55000,10200; escala 1 sobre geometría convertida a 100 unidades por metro de diseño. Envolvente aproximada: X149984–162900, Y51193–58807, Z10200–14200.
- Llegadas exactas y cantidades en `collision-audit.json`; archivos y hashes antes/después en `installation.json`.

La conversión elimina las dos referencias humanas de escala, evalúa curvas/textos/modificadores y descarta 864 triángulos degenerados del origen. UCC recibe 50.365 triángulos; el lector de mallas usado para geodata obtiene 50.317 después de la compilación. No se oculta esta diferencia ni se usa el conteo del Blender original como conteo nativo.

## Colisiones y geodata

Se usa el recurso original del cliente `deco01.Box02` oculto, sin modificarlo, para 21.127 losetas de apoyo y 5.677 barreras laterales. Es la técnica que ya sostuvo suelos y paredes de Dust2 en este proyecto. Las cajas siguen la cuadrícula de geodata de 16 unidades, con pequeños solapes y altura limitada antes del siguiente piso.

La geometría visual importada no se usa como única garantía de colisión. Los bordes cerrados reciben barreras; los descensos dirigidos y pasos abiertos se conservan. Esto aproxima los contornos de superficies curvas con una cuadrícula: requiere comprobar las holguras de la cápsula del personaje en el cliente, especialmente escaleras, puertas, piscina y mobiliario. No se certifica un recorrido completo por todos los camarotes.

Verificación estática: 393.667 capas alcanzables desde los puntos de revisión, 1.546.924 transiciones abiertas comprobadas contra las barreras, cero conflictos en esas líneas centrales; 24.738 payloads anteriores del mapa fuera de myLevel preservados byte por byte; 4.421.275 capas de geodata anteriores conservadas. No equivale a una prueba de física del cliente.

## Apariencia y límites

Se preservan los diez colores de material del modelo mediante un atlas y UV propias. Se corrigieron los ejes LightWave→Unreal y la orientación vertical del atlas, y se inspeccionó `native-preview.png` reconstruido desde el paquete nativo mediante UModel/glTF. Ese render no es una captura ingame. UCC compila sin errores, con los avisos del importador de aristas compartidas por más de dos triángulos.

Es una nave **estacionada**. No hay vuelo, rutas, transporte móvil, tripulación NPC ni animación de motores. El agua y los cristales son superficies visuales; no se implementó natación, volumen de agua ni refracción. No se transfieren luces o shaders PBR de Blender. Sigue pendiente la observación ingame de apariencia, rendimiento y física.

## Reproducción y restauración

Fuentes: `export_source.py` (Blender), `build_native.py`, `build_geodata.py`, `build_collision.py`, `prepare_server.py`, `verify_stage.py`, `install.py`, `prepare_smoke.py`. La preparación usa el mapa y geodata actuales y rechaza instalaciones duplicadas o cambios concurrentes.

Para restaurar, cerrar cliente y GameServer de forma sostenida y ejecutar `python research/aurelia-integration/install.py --restore`. Se comprueban los hashes de los nueve archivos instalados antes de recuperar el respaldo. Retirar Aurelia antes de cualquier rollback histórico de Dust2, aeronave anterior o muelle. No ejecutar constructores/instaladores históricos sobre el mapa actual.

No hay commit ni push. El estado del ensayo con personaje temporal está en `server-smoke.txt`, cuando el GameServer termina su arranque. No se modifica ni guarda ningún personaje persistente para ese ensayo.

## Ensayo real en GameServer completado

`server-smoke.txt`: PASS. Los cuatro comandos de acceso funcionan con el handler instalado en el servidor activo. Llegadas efectivas: terraza 153400,55800,12045; A 156000,55000,11301; B 156000,55000,10797; puente 151700,55000,11677. Los cuatro puntos permiten movimiento en las cuatro direcciones cardinales y tienen paz/respawn al muelle. Se comprobaron 24 pasos abiertos y 16 bloqueados, los pisos anteriores y los viajes de regreso al muelle, al Coliseo y a la nave anterior. Ensayo con Player transitorio, sin cuenta ni personaje guardados.

Respaldo de los nueve archivos: `E:/l2-local/backups/aurelia-integration-20261014-193611`. LoginServer y GameServer arrancados con el lanzador habitual después de instalar. Esta prueba valida lógica y geodata del servidor; el recorrido y el aspecto dentro del cliente L2 siguen pendientes.
