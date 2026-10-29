# L2: cobertura nativa de diagnóstico V1 — 25/10/2026

Usuario autorizó implementar después del análisis REA. Trabajo real E:\l2-local\research\map-fog-native-v1. Proxy d3d9.dll añadido a E:\l2\system-hud con INI; NWindow/Engine/Interface intactos. Hash estricto de NWindow y prólogos; hooks en memoria DrawWorldMap/DrawTownMap pintan rectángulo semitransparente usando NCGDevice nativo, mismo desplazamiento/visor. Ancla por proyección al centro de primera vista, NO región real todavía.

MSVC x86 build PASS; harness nativo20.012checks y proxy D3D9 HAL16Present PASS. Instalado con cliente cerrado; no se abrió juego ni reinició GS. Falta validación in-game. Controles raíz NIEBLA-1-PARCIAL/2-OPACA/3-APAGAR/4-CENTRAR.cmd. Guía NIEBLA-MAPA-PRUEBA.md. Log cliente NexusMapFog.log. Restore guardado en research/map-fog-native-v1/restore.py; manifiesto/backups/map-fog-native-v1-20261025-214418. .explora todavía independiente; ninguna sincronización gráfica con TOTAL/PARTIAL/CLEAR.

REA evidencia adicional: research/map-fog-analysis-20261025/rea-fog-implementation-evidence.json. Convenciones thiscall worldRET4/townRET8/drawRET44 verificadas en ensamblado. Mantener distinción entre envío de dibujo/log y validación visual. README técnico recoge implementación y pendientes.
