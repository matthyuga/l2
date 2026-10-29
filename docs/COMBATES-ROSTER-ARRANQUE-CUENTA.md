# Combates bloqueados al arrancar y cambio de cuenta

10/10/2026. El usuario encontró «Espera la preparación completa del laboratorio» y «Espera el roster completo» después del reinicio.

El preparador no llegó a 19/19: ArenaMyrentha tenía clase activa 111, subclase 2, y principal 110. Su raza, origen racial, principal y las tres subclases eran correctos. El código rechazaba cualquier perfil que no se cargara con la principal activa, aunque terminar un combate en una subclase era un estado válido. El fallo dejaba READY=false y bloqueaba las modalidades que requieren los 19 perfiles.

La corrección valida primero la identidad del perfil técnico reservado. Si está activa una subclase existente y coherente con su clase cargada, selecciona su principal con la API normal. Luego continúa la verificación completa de las cuatro clases, equipo, buffs y estadísticas tras recarga. No recrea el personaje ni sobrescribe su receta.

El acceso solicitado se migra de la cuenta existente `solo` a `hellkevin`, cambiando también su contraseña. Se mantiene el mismo ID de Hellkevin, sus clases, equipo, clan y progreso. La operación actualiza accounts, accounts_ipauth, account_data, account_gsdata, account_premium y characters en una transacción; copia privada de las filas anteriores en backups/roster-startup-account-2026-10-10. El informe público y las bitácoras no incluyen la contraseña ni su hash.

La prueba debe confirmar la restauración de Myrentha y 19/19 perfiles, y ejecutar el ensayo 4vs4 existente en una instancia privada con pilotos técnicos. Después se reinicia en modo normal y se espera de nuevo la preparación completa. El cliente, Amber y GameServer.jar permanecen intactos.


Resultado: 19/19 perfiles preparados en ambos arranques; Myrentha recuperada desde sub2 y luego verificada de nuevo con sus cuatro clases. 4vs4 PASS con151 impactos,225 usos de habilidades y summons. ArenaSpawnVerification PASS con63 comprobaciones: los19 rivales bajo demanda, cancelacion, victoria, siguiente ronda, derrota y desconexion. Cuenta hellkevin y nuevo hash de contrasena verificados; mismo ID y datos de Hellkevin. Cliente y core sin cambios.

Arranque final: ensayo grupal desactivado; comprobacion de arena de una sola ejecucion terminada y sus probes retirados. El servidor queda libre para jugar. Los siguientes arranques con 2-JUGAR utilizan las banderas normales de Start-L2Local.ps1.
