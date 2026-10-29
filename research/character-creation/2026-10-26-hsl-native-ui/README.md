# Interfaz HSL nativa preparada

Estado: componente Win32 **x86** compilado y probado, con aspecto adaptado a L2. **No está instalado ni conectado al creador, al material de cabello del motor ni al servidor.** No se modificó ningún archivo activo de L2. La versión v14 que retira las caras problemáticas del orco continúa activa.

## Probar la interfaz

Abrir `build/NexusHairHslDemo.exe`. Es una demostración local independiente. El botón «Personalizar color» abre la ventana propietaria del demo. El cuadro de muestra responde a los eventos de color. La imagen de personaje es una referencia fija original: **no cambia el tinte del cabello**. Para previsualizar el color sobre los modelos reales se mantiene el prototipo WebGL en `../2026-10-26-hsl-selector/index.html`.

Captura reproducible del componente nativo: `native-interface.png`. No es una captura dentro del juego: se generó con WM_PRINT de la ventana real durante las pruebas ocultas.

Controles: plano tono/saturación, barra de luminosidad, tres deslizadores, campos H/S/L editables, HEX, muestra RGB, doce tonos de partida, casilla para conservar máscaras/adornos y botones Original, Aceptar y Cancelar. Se puede mover arrastrando la cabecera. Aceptar emite el estado elegido; Cancelar, Escape, la X y destrucción de la ventana restauran el estado completo recibido al abrir. Original selecciona el modo A-D de reserva, conservando el índice legacy. La casilla es un dato de estado para el renderer, no una modificación de texturas implementada en esta DLL.

## Componente para integrar

`build/NexusHairHslUi.dll` exporta cuatro funciones C con convención stdcall:

- `NexusHslOpen`: crea una ventana propiedad del HWND indicado, en el mismo hilo UI.
- `NexusHslRead`: devuelve una copia del estado actual.
- `NexusHslSet`: establece un estado válido y emite Preview.
- `NexusHslFinish`: acepta o cancela y cierra la ventana.

El contrato en `hsl_picker.h` separa modo Original/Custom, HSL, RGB 0x00RRGGBB, índice A-D original y protección de adornos. Los eventos Preview/Apply/Cancel son callbacks locales; no son mensajes de red de L2. El callback recibe una copia temporal y debe copiarla si la retiene. No debe descargar la DLL mientras existan ventanas. El anfitrión debe mantener un bucle de mensajes e incorporar IsDialogMessage para Tab/Enter/Escape. No abrir desde DllMain ni desde un hilo de render ajeno. Todas las funciones de manipulación deben invocarse desde el mismo hilo de la ventana. El parámetro options=1 permite crearla oculta para pruebas.

La integración pendiente es un botón en el creador nativo y un puente que traduzca Preview a la ruta de tinte del personaje, Apply al estado del creador y Cancel al snapshot inicial. Antes de instalar ese puente falta implementar/verificar el material dinámico que conserva alfa y máscara de tinte. Después, conectar creación, guardado, selección y sincronización con otros clientes. La DLL preparada no realiza esas tareas ni manipula memoria del juego.

## Verificación

Compilado con Visual C++ 2019 y runtime estático, para la arquitectura de 32 bits del cliente. `build-native.cmd` reconstruye DLL, demo y tests. Las advertencias C4458 del SDK GDI+ son de las cabeceras del SDK; la compilación termina correctamente.

Pruebas nativas con ventanas ocultas: 4.096 conversiones RGB/HSL exactas, lectura de campos y estados, Preview, Apply, Original, Cancel, X, destrucción de ventana, Escape mediante IDCANCEL y rechazo de estados inválidos; 4.121 comprobaciones totales. La prueba independiente carga la DLL por LoadLibrary/GetProcAddress, verifica las exportaciones y ejecuta 50 ciclos abrir/previsualizar/aceptar/cerrar sin crecimiento de handles GDI/USER. Estos tests no certifican compatibilidad con el modo exclusivo de pantalla completa de L2 ni con su sistema de foco: eso requiere el puente dentro del cliente y pruebas con él.

No copiar esta DLL encima de engine.dll, NWindow.dll, d3d9.dll ni Interface.u. Es un componente adicional preparado para una integración posterior, no un reemplazo de las librerías existentes. Las fuentes y el contrato permiten revisar esa integración sin tocar los recursos activos ahora.
