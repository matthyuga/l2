# Behemoth: corregir malla del strider nativo, instalaci?n pendiente de cerrar cliente


## Prueba real: Ride mostraba un strider; correcci?n de la clase nativa

El usuario confirm? pose de jinete sobre el strider original, sin equipo Behemoth. Esto demuestra que activar Ride funcion?, pero no que seleccionara el modelo correcto. No declarar montaje Behemoth visualmente validado.

Inspecci?n adicional de Engine.dll: RiderEnter crea LineageMonster.strider; SetPawnResource separa al jinete humano mediante RidePawn y recorre la rama de recursos de jugador, sin reemplazar la malla del cuerpo montado con npcgrp59091. Por tanto el cambio de ID por s? solo no reemplaza su malla predeterminada. Evidencia set-pawn-resource-disassembly.txt.

Se prepar? LineageMonster-native-ride.u: conserva todos los exports salvo los defaults de strider. Agrega Mesh=BHMTransport.BehemothMesh, animaciones Behemoth y colisi?n54/63. No se cambia Engine.dll. Main E:/l2/system-hud/LineageMonster.u conserva SHA256f06ac53f7df24bd13d6e7a0d25d9e3ca4e4502af2437518e49d96a053987d7b6. Ver native-ride-class-patch.json y native-ride-defaults-verification.json.

Alcance deliberado: TODOS los striders montados en este perfil privado se ven como Behemoth. El cliente habitual, IDs del servidor y archivos principales no se reemplazan. El perfil privado queda reservado para ensayos de Behemoth; no usarlo para evaluar apariencia de un strider normal.

El archivo del perfil estaba bloqueado por L2.exe. Se solicit? cerrar el juego. Paquete preparado y validado; instalaci?n pendiente mientras siga abierto. El acceso26 ahora verifica e instala el paquete preparado antes de iniciar el cliente y explica el bloqueo si L2 sigue abierto. No reiniciar servidor. Segundo ocupante sigue pendiente.

Instalaci?n confirmada tras cierre del cliente por el usuario: LineageMonster.u privado coincide con el paquete preparado, con malla predeterminada Behemoth. Cliente principal intacto. Sigue pendiente la comprobaci?n visual dentro de L2.
