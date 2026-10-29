# Navegación de Studio y adaptación al Taller

17/10/2026. Análisis estático y pruebas de la implementación propia; no se probó Chara Studio en ejecución.

## Qué se comprobó

REA inspeccionó los cuerpos CIL de `Studio.CameraControl.InputMouseProc`, `InputMouseWheelZoomProc`, `InputKeyProc` y `CameraUpdate` en la evidencia de miembros `ev_4533f1694573c21bce09730c23364c24f276a4305ea22f3268576d0f352b7914` del informe anterior. La selección mantiene el hash/MVID de Assembly-CSharp.dll. La desensamblación estática con Mono.Cecil ya instalado conserva instrucciones compactas que las anclas REA no enumeran individualmente; ver camera-cil.txt y read_camera_il.ps1. No se ejecuta código del juego.

En InputMouseProc, los bloques son:

| Entrada | Bloque IL | Operación observada |
|---|---|---|
| Izquierdo + derecho | IL_0098 a IL_0147 | Traslada el centro en X/Z locales de cámara |
| Izquierdo | IL_014c a IL_01f6 | Modifica rotación yaw/pitch |
| Derecho | IL_01fb a IL_027e | Mouse Y modifica altura del centro; Mouse X modifica distancia |
| Central | IL_0283 a IL_0329 | Traslada el centro en X/Y locales de cámara |

Se evita iniciar arrastre sobre UI y se mantiene mientras alguno de los botones permanece pulsado. Esas ramas respaldan la navegación adaptada; no se afirma igualdad exacta de unidades/sensibilidad entre Unity y el navegador.

## Shift y Ctrl proceden del pack instalado

`BepInEx/config/com.joan6694.illusionplugins.kkus.cfg` habilita Camera Speed Modifier Keys, con Speed Modifier Fast=4 y Speed Modifier Slow=0.6.

REA inspeccionó `HSUS.Features.CameraShortcuts` en KKUS.dll: evidencia padre `ev_68af4aa8a58fcdc7b7d3ba8b8cdfd425503171a5963a49b05e0e14ac9151069c`. Su Awake referencia el parche InputMouseProc_Patches. La lectura Cecil del parche muestra que modifica InputMouseProc de Studio.CameraControl y que GetCameraMultiplier consulta LeftControl (306) antes de LeftShift (304), multiplicando GetAxis por CamSpeedSlow/Fast. Se conserva en kkus-camera-cil.txt.

El Taller adopta Ctrl ×0,6 y Shift ×4, con prioridad de Ctrl si se pulsan ambos. Usa eventos de teclado del navegador; admite los modificadores de ambos lados del teclado. La rueda también admite sensibilidad modificada en nuestra implementación.

## Atajos y cámaras del Taller

- W / E / R: mover / rotar / escalar el objeto seleccionado.
- F: trasladar cámara y punto de enfoque al pivote del objeto, conservando ángulo y distancia relativos.
- C: mover el pivote del objeto al punto de enfoque actual de la cámara. No lo coloca literalmente dentro de la cámara. Respeta Bloqueado y participa en Deshacer.
- Q: mostrar/ocultar pivotes seleccionables de los objetos. El seleccionado conserva su indicador. Son nodos de objetos, no vértices ni huesos internos de malla.
- Diez slots con Save y número: Save captura posición, target y FOV; el número restaura la toma. Se incluyen en proyectos JSON y borradores. Guardar versión escribe esa información en disco.
- Panel izquierdo de190px; Mostrar panel lo contrae a rail de44px; pulsar un icono vuelve a abrirlo. El área3D permanece a la derecha.

Estas asignaciones C/F/Q/W/E/R implementan la solicitud de Kevin; no se atribuyen todas al código base de Chara sin haber rastreado cada plugin que modifica atajos.

## Verificación

`research/scene-editor/verify-studio-controls.cjs` verifica eventos reales de ratón y teclado en navegador aislado: orbitar, elevación/distancia, desplazamiento central, combinación izquierdo+derecho, velocidad Shift/Ctrl, protección de bloqueo, F/C, Q, guardado de tomas, persistencia en disco y recuperación tras recarga, validación de cámaras y panel compacto. Resultado en studio-controls-verification.json. Las pruebas no certifican una sesión runtime de Chara Studio.
