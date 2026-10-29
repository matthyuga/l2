# Behemoth V2 · L2 Lab · 19 octubre 2026

**Estado actual: nueva prueba del conductor con montaje nativo preparada. Leer PRUEBA-CONDUCTOR-NATIVO.md. Segundo ocupante pendiente; validaci?n visual del cliente pendiente.**

## Abrir la sala gris

Ejecutar `E:\l2-local\27-SALA-ENSAYO-BEHEMOTH.cmd` o abrir:

http://127.0.0.1:32302/assets/exports/l2lab-behemoth-two-riders-animated/lab.html

Sala visual independiente de 36 × 36 metros, cuadrícula de un metro, paredes, anillo de giro de seis metros y marcas de distancia. W/S desplazan, A/D giran, espacio pausa; ratón orbita y acerca. Las paredes limitan el centro de la montura a ±14 metros. Volver al centro restablece posición y cámara. El navegador pierde el control de movimiento al perder el foco.

El selector permite caminar con dos personajes de referencia o revisar nueve secuencias originales del Behemoth sin ocupantes. Los personajes de referencia son modelos reales L2 en material blanco de estudio: conductor sentado y pasajero de pie. El arnés y la plataforma están vinculados al esqueleto original. Se conservan los 98 huesos y sus nombres. Las manos, estribos y ajustes para otras razas aún requieren refinamiento visual.

Esta sala es una simulación del visor, **no un mapa nativo de L2**. Su movimiento y sus límites no validan geodata, paquetes de red, colisión del cliente ni combate. No se identificó con certeza la sala gris usada en las antiguas pruebas de cámara. La recreación nativa y la comprobación visual con dos clientes siguen pendientes.

## Editor y archivos

Editor V2: http://127.0.0.1:32302/?project=BEHEMOTH-DOS-OCUPANTES-V2.json

Proyecto sin personajes, nueve secuencias: `BEHEMOTH-ANIMADO-V2.json`.

El servidor alternativo 32302 evita interrumpir el editor ya abierto en 32290. Los proyectos de prueba tienen su propio contexto de borrador. Los controles de animación aparecen al seleccionar el modelo. La selección y reproducción de un clip son controles de revisión; no se guardan como una línea de tiempo del proyecto.

Fuente editable: `Behemoth-Two-Riders.blend`. Generadores: `build_animated.py`, `merge_animations.py`, `build_native.py`. Assets animados: `research/model-catalog/exports/l2lab-behemoth-two-riders-animated/`.

## Prototipo nativo preparado, pendiente de validación visual

`26-PROBAR-BEHEMOTH-L2.cmd` abre el perfil privado `client-lab/system/L2.exe`; requiere servidor local iniciado y acceso habitual del usuario. No crea cuentas ni inicia sesión automáticamente. El perfil original del cliente permanece aparte.

Paquete `BHMTransport.u`: malla, ocho materiales y clase experimental. Usa la animación original `LineageMonsters3.antaras_ex_a_anim`. Registro de visualización 59091; NPC experimental del servidor 902791. No reemplaza el strider ni la montura original. El perfil privado conserva las 6523 filas previas de npcgrp más una fila nueva; roundtrip DAT verificado. Las carpetas de recursos inmutables están enlazadas mediante hard links: no editar esos recursos desde el perfil privado.

Comandos de prueba en L2, solo tras revisar el perfil:

- GM: `.behemoth invocar`, `.behemoth conducir`.
- Conductor: `.behemoth permitir Nombre`.
- Pasajero autorizado cerca y con la montura seleccionada: `.behemoth subir`.
- `.behemoth parar`, `.behemoth bajar`, `.behemoth estado`.
- Con ambos abajo: `.behemoth guardar`.
- `.behemoth recuperar` restaura un retorno pendiente cuando corresponda.

La invocación actual está restringida al mundo principal. **Todavía no hay un comando para ingresar en una sala nativa privada.** El conductor dirige; el segundo personaje conserva ataques normales y no puede conducir. No se han verificado aún el montaje visual, la orientación de los asientos, los ataques/skills desde otro cliente ni todas las razas. El cliente puede necesitar correcciones antes de funcionar: compilar y extraer el paquete no prueba su ejecución.

Computer Use no pudo conectarse al servicio nativo de Windows (`native pipe unavailable`, error 2), incluso tras reintentar y reiniciar la sesión de herramientas. Por ello no se certifica prueba visual ni combate con dos clientes.

## Verificaciones realizadas

- `server-smoke.json`: 15 comprobaciones PASS con actores temporales reales del servidor; no se crearon personajes persistentes ni cuentas. Incluye ocupación, autorización, sincronización, conducción, validación de posición, roles de combate, bajada, muerte y desconexión. No son dos clientes de red.
- `lab-verification.json`: ocho comprobaciones PASS; carga de los tres conjuntos con esqueleto, pausa, límites, giro, reinicio, nueve clips, cambios de huesos y ausencia de errores JavaScript. `deathwait` es deliberadamente estático.
- `editor-v2-verification.json`: siete comprobaciones PASS, incluidas reproducción, pausa y guardado/reapertura de proyecto; 18220 triángulos renderizados.
- `native-roundtrip-final.log`: UModel extrae la malla final y sus ocho texturas, resolviendo la animación original. El paquete instalado en el perfil privado tiene el mismo SHA256 que el generado.
- Pruebas de reglas de asientos y compilación Java completadas. El primer smoke falló por colocar al pasajero de prueba demasiado lejos de una segunda invocación; se corrigió la posición de la fixture y la repetición pasó sin relajar el alcance del producto.

## Cambios del servidor y reversión

Solo L2 Lab: `server/libs/GameServer.jar` contiene los hooks de movimiento/validación y `BehemothSeatSync`; el resto de entradas conserva su contenido. Manifiesto: `core-patch-manifest.json`. El módulo está en `server/game/data/scripts/custom/BehemothTransport/`, registrado en `Custom/WorldContent.ini`. Se cargó también en el servidor activo sin redefinir clases existentes. No se invocan NPC automáticamente en uso normal.

Copia anterior del JAR y configuración: `backups/behemoth-v2-20261019/`. Para revertir, cerrar ordenadamente el servidor, revisar que no hubo cambios posteriores al backup, retirar el módulo de CustomScriptFolders y restaurar selectivamente los hooks o el JAR anterior. No sobrescribir un JAR posterior con el backup sin comparar. Los fuentes anteriores de tres clases están en `core-source-before/`. El perfil privado y la sala del visor son independientes del cliente habitual.

Pendiente: sala nativa aislada, revisión con dos clientes reales, alineación y animaciones de ocupantes por raza, combate/red/geodata, revisión de muerte y reconexión desde clientes, y refinamiento de rig. No considerar V2 lista para producción.


## Correcci?n del cierre al invocar ? 19 octubre 2026

El cliente mostr? `Assertion failed: index < 5` en `User::GetNpcTexName` al invocar. El prototipo anterior ten?a ocho slots de textura. Se agruparon los seis materiales del equipo en un atlas, manteniendo las dos texturas del cuerpo: tres slots en total e ?ndices 0..2. Se ajustaron UVs y materiales de las caras/cu?as sin cambiar posiciones, pesos ni esqueleto.

Nuevo paquete instalado ?nicamente en client-lab/system, junto al npcgrp corregido. Los 6523 registros originales se conservan; DAT encode/decode exacto. UModel extrae 98 huesos y tres materiales; las tres texturas extra?das son id?nticas p?xel a p?xel al origen. Evidencia: texture-limit-fix.json, native-roundtrip-3mat.log. Scripts: pack_native_materials.py e install_3mat_fix.py; build_native.py y prepare_lab.py actualizados. Los informes anteriores de ocho materiales corresponden al prototipo que produjo el cierre y quedan superados por esta correcci?n.

Reabrir el cliente privado con 26-PROBAR-BEHEMOTH-L2.cmd para que lea ambos archivos nuevos; no requiere reiniciar el servidor. Si la montura sigue invocada puede mostrarse al entrar. La ejecuci?n visual dentro de L2 sigue pendiente hasta repetir la prueba.


## Estado vigente tras prueba real: montaje deshabilitado

19 octubre 2026: el usuario confirm? NPC elevado y control del Behemoth sin personaje visualmente montado. El cliente ya carga los tres materiales, pero la funci?n de montar fall?: no considerar usables los dos asientos.

Se retiraron los NPC experimentales y se bloquearon subir/conducir en el handler activo. Al recuperar no quedaban miembros; al comprobar luego Hellkevin estaba offline. El archivo de retornos no conten?a pendientes. En fuente tambi?n se rechaza montar personajes reales antes de modificar cualquier estado; las fixtures labControlled conservan su ruta de QA.

Origen nativo comprobado con UModel: original Z=57 y Yaw=49152; el prototipo omit?a ambos (Z=0, Yaw=0). Se a?adi? MESH ORIGIN Z=57 YAW=192 al compilador (192 se convierte a 49152). El dump final coincide exactamente en MeshOrigin, MeshScale y RotOrigin. Colisi?n original del NPC29069: radio63/altura54, frente a los anteriores42/120. Corregida en fuente y mediante adaptador de comando en el m?dulo vivo.

El DAT privado usa temporalmente la clase original LineageMonster3.antaras_ex_a y la malla BHMTransport.BehemothMesh para aislar la revisi?n visual. La clase experimental de uni?n a huesos queda fuera del registro activo. No afirmar que la uni?n del jugador al esqueleto funciona. El servidor aplicaba estado de asiento y redirig?a movimientos sin comprobar el montaje visual: ese comportamiento queda bloqueado hasta implementar y validar un mecanismo de montaje compatible.

Pr?xima prueba manual: reabrir cliente26, entrar y usar solo .behemoth invocar para comprobar contacto con suelo y orientaci?n. No requiere reinicio de servidor en esta sesi?n: hay adaptador visual activo. Tras reinicio, fuentes compiladas usan los mismos valores y mantienen bloqueo. Pendiente prueba de suelo in-game y redise?o/validaci?n del montaje real. Evidencia grounding-safety-fix.json y corrected-origin-dump.txt.


## Segunda prueba real: segu?a elevado; correcci?n de inicializaci?n

El usuario volvi? a confirmar separaci?n del suelo. Inspecci?n en vivo: Hellkevin (83190,148920,-3455), geoZ=-3455, seated=false, movementDisabled=false. NPC (83049,148950,-3495), geoZ=-3495, colisi?n54/radio63. El NPC no ten?a Z por encima de su propia geodata. Esto no prueba la colocaci?n del modelo cliente.

El adaptador anterior modificaba dimensiones DESPU?S de summon/spawnMe: el m?dulo vivo segu?a creando primero con altura120. Un NpcInfo posterior no demuestra que SetSpawnResource recalcule el origen del Pawn existente. Se corrigi? el c?digo activo recargando ?nicamente custom.BehemothTransport.BehemothTransport mediante Instrumentation.redefineClasses; ning?n core fue redefinido. Estructura de clases conservada. Ahora el constructor NpcTemplate recibe radio63/altura54 ANTES del primer spawnMe. El servidor fr?o usa ese mismo fuente.

ReloadBehemothModule intent? reconstruir cliente-side los NPC existentes, pero en ese momento el mapa owned ya estaba vac?o (el usuario hab?a salido). El smoke V3 us? actores temporales, confirm? los valores iniciales y pas?16 checks; elimin? sus actores al finalizar. No son clientes reales y no certifica que se haya eliminado la flotaci?n. Evidencias: live-height-inspection.txt, module-reload.txt, server-smoke.json. Pr?xima verificaci?n visual debe distinguir altura de geodata y altura de dibujo; no seguir ajustando Z al azar. Subir/conducir siguen bloqueados.


## Prueba real: Ride mostraba un strider; correcci?n de la clase nativa

El usuario confirm? pose de jinete sobre el strider original, sin equipo Behemoth. Esto demuestra que activar Ride funcion?, pero no que seleccionara el modelo correcto. No declarar montaje Behemoth visualmente validado.

Inspecci?n adicional de Engine.dll: RiderEnter crea LineageMonster.strider; SetPawnResource separa al jinete humano mediante RidePawn y recorre la rama de recursos de jugador, sin reemplazar la malla del cuerpo montado con npcgrp59091. Por tanto el cambio de ID por s? solo no reemplaza su malla predeterminada. Evidencia set-pawn-resource-disassembly.txt.

Se prepar? LineageMonster-native-ride.u: conserva todos los exports salvo los defaults de strider. Agrega Mesh=BHMTransport.BehemothMesh, animaciones Behemoth y colisi?n54/63. No se cambia Engine.dll. Main E:/l2/system-hud/LineageMonster.u conserva SHA256f06ac53f7df24bd13d6e7a0d25d9e3ca4e4502af2437518e49d96a053987d7b6. Ver native-ride-class-patch.json y native-ride-defaults-verification.json.

Alcance deliberado: TODOS los striders montados en este perfil privado se ven como Behemoth. El cliente habitual, IDs del servidor y archivos principales no se reemplazan. El perfil privado queda reservado para ensayos de Behemoth; no usarlo para evaluar apariencia de un strider normal.

El archivo del perfil estaba bloqueado por L2.exe. Se solicit? cerrar el juego. Paquete preparado y validado; instalaci?n pendiente mientras siga abierto. El acceso26 ahora verifica e instala el paquete preparado antes de iniciar el cliente y explica el bloqueo si L2 sigue abierto. No reiniciar servidor. Segundo ocupante sigue pendiente.


## 20 octubre 2026: conductor oculto y animaci?n que no para

El usuario confirm? Behemoth equipado controlable, pero el jinete desaparece/se fusiona y el modelo sigue corriendo con pisadas al detenerse. No considerar validada la apariencia del conductor ni el reposo.

Causa de attachment confirmada por Engine.dll: AActor::AttachToBone (0x1052e3e0) llama MatchRefBone (0x1052e420). No resuelve el alias de socket a?adido anteriormente. Bone15 ten?a que ser un hueso real. Se export? un hueso real como hijo de Bip01 Spine1, con origen de referencia(0,-6.75,98), mediante el addon PSK para usar las convenciones nativas correctas. Se mantienen los98 huesos anteriores y se a?ade uno:99. Se conservan puntos, pesos y registros anteriores salvo el contador de hijos de Spine1. Se quit? el alias. Evidencia native-seat-idle-disassembly.txt.

La selecci?n de reposo/marcha usa arrays de8 nombres por CurWeaponType. El parche anterior solo defin?a ?ndice0. El nuevo paquete define los8 slots para WaitAnimName/AtkWaitAnimName/WalkAnimName/RunAnimName/DeathAnimName/DeathWaitAnimName:48 entradas. El reposo apunta a atkwait y carrera a run. Esto corrige tablas faltantes; el resultado sonoro/visual final requiere cliente real. Snapshot runtime capturado cuando Hellkevin YA HAB?A BAJADO: moving=false,mounted=false,mountId0,guardfalse. No usar ese snapshot para afirmar que se comprob? la detenci?n mientras estaba montado.

Verificaciones PASS: UModel extrae99 huesos, Bone15 real con padre Spine1; geometr?a/pesos preservados;48 entradas serializadas y decodificadas; Blender importa el roundtrip99 con PSA98 y comprueba que Bone15 sigue exactamente al torso en run y atkwait. Archivos real-seat-idle-verification.json, seat-pose-verification.json. No son prueba del cliente L2.

Paquetes preparados BHMTransport.u y LineageMonster-native-ride.u; instalaci?n pendiente mientras L2 siga abierto. Se pidi? al usuario cerrar el juego. Open-NativeBehemoth.ps1 ahora verifica y copia AMBOS paquetes antes de abrir, o con -InstallOnly para instalar sin ejecutar la interfaz. Protege contra actualizaci?n parcial con el juego abierto. Acceso26 mantiene esa ruta. Cliente principal intacto. Segundo ocupante pendiente.


## Postura y parada al llegar ? 20 octubre 2026

Nueva captura del usuario: jinete ya visible pero mal orientado; Behemoth sigue corriendo al llegar. Se extrajo strider_m00 original y su Bone15: quaternionWXYZ aproximadamente(0.7071069,0,0,-0.7071066), un giro de90grados respecto a la orientaci?n deseada que hab?amos usado. El exportador PSK no conserv? ese giro en el registro nuevo; la prueba del roundtrip detect? la discrepancia.

Correcci?n final: SeatBoneNativeRecord.bin se construye desde la jerarqu?a PSK REAL del Behemoth, calculando directamente posici?n y quaternion locales respecto a Spine1 con las convenciones de conjugaci?n nativas; orientaci?n mundial del Bone15 original del strider y posici?n nueva(0,-6.75,98). Los98 registros/pesos/posiciones previos permanecen intactos salvo el contador de hijos. Tras UCC y UModel, Blender reimporta y verifica dot abs de quaternion1.0 respecto al strider, posici?n de asiento y seguimiento del torso en carrera y reposo. Evidencia seat-orientation-reference.json y seat-pose-verification.json. Esto supera la correcci?n anterior basada ?nicamente en un hueso visible.

Llegada: nuevo helper NativeRideMotion sigue cambios moving/posici?n por jinete. Emite StopMove est?ndar a self y observadores al pasar a reposo, incluso si un recorrido corto termin? entre polls. No escribe coordenadas, no manda Ride otra vez, no interrumpe movimiento activo ni repite paquetes durante reposo. Al montar inicializa la parada despu?s de Ride. Limpia su registro al bajar. No se a?adieron campos al m?dulo vivo; helper definido en el mismo classloader y redefinidos solo m?todos de custom.BehemothNativeRide.BehemothNativeRide.

16 checks backend PASS con actores temporales: incluye inicio de movimiento, ausencia de parada prematura, paquete de llegada y ausencia de repetici?n en idle. Archivo native-ride-smoke.json y arrival-fix-install.txt. No son clientes de red y no confirman que cesaran las pisadas en el juego. El snapshot pedido durante investigaci?n encontr? a Hellkevin ya offline; no hay observaci?n directa del estado montado detenido en esa captura.

Instalaci?n de los dos paquetes privados completada con juego cerrado mediante Open-NativeBehemoth.ps1 -InstallOnly; hashes exactos y cliente principal intacto. El servidor17176 ya ejecuta la correcci?n de llegada, sin reinicio. Reabrir acceso26 y probar postura y llegada antes de declarar corregidos los dos s?ntomas. Segundo ocupante sigue pendiente.


## Reposo: causa localizada confirmada ? 20 octubre 2026

El usuario confirm? postura correcta, pero contin?a carrera en el lugar tras llegar; aclar? que falta pasar a idle. El StopMove adicional NO resolvi? ese s?ntoma en cliente real. No presentar la prueba de emisi?n de paquete como validaci?n de animaci?n.

Se descifr? copia de E:/l2/system-hud/LineageMonster.int (Ver111/XOR0xAC). La secci?n[strider] conten?a WaitAnimName[0]=wait y WalkAnimName[0]=run. Estas propiedades son localized y el archivo.int sobrescribe las modificaciones de defaults en el.u. La PSA real de Behemoth no tiene secuencia wait; s? atkwait. Esto explica la solicitud de una secuencia inexistente al detenerse y la continuaci?n de la ?ltima animaci?n.

Preparado LineageMonster-native-ride.int: la secci?n strider referencia atkwait para reposo/espera, Walk para caminar y run para correr, con8slots por estado. Todas las secuencias existen en PSA. El resto de secciones se conserva byte a byte; recifrado Ver111 exacto, cliente principal sin cambios. Reporte native-ride-int-fix.json. Script patch_private_ride_int.py. No se toc? la postura ya confirmada ni la malla.

Acceso26/Open-NativeBehemoth.ps1 incorpora instalaci?n y verificaci?n del.int privado, con backup. En el momento de preparaci?n L2pid7704 segu?a abierto; se solicit? cerrarlo para instalar y volver a cargar localizaci?n. Instalaci?n del.int y confirmaci?n visual del reposo pendientes. Segundo ocupante pendiente.
