# Lineage II: Amber con asistencia IA — 10/10/2026

Ruta real E:\l2-local, disco portátil Seagate. Cliente E:\l2. Sesión Amber; usuario pidió autonomía después de ganar el TvT Hellsing contra Holly/Sacred. Se mantuvo core/client/VFX y pilotos de otras sesiones.

Implementados AmberAssist y controles .amber auto/manual. Default IA al invocar. Selecciona Players y summons cercanos según amenaza/cercanía, excluye aliados y respeta pausas de TvT. Foco de ataque manual prevalece; seguir/detener nativos o por voz desactivan asistencia. No cambia el target del jugador.

Skills automáticos conservan MP, shots y recargas. Lluvia: controles activos con tiempo suficiente (Anchor, Lightning Strike, Binding/Spark Cubic), UD/Vengeance y oportunidades de quietud/grupo. Según preferencia explícita del usuario: otros blancos menos protegidos para arco; root/parálisis primero para lluvia; UD si no hay control mejor; puede arriesgar un grupo con rendimiento estimado mucho mayor. Evalúa enemigos como centros para cubrir más área y su PDef/resistencia/movimiento. Es heurística, no garantía ni daño artificial.

104 checks PASS con cuatro probes reservados y un summon en instancia privada. Log: backups/amber-assist-2026-10-10/verification-104-checks.log. Registra AMBER_AI para analizar próximo TvT. Modo normal del servidor al entregar; no lanzar verificadores para jugar.

Scripts server/source/dist/cloud sincronizados, sin commit/push. Core SHA256 2e35d88f6050eb22619adf00ee0070494126ae0ed535dc33b0e4c1e18bc99349. Documentación actual AMBER-ASISTENCIA-IA.md y CONTINUIDAD-W10/16_AMBER_ASISTENCIA_IA_2026-10-10.md. La nota y documentación viajan en E:; Nexus K: solo mapa.

Pendiente: prueba real del usuario en otro TvT para ajustar selección y medir aporte; no se atribuye resultado de balance ni éxito visual a las pruebas del servidor.
