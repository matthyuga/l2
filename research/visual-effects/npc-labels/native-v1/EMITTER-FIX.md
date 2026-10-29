# Emisores invisibles: correccion preparada

14/10/2026. El usuario llego al NPC y no vio el efecto. Inspeccion del Engine.u activo confirma que ParticleEmitter hereda TriggerDisabled=True, LevelOfWeather=2 y AlphaTest=True. El paquete compilado con defaults de UT2003 no incluia overrides de esos valores; la primera comprobacion no verificaba las propiedades heredadas.

Se preparo fixed/HellgamesLabelsV1.u con TriggerDisabled=False, Disabled=False, AlphaTest=False y LevelOfWeather=0 en ambos SpriteEmitters. Lectura nativa posterior verifica exactamente los cuatro valores de ambos emisores (fix-emitter-defaults.log). Esto corrige una causa identificada, pero el resultado visual requiere otra prueba jugando.

install-fix.ps1 requiere L2 cerrado, respalda el paquete anterior, verifica hashes y actualiza el manifiesto de restauracion completo para conservar la posibilidad de retirar toda la prueba. No cambia npcgrp ni el servidor. No ejecutar sobre un paquete modificado por otra sesion.

Correccion instalada despues de que el usuario cerro L2. Hash final fc0ea20229e4a32d3e214cd96974ddf382283072fe8e35544d248210e0d2d321; backup backups/hellgames-labels-emitter-fix-20261014-110408. GameServer sin reinicio. Pendiente comprobacion visual por el usuario.
