# Vigilia del Dragón V2 — nave de clan, 15/10/2026

Revisión posterior: las capturas del usuario mostraron muebles demasiado grandes, silla sin patas y encuentro de cabina/piso desalineado; solicitó corregir también circulación y escaleras. V3 preparada/instalada en `../vigilia-clan-v3`, con escala de objetos reducida, frente de cabina hacia proa, encuentro rectangular y rampas de apoyo nativas. Consultar su README y manifest para el estado exacto. Retirar V3 antes de este rollback histórico; las pruebas de V2 descritas debajo eran del servidor y no acreditaban el recorrido del cliente.

Revisión a partir de las capturas ingame y comentarios de Kevin. Sustituye la V1 estacionada conservando ubicación y escala general; distribución y muebles pensados para un grupo/clan. No se impone un aforo ni se implementa propiedad de clan.

## Cambios visibles

- Mascarón nuevo: cabeza angular con ojos rasgados, pupilas verticales, cejas, cuernos segmentados, abanicos de mejilla, placas en la frente, escamas superpuestas con bordes dorados, cresta y dientes superiores/inferiores con colmillos. Mantiene el bronce/jade de la identidad original.
- Escaleras: 22 peldaños por banda, en lugar de ocho. Subida de 0,15 m de diseño (15 unidades L2), huella de 0,32 m y ancho de 1,35 m. Conectan la cubierta Z4,15 con el puesto del capitán Z7,45.
- Habitación de popa abierta mediante paredes separadas y entrada libre de 2,4 m. Cama con colchón, manta y almohada; mesa y mapa, silla y cofre decorativo. No son inventario, almacén ni cama interactiva.
- Se retira el tejado a dos aguas y el antiguo timón aislado. Nuevo puesto superior de capitán con cubierta plana, timón, cartas/brújula, mamparos, parabrisas laterales y dosel plano.
- El antiguo toldo intermedio se convierte en galería rígida a Z11,2 con piso, barandas perimetrales, bancos y tirantes. Tiene suelos y límites nativos, más geodata a su altura.
- Estandartes de clan y mesa de estrategia en cubierta. Muebles dimensionados tomando una persona de 1,8 m como referencia. El casco/globo conservan la escala de la nave anterior.

## Accesos

- `.muelle dragon` / `.muelle vigilia`: cubierta.
- `.muelle dragon proa`: cerca del mascarón.
- `.muelle dragon habitacion`: entrada interior al aposento.
- `.muelle dragon capitan`: puesto superior.
- `.muelle dragon galeria`: galería intermedia.
- `.muelle`: regreso al muelle; `.muelle coliseo` conserva el acceso de salida.

Tres NPC **Contramaestre / Vigilia del Dragon** (ID902710, apariencia nativa30146) en cubierta, puesto de capitán y galería. Ofrecen cuatro destinos mediante diálogo: cubierta, galería, capitán y aposento. Traslado gratuito, a pie y fuera de combate/PvP/karma/eventos/instancias. El bypass requiere el NPC correcto, proximidad XY y altura; no permite pedir el traslado desde otra planta o a distancia.

## Conversión y reemplazo

Archivo editable `Vigilia-clan-v2.blend`; renders `vista-general.png`, `dragon-detalle.png`, `cubierta-clan.png`, `aposento.png`, `puente-y-galeria.png`.

`HGVigiliaV2.usx` utiliza un paquete independiente del V1. El mapa actual pierde únicamente las 297 referencias activas de V1 (23 visuales, 274 soportes); sus payloads quedan intactos pero fuera de la lista de actores del nivel. Añade el recurso visual nuevo y los soportes V2. Aurelia, Dust2, muelle y otros actores anteriores se conservan. No se restaura un mapa antiguo sobre el actual.

`clean_previous_geo.py` retira solamente las 48.441 capas exactas de V1 registradas en `../vigilia-integration/encoded-layers.json`, comprobando que existen. Conserva los demás datos del archivo actual. Luego se añaden las capas V2: 12.527 accesibles desde cubierta/habitación/capitán, más 3.328 en galería. No quedan el techo o las paredes cerradas de V1 como obstáculos invisibles.

La navegación V2 se construye con proxies explícitos de suelos transitables y paredes: no se toman techos, dientes, globo o muebles como pisos fantasma. El soporte del cliente usa `deco01.Box02`, malla nativa sin modificar: 147 losetas y 356 barreras. Son aproximaciones en cuadrícula de16 unidades, con topes de altura antes de otro nivel. Falta comprobar las holguras de la cápsula en el cliente.

El atlas conserva los 21 colores de material, incluyendo los detalles de geometría del dragón. Bump procedural, refracción e iluminación de Blender no se transfieren al motor. Faroles y ojos no añaden luces dinámicas. No hay vuelo, rutas ni animación de timón/hélices.

## Verificación previa al despliegue

- Exportación de46.773 triángulos; se retiran128 degenerados. UCC compila46.645, con avisos del importador sobre aristas compartidas por más de dos triángulos; cero errores. UModel recarga26 mallas, atlas y material sin referencias faltantes.
- `native-preview.png`: reconstruido desde el paquete nativo para inspeccionar geometría/ejes/atlas. Es un render de revisión, no captura de L2.
- Se conservan51.867 payloads previos fuera de myLevel y5.044.468 capas previas ajenas a la V1 retirada. Cifrado Ver121 con roundtrip completo y CRC.
- 15.855 capas cubiertas por los soportes;61.686 transiciones abiertas verificadas frente a barreras, cero conflictos en líneas centrales.
- `navigation-routes.json`: dos subidas, dos bajadas y entrada al aposento;46 nodos por ruta de escalera y23 por entrada. `navigation_checks.py` reconstruye las rutas dirigidas.
- Java del handler y NPC compilado contra las librerías del servidor antes de instalar. El ensayo real posterior está en `server-smoke.txt` cuando termina el arranque.

## Instalación y respaldo

Doce archivos instalados, con hashes antes/después en `installation.json`. Respaldo: `E:/l2-local/backups/vigilia-clan-v2-20261015-203054`.

Cliente: mapa `24_19.unr` y paquete nuevo `HGVigiliaV2.usx`. Servidor: geodata24_19; en runtime, source/dist y cloud overlay, GludioSky.java actualizado, nuevo VigiliaCrew.java dentro de la carpeta de scripts existente y template `vigilia_crew.xml`. No se modifica la lista de CustomScriptFolders ni se reemplaza configuración completa.

Kevin confirmó cerrar el cliente; la primera guarda esperó su cierre efectivo y no escribió archivos hasta que el proceso desapareció. Apagado de GameServer ordenado con cero clientes conectados. LoginServer y base de datos conservados. Servidor reiniciado con el lanzador habitual.

Para volver a V1: cerrar cliente y GameServer de forma sostenida, luego `python research/vigilia-clan-v2/install.py --restore`. Se verifican todos los hashes antes de restaurar el estado exacto inmediatamente anterior. Retirar V2 antes de cualquier restauración de V1, Aurelia o integraciones anteriores.

No hay commit ni push. La confirmación ingame de las colisiones, los peldaños y el diálogo de NPC queda pendiente de recorrido del usuario; no se confunde el ensayo del servidor con física del cliente.

## Ensayo real completado

`server-smoke.txt` PASS sobre GameServer7876, puerto7777. Cinco accesos con suelo y movimiento cardinal4/4: cubierta146500,52000,12061; proa147400,52000,12061; habitación145650,52000,12061; capitán145500,52000,12389; galería146700,52000,12765. Se verifican202 pasos de rutas completas por ambas escaleras en subida/bajada y entrada al aposento, además de24 pasos abiertos y16 bloqueados. Todos los accesos tienen paz/respawn.

Tres NPC instanciados; menú comprobado mediante el script cargado en el servidor; cuatro traslados realizados de verdad por su onEvent. Se rechaza bypass remoto y de personaje muerto. Se conservaron accesos/pisos de Aurelia, nave anterior, muelle y Coliseo. Player de ensayo transitorio, sin cuenta ni personaje persistido. Cliente visual/física V2 continúa pendiente del usuario.
