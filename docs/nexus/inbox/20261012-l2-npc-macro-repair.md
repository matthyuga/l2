# L2: NPC y macros reparados

- Ruta: `E:\l2-local`. Aplicado en caliente sin desconectar a Hellkevin.
- SevenSigns desactivado dejaba mapas de sellos vacíos; todos los diálogos NPC
  consultaban getSealOwner y lanzaban NPE. Consultas seguras y constructor neutral;
  no se reactiva el contenido clásico. Diálogos de Thiago/Mirellas verificados.
- Hellkevin no tenía chatBan de servidor. Aviso compatible con antispam del cliente.
  Dos macros tenían `.amenaza macro` (creador) en vez de selección. Tres macros
  migrados conservando IDs a `//amenaza`; IA Mago/IA Fisico creados con aliases GM
  `//ia mago` y `//ia fisico`. `//ia macros` los instala sin duplicados.
- Persistencia: Windows bloquea el JAR en uso. SevenSigns ya reparado en memoria;
  clase pendiente bajo `server\pending-core-patches\20261012-lab-service-repair`.
  Start-L2Local aplica pendientes automáticamente antes de iniciar un GameServer
  nuevo, sin tocar el servidor en marcha. Sintaxis y aplicación offline comprobadas.
- Docs: `REPARACION-NPC-Y-MACROS-2026-10-12.md`; evidencia SUCCESS en
  `reports\lab-service-repair-2026-10-12\repair.txt`.
- Fuentes/scripts/config/launcher espejados en cloud-repo. No commit/push.
