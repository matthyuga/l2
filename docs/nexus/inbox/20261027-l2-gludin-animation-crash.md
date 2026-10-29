# L2: Critical Error al volar por Gludin

27/10/2026. Proyecto E:\l2-local. Usuario solicitó REA. Captura16:09:09: General protection fault en UpdateAnimation <- AActor::Tick. Registros ubican Hellkevin en Gludin segundos antes. Sin dump actual ni dirección de excepción; los dumps encontrados son antiguos.

REA/Ghidra analizó Engine.dll real, identificó/decompiló AActor/APawn/USkeletalMeshInstance::UpdateAnimation. Sus tres cuerpos coinciden byte a byte entre system-hud, respaldo preHSL y system-clean. No hay cambio directo en esos rangos; eso no descarta efectos indirectos de módulos o recursos. No se estableció actor o asset causante y no se modificó el cliente.

Informe, hashes, logs y evidencias: E:\l2-local\research\gludin-animation-crash-20261027\DIAGNOSTICO.md . Pendiente respuesta sobre modo de vuelo (GM/wyvern/aeronave) para orientar reproducción. No confundir este cierre cliente con el fallo HtmlUtil del servidor ya recuperado.

Kevin confirmó wyvern. Se identificaron NPC12621 y malla LineageMonsters.wyvern_m00. Se revisaron ruta nativa de montaje, recursos locales y comparación de paquetes por perfil. Pendiente reproducción a pie frente a wyvern y captura de excepción actual; no se aplicó corrección especulativa ni se dio por culpable a HSL o al modelo.
