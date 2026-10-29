# 2026-10-09 - Selector de clases para .raza activo

Trabajo: E:\l2-local. Usuario pidió tomar raza/atributos de su principal o tres subclases y botones Confirmar/Cancelar/Aplicar.
RaceCustomization v2 activo tras cierre del cliente confirmado por usuario, listener7777 PID13276. Cambios sólo en scripts RaceCustomization y su verificación; sin recompilar core ni editar IA/Amber.
Selector slots0..3 propios; origen nativo del enum/root, no de aspecto actual. Mystic Muse=Elfo místico, Paladin=Humano guerrero, Phantom Summoner=Elfo oscuro místico, Overlord=Orco místico. Elegir no activa la clase; toggles independientes, origen aplicado es global del personaje. Comparación con build activa. Selector manual anterior sigue disponible.
Controles antes de tabla y textura Interlude L2UI_ch3.smallbutton2. Confirmar abre resumen, Aplicar requiere token vigente, Cancelar resetea selección sin aplicar. Restricciones de paz/GM y gratuidad se conservan.
Compilación PASS; motor RaceCustomizationVerification SUCCESS68 checks, RacialProfileVerification8; roster listo19/19 y verify-arena-roster SUCCESS19/19+copias7/7. Intento de roster antes de preparación completa dio discrepancia temporal Riven, resuelta al terminar readiness sin cambios de código.
Runtime/source-dist/cloud-overlay y docs sincronizados localmente, sin commit/push. Backup/evidencia E:\l2-local\backups\race-class-selector-2026-10-09. Manual E:\l2-local\PROBAR-PERSONALIZACION-RACIAL.md. Falta revisión visual en cliente por usuario.
