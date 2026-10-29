# L2 Dust2 cámara V9 preparada — 2026-10-14

Ruta real E:\l2-local. Kevin reportó zonas faltantes en V8; dejó al personaje y hay capturas Shot00082..85 (PNG en research/dust2-camera-v8/qa). Posiciones leídas142414,56349,8000 y después142557,54506,8088. Se vio exposición de paredes/bordes con cámara distante. V8 no está validada por completo.

V9 preparada, NO instalada aún: research/dust2-camera-v9. Recupera4621 celdas de techo de228 rectángulos descartados por un conflicto local de altura.462 nuevas piezas de techo,2101 uniones cortas; separación conservadora de todas las capas caminables.900 celdas requieren elevar el techo (máx216u);206 uniones se recortan para no bloquear el paso. No prometer cierre hermético en toda dirección. No cambia rampas/geodata/user.ini/apariencia; todos los payloads anteriores preservados salvo myLevel para añadir actores.

Verificación de paquete cifrado y malla nativa recargada PASS2563 actores, referencias únicas y189 rampas confirmadas conservadas. Auditoría geométrica de360 direcciones ascendentes por punto: escapes latest_user67->0; previous_user151->0; CT y escalera20->0. No equivale a prueba nativa de cámara ni de apariencia completa.

Se pidió cerrar L2 mediante async para instalar; al último chequeo PID9040 seguía abierto. Tras cierre ejecutar python research/dust2-camera-v9/install.py (guardia SHA/8manifiestos/backup). Después verificar9manifiestos y pedir comparar cámara en la posición donde dejó al personaje. Detalles README y verificación en directorio V9. Escalera larga confirmada; critical de salida sin causa determinada.

Actualización: Kevin confirmó cierre y V9 quedó instalada. Backup E:\l2-local\backups\dust2-camera-v9-20261014-173421. Nueve manifiestos y mapa vivo cotejados. Sin reinicio de GameServer. Pendiente prueba visual desde la zona donde dejó al personaje.
