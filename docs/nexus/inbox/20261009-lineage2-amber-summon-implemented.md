# Amber: contrato y summon implementados

Proyecto real: E:\l2-local. Sesión Codex, 09/10/2026.

Usuario autorizó implementar la propuesta. NPC902500 del Coliseo ofrece contrato GM
gratuito; concede temporalmente Invocar19001, Fuego19002, Lluvia19003, Romper19004.
Servitor real902501/display59002, Infinity Bow6619 cosmético, Beast Soulshots6645.
Fuego15s +25%PAtk; lluvia carga3500ms inmóvil y libera movimiento al completarla;
centro fijo/radio200/tres pulsos500ms. Romper revoca habilidades y actor/acciones.
Persistencia en PlayerVariables; no cambia clase, equipo ni perfil racial.

37 checks PASS con dos Players técnicos propios en instancia privada. Probes
AmberOwnerProbe/AmberTargetProbe (ambercontracttest) quedaron offline. Evidencia:
backups/amber-contract-2026-10-09/verify-37-checks.log y
reports/amber-contract-verification.json. Core GameServer.jar conservado, incluida
la corrección de SummonAI/geodata de otra sesión. No se editó su IA ni el roster.

Recursos nuevos L2AmberArcher.ukx, L2AmberArcherMotion.ukx y AmberEffects.usk en
E:\l2\animations; AmberParticles.u y cuatro catálogos extendidos en system-hud.
Todas las filas previas se preservaron. Archivos originales de Amber v4/HUD intactos.
Usar **2-JUGAR.cmd**, hablar con Amber y firmar tras retirar Nightshade.

Pendiente revisión visual EN CLIENTE: las poses modificadas se verificaron en
Blender/UModel y los efectos compilan/se reexportan; no afirmar que el agarre,
disparador de animación, círculo o caída ya fueron vistos funcionar en L2.
Perfil system-amber antiguo no fue actualizado para estos skills. Balance inicial.

Servidor quedó iniciado sin pruebas opt-in (-Dlab.amber.verify=false), puerto7777;
DB/login permanecieron activos. Fuente/dist y overlay cloud sincronizados, sin
commit/push. Documento principal: E:\l2-local\AMBER-CONTRATO-SUMMON.md.
Instalador: research/amber-l2/Install-AmberContract.ps1, rechaza cambios desconocidos.
