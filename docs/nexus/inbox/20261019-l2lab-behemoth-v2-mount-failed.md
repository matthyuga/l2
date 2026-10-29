# Behemoth: montaje fall? en cliente real; no reactivar sin validaci?n


## Estado vigente tras prueba real: montaje deshabilitado

19 octubre 2026: el usuario confirm? NPC elevado y control del Behemoth sin personaje visualmente montado. El cliente ya carga los tres materiales, pero la funci?n de montar fall?: no considerar usables los dos asientos.

Se retiraron los NPC experimentales y se bloquearon subir/conducir en el handler activo. Al recuperar no quedaban miembros; al comprobar luego Hellkevin estaba offline. El archivo de retornos no conten?a pendientes. En fuente tambi?n se rechaza montar personajes reales antes de modificar cualquier estado; las fixtures labControlled conservan su ruta de QA.

Origen nativo comprobado con UModel: original Z=57 y Yaw=49152; el prototipo omit?a ambos (Z=0, Yaw=0). Se a?adi? MESH ORIGIN Z=57 YAW=192 al compilador (192 se convierte a 49152). El dump final coincide exactamente en MeshOrigin, MeshScale y RotOrigin. Colisi?n original del NPC29069: radio63/altura54, frente a los anteriores42/120. Corregida en fuente y mediante adaptador de comando en el m?dulo vivo.

El DAT privado usa temporalmente la clase original LineageMonster3.antaras_ex_a y la malla BHMTransport.BehemothMesh para aislar la revisi?n visual. La clase experimental de uni?n a huesos queda fuera del registro activo. No afirmar que la uni?n del jugador al esqueleto funciona. El servidor aplicaba estado de asiento y redirig?a movimientos sin comprobar el montaje visual: ese comportamiento queda bloqueado hasta implementar y validar un mecanismo de montaje compatible.

Pr?xima prueba manual: reabrir cliente26, entrar y usar solo .behemoth invocar para comprobar contacto con suelo y orientaci?n. No requiere reinicio de servidor en esta sesi?n: hay adaptador visual activo. Tras reinicio, fuentes compiladas usan los mismos valores y mantienen bloqueo. Pendiente prueba de suelo in-game y redise?o/validaci?n del montaje real. Evidencia grounding-safety-fix.json y corrected-origin-dump.txt.
