# Lineage II Interlude Lab — hotfix de juego/PvP

Fecha: 2026-10-07 21:33 (America/Buenos_Aires)  
Ruta real: `E:\l2-local`

- Buffer configurado a 7.200 segundos para buffs, songs, dances y especiales.
- Noblesse Blessing (1323) añadido al Scheme Buffer.
- Mana Potion (728) añadida a `50039928` del GM Shop por 2.000 Adena.
- Cubics ajustados al tope retail de tres para builds acumulativas sin Cubic Mastery activa.
- Sala Elven PvP: 9 fake players ahora reciben blancos FFA; jugadores entran/reaparecen con Noblesse y HP/MP/CP completos.
- Core compilado, `GameServer.jar` desplegado y servidor reiniciado correctamente a las 21:33; cargó 128 scripts, 86 buffs disponibles y sin errores de compilación.
- Backup del jar anterior: `E:\l2-local\backups\pre-pvp-hotfix-2026-10-07-2133\GameServer.jar`.
- `Alt+R` liberado: se desactivaron de forma persistente `IsShadowPlayEnabledUser` e `IsShadowPlayEnabled`, se reinicio solo el contenedor `SPUser` y se confirmo que quedan 0 procesos `NVIDIA Overlay.exe`. `Alt+Z` deja de funcionar intencionalmente mientras el overlay este desactivado.
- Copia reversible del registro: `E:\l2-local\backups\nvidia-overlay\NVSPCAPS-20261007-214003.reg`.
