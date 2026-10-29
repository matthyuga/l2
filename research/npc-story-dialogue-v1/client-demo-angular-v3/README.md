# Diálogo angular de Amber — V3

Instalado el 26/10/2026. Validación visual y de clics dentro de L2 pendiente del usuario.

## Cómo probar

Abrir L2 normalmente, entrar al mundo y pulsar el botón AMBER existente.

- Fondo: Opaco, Semi o Transparente. Solo cambia el fondo decorativo; marco, placa, texto, retrato y botones permanecen visibles. Semi es el predeterminado (alfa 156/255).
- Original y Compensar conservan los controles anteriores del retrato y son independientes del fondo.
- Probar ambas respuestas y Continuar/Volver al inicio; cambiar fondo, cerrar con X y reabrir para comprobar conservación de selección durante la sesión.
- Al reiniciar el cliente se vuelve a Semi y al retrato compensado. No hay guardado permanente de preferencias todavía.

Historial, cartas, neón y conexión al NPC/servidor quedan para etapas posteriores. Se conserva el texto fijo de prueba.

## Implementación

Nueva clase AmberAngularUI en Interface.u; todos los exports anteriores quedan idénticos. Interface.xdat conserva 147 ventanas: se modificaron las cuatro páginas de Amber y el enlace de script del lanzador; las 142 restantes quedan idénticas. Nuevo paquete NexusAmberAngularV3.u con 35 texturas: tres fondos, marco, placa del nombre y diez juegos de botones con tres estados. El lanzador mantiene su textura anterior.

Marco y fondos construidos con geometría y patrones propios por código, usando Arcane como referencia formal. Retrato y compensación reutilizados de los paquetes instalados. Opacidad mediante sustitución de la textura de fondo en las cuatro páginas, sin sondeo, temporizadores ni nuevas llamadas de red. No se cambiaron servidor, quests ni gamma global.

## Verificación

UCC, wrapper121, CRC y roundtrip del paquete de texturas. Lectura fresca de clase, cadena sin ciclos, destinos VM válidos; simulación de apertura, ambas ramas, continuación, reinicio, cierre, botón desconocido y salida del mundo. En esa simulación los tres fondos sobreviven navegación y reapertura y no modifican la selección del retrato.

Conservación byte a byte de exports anteriores y ventanas ajenas; XDAT exacto y controles dentro de ventana 920×440. Hashes del cliente instalado y respaldos comprobados; restauración verificada con --check.

Previsualizaciones revisadas a 1024×640 y 1280×720. Son composiciones previstas sobre un fondo de prueba, NO capturas de L2. Falta comprobar renderizado, transparencia y clics reales en el juego. UCC emitió mensajes por xDxTex.exe ausente pero terminó con cero errores y cero advertencias; paquete leído y texturas inventariadas sin depender de esa utilidad.

## Archivos

- comparacion-fondos.jpg: las tres opciones.
- preview-semi-1024.png y preview-semi-1280.png: composición esperada.
- build-verification.json, verify-angular.log, build-angular-xdat.log, install-verification.log: comprobaciones.
- input-hashes.json, output-hashes.json e installation.json: trazabilidad.

## Restauración

Con L2 cerrado:

`python E:\l2-local\research\npc-story-dialogue-v1\install-angular-demo.py --restore`

Devuelve exactamente a la capa anterior con compensación V2. Rechaza cambios concurrentes. Agregar `--check` para revisar sin modificar.

Respaldo: `E:\l2-local\backups\npc-story-angular-v3-20261026-135220`.

El constructor parte del snapshot capturado antes de instalar; no volver a ejecutarlo sobre la capa instalada. El instalador no abre, cierra ni reinicia el juego.
