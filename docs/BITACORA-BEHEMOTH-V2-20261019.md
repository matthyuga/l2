# Behemoth V2 y sala de ensayo · 2026-10-19

Continuación del prototipo de arnés y plataforma de dos ocupantes. Detalle, comandos, estado verificable y reversión en `research/mounts/behemoth-v2/README.md`.

Se prepararon rig con 98 huesos originales, nueve secuencias, ocupantes de referencia sentados/de pie, perfil de cliente separado y módulo experimental del servidor. Se incorporó revisión de animación al editor. El servidor pasó 15 comprobaciones con actores temporales; no hubo cuentas nuevas ni personajes persistentes. Editor y sala del visor pasaron sus verificaciones automáticas.

Nuevo acceso `27-SALA-ENSAYO-BEHEMOTH.cmd`: sala gris de 36 m con cuadrícula, movimiento, giro, límites y selector de animaciones, servida por un proceso independiente en 32302. Es una sala del visor, no un mapa L2 nativo. `26-PROBAR-BEHEMOTH-L2.cmd` abre el perfil nativo privado preparado.

No se confirmó la identidad de la sala gris usada antes en cámaras. Quedan pendientes sala nativa y revisión con dos clientes: Computer Use no conecta al servicio nativo de Windows (pipe error 2). No afirmar montaje/combate visual funcionando ni preparación para producción. Ver README para pendientes y riesgos concretos.

Academy y Hellgames no se modificaron. El editor previo en 32290 siguió abierto. El servidor L2 Lab quedó iniciado para pruebas y el módulo cargado; el smoke eliminó todos sus actores temporales.


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


## Conductor nativo preparado

Nueva ruta BehemothNativeRide activa con Player.mount y paquete Ride, categor?a STRIDER e ID propio59091. Se a?adi? alias Bone15 sobre Spine1 sin agregar huesos; el modelo conserva98. Se abandon? el control remoto para el conductor. Se retiran NPC de preparaci?n al montar; el personaje montado usa su movimiento normal.

12 pruebas con Player temporal PASS incluidas subida/bajada/muerte/desconexi?n, sin personajes persistentes; no validan cliente visual. Comandos .behemoth invocar / conducir / parar / bajar / guardar. Reabrir cliente26 para leer el socket nuevo. Segundo ocupante pendiente, no simularlo como montado. Gu?a vigente research/mounts/behemoth-v2/PRUEBA-CONDUCTOR-NATIVO.md. Config cold-start reemplaza BehemothTransport por BehemothNativeRide; m?dulo nativo activo en GS17176. No reinicio requerido en esta sesi?n.


## Prueba real: Ride mostraba un strider; correcci?n de la clase nativa

El usuario confirm? pose de jinete sobre el strider original, sin equipo Behemoth. Esto demuestra que activar Ride funcion?, pero no que seleccionara el modelo correcto. No declarar montaje Behemoth visualmente validado.

Inspecci?n adicional de Engine.dll: RiderEnter crea LineageMonster.strider; SetPawnResource separa al jinete humano mediante RidePawn y recorre la rama de recursos de jugador, sin reemplazar la malla del cuerpo montado con npcgrp59091. Por tanto el cambio de ID por s? solo no reemplaza su malla predeterminada. Evidencia set-pawn-resource-disassembly.txt.

Se prepar? LineageMonster-native-ride.u: conserva todos los exports salvo los defaults de strider. Agrega Mesh=BHMTransport.BehemothMesh, animaciones Behemoth y colisi?n54/63. No se cambia Engine.dll. Main E:/l2/system-hud/LineageMonster.u conserva SHA256f06ac53f7df24bd13d6e7a0d25d9e3ca4e4502af2437518e49d96a053987d7b6. Ver native-ride-class-patch.json y native-ride-defaults-verification.json.

Alcance deliberado: TODOS los striders montados en este perfil privado se ven como Behemoth. El cliente habitual, IDs del servidor y archivos principales no se reemplazan. El perfil privado queda reservado para ensayos de Behemoth; no usarlo para evaluar apariencia de un strider normal.

El archivo del perfil estaba bloqueado por L2.exe. Se solicit? cerrar el juego. Paquete preparado y validado; instalaci?n pendiente mientras siga abierto. El acceso26 ahora verifica e instala el paquete preparado antes de iniciar el cliente y explica el bloqueo si L2 sigue abierto. No reiniciar servidor. Segundo ocupante sigue pendiente.

Instalaci?n confirmada tras cierre del cliente por el usuario: LineageMonster.u privado coincide con el paquete preparado, con malla predeterminada Behemoth. Cliente principal intacto. Sigue pendiente la comprobaci?n visual dentro de L2.
