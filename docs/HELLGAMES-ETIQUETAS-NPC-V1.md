# Etiqueta HELLGAMES con partículas — prueba nativa V1

Instalada el 14/10/2026 en el cliente habitual `E:\l2\system-hud` y en el mundo personalizado del laboratorio.

## Cómo verla

Entrar con `2-JUGAR.cmd` y visitar el Coliseo. Junto a Thiago y Mirellas hay un NPC llamado HELLGAMES, con título Prueba visual. Su posición es 149140, 46700, -3400. La etiqueta dice HELLGAMES / EVENTO, con borde dorado y motas flotantes. Al hablar muestra instrucciones de la prueba.

Girar la cámara alrededor del NPC y probar distintas distancias. Revisar orientación del texto, proporción del cartel, altura respecto al nombre nativo, transparencia y partículas. La imagen se preparó con la orientación usada por los SpriteEmitters de cifras del laboratorio; su lectura correcta aún necesita comprobación en el cliente. Esta primera versión incluye sólo el estilo dorado de Evento, no el selector de estilos del navegador.

## Integración

- Paquete propio `HellgamesLabelsV1.u`: clase EventGold, dos texturas RGBA y dos SpriteEmitters relativos al NPC; una etiqueta persistente y hasta 16 motas. Orientación de sprite por defecto PTDU_None para mirar a la cámara.
- `npcgrp.dat`: añadido el display 59030, clonado de la apariencia nativa 30004, con un único deco_effect que referencia HellgamesLabelsV1.EventGold. Los 6.522 registros anteriores y el trailer permanecen idénticos byte a byte.
- NPC de servidor 902530, display 59030; Folk pasivo, sin evento jugable ni recompensas. Plantilla `data/stats/npcs/custom/hellgames_label_test.xml` y diálogo `data/html/default/902530.htm`.
- Spawn aislado `data/lab/world-spawns/HellgamesLabelTest.xml`, en la carpeta activa indicada por CustomWorldOnly. No se modifica World.xml ni los NPCs de servicio previos.

El servidor transmite el display del NPC; el cliente resuelve la etiqueta y anima las partículas. No se transmite una imagen por jugador o por fotograma. La etiqueta es fija de rol, no un nombre dinámico.

## Comprobaciones y límite

Compilación UCC correcta; lectura de propiedades nativas verifica clase, texturas y dos emisores relativos con ForcedMaxParticles. Descifrado/recifrado de npcgrp con roundtrip exacto y comparación de todos los registros existentes. XMLs validados contra sus XSD. UModel volvió a exportar la textura instalada: 1024×256, alpha 0..255. La falta de xDxTex en el compilador deja la textura sin compresión, pero no impide importarla ni leer sus píxeles.

El primer chequeo de runtime detectó que el spawn estaba en la carpeta clásica inactiva; se trasladó a la carpeta del mundo personalizado, se actualizó el manifiesto de restauración y se volvió a arrancar. Verificación posterior de sólo lectura: exactamente un NPC 902530 activo, display 59030, coordenadas correctas, sin combate y no autoatacable. No se alteró GameServer.jar ni se crearon cuentas o personajes. Reinicios realizados sin conexiones de jugadores.

**Pendiente:** revisión visual dentro de L2 y prueba de rendimiento con varios NPCs. Las comprobaciones de archivos y servidor no validan el dibujo del cliente.

## Respaldo y fuentes

Respaldo: `E:\l2-local\backups\hellgames-labels-v1-20261014-104807`. Restore.ps1 comprueba hashes y requiere cerrar L2; restaura npcgrp y retira únicamente los archivos nuevos. Reiniciar el servidor sin jugadores después de restaurar para retirar el spawn activo.

Fuentes y pruebas: `research/visual-effects/npc-labels/native-v1/`. Los scripts de build/install tienen guardas y no deben reejecutarse como actualizadores del cliente vigente. `installed.json` registra instalación y estado de comprobaciones; `runtime-verification.txt` verifica el NPC activo.
