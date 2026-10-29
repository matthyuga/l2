# L2 Dust2 escaleras V4 — 14/10/2026

Kevin confirmó V3: puertas y apoyo de pies funcionan; faltan escalones por todo el mapa. Envió captura de2 peldaños frente a un arco. Se corrigió auditoría:192 pruebas previas solo muestreaban aristas ya abiertas, no encontraban subidas descartadas por límite16u.

Instalado V4 en E:/l2-local, cliente E:/l2:442 transiciones de escalones con cuerpo libre comprobado en BSP (407subidas32u,19de24,16de16);11 candidatos obstruidos y138 demasiado altos excluidos. Solo NSWE Dust2, alturas intactas y sin cambiar GeoEngine global. GameServer9536 API reloadRegion(24,19), no reinicio. Primer426probe detectó4 bits pisados al abrir2 direcciones de una celda, corregido acumulando OR; final442/442PASS. Smoke40inicios+192subidas+zonas/retorno/muelle/nave siguePASS.

Fue necesario ampliar soporte nativo:31.234 capas alcanzables,862 más;1.855 pisos y1.286 paredes nuevos prefijosHGDust2V4. Desactivadas/retiradas refsV3.120.415 pasos abiertos sin conflicto de pared superior. Cuerpo10.5radio/70alto conecta40inicios y27.711centros.9.737payloads ajenos preservados. Misma escala1.0/UV/espejo/modelos visibles. Bots/galería sin cambios.

Backup combinado E:/l2-local/backups/dust2-stairs-v4-20261014-160116: rollback debe restaurar mapa y geodata juntos; la geo guardada esV3 anterior a reparación completa (07fe6604...), no la temporal426. Backupinicialgeo/manifiestos E:/l2-local/backups/dust2-stairs-20261014-155816. Manifiestos principal/V2/V3/V4 hashes sincronizados. No ejecutar instaladores históricos ni prepare.pyV4 sobre mapa ya instalado. Documentación research/dust2-stairs-v4/README.md. Sin commit/push.

Pendiente prueba cliente de Kevin con `.dust2`, async enviada. Si persiste mismoescalón, obtener coordenadas mientras esté allí: lectura online no encontró jugador, posición DB139334,56447,8072 heading40411 podría ser posterior a captura. No declarar todas las escaleras resueltas solo por PASS servidor. Critical de salida sigue pendiente y separado.
