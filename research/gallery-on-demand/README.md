# Galería de Giran y bots bajo demanda — 14/10/2026

Petición de Kevin: ocultar los bots de Giran y mostrarlos con una macro solo para ver sets, evitando carga al entrar. La captura mostraba además la preparación automática de 39 perfiles de combate.

- EquipmentShowcase.xml queda disabled en runtime/source/cloud; conserva sus 157 entradas y todas las plantillas.
- Al iniciar no aparece ningún maniquí. `.galeria` muestra 51 sets de armadura y viaja a Giran. `.galeria alternar` o macro nativa `//galeria alternar` muestra/oculta los 51, sin teletransporte. `.galeria ocultar` elimina solamente los NPC 62000..62156 y detiene sus respawns. `.galeria todos` permite exhibición completa opcional; `.galeria estado` y `.galeria macro` disponibles.
- Macro **Galeria** se instala automáticamente al iniciar sesión GM, sin duplicarla ni reemplazar macros existentes. Si hay 48 macros, se informa al jugador para que libere una o use el comando.
- NormalNpcRoster deja de preparar 39 perfiles automáticamente. También se difieren los 7 pilotos auxiliares RealHumanPilots. `.roster preparar` los prepara secuencialmente y luego prepara el roster; `.roster estado` informa su estado. No se borraron personajes ni builds. Los sistemas de combate que requieren el roster necesitan esa preparación manual por reinicio.
- Wait-L2LabReady.ps1 reconoce el marcador ROSTER_MANUAL_READY y no espera por los 39 bots. El lanzador sigue esperando a que Start-L2Local confirme que el servidor escucha.

Respaldo previo: E:/l2-local/backups/gallery-on-demand-20261014-153217. Java compilado contra las librerías reales. Probe final en GameServer9536 comprobó 0 al iniciar, preparación de roster y 7 pilotos diferida, comandos registrados, permiso GM maestro para el alias de macro y dos ciclos de 51 -> 0 sin armas ni duplicados. Macro de login pendiente de observación con el cliente; no se fabricó un personaje persistente de prueba. La primera prueba detectó que doSpawn() respeta stopRespawn y devolvía null; se corrigió usando doSpawn(false), sobrecarga que crea una instancia sin habilitar respawn, y pasó la segunda prueba. verification.txt conserva resultado final.

install.py y defer_pilots.py son registros de la instalación inicial: no reejecutarlos sobre los archivos actualizados. No se cambiaron el mapa, los equipos del personaje ni los sistemas de aeronave por este trabajo. Los cambios posteriores de Dust2 están documentados en ../dust2-fit-v3.
