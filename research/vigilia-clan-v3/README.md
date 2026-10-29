# Vigilia V3 — proporciones de personaje y circulación

Revisión del15/10/2026 a partir de las nuevas capturas de Kevin. **Casco, globo, dragón y galería conservan tamaño y ubicación.** Se corrige la escala interna de los objetos y se reconstruye la cabina y sus accesos. La referencia de1,8m usada en las versiones anteriores no había sido calibrada con el tamaño que muestra el cliente L2.

## Cambios

- Cama, colchón, manta, almohada, cabecero, mesa, silla y cofre al25% de las dimensiones V2. Cama60×38,75u; mesa50×30u; silla16,25×16,25u; cofre37,5×21,25u. Se añade la silla con cuatro patas que llegan al piso.
- Bancos rehechos con asiento85×20u a12,5u del piso, respaldos y cuatro patas. Ocho bancos en cubierta y ocho en galería, con separación entre ellos. Todos los bancos de cubierta están al este del pie de escaleras, sin cruce entre ambas piezas.
- Dos mesas pequeñas de estrategia85×42u, con patas y mapas. El corredor central se conserva despejado.
- Aposento reducido y rectangular, con entrada abierta y umbral al nivel de cubierta. Se conserva dormitorio/muebles decorativos; sin almacén ni interacción nueva de objetos.
- Puesto de capitán más bajo: suelo a Z5,43 de diseño, antes7,45. Paredes y cristales frontales orientados a proa(+X), **delante del timón**. Acceso por atrás. Timón reducido a radio20u y manijas25u. Consola48×38u.
- Piso de puente rectangular, paredes rectangulares y techo rectangular con cornisa y esquinas alineadas. Se retira el perfil triangular anterior. Los muros inferiores terminan bajo la losa para evitar superficies coplanares/oscuras en los bordes.
- Dos escaleras cortas:16 peldaños por banda, subida8u, huella24u, ancho88u. Nuevos pasamanos y zancas. Además del soporte de geodata, cada una tiene una rampa invisible continua con el recurso nativo `deco01.Box02`, para que el cliente no dependa de pequeños apoyos separados.

## Escala

Las dimensiones se documentan en **unidades L2**, no se equipara un metro real con100u como referencia humana. El modelo fuente mantiene100u por unidad de diseño para no alterar la nave. Se usan referencias visuales de46u en el archivo Blender para comparar mobiliario y circulación; quedan en la colección de estudio y no se exportan al juego. El template HumanFighter local tiene collisionHeight23; ese dato físico no demuestra por sí solo la altura renderizada de todas las razas, monturas y transformaciones. La calibración final requiere revisión en el cliente.

El generador de navegación V3 usa64u de espacio libre, sin cambiar la configuración global del servidor ni otras geodatas. Permite un aposento coherente con la nueva escala sin aplicar el filtro anterior de128u a este mobiliario más pequeño.

## Accesos conservados

`.muelle dragon`, `proa`, `habitacion`, `capitan`, `galeria` y sus alias `vigilia`. Los contramaestres mantienen ID902710 y cuatro opciones de traslado. Se actualizan las coordenadas del aposento y del puesto de capitán, y el spawn del contramaestre superior, para coincidir con los suelos nuevos. `.muelle` regresa al muelle.

## Reemplazo y verificaciones

Se prepara sobre el mapa actual, retirando únicamente las529 referencias activas V2(26 visuales y503 soportes). Las capas exactas V2 se restan mediante su registro `encoded-layers.json`; se preservan los demás datos actuales. Los payloads antiguos quedan intactos pero fuera de la lista activa del nivel. El paquete nuevo es `HGVigiliaV3.usx`.

Las comprobaciones completas y cantidades finales quedan en `verification.json`, `ramp-verification.json`, `collision-audit.json` y `navigation-routes.json`. Se prueban rutas de subida/bajada, líneas desplazadas16u a ambos lados del centro de las escaleras, acceso al aposento y pasillos laterales por fuera de las escaleras. Las rampas nativas se releen del mapa y se comprueban sobre su transformación real, no solo sobre las coordenadas previstas.

`native-preview.png` es un render del paquete convertido, no una captura de L2. `server-smoke.txt` registra el ensayo posterior contra el GameServer activo. Ninguna de esas pruebas reemplaza el recorrido del usuario desde el cliente ni la holgura completa de las cápsulas de todas las razas/monturas.

## Archivos y restauración

Modelo editable `Vigilia-clan-v3.blend`; fuentes Python; vistas `vista-general.png`, `cabina-frente.png`, `aposento.png`, `escaleras.png`, `mobiliario.png`. Los maniquíes de comparación solo aparecen en las vistas de estudio.

La instalación cambia paquete nuevo y mapa de cliente, geodata, y las dos clases GludioSky/VigiliaCrew en runtime, source/dist y cloud overlay. Los hashes y el respaldo exacto se registran en `installation.json` al instalar. No cambia el template de NPC, las cuentas, equipo, puntos de nacimiento ni otras zonas.

Para restaurar: cerrar cliente y GameServer de forma sostenida y ejecutar `python research/vigilia-clan-v3/install.py --restore`. Comprueba hashes antes de restaurar el estado inmediatamente anterior. Retirar V3 antes de restaurar V2, V1, Aurelia o cualquier integración histórica.

No hay vuelo ni nuevos sistemas de clan; muebles y timón decorativos. Sin commit ni push.

## Instalado y ensayado

Respaldo exacto `E:/l2-local/backups/vigilia-clan-v3-20261015-205848`. Nueve archivos instalados. Apagado ordenado del GameServer con cero clientes conectados y cliente L2 cerrado; LoginServer/base de datos conservados. Nuevo GameServer3064, puerto7777, listo.

Paquete nativo:27 mallas, atlas y material;48.517 triángulos compilados después de retirar128 degenerados. El importador conserva los avisos `BuildStripifyInfo`; UModel recarga los29 recursos sin referencias faltantes.123 apoyos horizontales,306 barreras y2 rampas inclinadas. Se conservan52.396 payloads previos fuera de myLevel y5.044.468 capas ajenas a V2. Se retiran16.533 capas exactas V2 y sus529 referencias activas.

`verification.json`:15.233 capas de apoyo y59.492 transiciones abiertas sin conflicto con barreras. `ramp-verification.json`:150 muestras sobre las rampas nativas transformadas, error máximo de altura0,0069u frente al plano de diseño.11 rutas dirigidas,307 pasos en total, incluyendo centro y lados de escaleras y corredores laterales.

`server-smoke.txt` PASS en el servidor activo: cinco llegadas con movimiento4/4 y paz/respawn;307 pasos completos de rutas y24 abiertos/16 bloqueados adicionales. Tres contramaestres, menú válido y cuatro traslados reales. Bypass remoto, desde otra planta y estando muerto rechazados. Conserva Aurelia, nave anterior, muelle y Coliseo. Player temporal, sin personaje persistido.

Llegadas efectivas: cubierta146500,52000,12061; proa147400,52000,12061; habitación145450,52000,12061; capitán145350,52000,12189; galería146700,52000,12765. Pendiente confirmación en cliente de apariencia, escala real y física de escaleras/rampas.
