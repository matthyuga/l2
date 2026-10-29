# Dust2 cámara: resultado V7 y prueba V8 preparada — 2026-10-14

Proyecto real E:\l2-local. Kevin confirmó que `.dust2 escalera2` sube completa. Cámara V7 falló: inspección de E:\l2\system-hud\Shot00079.bmp..Shot00081.bmp muestra exterior, reversos y terreno original por arriba/abajo. No declarar cerrado el problema de cámara.

Preparada V8 en research\dust2-camera-v8; NO instalada todavía. Cliente L2 PID4008 continúa abierto. Se preguntó por cierre mediante async. Instalar con python research\dust2-camera-v8\install.py solo después del cierre; script verifica cliente cerrado y hashes. 7 manifiestos previos coinciden con vivo. V8 cambia solo bBlockNonZeroExtentTraces en 4225 techos/juntas con envolvente de personaje libre; 440 excluidos por poca separación. 1286 límites laterales y todas las rampas/paredes físicas/payloads ajenos preservados. Perfil y geodata intactos. Basado en inspección estática de Engine.dll: cámara tiene una traza de extensión (0.1,0.1,5), desactivada en V7; no es causa única demostrada. No se modificó DLL ni proceso.

Prueba pendiente tras instalar: cámara desde `.dust2` y `.dust2 escalera2`, ambos tienen techo habilitado. La antigua coordenada de cámara141496,55320 está en grupo excluido y no sirve para esta comparación. No prometer que V8 cierre todos los huecos: primero verificar que este tipo de bloqueo afecta a la cámara real. Ver research\dust2-camera-v8\README.md y verification.json. Critical de salida sin causa confirmada.

Actualización 17:23: Kevin cerró L2 y V8 quedó instalada. Backup E:\l2-local\backups\dust2-camera-v8-20261014-172322. 8 manifiestos cotejados con archivos vivos. Cámara pendiente de prueba desde .dust2 y .dust2 escalera2; servidor no reiniciado.
