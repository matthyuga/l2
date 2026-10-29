> Estado posterior: Dust2 está añadido al mismo mapa. Antes de restaurar esta aeronave, retirar Dust2 con su restore.py y revisar los hashes. Ver ../dust2-integration/README.md.

# Aeronave integrada — 14/10/2026

## Uso dentro del juego

- `.muelle nave` o `.muelle barco`: llegada a la cubierta de la nave estacionada, al este del muelle aéreo.
- `.muelle`: regreso al punto habitual del muelle.
- `.muelle coliseo`: bajar al Coliseo desde muelle o aeronave.
- `.muelle estado`: coordenadas y diagnóstico.

Esta versión instala el modelo, materiales, colisión estática y geodata para recorrerlo. **No vuela, no recorre Giran y no tiene tripulación NPC todavía.** El transporte móvil sigue pendiente. No se cambiaron los puntos de nacimiento de personajes nuevos, que siguen llegando al muelle.

## Instalado

- Cliente `E:/l2/StaticMeshes/HGSkyAirship.usx`: 12 piezas nativas, atlas de 2048² con mipmaps y material FinalBlend de doble cara. 20394 triángulos tras retirar cuatro degenerados.
- Cliente `E:/l2/Maps/24_19.unr`: doce actores nuevos. Los 5054 payloads originales fuera de myLevel permanecen idénticos; se mantiene el muelle ya visible y el Coliseo inferior.
- Actor location 152000,46700,11752.8, escala 3; cubierta central de malla en Z ~12000, geodata en Z12040 y llegada efectiva del servidor en Z12045.
- Geodata `server/game/data/geodata/24_19.l2j`: añade 7674 celdas de nave, conserva capas anteriores, cierra bordes sin soporte y valida 3311 capas accesibles desde la cubierta.
- Handler GludioSky y zona peace/respawn extendida hasta X154000 para abarcar la aeronave; código y zona persistidos también en source/dist y cloud overlay.

Respaldo completo anterior a la instalación: `E:/l2-local/backups/airship-integration-20261014-122332`. Manifest con hashes antes/después en `installation.json`. Son nueve archivos instalados.

## Materiales y comprobaciones

Se conservaron las siete imágenes empaquetadas del original y se hornearon sus materiales en un atlas. La salida respeta color base; efectos PBR, bump y microdetalle no se reproducen exactamente en Interlude. La tela pierde detalle al reunir todos los recursos en 2048²; mejora de densidad/resolución queda abierta.

Se verificó visualmente `baked-preview.png` y, más importante, `native-preview.png`, esta última reconstruida desde el paquete compilado mediante UModel/glTF y la textura exportada por el lector nativo. La exportación nativa de la imagen tiene orientación vertical opuesta a Blender, coherente con la conversión UV: no corregir solo la imagen sin revisar el par malla/textura. No se declara igualdad de píxeles sin transformación.

Verificaciones:

- UCC compila, guarda y recarga las doce piezas. Se conserva aviso del importador sobre aristas compartidas por más de dos triángulos; render posterior inspeccionado.
- UModel modo L2 carga las doce mallas, textura y FinalBlend sin recursos faltantes.
- Ambos archivos de cliente están cifrados Ver121 y comprobados por CRC y roundtrip íntegro.
- Se comprobaron hashes de todos los archivos instalados.
- Prueba real del handler en el GameServer activo con Player transitorio, sin cuenta/personaje persistente: cubierta12045, instancia0; movimiento permitido en cuatro direcciones, zona de paz, regreso a muelle12021 y Coliseo-3403. `server-smoke.txt`: PASS.
- **Pendiente observación dentro del cliente L2:** los renders anteriores son comprobaciones del recurso convertido, no capturas del juego. No afirmar validación visual ingame ni pruebas de transporte móvil.

Servidor actual después del despliegue: PID18080, puerto7777. Se solicitó apagado ordenado sin clientes conectados; el lanzador lo reinició automáticamente después de instalar. Un segundo arranque manual falló al enlazar el puerto y se cerró, dejando una sola instancia GameServer. La prueba PASS se ejecutó sobre la instancia dueña de7777. LoginServer no se reinició.

## Reproducción y restauración

Origen del bake: `research/airships/external-downloads/bake_airship_l2.py`; modelo editable de trabajo `HGSkyAirship-baked.blend`. `build_native.py`, `build_geodata.py`, `prepare_server.py`, `verify_stage.py` preparan recursos con pruebas; el build se niega a añadir actores duplicados sobre un mapa ya integrado.

No ejecutar instaladores históricos de Gludio sobre este estado. Para retirar esta integración, cerrar cliente y GameServer y ejecutar `restore.py`: comprueba hashes y restaura exactamente el estado anterior a la nave. El rollback anterior de Gludio debe realizarse después de este, nunca antes. El lanzador tiene reinicio automático: confirmar que GameServer permanece cerrado antes de restaurar.

Siguiente sistema: definir y probar vehículo móvil con coordenadas relativas, embarque, rutas verticales, pasajeros/NPCs y reconexión. La geodata actual es para la nave estacionada; no se debe desplazar esta malla y esperar que el suelo del servidor la acompañe.
