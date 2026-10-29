# Amber L2: revision de materiales v4

Proyecto real: `E:\l2-local\research\amber-l2`.

El usuario mostro v3 dentro de L2 y confirmo mejora de forma. La ropa y el pelo estaban demasiado oscuros frente a la cara: v3 solo daba iluminacion propia al cuerpo. V4 aplica SelfIllumination a ambos atlas para conservar los colores toon originales.

Instalado `E:\l2\animations\L2AmberNPCv4.ukx`; reutiliza `L2AmberMotionv3.ukx`. Solo se actualizo el npcgrp del perfil system-amber, display 59001 / NPC 902500. Acceso `E:\l2-local\13-PROBAR-AMBER.cmd`.

Verificado: malla y pesos exportados byte a byte iguales a v3, paquete de animaciones sin cambios, pixeles RGBA intactos, un solo LOD completo, shaders con profundidad y alpha 128. Informes `reports/validation.json` y `reports/v4-native-validation.json`.

El usuario luego mostro v4 dentro de L2 y aprobo el aspecto: "esta buena ahora". Conservar v4 como base visual aprobada. La captura fija confirma apariencia y color, pero no todas las animaciones, combate ni rendimiento. Registro en `reports/user-visual-acceptance.json`. Proximos pasos propuestos: encaje en L2 (altura, pies, etiquetas), movimiento y arco, luego definir uso NPC/companera/apariencia jugable. Rollback del catalogo con `Restore-AmberV3.ps1`.

Integracion posterior en el acceso habitual: el usuario veia un conejo al entrar por 2-JUGAR.cmd porque system-hud conservaba los catalogos originales. Se verificaron contra la base original y se instalaron solo npcgrp.dat y NpcName-e.dat con la fila de Amber v4. HUD estatico intacto; 6519 filas originales preservadas y descifrado instalado comprobado. El launcher sigue usando system-hud y comparte animations. Script research/amber-l2/Install-AmberMain.ps1; informe reports/main-client-installation.json con ruta de backup. Pendiente reiniciar L2 y confirmar visualmente especificamente por 2-JUGAR.cmd.
