# Critical Error volando por Gludin - 27/10/2026

## Hechos conservados

Kevin reporta cierre mientras volaba por Gludin. Captura: 2026.10.27 16:09:09, General protection fault; History: UpdateAnimation <- AActor::Tick <- TickAllActors <- ULevel::Tick <- (NetMode=0) <- TickLevel <- UGameEngine::Tick <- UpdateWorld <- MainLoop. La captura no contiene EIP, registros, nombre de actor, mesh ni secuencia.

El servidor registró descubrimiento de Gludin Village a las16:08:48 y Gludio Territory a las16:09:01 para Hellkevin objectId268473899. Es correlación de ubicación/tiempo, no prueba de que la niebla causara el fallo. Copias de logs del servidor, niebla y HSL conservadas en esta carpeta.

No se encontró un dump de este evento. Los cuatro L2.exe.*.dmp de AppData/Local/CrashDumps son del19 y23/10: no deben atribuirse al cierre del27/10. No había proceso L2 disponible en la comprobación posterior. No se instrumentó ni lanzó el cliente.

## REA: análisis estático del cliente real

Engine.dll: E:\l2\system-hud\engine.dll, x86 PE, SHA256 6b2598b0103dc16fc2e1a9202751bdd442f637bc4751b2a192b52bc52d049c91. Ghidra12.1.4, importación efímera de solo lectura.

Funciones exportadas encontradas:

- AActor::UpdateAnimation: 0x1030fd4e; salto relativo al cuerpo0x105258b0, 51 bytes.
- APawn::UpdateAnimation: 0x10302504; cuerpo0x1062fae0, 2003 bytes.
- USkeletalMeshInstance::UpdateAnimation: 0x10303c74; cuerpo0x106ba890, 1601 bytes.
- También existen UVertMeshInstance::UpdateAnimation y UMeshInstance::UpdateAnimation. El texto de la captura no selecciona inequívocamente una implementación.

El pseudocódigo de AActor delega desde el mesh a una instancia y a su actualización virtual. APawn añade sincronización de piezas/materiales y escalado de huesos. Esto delimita una ruta de animación, pero sin dirección de excepción ni actor vivo no demuestra qué puntero o recurso falló. Los tipos/variables del decompilador son reconstrucciones, no código fuente original.

Evidencias: ev_81cb0165280fee1541b12941554305489f44321a3934ee3d9c0ed5e9a5c7db6e (búsqueda); ev_7ae14fd7e69b7916aa6a3fce1ae61ef1e8a8e653c2593d40af4b9f1de07fd092 (actor); ev_56ef790616b34d284959d059aa8c018dbb8b329337e1cb7a7d77526bfd400d20 (pawn); ev_60a709ca8558ffef8a65fc4d6c037397779cbe669e88046d3bf8d9ae676b44ab (skeletal). JSON completos retenidos junto al informe.

## Comparación con copias anteriores

Se compararon los rangos reales de las tres funciones contra el respaldo anterior a HSL (backups/hair-hsl-ingame-v1-20261026-230921/1-engine.dll) y system-clean/engine.dll. Los tres cuerpos son idénticos byte por byte en las tres copias. Detalle: animation-code-comparison.json.

El Engine completo sí tiene modificaciones registradas: el hash coincide exactamente con el manifiesto HSL v1; sus dos entradas de hook son0x104872f0 y0x10486000, fuera de los tres rangos. La igualdad del código de animación descarta cambios directos en esos rangos comparados, pero NO descarta efectos indirectos de materiales, recursos, otros hooks o estado de actor. Tampoco prueba corrupción de mapa, fallo de wyvern, falta de RAM o problema de driver.

## Estado y siguiente paso

Diagnóstico parcial: fallo del cliente en la ruta de animación; actor/recurso causante aún desconocido. Es una ruta diferente del error de HtmlUtil del GameServer corregido previamente. No se aplicó un parche especulativo, no se cambiaron opciones gráficas ni archivos del cliente.

Se preguntó si volaba con comando GM, wyvern o aeronave/cámara. Con esa respuesta se puede seleccionar una reproducción concreta y comparar la misma zona a pie frente al modo de vuelo. Si se repite, capturar dirección de excepción, módulo y actor/mesh antes de culpar al escenario o retirar módulos. La reproducción y la captura de memoria aún no se realizaron.

## Confirmación del usuario: montado en wyvern

Kevin confirmó wyvern. La revisión adicional local identifica NPC12621 y malla LineageMonsters.wyvern_m00 (catálogo m0235), texturas LineageMonstersTex.wyvern_t00 y t01. AdminRide usa NPC12621 y Player.setMount aplica el tipo WYVERN, estado de vuelo y habilidad de aliento. Es la ruta de montura nativa, no un simple comando de vuelo del cuerpo humano.

Se compararon LineageMonster.u y LineageMonster.int en system-hud, system-clean y system-amber: hashes conservados en wyvern-package-comparison.json. El prototipo Behemoth revisado documenta su cambio de la clase strider únicamente en un perfil de ensayo privado, sin cambiar wyvern. No se deduce de esto que todo archivo de animación o estado vivo esté sano.

El código fuente disponible de HSL también sigue y retoca materiales de actores durante actualización de apariencia. Esto impide excluir efectos indirectos solo porque UpdateAnimation sea idéntico al original; tampoco demuestra que HSL sea el causante. No se modificó HSL ni se lo desactivó.

Prueba propuesta, aún sin ejecutar: misma ruta con el mismo personaje a pie y luego montado en wyvern, registrando si falla al montar, al despegar, durante vuelo sostenido o al entrar en una zona concreta. Mantener los mismos archivos y cambiar una sola condición. Si vuelve a ocurrir en vuelo, capturar excepción/actor antes de decidir un parche.

### Aclaración del contexto

Kevin indica que entró al juego para buscar las estatuas y sufrió el crítico mientras volaba normalmente en wyvern por Gludin, sin modo cámara ni una prueba especial. No describe el fallo como inmediatamente ligado a montar o despegar. No se midieron tiempo de vuelo, coordenadas exactas ni reproducibilidad. La intención de visitar las estatuas no demuestra que hubieran llegado a cargarse ni que causaran el cierre.

Con esta aclaración queda resuelto el modo de uso; no hace falta volver a preguntar por cámara o vuelo GM. Mantener abierta la identidad del actor en UpdateAnimation. No hay fundamento para cambiar modelos o animaciones concretos con la evidencia disponible.
