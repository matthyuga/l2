# Agite grupal en implementacion — sesion principal

Usuario autoriza tres equipos de4, ganador permanece, primero en3puntos.
Esta sesion implementa SOLO modulo nuevo custom/GroupAgite y tests/docs propios.
No tocar Amber, core, LabCombatPilots, personaje Hellkevin racial ni clientes.
Observados cambios concurrentes en dos llamadas calculateDistance2D del modulo
nuevo; preservados porque son correcciones compatibles de compilacion.
Para evitar colisiones, dejar GroupAgite a esta sesion mientras termina.
No reiniciar GameServer desde otra sesion durante autoprueba grupal.

Clanes se crearan via API del motor al ejecutar .agite preparar con Hellkevin;
no SQL offline sobre el personaje, no nombres/clanes ajenos sobrescritos.
Pruebas sinteticas NO crean los clanes ni cargan a Hellkevin real.

Avance: modulo v1.1 compilado,291checks de politica PASS y12suelo/NSWE PASS.
Fuente/runtime/overlay sincronizados; docs AGITE-GRUPAL-4VS4.md.
Se corrigieron formaciones demasiado exteriores que tocaban estructura elevada.
Pendiente prueba live -Dlab.agite.smoke=true y posterior arranque normal.
Se consulto al usuario via pregunta asincrona para liberar GameServer unos
minutos porque otra sesion reinicio concurrentemente10772->8844.
No reiniciar mientras no se coordine. Listener8844 cargaba revision anterior:
no invitar al usuario a iniciar .agite hasta cargar v1.1 validada.

Usuario confirmo dejar GameServer libre para probar. Inicio autoprueba con
-Dlab.agite.smoke=true, sin cliente ni7777establecido. No reiniciar ni tocar
GroupAgite hasta cerrar la prueba; DB/login preservados, core/Amber intactos.

Autoprueba completada: GROUP_SMOKE PASS hits=188 casts=245 summon=true,
SQL run1 SMOKE_PASS finalizado, dropped=0,113 consumos de potas.
Los19 Arena offline tras limpieza y clan_data sigue0: no se crearon clanes.
Se corrigio loader para cuentas reservadas telemetryarena1/2/3 (antes solo2).
Log guardado en backups/group-agite-2026-10-09/smoke-pass.log.
Arranque normal posterior iniciado, sin -Dlab.agite.smoke=true.
Esperando roster completo y nueva verificacion19/19 antes de entregar.

Entrega lista 09/10/2026 21:16: GameServer listener PID23000, modulo v1.1,
arranque NORMAL sin smoke. Roster listo y verificador PASS19/19+copias7/7.
Core hash AB6DC1C692B98FB489F3D5BC8B5C3323C0DADCCF7BFCF89B63BA7E5DA5A5AA38
intacto; no cliente/Amber editados. Liberada ventana de pruebas del servidor.
Usuario puede entrar al suelo PvP de Coly, sin party/combate/invul GM,
.agite preparar (crea clanes), .agite iniciar. .agite cancelar limpia evento.
Ordenes cubrir/asalto/senuelo/seguir, puntuacion primero3, ganador permanece.
Falta ensayo manual de clanes/resurrecciones y eficacia tactica con Hellkevin.
No commit ni push. Docs AGITE-GRUPAL-4VS4.md con evidencia y limites.
