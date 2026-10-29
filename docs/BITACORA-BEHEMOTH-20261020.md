# Behemoth: hueso real del asiento y tablas de reposo


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
