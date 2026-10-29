# Paneles de clan de prueba — 10/10/2026

Dentro del juego: `.clanlab` abre inicio con dos botones. `.clannivel` abre niveles; `.clanskills` abre habilidades. Solo Hellkevin GM y lider de su propio clan. No requiere target y no selecciona clanes ajenos.

Niveles: ascenso directo hasta8, sin rebajar, con resumen y Aplicar/Cancelar. No aprende skills automaticamente. Prueba gratuita sin consumir adena, objetos, SP ni reputacion; condiciones habituales de poblacion/quests son omitidas para el laboratorio. Los maestros de clan normales conservan sus reglas.

Skills: catalogo instalado22habilidades, filtros por nivel5/6/7/8 y Todas, paginacion, Actualizar, detalle con icono/efecto/rango minimo, nivel aprendido/maximo. Aprender siguiente nivel normal, con Aplicar/Cancelar. No puede saltarse rangos, aprender skills futuras, superar maximo ni otorgar habilidades de residencia/subunidad. Pasivas modifican stats automaticamente; la elegibilidad social del miembro se respeta. Una skill aprendida por el clan no necesariamente beneficia a todos sus integrantes. Reputacion negativa desactiva efectos segun reglas nativas.

Los cambios son persistentes al aplicarlos. Se usan Clan.changeLevel y Clan.addNewSkill con verificacionDB; refresca rango social, pasivas, skills y estado de miembros conectados. Una confirmacion vence2minutos y se cancela al navegar. Revalida clan/lider/nivel/skill al aplicar y bloquea cambios durante muerte, combate/casteo/ataque/eventos/Olimpiadas/disolucion. No fija el GM para personajes nuevos; el acceso queda limitado al laboratorio.

Instalacion: dos archivos nuevos en server/game/data/scripts/custom/ClanLab. No se modifico GameServer.jar ni el cliente. Sin NPC nuevo ni cambios de apariencia. Tu Hellsing sigue nivel5 sin skills hasta que uses Aplicar; Holly y Sacred tambien sin cambios.

Verificacion: 342 checks PASS en motor real con AmberOwnerProbe offline y clan descartable negativo, no Hellsing. Ascenso4a8, secuencia completa22skills, persistencia y recarga, efectos segun rango, aumentoHP real, rechazos de datos invalidos/stale/niveles futuros, HTML paginado dentro del limite y rutas voice. SnapshotDB de clanes/skills/12miembros/probe identico antes/despues; fixture borrado. No se confirmo visualmente el menu dentro del cliente. Roster19/19,6crests, hashescore/cliente conservados.

Fuentes, script de instalacion, snapshot y prueba: research/clan-lab. Backup: backups/clan-lab-2026-10-10. Verificador opt-in lab.clanlab.verify=true one-shot completado, no prueba en curso. Arranque habitual no activa esa propiedad. Fuentes source/dist y cloud-repo sincronizadas sin commit/push.
