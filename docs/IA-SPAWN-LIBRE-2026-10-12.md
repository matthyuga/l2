# Invocacion manual de pilotos IA

`//ia mago` y `//ia fisico` (macros IA Mago / IA Fisico) invocan al piloto cerca del operador, en su misma instancia. Tambien siguen disponibles `.ia mago` y `.ia fisico`.

Ya no requieren suelo PvP del Coliseo, salir de combate ni desactivar invulnerabilidad GM. Invocar otra vez reemplaza el piloto propio anterior, incluyendo cambiar de clase. Otros jugadores presentes no cancelan la prueba.

Se mantienen los 20 segundos de preparacion, operador vivo y conectado, permisos GM, un piloto global y exclusion con el experimento `.arena`. Cambiar de instancia, desconectarse, morir o el limite de seis minutos termina la prueba. Las reglas nativas de combate y zonas de paz siguen vigentes.

El spawn y el retroceso del mago usan GeoEngine cerca de la posicion actual. Se conserva la restauracion y descarga del perfil reservado al terminar.

Aplicado al GameServer en caliente con redefinicion de metodos, sin reinicio. Runtime, source y overlay tienen contenido identico para el siguiente inicio normal.

Validacion: compilacion y ocho comprobaciones reales en una instancia privada fuera de PvP, con controlador en combate e invulnerable: spawn mago, cercania e instancia, permanencia tras tick, reemplazo por fisico y descarga correcta de ambos perfiles. Evidencia: `reports/ia-free-spawn-2026-10-12/verification.txt`. Respaldo: `backups/ia-free-spawn-2026-10-12/LabCombatPilots.java`.

La primera prueba detecto un error del propio probe: registrar AttackStance no marca por si solo `isInCombat()`. Se corrigio activando el estado de autoataque del controlador aislado; las ocho comprobaciones finales pasaron.
