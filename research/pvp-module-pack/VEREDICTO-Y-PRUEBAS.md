# Veredicto para las salas HELLGAMES

15/10/2026. **Conviene ampliar nuestras salas sobre Mobius y adaptar ideas concretas de Orion; no instalar ninguno de estos módulos tal cual.** Usar sus archivos como material de partida es viable, especialmente los polígonos y spawns, pero reemplazar nuestro controlador perdería reglas que ya pedimos.

## Qué se probó realmente

- Se compilaron las clases originales `L2RandomZone` de Orion, `FlagPvPZone` y `PvpFlagTaskManager` de nuestro source en un banco Java separado. Se ejecutaron **15 comprobaciones** sobre esos métodos reales usando colaboradores mínimos para jugador, zona, mensajes y motor. Todas reprodujeron el comportamiento esperado, incluidos los casos problemáticos. No significa que los módulos estén libres de fallos.
- `FlagPvPZone.java` también compiló contra el **GameServer.jar desplegado**, sin esos colaboradores. El .class quedó exclusivamente en `review-tests/native-jar-compile`, sin cargarlo en el servidor.
- Se descargó el parche Lisvus desde la API del gist, conservando revisión y SHA256. Su clase original falla al compilar contra una API mínima que declara updatePvPFlag: llama `updatetPvPFlag` al salir. Es una errata reproducida bajo esa API; no se construyó un servidor Lisvus completo.
- Se validaron los **39 spawns** de los siete ejemplos Orion: todos dentro del polígono XY y del intervalo Z definido. IDs 1–7 contiguos y duración 2700 segundos por zona. Esto no verifica suelo, colisiones, geodata ni equilibrio del mapa.
- ChaoticZone y el parche del foro Mobius se revisaron a partir del código publicado/indexado en sus temas. El acceso directo al foro devolvió 403 previamente; **no se dispone de una descarga íntegra verificada ni se ejecutaron esos dos módulos**.

No se inició otro servidor, no se instalaron clases descargadas en el runtime, no se tocó la base de datos ni se realizó una prueba nueva dentro del cliente. Ninguna prueba certifica aún compatibilidad visual o de red de los packs completos.

## Lo observado en cada alternativa

### Mobius propio: buena base, insuficiente sin coordinar el flag

Se reprodujeron entrada con flag, salida con limpieza inmediata, muerte con limpieza y revive con flag. También se reprodujeron dos situaciones:

1. Entrar en dos objetos de zona y salir de uno borra el flag sin comprobar que el otro siga requiriéndolo. Es una comprobación del callback; el banco no reproduce el motor espacial completo.
2. Un jugador ya registrado en la tarea de expiración, con plazo vencido, pierde el flag aunque el callback de entrada lo haya puesto a uno. La clase de zona no retira ni coordina esa tarea.

Estas son razones para integrar el flag con el estado de sala, no añadir simplemente un XML alrededor de Elven. La clase nativa no cura ni aplica Noblesse.

### Orion: referencia útil de mapas y ciclo de zona

El banco confirmó que una zona inactiva no actúa, y que el jugador debe tener asignada previamente la instancia configurada para que la entrada lo marque. No es por sí solo un sistema de ingreso a salas.

Cuando activa auto-flag, detiene el flag previo y lo fija a uno. Al salir del contorno, devuelve inmediatamente al jugador a la instancia cero, detiene el flag y solicita updatePvPStatus. En el banco esa última llamada se registra con un colaborador; no se ejecutó el Player original de Orion. Esto no se puede importar como si garantizara un plazo concreto en Mobius.

El código real de nuestro Player.updatePvPStatus devuelve sin hacer nada si el jugador está en ZoneId.PVP. Además, coordinar el flag de combate previo requiere revisar stopPvPFlag/startPvPFlag y el temporizador. Copiar solo las llamadas de Orion no resuelve esa integración.

La configuración descargada prohíbe Cardinal, Eva Saint y Shillien Saint por defecto; el callback expulsó al Cardinal de prueba. La comparación se hace con la clase activa. Es una política ajena a nuestras salas y tampoco representa por sí sola un control de habilidades acumuladas de subclases.

Otros resultados: death/revive no tienen acciones en esta clase; una lista de spawns vacía falla al elegir una posición; pedir el centro de valla sin configurarlo falla. Validar el catálogo antes de activar una sala evita estos casos.

Revisión estática del reloj, no ejecutado en el banco: elige un número entre 1 y cantidad de zonas y busca ese ID. Los XML actuales cumplen esa numeración, pero quitar IDs intermedios puede dejar selección sin zona. No excluye el ID actual, así que puede repetir mapa. Descuenta ticks programados, sin usar un plazo monotónico; un retraso del servidor puede alargar la ronda. Sus anuncios se emiten globalmente. Las vallas dependen de clases propias de Orion y no se probaron en nuestro cliente.

### ChaoticZone: ideas de salida, demasiadas diferencias para usarlo directamente

El código publicado configura mensajes, flag y efectos, y al salir agrega al jugador al temporizador normal. Ese plazo es de flag; **no es nuestra expulsión vulnerable de cuatro segundos**. Hay condiciones de curación inconsistentes y un ejemplo de Monastery con minZ mayor que maxZ. El objetivo de no alterar HP/CP/MP ni efectos obliga a retirar sus rutas de curación/Noblesse. Publicación etiquetada C5, paquetes/API antiguos: adaptación necesaria.

Fuente: https://l2jmobius.org/forum/index.php?topic=5629.0 .

### Otros parches básicos

El del foro Mobius agrega Noblesse al entrar y quita flag al salir; no aporta lobby, ronda o voto. Lisvus C4 es más pequeño, pertenece a otra base y tiene la errata indicada. Ninguno mejora lo suficiente nuestra base como para justificar reemplazarla.

Fuentes: https://l2jmobius.org/forum/index.php?topic=11872.0 y https://gist.github.com/JMD13/8a14f647661440a3333405f8e6619c0b .

## Qué aprovechar y cómo

| Componente | Decisión recomendada |
|---|---|
| Controlador de ingreso/salida | Mantener PvpRooms y sus reglas de cuatro segundos, vulnerabilidad y regreso a Giran |
| Flag | Integrarlo con el estado de sala y franja; mantener el flag forzado mientras corresponda, coordinar expiración y no borrar una obligación de otra zona/combate |
| Catálogo de mapas | Tomar la estructura de datos de Orion: nombre, polígono, altura, apariciones y duración; validar antes de cargar |
| Primera sala | Conservar Elven y su instancia; usarla para probar el conjunto antes de sumar zonas |
| Otras zonas | Guardar las siete Orion como candidatas, sin activarlas todas; Primeval necesita definición y prueba propias |
| Reloj de ronda | Plazo monotónico y avisos a participantes de la sala |
| Selección siguiente mapa | Votación al terminar el tiempo, como pidió Kevin; no copiar selección aleatoria automática |
| Cambio de mapa | Separarlo del cruce del borde; definir el traslado de jugadores vivos/muertos, summons y desconexiones sin reiniciar recursos/efectos |
| Vallas | Posponer; no son necesarias para nuestra franja de salida |
| Buffs/heal/restricciones | No adoptar Noblesse, curación ni prohibiciones de clase de los ejemplos |

Se pueden modificar archivos externos en una copia de trabajo y preservar originales/licencias. Para este proyecto, la adaptación más pequeña consiste en crear un catálogo de salas propio y ampliar el controlador Mobius existente. Portar todo el sistema Orion implica trasladar más dependencias y rehacer casi todas sus transiciones para conseguir el mismo diseño.

## Evidencias reproducibles

- `run-isolated-review.py`: prepara el banco y compila/ejecuta los métodos originales.
- `review-tests/behavior-results.txt`: salida de las 15 comprobaciones.
- `review-tests/results.json`: alcance, geometría y hashes de fuente.
- `review-tests/compile.log`: compilación de banco.
- `review-tests/native-jar-compile/`: clase compilada contra nuestro JAR; resultado registrado por separado.
- `review-tests/lisvus-download.json`, `lisvus-0.patch`, `lisvus-compile.log`: parche original y resultado de compilación acotado.

La prueba no implementa aún la adaptación recomendada. El siguiente trabajo es integrar flag con la sala Elven y probar conservación de flag/recursos y salida vulnerable con el servidor real; después, reloj y votos.

Actualización posterior del 15/10/2026: la etapa de auto-flag fue autorizada, instalada y comprobada en el servidor activo. Ver `E:\l2-local\SALAS-PVP-ELVEN-AUTOFLAG.md` y `research/elven-autoflag/verification.txt`. Reloj y votación siguen pendientes. Los resultados anteriores se conservan como análisis de los módulos antes de esa adaptación.
