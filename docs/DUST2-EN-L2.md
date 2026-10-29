> Actualización V2,14/10/2026: mapa reducido y corregidas orientación de caminos y texturas; usa .dust2 para las nuevas llegadas. Falta confirmar esta versión dentro de L2. Detalles research/dust2-scale-v2/README.md.

# Dust2 en L2

Incorporado el 14/10/2026 como zona de exploración en paz.

- `.dust2`: entrar por CT.
- `.dust2 t`: ir al sector T.
- `.dust2 ct`: volver al sector CT.
- `.dust2 salir`: regresar al punto desde el que entraste.
- `.dust2 estado`: diagnóstico.

Los comandos se escriben en el chat del juego. El GameServer ya está reiniciado y tiene cargado el acceso. Se verificaron viajes, alturas y muestras de movimiento desde el servidor; queda pendiente revisar el aspecto y la cámara dentro del cliente. No incluye todavía rondas, bombas ni reglas PvP.

La aeronave y el muelle siguen disponibles con `.muelle nave` y `.muelle`.

Detalles, respaldo y restauración: [research/dust2-integration/README.md](research/dust2-integration/README.md).

## Validación dentro de L2

Kevin confirmó el 14/10/2026: «Sí, ahora pisos y paredes funcionan». La versión actual combina el mapa visual de Dust2 con soporte nativo de suelo y paredes siguiendo la geodata. Confirmación de recorrido manual, no certificación exhaustiva de todos los puntos.

El critical de salida reportado anteriormente sigue pendiente de diagnóstico/confirmación; no se declara corregido por esta prueba.
