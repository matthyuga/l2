# Brillo global al abrir L2 — diagnóstico inicial

24/10/2026. El usuario observa el escritorio y la imagen en VS Code sobreiluminados mientras L2 está abierto. Las capturas no reproducen ese cambio. También afecta la percepción del retrato dentro de la demo.

Hipótesis: corrección gamma de salida aplicada por el cliente/driver; no atribuida todavía de forma concluyente. Microsoft documenta que D3D9 SetGammaRamp puede afectar toda la pantalla en modo ventana. Fuente: https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-setgammaramp .

Lectura sin modificar cliente: Option.ini tiene StartupFullScreen=False y Gamma=0.8. Copia descifrada de l2.ini: render D3DDrv.D3DRenderDevice; WinDrv.WindowsClient Brightness=0.8, Contrast=0.7, Gamma=0.8. No se interpretan esos valores como prueba suficiente del origen.

GetDeviceGammaRamp sobre el DC del escritorio, con proceso L2 abierto, devolvió una rampa prácticamente lineal (i*256). Esa medición puntual NO captura el estado con el juego necesariamente en primer plano y NO confirma una curva alterada. Guardada en gamma-while-l2-open.json. El cambio podría depender del foco, del monitor, del driver u otra etapa de salida.

Siguiente diagnóstico: comparar juego activo, minimizado y cerrado o registrar pasivamente llamadas de gamma del proceso. No se modificaron gamma global, calibración de Windows, opciones del cliente ni texturas de Amber.
