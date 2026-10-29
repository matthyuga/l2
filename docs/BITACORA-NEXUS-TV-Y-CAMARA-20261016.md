# Bitácora: cámara y Nexus TV en Lineage II

Fecha de cierre: 16/10/2026. Kevin solicita guardar continuidad y retomar en otra sesión.

## Leer primero al retomar

Proyecto operativo: `E:\l2-local`. Clientes: `E:\l2`. La carpeta `E:\l2-damage` contiene la investigación del servidor de referencia; no es la raíz de nuestro servidor.

Última guía: [GUIA-1080P-Y-CONTROL.md](nexus-tv/GUIA-1080P-Y-CONTROL.md).

**Próximo paso:** abrir el acceso **L2 - Pantalla Giran**, entrar con el GM local y probar `.pantalla ir` y `.tv`. Está instalada la versión nueva, pero falta confirmar visualmente su menú y su modelo dentro de L2. No confundir las pruebas automáticas con esa confirmación pendiente.

No abrir ni cerrar clientes automáticamente: Kevin prefiere abrir ambos y realizar las pruebas él mismo. No reutilizar PID históricos ni reinstalar agentes de diagnóstico antiguos. Consultar el estado actual antes de actuar.

## Referencias e ideas conservadas

Kevin recorrió L2 Damage y aportó capturas de selección inicial de arma/SA, gatekeeper personalizado, zonas de farmeo y PvP, buffer, cambios de clase, skill enchant, GM shop, tienda de apariencias, augment, casino, votos, clanes/subclase y bodas. Son referencias de una estructura interactuable del mundo; la adaptación de NPC a nuestro servidor queda para después.

Prioridades de diseño conversadas: modernizar amigos/mensajería y conexión con Discord; mejorar mapa, target y feedback conservando identidad de L2; unificar invitaciones con barra de tiempo; explorar iconos sobre el objetivo para estados negativos recibidos. No dar por implementados estos conceptos ni afirmar resuelta la discusión de información competitiva/VIP.

Eventos futuros pueden tener convocatoria y recorridos con encuentros previos, minijefes, puzzles y lore. PvP: entrada cerca de salida/teleport y opción de ingreso aleatorio al perímetro. Convocatorias, votos y NPC se definirán según el contenido final del servidor.

## Cámara: qué funcionó

La prueba offline de camera walking separó la cámara; Kevin la confirmó. En online, F9/F10 y `///camerawalking mode=on` no resolvieron el desplazamiento. Los diagnósticos recibían paquetes de movimiento: no atribuir todo el problema a AnyDesk. Desparalizar al actor tampoco movía la vista del observador fijo.

La solución adoptada usa vuelo nativo de wyvern con vista en primera persona, actor oculto y protegido. **Kevin confirmó que se desplaza correctamente con teclado y mouse desde AnyDesk.** Es un actor volador usado como cámara; no una cámara totalmente independiente del personaje.

- Cuenta reservada: `nexuscamera`; personaje `NexusCam`, ID268436061, sin GM.
- Credenciales solamente en `research/camera-observer/ACCESO-PRIVADO.txt`; no duplicarlas en bitácoras, Nexus ni repositorios.
- Acceso **L2 - Observador NexusCam** → `14-ABRIR-OBSERVADOR.cmd` → `E:\l2\system-camera-online`.
- Script persistente `custom/CameraFlight/CameraFlight.java`; autoentrada en vuelo, sin timeout de sesión.
- `.camvuelo`, `.camvuelo subir`, `.camvuelo bajar`, destinos `giran`, `coliseo`, `elven` y `off`.
- Origen de retorno persistido privadamente en configuración. Detalle: `CAMARA-VUELO.md`.
- Logo original de Interlude en este cliente para identificarlo; el resto conserva su identidad.

## Televisor en Giran: confirmado por Kevin

Se construyó un televisor 3D real frente al mural central. Los problemas iniciales de visibilidad/altura se corrigieron; `collisionHeight=30` es relevante. No volver a elevarlo ni modificar su ubicación por intuición.

- NPC visual59890, opt-in para cada espectador; no es un spawn global enviado a clientes sin parche.
- Posición `82165,148611,-3490`, heading0; marco648×498, área de imagen600×450.
- `.pantalla ir` lleva al espectador delante; `.pantalla off` lo oculta.
- Script `research/giran-screen/GiranScreen.java`, instalado en scripts custom y espejos correspondientes.
- Acceso **L2 - Pantalla Giran** → `15-PANTALLA-GIRAN.cmd` → `E:\l2\system-screen-lab`.

Kevin confirmó con capturas: imagen de NexusCam en el televisor, patrón de video local y reproducción de YouTube dentro del mundo. La fuente de cámara debe seguir abierta y renderizando; al dejar de actualizarse aparece la tarjeta sin señal.

## Reproductor y control

Código en `E:\l2-local\nexus-tv`. Control web `http://127.0.0.1:8796`, acceso **L2 - Control Nexus TV** / `16-CONTROL-NEXUS-TV.cmd`.

Chrome dedicado, perfil aislado, reproductor oficial IFrame de YouTube y archivos locales. No usa pestañas personales ni captura el escritorio. OBS no es necesario para esta implementación. Algunas herramientas de streaming se descargaron en la investigación inicial; no confundir descarga con instalación o uso.

La pestaña del navegador es solo el control: cerrarla deja la emisión funcionando. **Cerrar reproductor** termina el servicio y su navegador dedicado. Se conservan lista, volumen, repetición y calidad. Al iniciar nuevamente vuelve a la fuente NexusCam; todavía no reanuda automáticamente el video y su posición anteriores.

Una lista con varios videos avanza al siguiente al terminar si Repetir está desactivado. No hay agenda por horarios implementada.

## Actualización final: 1080p / 4K y `.tv`

Instalados controladorv3, receptor D3D9 actualizado y paquetes `E:\l2\nexus-tv\NexusTVPanel4.u` / `NexusTVMotion4.u`. El modelo conserva ubicación y marco; usa UV completo y textura de dimensiones variables.

- Canal `Local\NexusGiranTV_Program_v3`, máximo3840×2880.
- Perfil preferido guardado `fullhd`: lienzo1920×1440, video16:9 de1920×1080 con bandas.
- Perfil `uhd` experimental: lienzo3840×2880, video16:9 de3840×2160.
- Perfiles anteriores siguen disponibles. La cámara original sigue capturando512×384: subir el perfil no inventa detalle en esa fuente.
- CanalesProgram_v2/v1 compatibles con salida reducida para receptores anteriores.
- `Apply-HDClient.ps1` verifica manifiesto e instala desde `research/giran-screen/quality-v3/install`.
- No se modificó el cliente original `system-hud`; hashes verificados. No se sustituyó el proxy de la cámara.

Nuevo script `custom/NexusTvControl/NexusTvControl.java`, compilado e instalado con configuración persistente. `.tv` / `.televisor` abre control HTML nativo: play/pause, seek, anterior/siguiente, volumen, repetir, calidad, YouTube y biblioteca. Solo GM conectado porlocalhost. Peticiones HTTP fuera del hilo de paquetes; token privado temporal, nunca enviado al jugador. No se otorgó GM a NexusCam.

El GameServer estaba apagado durante esta última implementación; cargará el script al siguiente inicio. El acceso del espectador arranca servidor/controlador de la forma habitual. No se abrieron clientes para verificar visualmente la actualización.

## Pruebas y rendimiento

La auditoría anterior con ambos clientes y servidor activos mostró margen de RAM/GPU/servidor. Informe `reports/performance-20261016/INFORME.md`: CPU27.4% media, mínimo18.1GiB RAM libre, GPU38% media, servidor sin deadlock y DB sin consultas lentas en la muestra. No acredita ausencia de fugas durante horas ni capacidad con muchos jugadores. No se midieron FPS reales del motor L2.

Última actualización, pruebas aisladas sin L2/servidor simultáneos:

| Fuente/perfil | Resultado aproximado |
|---|---|
| Archivo1080p30 →1080p | 25–27 FPS |
| YouTube → lienzo1080p | 21 FPS salida, 17 contenido; fuente eligióhd720 |
| Archivo1080p ampliado →4K | 11 FPS |
| Archivo4K15 real →4K | 7.4 FPS |

4K funciona, pero **todavía no es fluido**. El selector controla resolución del transporte; no obliga a YouTube a entregar esa calidad. La calidad del reproductor oficial y del video de origen sigue importando.

Verificados: compilación Java/C++/Python; menú mediante HTTP y rechazo sin token; pausa/play/seek/volumen/cambios de calidad; video1080p/4K y YouTube; roundtrip npcgrp413; paquetes enumerados nativamente; hashes instalados. Pruebas D3D9 con lectura de vuelta:179/180 cuadros coincidentes1080 y167/180 en4K, incluyendo arranque, HRESULT0. Corregida una carrera al cambiar resolución durante decodificación.

Evidencia: `research/giran-screen/quality-v3/deployment.json`, `benchmarks.json`, `4k-source-test.json`, `youtube-1080-canvas-test.json`, `native/dynamic-tests.json`. Demos propias sin sonido en `nexus-tv/media`.

## Sonido: investigado, pendiente de implementar

**El sonido actual sigue saliendo del reproductor de Windows.** No se implementó aún audio integrado con el volumen del juego ni atenuación por distancia.

ALAudio del cliente usa OpenAL; Engine exporta `USound::Audio`, y ALAudio contiene funciones de música/volumen. Se identificó una vía de puente PCM al contexto OpenAL existente. No se llamaron esas funciones dentro de una sesión de juego ni se probó esa integración.

Para archivos locales: decodificar PCM y sincronizar buffers con pausa/seek/cambio de fuente. Para YouTube: obtener audio exclusivamente del reproductor dedicado, después llevarlo a L2 y evitar duplicación. La API de captura por proceso documentada por Microsoft requiere una versión de Windows posterior al build19042 instalado; no se capturó toda la mezcla del escritorio como atajo.

Detalle y fuentes: `research/giran-screen/quality-v3/AUDIO.md`. No se instaló driver virtual, OBS ni se parcheó ALAudio/Engine/OpenAL.

## Continuidad y respaldos

- Controlador previo: `backups/nexus-tv-v3-20261016-212237`.
- Cliente: `backups/nexus-tv-hd-launch-*`.
- Código/espejos de scripts actualizados; sin commit/push en esta sesión.
- Nexus: `K:\_CodexNexus\inbox\20261016-l2-tv-1080-remote.md`, notas anteriores de cámara/TV/rendimiento y enlace desde `sessions/lineage2-local.md`.
- Estado registrado al terminar la implementación: controlador8796 listo, versión3, perfilfullhd, fuentecamera, sin error; GameServer y clientes apagados. Es una instantánea, no asumir que seguirá igual en otra sesión.

Orden sugerido para continuar: confirmar `.tv` y pantalla nueva dentro del juego; después elegir entre optimizar1080p/4K, construir audio real de L2 o programar emisiones/recorridos de cámara. Las decisiones futuras quedan para Kevin.

## Actualización 17/10/2026: optimización v4 instalada
Ver research/giran-screen/optimization-v4/INFORME.md. Comparación aislada actual: archivo1080p30 de23,13 a28,59FPS; YouTube salida16,8 a22,2FPS, contenido11,7 a20FPS (hd720). Aún no30FPS estables ni FPS del juego. Calidad/resolución conservadas. Receptor180/180, controles y equivalencia de imagen PASS. Solo Python/controlador reiniciado; ningún cliente L2 abierto/cerrado. Estado finalv4 listo, cámara/fullhd/volumen30/sinerror. Respaldo backups/nexus-tv-opt-20261017. Sin commit/push; falta prueba real en Giran.


17/10/2026 Curva v5 PREPARADA para siguiente inicio, NO sustituida en cliente activo. Modelo y marco648x498, imagen600x450, radio961.5/arco36.36/avance48,48segmentos1392triángulos. UCC/UModel-game=l2/UV/pose/marker PASS; instalación aislada/idempotencia/guardia clienteabierto PASS. Acceso Pantalla Giran aplica al cerrar/reabrir Kevin. No abrir/cerrar clientes automáticamente. Informe research/giran-screen/curved-v5/README.md, preview.png; respaldo backups/nexus-tv-curved-20261017. Sincommit/push. Falta comprobación visual real.

