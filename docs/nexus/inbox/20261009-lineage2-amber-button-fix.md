# Amber: corregido botón de firmar

Usuario informó que Beast Soulshots decía que no tenía summon. El log mostró
`sent not handled RequestBypassToServer: [Quest AmberContract accept]`.
Hellkevin no había firmado: el menú enviaba un bypass Quest inexistente en este
servidor. El handler nativo de misiones usa Script; el apartado Amber ahora usa
la ruta compartida `voice .amber firmar` y `voice .amber romper`.

Firmar valida target NPC902500, distancia y GM, y llama al mismo servicio del
contrato. Test ampliado usa BypassHandler y VoiceCommand en lugar de llamar
directamente onEvent. 40 checks PASS, invocación y ruptura desde esos botones.
Evidencia E:\l2-local\backups\amber-contract-2026-10-09\verify-40-button-checks.log.
Probes offline, core conservado, source/cloud sincronizados. Se reinició tras
verificar cliente cerrado. Abrir 2-JUGAR, firmar con Amber y activar shots DESPUÉS
de que aparezca el summon. La reproducción visual sigue pendiente del cliente.
