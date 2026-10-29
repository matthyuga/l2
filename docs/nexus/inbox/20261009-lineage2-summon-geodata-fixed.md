# Summon y Coliseo corregidos

Proyecto E:\l2-local, 2026-10-09. Usuario autoriza implementar tras diagnostico.

SummonAI core: no rechaza follow/attack por findPath=null si falta geodata de
alguno de los extremos. Con geodata permite camino directo valido antes de A*;
rechaza instancia diferente. Conserva chequeos reales normales, PathFinding=2.

Instalada geodata L2J 24_19 del Coliseo, SHA256
E64898F18E4D8691C83D3901BB4DDB8F9C9FACA95E7DFBCF7BC7741B6D1F4454.
Fuente L2JOrion GitHub revision98e351766c569504210a24d96a9f39262f19b397;
installer con revision/hash fijados, binario NO al repo. Elven21_19 intacta.
10 puestos antiguos y45350/45150 estaban en gradas/paredes; cambiados a
y45750/45900 en SoloArena.xml y SoloArenaGauntlet, piso verificado -3408.

Backup E:\l2-local\backups\summon-geodata-2026-10-09: core previo, fuentes
previas, geodata, compilacion, pruebas y logs. Fullbuild core preserva cambios
raciales locales actuales. Scripts/source/overlay sincronizados.

GEO_SMOKE PASS 19puestos suelo/ruta al centro, frontera norte elevada bloqueada,
Elven preservado. AI_SMOKE SUCCESS12/12 a19:25:49: Nightshade sigue dueno y
se acerca/ataca causando dano real, privada instancia300000. Primer intento
fallo dano por montage teleport Player headless sin onTeleported; montaje
corregido, NO cambios dano/atributos para hacerlo pasar. 335+108+4 checks PASS.
No auditoria de todas paredes/puertas ni validacion del summon de Hellkevin
en cliente. No deshabilita root/stun/UD legitimos. Stats/equipo/build intactos.

Servidor funcionando sin abrir cliente; DB/login preservados en reinicio seguro
sin L2 ni7777establecido. GameServer11384, panel7976 abierto sin navegador,
PIDs actualizados. Fuente/docs/installer en cloud-repo local; SIN commit/push.
Documento E:\l2-local\SUMMONS-Y-GEODATA-COLISEO.md.
