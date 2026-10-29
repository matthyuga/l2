# Amber: movimiento, control y altura

Proyecto `E:\l2-local`, sesión Amber, 09/10/2026.

Instalado en cliente activo `E:\l2\system-hud` y GameServer:
- LineageNpc.int: únicamente categoría BOW [5] de a_traderB_FHuman, ausente antes.
  Enlaza reposo, caminar, correr, tiro y preparación de lluvia hacia arriba.
- Mallas nuevas L2AmberNPCv5 y L2AmberArcherV2: MeshOrigin.Z=26,5 y
  RotOrigin.Yaw=49152 del Fighter usado para el rig. Malla/materiales/anim links
  se preservan. Corrige la causa encontrada de flotación en NPC y summon.
- npcgrp cambia solo filas 59001/59002; otras 6520 idénticas byte por byte.
- Menú `.amber`: atacar, seguir, detener, retirar. Atacar usa la IA nativa real.
  Mensaje explícito ante target inválido. Prototipo limitado a enemigos PvP.

45 checks PASS con los dos probes privados, que quedaron offline. Incluye ataque
real vía botón/bypass/SummonAI, seguir/detener y bloqueo durante lluvia. Core JAR
sin cambio. GameServer activo. Falta ver en L2 el resultado de movimientos,
agarre del arco y pies; no se afirmó verificación visual dentro del cliente.

Documentación: AMBER-CONTRATO-SUMMON.md; reporte reports/amber-contract-verification.json.
Respaldo y log: backups/amber-contract-2026-10-09/motion-fix.
Instalador: research/amber-l2/Install-AmberMotionFix.ps1.
Fuente/dist y overlay local sincronizados, sin commit/push ni assets binarios cloud.
Dos llamadas GroupAgite incompatibles se corrigieron para permitir compilación
global; ver nota separada de coordinación. No se cambió su lógica ni el roster.
