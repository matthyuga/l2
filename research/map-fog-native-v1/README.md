# Cobertura nativa del mapa V1 — 25/10/2026

Estado: compilada, probada en harness nativo y cargador Direct3D9 aislado, instalada en system-hud para el próximo inicio. Falta validación del dibujo real dentro de L2. Es una cobertura rectangular de diagnóstico, no la niebla final del continente.

## Uso inmediato

Abrir el juego de forma habitual y abrir el mapa. Debería aparecer un rectángulo negro semitransparente de160x120, anclado al centro cartográfico de la primera vista de cada mapa/proyección. Al arrastrar, el rectángulo debe seguir al terreno; al ampliar la ventana debe conservar la posición cartográfica. El marco y botones deben quedar intactos.

Controles en la raíz E:\l2-local:
- NIEBLA-1-PARCIAL.cmd: modo semitransparente.
- NIEBLA-2-OPACA.cmd: modo opaco.
- NIEBLA-3-APAGAR.cmd: oculta la cobertura sin salir del juego.
- NIEBLA-4-CENTRAR.cmd: invalida los anclajes de prueba; con el mapa abierto se fija uno nuevo en el centro de la vista actual.

Los controles usan control.py y NexusMapFog.ini. Se relee como máximo cada segundo cuando se dibuja el mapa. No cambian el progreso de ExplorationLab. Los modos de ciudad y continente conservan anclajes cartográficos separados, compartidos entre ventana pequeña y ampliada para el mismo identificador de mapa. No interpretar ese anclaje como una ubicación real descubierta ni como transformación entre ciudad y continente.

## Implementación

Se añadió un cargador d3d9.dll x86 que reenvía Direct3DCreate9 al DLL del sistema por ruta absoluta. L2.exe y D3DDrv.dll solo importan ese export de D3D9, verificado con pefile. No se reemplazó un proxy previo.

Una vez disponible NWindow.dll, verifica su SHA256 exacto a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292 y los prólogos de las dos funciones. Solo entonces instala trampolines en memoria para DrawWorldMap RVA187910 y DrawTownMap RVA189130. Los archivos originales NWindow.dll, Interface.u/XDAT y Engine.dll permanecen intactos.

REA confirmó ensamblado y limpieza de pila: DrawWorldMap thiscall con un argumento de pila (dispositivo), RET4; DrawTownMap thiscall con dos (dispositivo y datos de zona), RET8. Los hooks fastcall incorporan ECX explícitamente, dejan EDX sin uso y delegan primero al original. Prólogo exacto55 8B EC 6A FF: cinco bytes enteros, sin instrucciones relativas. Trampoline copia esos cinco bytes y vuelve a original+5.

PaintFog corre al terminar el fondo nativo, dentro del recorrido OnPaint, antes de finalizar el contexto de dibujo. Reutiliza NCGDevice::DrawTexture RVA21a00, thiscall con11 argumentos/RET44, y la textura nativa Default.BlackTexture cargada por RVA3f630, thiscall con2 argumentos/RET8. La posición se calcula en el plano cartográfico restando offsets internos+25c/+260 y se recorta adicionalmente contra dimensiones del visor(+88/+8c). La transparencia usa el parámetro alpha del render nativo. No se toca el estado de dibujo de Direct3D para pintar la cobertura.

La instalación de hooks ocurre en la llamada de creación D3D, si NWindow ya está cargado, o en Present como respaldo en el hilo de render tras terminar el dibujo del frame. No hay hilo que parchee mientras el render está ejecutando la función. Apagar el modo omite PaintFog, manteniendo los trampolines hasta cerrar el proceso. No se descarga dinámicamente el proxy porque sus referencias de vtable deben permanecer válidas.

## Pruebas realizadas

build-native.cmd con MSVC2019 x86, runtime estático /MT:
- native_test.exe:20.012 comprobaciones de recorte, firmas thiscall/fastcall,20.000 llamadas intervenidas, trampolines y restauración.
- proxy_test.exe: carga del DLL, factory D3D9 real, creación de dispositivo HAL en ventana oculta y16 Present correctos, sin cargar NWindow.
- Instalación con guardia de cliente cerrado, hash de NWindow, ausencia de archivos previos y hashes de los seis archivos nuevos.

Estas pruebas no acreditan dibujo, orden de capas, transparencia ni estabilidad in-game. Se requiere observar mapa pequeño/ampliado, arrastre a los cuatro bordes, centrado, alternancia ciudad/continente y modo apagado. El log NexusMapFog.log distingue START, INSTALLED, WORLD/TOWN, ANCHOR, textura cargada, DRAW o rechazo/desactivación por fallo. DRAW significa llamada enviada al render, no validación visual.

## Instalación y restauración

installation.json contiene archivos, hashes y respaldo/manifiesto en backups/map-fog-native-v1-20261025-214418. Para retirar, cerrar L2 y ejecutar `python research/map-fog-native-v1/restore.py`. Verifica los destinos/hashes y elimina solo los archivos nuevos de esta entrega. Puede usarse NIEBLA-3-APAGAR.cmd de inmediato sin cerrar.

No hubo cambios de servidor ni reinicio de GameServer. No se abrió/cerró el juego automáticamente durante esta entrega.

## Pendientes después de la prueba visual

Coberturas por región, máscaras suaves, política de marcadores bajo niebla y sincronización servidor→cliente. Los marcadores nativos posteriores al fondo pueden quedar encima del rectángulo; es deliberado para no modificar otras funciones en esta prueba. El estado TOTAL/PARTIAL/CLEAR de .explora no controla aún este overlay.

La investigación REA completa de implementación está en ../map-fog-analysis-20261025/rea-fog-implementation-evidence.json; composición previa en COMPOSICION-REA.md. El ensamblado recupera además escala global0.0050048828125 y offsets mundo+131072/+262144 para la proyección base, y escala/origen por ciudad; no se usa esa fórmula todavía, porque los anclajes de este diagnóstico son coordenadas del mapa activo.
