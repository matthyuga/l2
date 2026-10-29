# Dust2: escaleras V4 — 14/10/2026

Kevin confirmó que en V3 ya funcionan puertas y apoyo de los pies, pero quedan escalones bloqueados por todo el mapa. Envió captura de una escalera de dos peldaños frente a un arco. V3 queda validado para puertas/suelo, no para todas las escaleras. Critical de salida anterior sigue sin causa confirmada; esta revisión no lo resuelve ni lo atribuye a un recurso concreto.

## Diagnóstico y cambio

La prueba anterior muestreaba solamente subidas que ya tenían NSWE abierto, así que no detectaba escalones legítimos descartados por el generador. Se auditaron todas las subidas cerradas con retorno abierto y geometría real del BSP: 591 candidatos de8..48u. Se comprobaron muestras a lo largo del paso, ancho21u y alturas4/24/48/68 sobre el piso superior. Se admitieron442 pasos de altura real<=32u:407 con subida de geodata32,19 de24 y16 de16. Se descartaron138 demasiado altos y11 obstruidos por geometría. No se subieron los límites generales del GeoEngine ni se alteraron las alturas de geodata: solamente bits de dirección dentro de Dust2.

La primera implementación de las426 transiciones altas pasó422: cuatro celdas tenían dos direcciones nuevas y una actualización pisaba el bit anterior. Se corrigió acumulando OR sobre el valor actual;426/426 pasó. Luego se incorporaron16 transiciones bajas válidas que el detector inicial, limitado a >16u, no había incluido. Prueba final: **442/442 PASS**, sin fallos (`stairs-repair-server.txt`). El GeoEngine admite estas alturas con su límite existente40; la física del cliente aún necesita confirmación de Kevin.

El soporte anterior solo cubría la componente alcanzable con subidas<=16. Abrir pasos sin extenderlo habría permitido llegar a lugares sin suelo nativo. V4 reemplaza conjuntamente los pisos/paredes V3 y amplía la cobertura a31.234 capas (862 más).1.855 pisos nativos y1.286 paredes, siempre deco01.Box02. Se comprueba que cada nueva arista accesible desde CT tenga apoyo en su destino. Los candidatos restantes fuera de la componente CT no se declaran zonas caminables del recorrido conectado.

Los pisos conservan las alturas visuales de V3; escala1.0, disposición y UV quedan iguales. No se modificaron los37 modelos visibles ni HGDust2Arena.usx. Nuevos actores HGDust2V4Floor/HGDust2V4Wall; se desactivaron y retiraron de myLevel las colisiones V3.9.737 payloads ajenos a esta revisión se comprobaron byte por byte, incluidos muelle/aeronave. Los exports históricos permanecen en el paquete; no reejecutar instaladores viejos.

## Verificación e instalación

- Pisos:31.234 centros cubiertos,9.275 pruebas geométricas de rayo,40 inicios apoyados.
- Paredes:3.980 bordes cubiertos;120.415 pasos abiertos dirigidos verificados, sin conflictos de paredes de otro piso.
- Cuerpo radio10.5/alto70:27.711 centros conectados y40 inicios CT/T conectados. Geometría, no ejecución de física del cliente.
- GameServer9536 recargó región24_19 por API nativa, sin reiniciar ni desconectar usuarios. L2 estaba cerrado al reemplazar el mapa. Prueba final442 subidas PASS y smoke previo:192 subidas,40 inicios, paredes, capas, zonas, CT/T/regreso, muelle/nave/Coliseo conservados.
- Posición guardada de Hellkevin139334,56447,8072 heading40411 leída como referencia. No se certifica que sea la posición exacta de la captura: la lectura viva no encontró personaje conectado.
- Backup combinado **E:/l2-local/backups/dust2-stairs-v4-20261014-160116**. El par de rollback contiene mapa V3 y geodata V3 anterior a todas las reparaciones de esta sesión (07fe6604...), aunque la geodata temporal al instalar ya llevaba la primera reparación de426 pasos. `pre_install_sha256` registra ese estado temporal. También se conserva intermediate-426-steps.l2j. Respaldo de geodata original y manifiestos: E:/l2-local/backups/dust2-stairs-20261014-155816.
- Manifiestos principal, V2, V3 y V4 sincronizados y cotejados contra archivos instalados. Sin commit/push. Galería bajo demanda y bots sin cambios.

Scripts de esta sesión son registros de preparación/instalación, no instaladores idempotentes. `prepare.py` parte del V3; no ejecutarlo sobre V4. `finish_stairs.py` integra las16 reparaciones adicionales y tampoco debe reejecutarse. `../dust2-fit-v3/repair_stairs.py` admite un archivo de geodata de entrada; se usó el respaldo anterior para crear la reparación completa sin acumular parches sobre datos ya modificados. La geodata no se copia a espejos source/cloud porque el archivo vivo es el único utilizado por el perfil local; código y assets de servidor no cambiaron.

## Pendiente

Kevin debe abrir de nuevo L2, usar `.dust2` y verificar los escalones de la captura y otros recorridos. Pregunta async enviada. No declarar todas las escaleras resueltas hasta esa prueba. Si el mismo peldaño persiste, capturar posición viva mientras esté parado frente a él para distinguir bloqueo del cliente de NSWE/geometría. Critical al cerrar sigue separado y pendiente.
