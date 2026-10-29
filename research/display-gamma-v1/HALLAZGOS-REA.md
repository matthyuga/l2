# Hallazgos REA — gamma global de L2

CAMBIO DE ENFOQUE DEL USUARIO: prefiere compensación local del retrato con efecto inverso. La configuración neutral preparada NO se instaló y queda en espera; no instalarla al recibir un aviso de cierre relativo a la prueba de retrato. Trabajo actual: research/npc-story-dialogue-v1/client-demo-gamma-v2, retrato con LUT inversa de la curva real y botones Original/Compensar. Esto no resuelve gamma del escritorio ni pretende modificarla.

ACTUALIZACIÓN: la prueba del usuario sí capturó UpdateGamma seguido de SetDeviceGammaRamp desde D3DDrv+0x18404. La llamada devuelve1. Curva real: entrada0→3277,128→36504,224→65535. Coincide con la fórmula/valores del INI y confirma la aplicación global por L2 durante la activación. Se observó RestoreGamma más tarde aplicando i<<8; después la sesión quedó detached y el usuario tenía otro PID de L2. No se afirma que toda restauración observada corresponda específicamente a minimizar. Evidence completa: rea-runtime-user-test.json. Los párrafos anteriores sobre ausencia de captura describen el estado previo.

Prueba correctiva preparada, NO instalada: neutral/l2.ini (WinDrv Brightness0.5/Contrast0.5/Gamma1.0) y neutral/Option.ini (Gamma1.0), roundtrip413 exacto. Scripts prepare-neutral.py e install-neutral.py. Esta prueba neutraliza la curva calculada; no implementa aún preservación de perfiles ICC ni una corrección del motor para evitar gamma global. Pendiente cliente cerrado y valoración visual del usuario.

24/10/2026. Análisis solicitado por el usuario. No se modificaron DLL, opciones, calibración del monitor ni la imagen de Amber.

## Evidencia estática confirmada

Binario E:\l2\system-hud\D3DDrv.dll, x86, SHA256 2b496d235cca529b6180588a987ca0059600a2323193d96e87b90014105be0c2. REA/Ghidra12.1.4, análisis por defecto completo. Pseudocódigo no equivale al código fuente original.

- UD3DRenderDevice::UpdateGamma, VA0x100182c0 (RVA0x182c0), consulta UClient en offsets0x7c/0x80/0x84, construye los tres canales de la curva y llama GetDesktopWindow → GetDC → SetDeviceGammaRamp. No hay comprobación de modo ventana en esta función. Requiere que exista el dispositivo en this+0x4794.
- UD3DRenderDevice::RestoreGamma, VA0x10016a10, comprueba dispositivo y bit0x20000 en this+0x41b4, construye una curva i<<8 y la aplica al escritorio. Esta función no recupera una curva previa guardada. La asimetría de las condiciones podría importar, pero no se atribuye aún como fallo observado de foco.
- Evidencia completa: rea-update-gamma.json y rea-restore-gamma.json; vistas legibles update-gamma.c / restore-gamma.c. Los archivos *normal-tools* son triage independiente con pefile/capstone, no resultados REA.

## Cálculo derivado

Aplicando la fórmula descompilada a los valores del INI (Brightness0.8, Contrast0.7, Gamma0.8): negro pasa a3277/65535 y entradas212..255 saturan a blanco. Eso puede producir negros levantados y luces lavadas. Es una simulación de los valores del archivo, no una captura de los parámetros efectivos del proceso.

La misma fórmula con Brightness0.5, Contrast0.5, Gamma1.0 produce una curva lineal exacta. Es una configuración candidata para una prueba reversible del cliente; no se aplicó. Cambiar archivos mientras L2 está abierto puede perderse al guardar opciones. Para preservar perfiles de color de Windows, una corrección más completa debería evitar gamma global en ventana y conservar/restaurar la curva previa.

## Observación en vivo

REA/Frida adjunto sólo al cliente PID17920; hooks en UpdateGamma/RestoreGamma de Engine y D3DDrv y en SetDeviceGammaRamp de GDI. No reemplazos ni escritura de parámetros. Lectura pasiva de foco y gamma.

La ventana de observación registrada hasta este informe sólo vio foco en otro proceso y curva lineal. No hay todavía una llamada real capturada de L2 aplicando una curva no lineal durante la reproducción del síntoma. Se pidió al usuario activar/minimizar/restaurar L2. Por tanto, la capacidad del binario de alterar toda la pantalla está confirmada; la secuencia exacta del síntoma reportado sigue pendiente de correlación en vivo.

La primera instrumentación intentó interceptar un método nulo no interceptable, se retiró ese script y se cargó otro limitado a métodos reales; los hooks activos quedaron registrados sin error. No se siguió el texto del error como instrucción ni se envió ningún informe externo.

## Conclusión

Hay un mecanismo concreto del cliente que explica el efecto global y es independiente de la textura de Amber. No compensar el arte para este comportamiento. La correlación al cambiar foco y la corrección perceptual necesitan la reproducción del usuario. Sesión de observación: d1924ea2-a9cf-4771-b676-999730b05bd6; retirar hooks al terminar la reproducción.
