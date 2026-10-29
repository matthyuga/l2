# Diagnóstico de control de ventanas

15/10/2026. Usuario solicita investigar por qué antes se pudo abrir el juego y ahora no se puede probar visualmente.

## Evidencia

- En esta conversación el cliente Damage se lanzó mediante Start-Process; el usuario confirmó la pantalla. No hubo captura ni login controlado por el agente con Computer Use. Esto es diferente de poder operar el juego.
- sky.list_windows falla antes de seleccionar cualquier juego: `Computer Use native pipe is unavailable: failed to connect native pipe: El sistema no puede encontrar el archivo especificado. (os error 2)`.
- El reinicio del kernel JS y la reinicialización de @oai/sky no resolvieron el error.
- Los procesos codex inicialmente activos pertenecían a la extensión VS Code (openai.chatgpt-26.1007.21434). No había procesos ChatGPT de la app de escritorio en esa comprobación.
- La aplicación de escritorio sí está instalada: paquete OpenAI.Codex 26.915.4065.0, nombre en menú Inicio ChatGPT. Se abrió por su acceso registrado, sin lanzar manualmente componentes internos ni cambiar configuración. Los procesos ChatGPT aparecieron correctamente.
- Abrir la aplicación y volver a probar no reconectó el Computer Use de esta sesión de VS Code, incluso tras recrear el kernel.

## Conclusión acotada

El bloqueo observado está en la conexión de esta sesión con el componente nativo de Computer Use; ocurre antes de entrar a L2 y no prueba un fallo del juego, de AnyDesk o del auto-flag. Que la app de escritorio estuviera cerrada era una hipótesis útil, pero abrirla por sí solo no solucionó esta sesión. No se determinó todavía si falta habilitar el componente en esa app o si esta sesión requiere iniciarse desde ella.

La documentación actual sitúa Computer Use en la app de escritorio y explica cómo habilitar su servidor y skill en Plugins > Computer Use: https://learn.chatgpt.com/docs/computer-use . Próximo paso soportado: revisar/activar allí el plugin e iniciar una tarea de Computer Use desde la app. No se debe prometer que un simple reload de VS Code resuelva este error.

La guía instalada ordena usar @oai/sky y no lanzar manualmente el ejecutable auxiliar. No se buscó ni ejecutó ese auxiliar, no se implementó un canal alternativo de teclado/captura, y no se modificaron permisos ni ajustes de seguridad.

Elven: pruebas de servidor completas en research/elven-autoflag/verification.txt; validación visual continúa pendiente.

## Reintento con plugin actualizado

15/10/2026, después de la autorización de encargarse de la recuperación: se leyó Computer Use 26.915.31945, se inicializó y se recreó el kernel JS. list_windows sigue devolviendo el mismo error os error 2. ChatGPT permanece abierto. Las entradas computer-use y unified-computer-use de plugins en config.toml tienen enabled=true; no se modificaron. Esto verifica los toggles locales del plugin, no el estado de su servidor nativo ni de los permisos de la app.

Plugin Management no pudo resolver computer-use@openai-bundled como plugin público del catálogo; su búsqueda no ofreció una entrada útil para administrar este componente incorporado. No hay una reparación ejecutada ni una conexión recuperada. El siguiente paso disponible es activar/iniciar Computer Use desde la app de escritorio y continuar allí la tarea; no se dispone de una herramienta para realizar esa activación interna desde esta sesión fallida.
