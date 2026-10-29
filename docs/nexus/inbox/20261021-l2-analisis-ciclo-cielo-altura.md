# L2 — sistema nativo de cielo y ciclo diario

21/10/2026. Kevin pidió analizar el sistema antes de implementar sol/ciclo nuevos.

- Informe principal: `E:\l2-local\ANALISIS-CIELO-CICLO-Y-ALTURA.md`.
- Evidencias en `research\day-night-analysis`. Lectura estática; no se ejecutó el juego ni se alteraron cliente/servidor.
- Cliente habitual confirmado system-hud. Timeenv0..3 idénticos en system/system-hud; Engine.u difiere pero 13 ScriptText relevantes se corroboraron idénticos.
- El mapa real del muelle ya contiene NSun0, NMoon0, NMovableSunLight0 y SkyZoneInfo0. Sol separado: L2_Skies.FlareSet.Sun01.
- Engine.dll activo: pefile/Capstone confirman interpolación lineal de colores/escalas y cálculo trigonométrico de dirección solar según hora. ChangeEnv/CalcEnvDelta/GetEnvColor implementan cambio/mezcla de ambientes. No confundir esto con mezcla automática de panoramas nuevos.
- Servidor6x, ciclo4h reales, noche00–06. CharSelected manda hora; no se encontró envío efectivo de ClientSetTime. Overrides GM day/night/red visuales no cambian reloj.
- Altura: ValidatePosition ±20000 para Z reportada por jugador; particionado ±16000 no es clamp global; geodata compleja -16384..16376 paso8. Sol/cielo nativos alrededorZ24700, separados del espacio jugable. Máximo renderer/vuelo no medido.
- Pendiente validar jugando: sincronía continua, sombras solares reales, clima funcional y selección completa de perfiles. No prometer sombras modernas ni colores arbitrarios por paquete.
- REA Ghidra no abrió por detección runtime_missing; se documentó y se usó inspección estática ordinaria instalada, sin cambiar configuración ni instalar software.
