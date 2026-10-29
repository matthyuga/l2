# Prueba de conductor nativo · 19 octubre 2026

Estado actual: preparada para prueba manual en el cliente. El segundo ocupante todavía NO está implementado en esta ruta. La revisión visual dentro de L2 sigue pendiente.

## Cómo probar

1. Cerrar y reabrir el cliente privado con `26-PROBAR-BEHEMOTH-L2.cmd`: la malla incorpora un socket nuevo y el cliente necesita volver a leer el paquete. El servidor activo ya tiene el módulo nuevo; no requiere reinicio.
2. Entrar en L2 Lab con un personaje GM. Buscar suelo plano, quedar de pie, fuera de combate, sin summon ni otra montura.
3. `.behemoth invocar`: aparece el Behemoth de preparación.
4. Acercarse y usar `.behemoth conducir`: se elimina aquel NPC y el personaje entra en la montura nativa. Debe verse sentado. Clic en el suelo mueve al personaje montado; no es control remoto de otro NPC.
5. `.behemoth parar` detiene; `.behemoth bajar` restaura el personaje normal. `.behemoth guardar` también baja y elimina cualquier NPC de preparación.
6. Si el dibujo del personaje no coincide con el asiento, bajar y registrar una captura lateral; no considerar esa alineación validada por los tests de servidor.

El comando nativo de montar desarma las armas y el escudo según el comportamiento estándar de L2; pueden requerir equiparse otra vez al bajar. No consume comida. La apariencia de los striders montados se sustituye por el Behemoth ?nicamente dentro del perfil privado de pruebas; el cliente habitual y los IDs originales del servidor permanecen intactos.

## Cambios

Nueva implementación `server/game/data/scripts/custom/BehemothNativeRide/BehemothNativeRide.java`, activada con el mismo comando `.behemoth`. Usa `Player.mount(59091,0,false)` y el paquete estándar `Ride`, tipo STRIDER. No asigna `BehemothSeatSync` ni cambia las coordenadas del jugador al asiento cada 200 ms. El movimiento normal del jugador sigue autorizado.

Al arrancar registra una plantilla NPC propia con ID59091, radio63/altura54, y agrega ese ID al conjunto STRIDER de CategoryData. Comprueba colisión de ID antes de registrar. No reemplaza una plantilla existente ni modifica IDs12526/12527/12528. El registro se reconstruye al reiniciar desde el módulo; no requiere cambios en el enum MountType ni otra compilación del core.

Cliente privado: npcgrp59091 conserva la malla `BHMTransport.BehemothMesh` y tres materiales. `BHMTransport.u` añade un socket/alias `Bone15` unido a `Bip01 Spine1`, conservando98 huesos y la animación original. UModel confirma el alias y los parámetros originales MeshOriginZ57/Yaw49152. El offset/rotación del alias está en `native-seat-socket.json`; la alineación de la pose por raza requiere observación en el cliente.

Evidencia nativa: Engine.dll SHA256508974c711f207402719e92737e211a2f029c95c2f68fc0e1c31fcbb9dbb232d; `UGameEngine::OnRide` (0x10488330) llama `APawn::RiderEnter` (0x106290e0). La ruta tipo1 crea `LineageMonster.strider`, usa el ID del paquete para el recurso y llama AttachToBone con el nombre literal `Bone15`. Archivo `native-ride-disassembly.txt`. REA Ghidra no completó analyze_function y se detuvo; esta evidencia procede de la lectura local PE/exportaciones y desensamblado Capstone, no de un decompilado completado por REA. No se parcheó Engine.dll.

## Validación y límites

`native-ride-smoke.json`:12 comprobaciones PASS con Player temporal real, sin cuenta ni personaje persistente. Verifica estado montado, tipo1/ID1059091 de Ride, movimiento libre, eliminación del NPC de preparación, colisión, velocidad, bajada, muerte, desconexión y handler activo. **No son clientes reales y no prueban la alineación visual ni la animación observada.**

La prueba del conductor requiere el cliente privado actualizado. Las animaciones de movimiento usan el mecanismo nativo: su resultado concreto debe observarse. El pasajero de pie y su combate siguen pendientes; `.behemoth subir` y `permitir` lo indican expresamente, sin asignar un asiento ficticio.

WorldContent.ini utiliza `BehemothNativeRide` en lugar de `BehemothTransport` para los próximos arranques. La sesión activa cargó el módulo nuevo, retiró los transportes antiguos y reemplazó el handler. Los listeners del módulo anterior permanecen en memoria hasta el reinicio, con sus mapas vacíos; no controlan a los nuevos ocupantes. El core BehemothSeatSync anterior queda inactivo porque el nuevo módulo no registra asientos en él.

Para retirar la prueba: bajar/guardar los Behemoth, cerrar el servidor ordenadamente y quitar BehemothNativeRide de CustomScriptFolders. Reiniciar deja sin el registro dinámico59091 ni la categoría añadida. Mantener el cliente privado separado. El historial de pruebas remotas anterior está superado por esta implementación para el conductor.


## Prueba real: Ride mostraba un strider; correcci?n de la clase nativa

El usuario confirm? pose de jinete sobre el strider original, sin equipo Behemoth. Esto demuestra que activar Ride funcion?, pero no que seleccionara el modelo correcto. No declarar montaje Behemoth visualmente validado.

Inspecci?n adicional de Engine.dll: RiderEnter crea LineageMonster.strider; SetPawnResource separa al jinete humano mediante RidePawn y recorre la rama de recursos de jugador, sin reemplazar la malla del cuerpo montado con npcgrp59091. Por tanto el cambio de ID por s? solo no reemplaza su malla predeterminada. Evidencia set-pawn-resource-disassembly.txt.

Se prepar? LineageMonster-native-ride.u: conserva todos los exports salvo los defaults de strider. Agrega Mesh=BHMTransport.BehemothMesh, animaciones Behemoth y colisi?n54/63. No se cambia Engine.dll. Main E:/l2/system-hud/LineageMonster.u conserva SHA256f06ac53f7df24bd13d6e7a0d25d9e3ca4e4502af2437518e49d96a053987d7b6. Ver native-ride-class-patch.json y native-ride-defaults-verification.json.

Alcance deliberado: TODOS los striders montados en este perfil privado se ven como Behemoth. El cliente habitual, IDs del servidor y archivos principales no se reemplazan. El perfil privado queda reservado para ensayos de Behemoth; no usarlo para evaluar apariencia de un strider normal.

El archivo del perfil estaba bloqueado por L2.exe. Se solicit? cerrar el juego. Paquete preparado y validado; instalaci?n pendiente mientras siga abierto. El acceso26 ahora verifica e instala el paquete preparado antes de iniciar el cliente y explica el bloqueo si L2 sigue abierto. No reiniciar servidor. Segundo ocupante sigue pendiente.

Instalaci?n confirmada tras cierre del cliente por el usuario: LineageMonster.u privado coincide con el paquete preparado, con malla predeterminada Behemoth. Cliente principal intacto. Sigue pendiente la comprobaci?n visual dentro de L2.


## 20 octubre 2026: conductor oculto y animaci?n que no para

El usuario confirm? Behemoth equipado controlable, pero el jinete desaparece/se fusiona y el modelo sigue corriendo con pisadas al detenerse. No considerar validada la apariencia del conductor ni el reposo.

Causa de attachment confirmada por Engine.dll: AActor::AttachToBone (0x1052e3e0) llama MatchRefBone (0x1052e420). No resuelve el alias de socket a?adido anteriormente. Bone15 ten?a que ser un hueso real. Se export? un hueso real como hijo de Bip01 Spine1, con origen de referencia(0,-6.75,98), mediante el addon PSK para usar las convenciones nativas correctas. Se mantienen los98 huesos anteriores y se a?ade uno:99. Se conservan puntos, pesos y registros anteriores salvo el contador de hijos de Spine1. Se quit? el alias. Evidencia native-seat-idle-disassembly.txt.

La selecci?n de reposo/marcha usa arrays de8 nombres por CurWeaponType. El parche anterior solo defin?a ?ndice0. El nuevo paquete define los8 slots para WaitAnimName/AtkWaitAnimName/WalkAnimName/RunAnimName/DeathAnimName/DeathWaitAnimName:48 entradas. El reposo apunta a atkwait y carrera a run. Esto corrige tablas faltantes; el resultado sonoro/visual final requiere cliente real. Snapshot runtime capturado cuando Hellkevin YA HAB?A BAJADO: moving=false,mounted=false,mountId0,guardfalse. No usar ese snapshot para afirmar que se comprob? la detenci?n mientras estaba montado.

Verificaciones PASS: UModel extrae99 huesos, Bone15 real con padre Spine1; geometr?a/pesos preservados;48 entradas serializadas y decodificadas; Blender importa el roundtrip99 con PSA98 y comprueba que Bone15 sigue exactamente al torso en run y atkwait. Archivos real-seat-idle-verification.json, seat-pose-verification.json. No son prueba del cliente L2.

Paquetes preparados BHMTransport.u y LineageMonster-native-ride.u; instalaci?n pendiente mientras L2 siga abierto. Se pidi? al usuario cerrar el juego. Open-NativeBehemoth.ps1 ahora verifica y copia AMBOS paquetes antes de abrir, o con -InstallOnly para instalar sin ejecutar la interfaz. Protege contra actualizaci?n parcial con el juego abierto. Acceso26 mantiene esa ruta. Cliente principal intacto. Segundo ocupante pendiente.

Instalaci?n confirmada tras cierre de L2 por el usuario: los dos paquetes privados coinciden con sus hashes preparados. Hueso real Bone15 y48 entradas de animaci?n instalados. Falta prueba visual del cliente; no declarar ambos fallos resueltos a?n.


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

Instalaci?n confirmada tras cierre del cliente: LineageMonster.int privado coincide con el parche; secci?n[strider] WaitAnimName[0]=atkwait y WalkAnimName[0]=Walk verificados tras descifrar el archivo instalado. Principal intacto. Falta confirmaci?n visual de idle en L2.
