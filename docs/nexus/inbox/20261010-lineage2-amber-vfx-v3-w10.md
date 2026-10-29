# Amber VFX V3 — W10

10/10/2026. Ruta operativa `E:\l2-local`; cliente `E:\l2\system-hud`.

Usuario encargó efectos de fuego/soulshot, lluvia y su relación con zona/impactos. Aclaró que los fallos observados eran anteriores a los últimos ajustes W11.

Instalada V3: encendido naranja y carga blanca en mano/arco, fases CastingActions, caída circular de 30 flechas por oleada y destellos en suelo a 650ms, traza de fuego por distancia/origen vertical y tiempo completo del arco. Nuevos AmberEffectsV3.usk y AmberParticlesV3.u; paquetes anteriores conservados.

64 checks de servidor PASS con probes privados; radio 199 daña, 201 evita. Probes offline. Catálogos instalados verificados, filas ajenas íntegras; texturas exportadas iguales. Core y XML de stats no cambian. Normal después de la prueba, tres verificadores false, un GameServer. No commit/push.

La lluvia sigue siendo área circular fija, sin colisiones individuales ni trayectoria balística completa. La revisión de enganches/reproducción visual en L2 permanece pendiente: no se observó el parche en juego.

Continuidad: `E:\l2-local\CONTINUIDAD-W10\14_AMBER_VFX_V3_2026-10-10.md` y `reports\amber-vfx-v3-verification.json`. Respaldo `backups\amber-vfx-v3-2026-10-10`. El cierre anterior de W11 con 61 checks describe V2, no la última versión.
