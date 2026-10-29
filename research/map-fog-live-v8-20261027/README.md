# Niebla V8: actualizaci?n desde el mapa nativo

27/10/2026. INSTALADA tras confirmar el cierre del cliente. Pendiente validaci?n dentro de L2.

Kevin report? que V7 no revela en tiempo real. El log recibe snapshots completos, pero no tiene DRAW V6 ni UPDATED V7. REA/Frida observ? L2 PID3116 con V7 en E:/l2/system-hud/d3d9.dll, base 6d480000. El dispositivo real 18fc7020 usa vtable18fc9fac; sus slots17/65/81/82/83/84 apuntan al d3d9 de Windows (69790000), no al proxy. En 3s se observaron569 Present,250146 SetTexture y llamadas118598 DrawPrimitive /135375 DrawIndexedPrimitive. Eso demuestra que la tabla activa no contiene los hooks; NO establece cu?ndo o qui?n los retir?. La sustituci?n frente a sobrescritura de la tabla sigue sin determinarse.

Evidencias REA: ev_16fee0eb3f65684e7e637438a46f0047cd0e6860f370a57a98747480b498a03a y ev_ddaf71455621815462b00470e640dec7b1e5f304da8b47edb93505b8bde80e10. Las observaciones adjuntaron instrumentaci?n temporal y se desprendieron al terminar; no cambiaron archivos ni datos del juego. runtime-V7-before.log conserva el log de entrada.

V8 actualiza el atlas dentro de paintUnchecked, en la entrada nativa de mapa mundial/ciudad, antes de enviar la cobertura. Adem?s comprueba/repara los ocho slots del dispositivo activo desde el mapa y la cach? nativa; conserva el m?todo subyacente actual al reparar. No depende exclusivamente de CreateDevice, Present o de volver a enlazar el marcador. Las revisiones sin cambios no regeneran el atlas.

Regresi?n HAL: se mantiene el atlas enlazado y se retiran los hooks de la tabla activa. V7 reproduce mapa congelado: primer p?xel4e5860 no cambia (exit8). V8 repara y actualiza tres descubrimientos a208020 sin SetTexture/Present. Otro personaje sigue cubierto. Tambi?n pasan30415 checks nativos y HAL MANAGED / SYSTEMMEM->DEFAULT (framebuffer, opacidad, restauraci?n de estado y16Present).

Instalar con `python research/map-fog-live-v8-20261027/install.py`. Rechaza L2 abierto, hashes originales distintos o candidato sin verificaci?n. Reemplaza solo d3d9.dll y guarda respaldo. Servidor, HSL, NWindow, D3DDrv y progreso conservados. Restore exige cliente cerrado e identidades exactas.

Validaci?n real pendiente: START map fog V8; ATTACHED V8 hooks; DRAW V6 atlas alpha; UPDATED V8 exploration atlas at native map draw boundary (o ruta draw/Present si ya se actualiz? antes). Recorrer terreno nuevo, observar revelado, probar mapa peque?o/grande y persistencia. No afirmar ?xito dentro del juego solo por las pruebas HAL. La investigaci?n del cr?tico UpdateAnimation es independiente.

Instalaci?n completada con identidad SHA256 verificada. Respaldo: E:\l2-local\backups\map-fog-live-v8-20261027-205003\d3d9.dll. Solo se reemplaz? d3d9.dll.
