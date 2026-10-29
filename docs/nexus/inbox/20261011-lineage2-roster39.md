# Lineage II: veinte bots añadidos

Origen: sesión Codex en `E:\l2-local`, 11/10/2026.

Usuario aprobó veinte builds nuevas y pidió implementarlas, dejando su IA para
después. El roster pasa de 19 a 39, NPC 901119–901138 y Players `ArenaDarion`
hasta `ArenaBorin`. Principal + tres subs nivel80 en tercera; segunda acumulada
y tercera sólo activa. Equipo/joyas S +4, raza/origen fijo y dyes legales.
Darion, Valerian, Malrik, Lucien, Seraphine, Darius, Thalion, Elowen, Faelith,
Nerys, Draven, Nysera, Veyron, Zareth, Saevra, Rhogar, Mazhura, Urkan, Dagna,
Borin. Listado con nombres de segunda en `TREINTA-Y-NUEVE-BOTS.md`.

39/39 preparados y recargados; 20/20 nuevos verificados en SQL; stats NPC=Player
39/39; copias anteriores7/7. Selector117 válidos/6 inválidos; autoprueba de
spawns123 checks PASS, terminada y limpia. Runtime/source/overlay/panel local
sincronizados. Sin commit/push. Backup privado: `backups/roster-39-2026-10-11`.

Acceso: `.arena lista`, `.arena probar Darion`, `.arena probar 20`, secuencia39.
Nuevos NPC sólo ataque básico; sin rotaciones/summons/curas/control táctico aún.
Los grupos fijos de Giran, agite y sala Elven mantienen su composición.
Siguiente trabajo: diseñar/integrar IA para las veinte builds con los perfiles
persistentes existentes; no recrearlos ni sustituir sus recetas.
