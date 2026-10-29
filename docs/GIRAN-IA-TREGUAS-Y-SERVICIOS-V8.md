# Giran: amenazas, treguas y servicios en el trono

11/10/2026. Instalado y validado: **1439 comprobaciones nativas PASS**; GameServer listo para jugar.

La IA anterior enviaba al líder directamente al artefacto durante conquista, antes de evaluar enemigos. Los compañeros también abandonaban un combate si el capitán superaba la distancia de formación. Esto permitía matar pilotos que solo corrían hacia su destino.

- Cada piloto identifica defensores Player/summons y guardias cercanos, con visión y reglas PvP nativas. Prioriza conquistadores rivales, agresores del líder o de la party, defensores y blancos debilitados. Los NPC de servicios y neutrales no son objetivos.
- Los líderes pelean contra amenazas inmediatas antes de llegar al artefacto. Esperan a la escolta si sigue combatiendo cerca. Una vez despejado el sector vuelven a Seal of Ruler. Un casteo ya iniciado sigue su comportamiento nativo; no se corta por decisiones propias de movimiento.
- La escolta conserva un combate local aunque el capitán se haya adelantado. El límite con el capitán pasa de1200 a3000 para combate válido; siguen los límites locales de objetivo1400 y persecución1500/1600 desde adquisición.
- El líder mide supervivientes, HP/MP y presión defensora alrededor de su escuadrón. Si la presión es desfavorable, dos escuadrones atacantes cercanos pueden acordar una tregua bilateral de20segundos. Se renueva mientras persiste la presión.
- La tregua detiene ataques dirigidos de los bots y summons entre esos clanes; evita también lanzar habilidades ofensivas de área cerca de sus socios. Ambos siguen pegando a defensores. Al iniciar conquista, traicionar el acuerdo o vencer el plazo dejan de respetarla; conquista/traición impiden renegociarla durante15segundos. No cambia alianzas, clanes, parties ni legalidad PvP. No convierte a rivales en aliados de los comandos de Hellkevin ni da inmunidad frente a daño incidental.
- `.giran` muestra la intención táctica y los clanes con tregua. Sigue siendo una competición por el castillo, con cooperación temporal para atravesar una defensa peligrosa.
- Mirellas(50010), vendedor, y Thiago(50008), buffer, tienen instancias adicionales a los lados de la sala del trono. Usan sus menús, artículos y buffs originales, incluidos los de summons. Permanecen en el Coliseo también y reaparecen al iniciar el servidor.

Se conservan V6/V7, geodata y estadísticas. La nueva IA no otorga daño, defensa, curación ni recursos artificiales adicionales. Usa habilidades, consumibles, movimiento y reutilización nativos.

Pruebas nativas PASS: daño real de los16atacantes incluidos los4líderes; escoltas que pelean a más de1200 del capitán; tregua bilateral/respeto/expiración real20s/traición/captura; líder espera y retoma conquista; navegación y menús de servicios; regresión de puertas/campamentos/revive/buffs/Amber/recorridoV6. Fixtures aislados sin Hellkevin, sin terminar conquista. Balance del siege completo requiere jugarlo.

Stage `research/giran-tactics-v8`; respaldo `backups/giran-tactics-v8-2026-10-11`. No reejecutar instaladores históricos.

Persistencia PASS: Hellkevin/inventario, clanes/skills/reputación, propietario/fecha de Giran y guardias conservados; cuatro rivales registrados y19 pilotos offline nivel80. Core, geodata, órdenes/alianzas y guardianes V7 sin cambios. Runtime/source/cloud sincronizados, sin commit ni push.
