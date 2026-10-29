# L2 niebla: corrección al abrir otras interfaces — 25/10/2026

Kevin confirma V2 pero ve mapa a través al abrir stickers/clan/inventario. REA/Ghidra confirmó GetFinalAlpha RVA21590:255 es sentinel que hereda alpha del dispositivo(+74), reducida a mitad con flag+70. Evidencia exportada en research/map-fog-giran-v2/rea-alpha-fix-evidence.json.

Trabajo real research/map-fog-alpha-v3: PaintFog guarda esos campos, usa flag0/alpha255 solo mientras dibuja y los restaura en __finally.20396 checks nativos PASS con matriz foco/opacidad y excepción; HAL16Present PASS. Sin cambios de assets/INI/servidor. README e installation.json indican si está instalado y respaldo. Pendiente confirmación visual del usuario abriendo varias interfaces; no presentar harness como prueba in-game.
