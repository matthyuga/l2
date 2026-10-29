# HELLGAMES: etiqueta nativa de NPC V1

Sesión L2, 14/10/2026. Ruta real E:\l2-local; cliente E:\l2\system-hud.

Usuario autorizó integrar al juego la etiqueta hacia la cámara y partículas. Instalado HellgamesLabelsV1.u y un registro nuevo de npcgrp (display 59030), preservando 6522 filas previas byte a byte. NPC pasivo 902530 HELLGAMES / Prueba visual, en Coliseo junto a Thiago y Mirellas: 149140,46700,-3400. Etiqueta dorada EVENTO + hasta16 motas, sin funcionalidad de evento. Spawn en data/lab/world-spawns por CustomWorldOnly; la primera ubicación clásica inactiva se corrigió.

Comprobados paquete/propiedades/textura/DAT/XSD y runtime: exactamente un NPC con ID/display/posición correctos, pasivo. Falta revisión gráfica real dentro de L2 y rendimiento. Servidor reiniciado sin jugadores; no se cambió GameServer.jar. Backup con Restore.ps1 protegido: backups/hellgames-labels-v1-20261014-104807.

Documento HELLGAMES-ETIQUETAS-NPC-V1.md; fuentes y pruebas research/visual-effects/npc-labels/native-v1. No reejecutar build/install históricos sobre el cliente actual. Siguiente acción: usuario entrar por 2-JUGAR.cmd y revisar etiqueta/partículas al girar y acercar cámara.

Prueba del usuario: NPC visible pero efecto no aparecia. Se detecto TriggerDisabled=True heredado de Engine ParticleEmitter, ausente del paquete UT2003. Corregido explicitamente en ambos emisores junto a Disabled=False, AlphaTest=False y LevelOfWeather=0. Lectura nativa PASS. Instalado con L2 cerrado y backup emitter-fix-20261014-110408; rollback principal actualizado. Pendiente volver a verlo dentro de L2. Sin reinicio GS.

Segunda captura real del usuario: sigue sin cartel/motas tras emitterfix. Preparada e instalada prueba de control al comprobar L2 cerrado: display59030 suma halo nativo LineageEffect.ra_boss_halo_a_ca junto al cartel; paquete personalizado con wrapper111, roundtrip exacto. Resto de filas identicas. Respaldo load-control y rollback original actualizado. Pendiente nueva revision visual; no afirmar causa definitiva ni solucion. Fuentes research/visual-effects/npc-labels/native-v1/load-control.

Control nativehalo/wrapper tampoco visible segun usuario. Nueva via preparada no instalada: HGLabelNpcV2.Npc clonado de athenas.u; PostSetPawnResource Spawn ahora apunta HellgamesLabelsV1.EventGold mediante cambio de constante bytecode misma longitud; vincula cuello y conserva limpieza. Clase/funciones lectura PASS, int clona trader, solo display59030 cambia class y retira deco. Falta cerrar L2/install/nueva revision. No confundir verificacion nativa con exito visual.

NPC hook V2 instalado tras confirmacion L2 cerrado. Catalogo instalado comprobado: display59030 class HGLabelNpcV2.Npc, deco0; paquetes nuevos/config copias exactas. Backup hellgames-label-npc-hook-v2-20261014-113254; rollback completo actualizado. Servidor sin reinicio. Pendiente resultado visual real.

Captura usuario confirma cartel visible tras hookV2, grande/alto/deformado. Solicita compacto/transparente, efectos despues. V3 preparada: sprite20x10, Z18, UniformSize/UseRegularSizeScaleFalse; textura512x256 fondoalpha48 borde130; motasdisabled. Lectura nativaPASS/roundtrip. Pendiente cierreL2/install/revisionvisual. No modificar server/npcgrp.

V3 instalada al comprobar L2 cerrado. Backup compact-v3 registrado en verification.json y rollback original actualizado. Servidor sin reinicio. Pendiente nueva captura ingame.
