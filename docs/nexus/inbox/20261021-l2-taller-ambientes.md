# Taller L2 — biblioteca de ambientes

21/10/2026. Kevin pidió ver los recursos descargados en el Taller de escenarios.

- Integración lista en `E:\l2-local\research\scene-editor`. Botón **☁ Ambientes** sobre el visor; controles **Vista → Ambiente**.
- Acceso: `http://127.0.0.1:32290/?ambientes=1`; servidor local iniciado con el Node portable. También sigue funcionando `19-EDITOR-ESCENAS-L2.cmd`.
- 89 cielos panorámicos y 182 texturas de partículas, con búsqueda/paginación. Cielo aplicable y emisor de prueba con imágenes originales. Presets de lluvia, tormenta con destellos, nieve, arena, viento/polvo, cenizas y niebla.
- 650 fragmentos WAV mono de hasta 12 s de audio ambiental de los ZIP de Sonniss terminados. Escucha manual, sin autoplay al abrir proyectos. Freesound sigue pendiente de login.
- Cielo y clima se guardan en proyecto/borrador y Deshacer/Rehacer; apertura de proyectos anteriores verificada.
- Originales intactos; vistas optimizadas en `research\atmosphere-library\preview`. Catálogo `preview-catalog.json`; constructor `build-preview.py`. **Actualizar descargas** incorpora nuevos recursos terminados.
- `verify-atmosphere.cjs` pasó en Chrome/WebGL: cielo, clima animado/pausa, partículas, audio/reproducción y rangos HTTP, export/API, rechazo de referencias desconocidas, apertura anterior, Deshacer/Rehacer, recarga y acceso directo. Informe `atmosphere-verification.json`; capturas `preview-biblioteca-ambientes.png`, `preview-ambiente-arena.png`.
- Se pausó temporalmente Sonniss para preparar previews y se reanudó al terminar. Ver estado real en `research\atmosphere-library\progress.json` y `run.json`.
- No se instaló clima en el cliente Interlude. Es simulación visual del Taller; continúa pendiente integración al juego.
