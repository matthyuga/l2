# Nexus TV en Giran ? laboratorio local, 16/10/2026

Implementacion instalada. Pendiente la prueba visual en Giran; no presentarla como realizada.

## Prueba manual

1. Abrir **L2 - Observador NexusCam**: splash original Interlude. Cuenta `nexuscamera`, personaje `NexusCam`; acceso privado en research/camera-observer/ACCESO-PRIVADO.txt. Si no comienza el vuelo automaticamente, escribir `.camvuelo`. Mover con teclado/clic; no F9/F10 ni `.camara on`.
2. Abrir **L2 - Pantalla Giran**, con Hell Games. Entrar con tu cuenta habitual y otro personaje. Para esta prueba usar esta copia receptora: el acceso normal antiguo no contiene el receptor de video.
3. En el espectador escribir `.pantalla ir`, esperar el teleport y mirar al oeste, hacia el mural del pedestal central. Pantalla en 82165,148611,-3550; jugador aparece600 unidades al este, mirando al oeste.
4. Mantener ambas ventanas abiertas, evitando minimizar la fuente. Alternar a NexusCam, moverse y volver al espectador para comprobar el cambio. Primera version: 512x384, unas 10 capturas/s, incluida la interfaz del piloto.
5. `.pantalla off` oculta el objeto; `.pantalla ir` lo reactiva. Al cerrar la fuente vuelve a SIN SENAL en pocos segundos.

Si reaparece un critical, guardar el texto completo e indicar que copia fallo y si fue antes o despues de `.pantalla ir`. No se abren clientes al terminar la preparacion.

## Instalacion

- Fuente E:\l2\system-camera-online, NexusTV.ini Mode=source.
- Receptor E:\l2\system-screen-lab, Mode=viewer, copia de system-hud.
- Proxy x86 d3d9.dll, fuente native/nexus_tv.cpp. Captura la salida real del piloto y la comparte por memoria local Local\NexusGiranTV_v1. Sin servicio de red ni grabacion. Sustituye solo la textura que coincide con el marcador exacto Nexus; fallback si no hay frames recientes. No modifica instrucciones de DLLs originales.
- Paquete propio E:\l2\nexus-tv\NexusTVAssets.u: malla estatica y materiales, display360x270, marco/pies. Mapas intactos.
- NPC59890 agregado a npcgrp.dat de ambas copias; registros anteriores byte exactos.
- Servidor custom/GiranScreen/GiranScreen.java y stats/npcs/custom/giran_screen.xml, cargados y persistidos en CustomScriptFolders. Optativo por cliente local, sin spawn en World global. Comandos .pantalla / ir / off. No ejecutar desde una copia sin el modelo instalado.
- Core GameServer.jar sin cambios. system-hud l2.ini/npcgrp.dat/L2.exe intactos, hashes en client-installation.json.

## Identificacion

Solo el L2.exe de camera-online cambia cuatro cadenas de ruta de splash de igual longitud, ASCII y UTF16, SysTextures -> camtextures. Tamano del ejecutable y todos los bytes ajenos a esas cadenas preservados. E:\l2\camtextures contiene las22 variantes Interlude de los originales decodificados de client-loading, cifradas121 y verificadas por ida/vuelta. No cambia el Hell Games compartido. camera-identity.json registra hashes, offsets y respaldo. Aspecto visual pendiente del arranque manual.

Ambos lanzadores usan RunAsInvoker para evitar el pedido de administrador heredado del ejecutable. No requieren administrar Windows.

## Evidencia y limites

- native/viewer-result.json: 179/180 frames correctos en relay grafico D3D9 real; recibe dos colores sucesivos; HRESULT0.
- native/unmarked-result.json: 180/180 frames conservando otra textura sin marcador.
- native/offline-result.json: 180/180 frames de fallback sin fuente.
- texture-verification.json / asset-reload.log: recarga UCC y marcador512x512 recuperado intacto.
- server-verification.txt: template/handler, rechazo caller nulo, objeto ausente de World, serializacion NPC_INFO correcta.
- Ultimos arranques reales registraron D3D9 DEVICE READY en ambas copias; fuente PUBLISHED FIRST FRAME. No demuestra todavia la pantalla ni el video dentro de Giran.
- Hubo un critical anterior cuyo texto Kevin cerro. Causa sin confirmar; agregado registro de factory/dispositivo y HRESULT para diagnosticar si se repite.
- NexusTV.log por copia: fuente debe mostrar PUBLISHED FIRST FRAME; receptor MATCHED NEXUS SCREEN TEXTURE y RECEIVED FIRST FRAME al mirar el objeto.
- Solo misma PC/sesion Windows. YouTube, clientes remotos y control automatico del piloto quedan para otra etapa. Fuente minimizada/sin render puede perder senal. Modelo/material y funcionamiento simultaneo dentro del juego pendientes de prueba manual.

## Respaldo

E:\l2-local\backups\giran-screen-20261016\source|viewer contiene l2.ini y npcgrp.dat previos; source tambien L2.exe antes del splash independiente. Cerrar clientes antes de restaurar. El acceso normal antiguo sigue disponible. No restaurar catalogos y despues invocar .pantalla en esa copia.

## Ajuste al mural ? 16/10/2026

Kevin eligio el panel del pedestal de la estatua AdenaGirl en su captura. Se leyo la ubicacion original desde22_22.unr, sin editar el mapa: Giran_AdenaGirl_Btm en81923.96875,148610.96875,-3355, yaw49152. Bounds locales recuperados del usx: X[-221.126,221.2994], Y[-225.3209,224.0981], Z[-140.7348,150.256]. Su limite este es82148.06685. Pantalla trasladada a82165,148611,-3550, heading0; plano visible+X en82171 queda delante de ese limite. Display abarca Z[-3470,-3200], frente al pedestal Z[-3495.73,-3204.74]. Es un encaje inicial, pendiente ajuste visual fino por Kevin.

La ubicacion anterior estaba en el lado opuesto de la plaza: el diagnostico de recepcion de textura no demostraba que Kevin tuviera la superficie delante. Se corrigio esa interpretacion. .pantalla ir ahora posiciona al espectador600 unidades al este, heading32768. Modulo custom actualizado en caliente con Instrumentation.redefineClasses, sin modificar core ni reiniciar/desconectar. Instancias ya activas reciben DeleteObject y nuevo NPC_INFO. Ver mural-placement-verification.txt y live-inspection.txt. Modelo/texturas del cliente sin cambios en esta intervencion.


## Televisor plano v2 ? area roja de la captura

Kevin confirmo que tampoco se veia el objeto separado/elevado y marco un rectangulo que ocupa todo el frente del monumento, entre columnas y desde la base hasta arriba. Se preparo panel-v2: superficie600x450(4:3), marco648x498, sin pies, espesor26. Nuevos paquetes NexusTVPanel2.u y NexusTVMotion2.u en E:\l2\nexus-tv. Se anadio una pose de raiz explicita, mediante escritor nativo Lineage2 ya disponible, evitando el PSA incompatible de UCC. No afirmar todavia que eso resuelve la invisibilidad: causa aun por validar en cliente.

UModel carga y exporta malla104vertices52triangulos1hueso, pose2frames, y textura con pixeles identicos. Marcador original conservado. Solo registro59890 actualizado en ambos catalogos; otros registros byte exactos. Ver panel-v2/installation.json, animation-link.json y logs roundtrip. Build: build_panel.py y link_pose.py. Posicion persistente82165,148611,-3490 heading0; displayZ[-3466,-3016], marco[-3490,-2992]. Custom server actualizado en caliente y espejos persistentes; fuera de la prueba temporal elevada.

AHORA se requiere cerrar y reabrir SOLO cliente espectador Pantalla Giran para recargar el catalogo y la malla; no reiniciar servidor ni fuente NexusCam. Luego .pantalla ir. La copia fuente tambien recibio catalogo nuevo para su proximo arranque, no necesita reinicio durante esta prueba. Ambos clientes continuaron abiertos; no se cerraron ni reabrieron automaticamente.

Respaldos npcgrp.dat previos: backups/giran-tv-panel-v2-20261016/source|viewer. Si vuelve a ser invisible, investigar pose de dibujo/clase old_tomb_stone o render directo, no repetir teleports como supuesto arreglo. Confirmacion visual pendiente.

Ajuste de altura posterior16/10: Kevin SI ve televisor nuevo en captura, pero elevado sobre estatua, pide bajarlo al piso al rectangulo anterior. Nuevo origenZ=-3860 (370 unidades abajo), X82165 Y148611 heading0 intactos. Actualizado GiranScreen en caliente y tres espejos; instanciaHellkevin reenviada visible=true. No hace falta reabrir cliente. Hipotesis offset vertical del Pawn asociado CollisionHeight370; compensacion aplicada en Z servidor, falta confirmacion visual de baseal piso. No afirmar video activo: captura muestra SIN SENAL. Fuente y receptor siguen conectados segun servidor. Evidencia research/giran-screen/live-inspection.txt y mural-placement-verification.txt. AgenteLowerFlatTV3.java. Pendiente usuario confirmar altura.

Altura4 y senal16/10: usuario sigue viendoTV alta, SIN SENAL, pregunta reiniciar ambos. NO se reiniciaron. Lectura propia metadata memoria compartida Local/NexusGiranTV_v1: seq3812 inmovil, edad1775s (29min),512x384; transporte existe pero fuente noactualiza. Preguntaasync pendiente: activar NexusCam visible no minimizada y moverunossegundos, luego verTV. No confundir logPUBLISHEDFIRSTFRAME con frescura actual.

Pruebaaltura4: collisionHeight deltemplate propio59890 reducido370->30 (valor original claseold_tomb_stone), tanto intcomo float runtime porreflexion SOLOtemplatecustom; XML persistido3espejos y research. OrigenZ restaurado-3490 porque compensar soloZantesnoresolvio, posibleajustefisico cliente. Scriptcustom redefinido, DeleteObject/reenvio instancia. Pendienteconfirmacionvisual, no afirmar causa demostrada ni solucioncompleta. CorrectTVHeight4.java height4.jar. No assets/DLLcambiados, no requiere reiniciar paraestaprueba. .pantalla off y .pantalla ir si requiere refrescar. Fuente puede necesitar reabrirse SOLO si activarvisible no reactiva frames; investigarpresentreset si persiste.

CONFIRMACION VISUAL16/10: Kevin respondio «ya esta, gracias» tras activar fuente y envio captura con televisor frente al pedestal, marco completo visible y contenido renderizado de NexusCam (vista aerea de arquitectura), ya sin placeholder SIN SENAL. Confirmado flujo real cliente fuente -> pantalla3D en espectador dentro de Giran. Altura4/collisionHeight30 y Z-3490 son la configuracion vigente; usuario no pidio mas ajuste. No afirmar medicionFPS/latencia ni que caso minimizado este resuelto. Mantener camara visible/renderizando; esta prueba desbloquea primera etapa local, YouTube/remoto pendientes.


16/10/2026 ? Control multimedia instalado en E:\l2-local\nexus-tv. Escritorio L2 - Control Nexus TV ->16-CONTROL-NEXUS-TV.cmd, panel http://127.0.0.1:8796. Archivos locales por HTML5, YouTube por IFrame oficial en Chromeheadless aislado (sin perfil personal, sin capturar escritorio), control pausa/play/seek/volumen/lista/loop/camera/off. No OBS ni descargaYT. Controlador emite nuevo canal Local\NexusGiranTV_Program_v1, receptor system-screen-lab proxy actualizado lee Channel deNexusTV.ini. Fuente camera-online intacta emite canaloriginal; hub reenvia segunfuente.15-PANTALLA-GIRAN.cmd iniciahub -NoBrowser automaticamente. Pythonw background enpuertolocal8796; perfil dedicado run/player-profile. Solo mismaPC, audio de navegador local; no audio espacial/red.

Pruebas: video local cambiante/pausa/seek PASS; YouTube videoejemploGoogle M7lc1UVf-VE avanza sinerror (mute enprueba); receptorD3D9real180/180pixeles correctos; camera->program doscoloresfixture PASS, fixturefinalizada; tokenAPIyrutas segurasPASS. UIbrowsertools iab/chrome no disponibles; no se hizoinspeccionvisualUI, JSsyntaxyAPIprobados. Evidencia nexus-tv/run/integration-tests.json,camera-program-test.json,research/giran-screen/native/program-result.json. Nuevo contenido enL2 pendientepruebavisualusuario. No se abrieronclientesL2. Hubquedaencendido con Demo Nexus TV.mp4(coloranimado8s)loop yvolumen30(sinaudioenelclip). PlaylistfinalsoloDemo, YTtestretirado. User puedeabrircontrol yPantallaGiran, .pantalla ir; pegarYT/importararchivo/clickNexusCam. Readmecompleto nexus-tv/README.md. Backups giran-tv-control-20261016, originalsystem-hudhashesintactos. No incluirplaylist, perfiles, run, media,DLLs encloud; copiar solocodigo/docslocalmente si hacefalta.

CONFIRMACION VISUAL 16/10/2026: Kevin dijo «bien ahi lo veo» y envio captura del personaje Hellkevin frente al televisor3D de Giran mostrando Demo Nexus TV.mp4 (barras de color, diagonal y contador00:00:06.800). Confirmado video LOCAL del nuevo controlador dentro del juego, con marco y perspectiva. YouTube ya paso prueba de reproduccion del controlador/render propio, pero todavia no hay confirmacion visual del usuario de YouTube en Giran. No confundir ambas verificaciones. Camara original ya confirmada en captura anterior. Sin cambios adicionales solicitados.

Actualizacion de calidad16/10: ver quality-v2/deployment.json y E:\l2-local\nexus-tv\README.md. Control v2 activo; clienteHD pendiente de reapertura manual del espectador. Nuevo resumen Nexus: inbox/20261016-l2-tv-hd.md.
