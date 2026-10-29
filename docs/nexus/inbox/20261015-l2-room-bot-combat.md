# Salas L2: consumibles y habilidades de bots

Sesion salas,15/10/2026. Trabajo real E:/l2-local/research/pvp-bot-combat; README y installation.json documentan cambio/respaldo.

Corregida IA incompleta del roster siege: stock/uso nativo de MP/HP/CP y shots por grado, habilidades ofensivas segun mago/guerrero, curas y summons/TransferPain conocidos. Magos no pasan a autoataque fisico si falla el casteo. Evidencia de eventos reales y consumo en combat-verification.json/live-audit.txt. Cambio activo PID27412 y fuentes runtime/source/overlay sincronizadas. Sin cliente/core/animaciones ni mover Hellkevin.

Solo seis bots estaban activos en THREE_TEAMS al aplicar (grupos anteriores detenidos15:23, sala reiniciada15:24). No se iniciaron otras salas. Respetar retirada normal antes de cerrar: snapshot roster aun no persistente ante crash. Hay timeouts transitorios DB bajo carga pendientes de diagnostico si reaparecen; pool/telemetria intactos. Verificador mas reciente de la cadena esta en pvp-bot-combat/finalize.py (52archivos), los anteriores no incluyen esta etapa. No ejecutar agentes de despliegue fallidos ni volver a definir helper ya cargado.
