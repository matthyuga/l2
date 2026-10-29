# Prueba de apoyo nativo — 14/10/2026

Kevin confirmó que la corrección anterior no evita la caída inmediata y reportó critical al cerrar: General protection fault, FMallocWindows::Free / DeleteObject(60112) / DeleteGarbage(anghel_fog) / UObject::PurgeGarbage / UObject::StaticExit / appPreExit,13:41:19. No atribuir causalidad a anghel_fog ni declarar resuelto el critical. No se encontró log nuevo en system/system-hud.

Se instalaron dos actores adicionales que usan **sin modificar** el recurso original del cliente L2fortress_02_s.Fort02_medic_base. Situados bajo llegadas CT/T, escala0.5; superficies centrales7804.65 y8188.65, unos3.35u bajo el suelo visual original. Se usan como diagnóstico de colisión/registro en el cliente frente al modelo convertido. Son pequeñas plataformas locales; no sustituyen la navegación de toda la arena ni cubren túneles.

La geometría nativa de la base tiene660 triángulos de secciones con colisión. Se consultó la superficie central antes de colocarla. Se conservan todos los payloads anteriores del mapa fuera de myLevel; solo se añaden dos actores y sus referencias. Cifrado Ver121/CRC y copia instalada verificados. Respaldo E:/l2-local/backups/dust2-native-arrivals-20261014-134719. Manifest principal actualizado para rollback íntegro.

Se ajustó el handler en sus tres copias runtime/source/cloud: `.dust2 salir` acepta a visitantes con posición de regreso registrada aunque ya estén por debajo del rango Z de la arena. Recompilado y redefinido solo ese handler en GameServer21308, sin reiniciar ni modificar core. reload.txt acredita carga; no equivale a prueba ingame. La restricción de estar vivo y fuera de combate sigue aplicando. `.muelle` también permanece disponible para salir.

Kevin tiene pendiente la pregunta asíncrona: volver a abrir L2 y usar .dust2 para saber si queda apoyado sobre esta base nativa. **Todavía no está resuelta la causa de la caída ni validada la corrección.** La prueba anterior del servidor y los lectores offline no certifican física real. La conversión de licencia del primer intento permanece instalada; no tocar aeronave/muelle ni activar arena competitiva mientras siga fallando.
