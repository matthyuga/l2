# Precarga y fondo épico V1

12/10/2026. El usuario pidió cambiar el panel de precarga y explorar imágenes para la pantalla de carga. Se generaron dos artes originales con la herramienta de generación de imágenes: una fortaleza entre nubes, aventureros y barcos voladores; y un panel con guerrero, marco dorado y el título Lineage II / Interlude. La ambientación es conceptual; no representa fielmente un mapa del juego. L2 ZyboX es una referencia de las capturas antiguas, no un nombre confirmado para esta versión.

Ambos están instalados en el cliente local. Abrir **2-JUGAR.cmd** muestra los nuevos recursos al iniciar el cliente. No hace falta reiniciar GameServer por este cambio.

## Actualizaci?n de marca: HELL GAMES

El usuario confirm? HELLGAMES y aport? un logo con HELL sobre GAMES, en serif plateada. Se edit? la precarga para usar esa disposici?n, conservando guerrero, marco, fortaleza y barco. La versi?n vigente es research/client-loading/startup-hellgames-v2.png (master) y startup-hellgames-640-v2.png (adaptaci?n). Se reemplazaron las 22 variantes BMP con el cliente cerrado y se verificaron codificaci?n, alpha y hashes. Fondo de carga sin texto conservado. Respaldo de V1: backups/client-loading-hellgames-20261012-231216; manifiesto hellgames-installation.json. El restaurador general Restore-Loading.ps1 fue mantenido con hashes vigentes para volver al splash original. Primera inspecci?n en el cliente pendiente.

## Recursos preparados

- Arte completo: research/client-loading/epic-arrival-v1.png (1672×941).
- Panel con transparencia: research/client-loading/startup-panel-v1.png; adaptación 640×480 en startup-panel-640-v1.png.
- Pantalla UE2: L2EpicLoadingV1-e.utx con Skins.LoadingBackground01, RGBA8 y 1024×1024. La composición conserva su proporción en la zona superior 1024×768 usada por la carga; el resto queda negro.
- Systextures/sp_32b_01.bmp hasta 11 y sp_256_01.bmp hasta 11: 22 variantes nativas del splash, reemplazadas por la misma propuesta para conservar identidad al variar el recurso seleccionado. Incluye alpha BGRA32 y fallback con paleta de 256 colores. Los BMP se codificaron con Lineage2Ver121 ligado al nombre exacto.
- system-hud/Localization.ini: solo cambió English_LoadingTexture, de L2Font-e.loading02-e a L2EpicLoadingV1-e.Skins.LoadingBackground01. Se conservan lengua, fuentes, logo del login y las otras configuraciones. Codificación Lineage2Ver111.

El L2Font-e.utx original no se modificó. El splash se localizó mediante las rutas literales de L2.exe y la inspección de los BMP reales. La textura antigua y Localization.ini se decodificaron para comprobar la referencia vigente. [Guía publicada sobre la configuración de texturas de carga](https://maxcheaters.com/topic/11942-guide-custom-loading-screen-no-editing-in-l2font-eutx/) usada como referencia secundaria; la configuración local se verificó directamente.

## Verificación y respaldo

UCC compiló el paquete; UEViewer lo leyó y exportó. Los píxeles exportados coinciden exactamente con la textura preparada. Se comprobó el wrapper 121, su clave según filename y CRC32. Los 22 BMP y Localization.ini se codificaron y decodificaron sin cambios de contenido. Hashes de los 24 archivos instalados conservados en research/client-loading/installation.json. Cliente cerrado al instalar.

Respaldo: backups/client-loading-v1-20261012-230817. Restauración: research/client-loading/Restore-Loading.ps1, con cliente cerrado; valida que nadie haya modificado posteriormente los archivos. No se tocó el EXE, las DLL, la IA ni los stats del servidor.

La primera visualización desde el cliente queda pendiente del siguiente arranque. Esta validación de recursos no prueba por sí misma su aspecto durante la carga real.

## Opciones de diseño pendientes

1. Llegada y exploración: castillo entre nubes, barcos y grupo de aventureros. Propuesta V1 generada e instalada.
2. Asedio: fortaleza en llamas, clanes, estandartes, magia y tropas. Concepto; aún no generado.
3. Santuario del Amanecer: ruinas monumentales y magia azul/dorada. Concepto; aún no generado.
4. Precarga con identidad del server: conservar el marco/guerrero o usar un emblema más sobrio; nombre y lema aún por definir.

No se implementó una escena de login 3D ni fondos aleatorios por evento; son trabajos distintos del splash y la textura de carga.
