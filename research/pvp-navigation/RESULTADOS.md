# Navegacion y utilidades de bots ?15/10/2026

Activo en GameServer3064. Se mantuvieron las salas, su reloj, parties y la posicion de Hellkevin. No se modificaron animaciones, cliente o core.

## Causas

El controlador intentaba acercarse350unidades por direccion local; sus alternativas no conservaban una ruta completa. Penalizar la diferencia de altura al elegir enemigo no resolvia escaleras. Ademas la invocacion se elegia por clase principal, ignorando habilidades efectivamente aprendidas por otras subclases de los builds hibridos.

## Cambio instalado

RoomRoutePlanner valida la ruta nativa completa hasta el destino. Si falla, busca sobre geodata en3dimensiones con pasos16,max45000expansiones y400ms de presupuesto por busqueda. Cada tramo debe aprobar canMoveToTarget nativo; limites de mapa y cambios verticales locales64. Los cambios acumulados de altura de una escalera estan permitidos. Compresion conserva solo tramos transitables. RoomRouteNetwork permite conectar mediante sectores de spawn verificados cuando una busqueda directa agota sus limites.

RoomNavigator conserva la lista de puntos y sigue la ruta con movimiento nativo. Dos trabajos de planificacion como maximo, fuera del monitor del lobby; pendientes no teletransportan ni mueven actores desde el worker. Solo se capturan coordenadas/mapa/instancia en esos trabajos. Memoria temporal de objetivos fallidos12s; detecta ausencia de progreso7s y replanifica despues de obstrucciones. Eleccion favorece objetivos transitables y conserva compromiso durante un trayecto(20s), en lugar de cambiar por cada nuevo spawn. Si no hay objetivos elegibles puede dirigirse a un sector para salir del atasco. No hay garantia de resolver todas las celdas de geodata o todas las multitudes.

Las invocaciones ahora consideran habilidades aprendidas y permitidas de subclases:familias gato/unicornio/sombra con preferencia de combate donde existe, incluyendo Kai/Merrow/Soulless; pantera/golem cuando procede. No se agregan skills. Se conserva una invocacion nativa, materiales/MP/reutilizacion/condiciones del juego. Cubics aprendidos,hasta2y sujeto a la condicion nativa de dominio. TransferPain cuando esta aprendido.

Utilidades por condicion y habilidad conocida:SpiritBarrier frente a caster,Guts/AngelicIcon al estar herido,ArcaneDisruption contra un caster lanzando,Entangle contra un enemigo moviendose,Fear al estar herido y cerca,Anchor ySurrender elemental apropiado. Siguen las defensas/curas/stuns previos. Debuffs no se fuerzan; las areas hostiles siguen excluidas. No se completo aun el uso de habilidades activas propias del servitor ni invocaciones sobre cadaver.

## Pruebas

- connected-routes.txt:12/12direcciones entre4sectores de Elven con ruta no vacia. El caso3->0 requirio puente por otro sector. No implica conectividad de todas las posiciones del mapa.
- native-walk.txt/status:dos personajes reservados en instancia vacia, uno del sector bajo al alto y otro del alto al bajo. Llegaron caminando en31y33segundos. Hubo un rechazo/recalculo en cada recorrido y continuaron. No se teletransportaron despues de la colocacion inicial. Finalmente retirados, inventarios restaurados e instancia destruida(native-walk-cleanup.txt).
- live-navigation-audit.txt:tres muestras durante40segundos en el encuentro FREE real, que ya estaba en Primeval cuando se inicio el diagnostico.10bots;ultima muestra6summons de4tipos(Boxer theUnicorn,Kat theCat,Shadow,Kai theCat),cubics presentes y rutas en uso. Ejecuciones nativas de139Guts,1092Fear,1170Anchor,102Entangle,1386ArcaneDisruption,Surrender1071/1074/1083 ycubics10/22/67/1279. Contadores antiguos de combate coexisten con los nuevos; no atribuir todos los casts al parche. Ejecucion no certifica que el debuff haya acertado ni su ventaja de balance.
- startup-check compila todas las fuentes instaladas de ElvenPvpRoom. installation-audit.json verifica76hashes de la cadena.

Los primeros intentos del fixture no son resultados validos:archivo conBOM rompio compilacion y el primer attach no encontro un helper; luego falto cargar RoomRouteNetwork y la prueba quedo sin rutas. Se retiro el fixture por finally y se corrigio el loader antes del ensayo valido. Evidencia fallida en discarded-fixture-loader; no hubo cambio de controlador productivo durante esos intentos.

## Operacion

12fuentes sincronizadas(runtime/source/overlay):PvpTacticalEngine y3helpers de navegacion. Backup yhashes en installation.json. Solo los helpers de produccion se instalan; NativeNavigationTrial y agentes quedan en research. .salas bots cerebro clasico permite volver a la logica anterior conservando infraestructura de salas. Rollback completo:retirar bots normalmente, detener GameServer, ejecutar restore.py y arrancar por lanzador normal. No ejecutar de nuevo agentes que definen clases ya cargadas.

## Limites

La prueba fisica de escaleras se hizo en instancia aislada; el combate observado fue Primeval. No se certifica que toda ubicacion de Elven tenga salida, que nunca haya un atasco ni que esta version sea un sistema de estrategia humana completo. Las rutas tienen presupuesto para proteger el servidor; un fracaso temporal puede significar presupuesto agotado. No se midio capacidad de cuatro salas llenas ni se repitio el benchmark de dano anterior despues de ampliar pets/utilidades. Persisten los limites de restauracion del roster ante crash.
