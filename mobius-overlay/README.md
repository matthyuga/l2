# Overlay de L2J Mobius Interlude

Esta carpeta conserva solamente los archivos modificados o creados por el proyecto.
La referencia local usada para producirla fue el commit `d47756357` de
`https://gitlab.com/MobiusDevelopment/L2J_Mobius.git`.

El contenido se copia sobre la raíz de un checkout compatible de Mobius. Por
ejemplo, `mobius-overlay/L2J_Mobius_CT_0_Interlude/...` debe terminar como
`source/L2J_Mobius_CT_0_Interlude/...`.

Incluye, entre otros cambios:

- Build Lab y comandos administrativos;
- persistencia racial al cambiar de clase/Sub;
- acumulación y resolución determinista de masteries;
- plantel y telemetría automatizados;
- arena local con Ares, Nyx y Atlas;
- límites de buffs y reglas de skills trabajadas por el proyecto;
- ajustes de fake players, NPCs, spawns y visualización.

No incluye `GameServer.jar`, clases compiladas ni la distribución completa.
