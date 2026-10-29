# Probar personalización racial

Implementación GM del 9 de octubre de 2026. Menú básico dentro del cliente,
gratuito; el NPC VIP y el precio público quedan para una etapa posterior.

## Uso

Entrar por `2-JUGAR.cmd` y escribir `.raza`. Para acceder mediante una macro,
poner `.raza` como primera línea. También hay un acceso desde Build Lab; este
menú siempre modifica el propio personaje GM, aunque Build Lab esté apuntando
a otro personaje.

1. Pulsar `Clase` y elegir la principal o una de las tres subclases propias.
   Mystic Muse propone Elfo místico; Paladin, Humano guerrero;
   Phantom Summoner, Elfo oscuro místico; Overlord, Orco místico.
   Se toma la raza/perfil nativo de la clase, aunque tu aspecto actual sea otro.
2. Marcar `[X] Apariencia`, `[X] Atributos` o ambas. Las casillas deciden
   qué tomar de la clase seleccionada. No cambia tu clase activa ni sus skills.
   `Elegir razas manualmente` conserva la posibilidad de usar destinos distintos.
3. Consultar las páginas Atributos, Combate y Otros. Los valores Actual/Nuevo
   y las diferencias salen de las fórmulas reales con clase/equipo/dyes/buffs
   actuales. Los críticos son valores del servidor, no porcentajes directos.
4. Si se cambió equipo, buffs o clase, pulsar Actualizar valores. Se conservan
   las selecciones; la hora indica la nueva lectura.
5. Pulsar `Confirmar`, visible antes de la tabla. Abre el resumen sin cambiar
   al personaje. `Cancelar` descarta la selección y la confirmación sin aplicar.
   Para aplicar, estar vivo y fuera de combate, en ciudad
   con zona de paz, sin duelo/olimpiada/instancia/comercio/pesca/montura.
6. Pulsar `Aplicar` en el resumen confirmado. Aplicar desde la comparación
   pide confirmar primero. Si cambió el contexto o pasó un minuto, hay que revisar
   nuevamente la comparación. Una confirmación no puede reutilizarse.

La elección se aplica al origen racial del personaje, no se guarda un origen
distinto por subclase. La comparación usa tu clase activa, equipo y buffs actuales,
incluso si elegiste otra clase como referencia. Explorar no modifica al personaje.
Elegir solo apariencia conserva los seis
atributos y su perfil. Elegir solo atributos conserva el aspecto. Ambos admite
destinos distintos, por ejemplo aspecto orco y atributos elfo místico.

El cambio no repone HP/CP/MP: conserva los recursos restantes, limitados al
nuevo máximo si baja. Al cambiar apariencia, rostro y cabello se reinician a0
para evitar índices incompatibles entre razas; el sexo se conserva.

El menú muestra la raza de destino por nombre. No incluye una representación
3D previa del modelo; queda pendiente comprobar visualmente el aspecto aplicado
y el diseño del menú en el cliente real. La compilación y las pruebas del motor
no sustituyen esa revisión visual.

## Persistencia y cálculo

`characters.race` sigue siendo la raza visual. Las variables `RACIAL_STAT_RACE`
y `RACIAL_PROFILE` guardan la raza y el perfil de atributos. Para personajes
anteriores sin la variable nueva, se usa su raza actual, preservando sus stats.

La proyección usa un contexto de plantilla por jugador y por hilo; no cambia
su raza real, no guarda y no comunica stats proyectados al resto del servidor.
Los getters de recursos máximos omiten efectos de regeneración/recorte mientras
están en ese contexto. Al salir o fallar la lectura, el contexto se limpia.

La telemetría identifica apariencia y origen por separado. El panel usa el
origen estadístico al mostrar los seis atributos, y descarta capturas que no
coinciden con el origen vigente. Las capturas de nuevos perfiles incluyen el
origen en su clave para no sobrescribir el historial de otro origen.

## Verificación

- Compilación completa del núcleo1617 archivos y de scripts/JS.
- Selector de clases activo en la versión2: controles antes de la tabla,
  con texturas de botones compatibles con Interlude.
- `RaceCustomizationVerification SUCCESS: 68 checks`: nueve orígenes,
  principal/tres subclases como referencia, controles previos a la tabla,
  aplicación sin confirmar bloqueada en el menú, elección sin activar clase,
  proyección=aplicación, sin modificar recursos al consultar, aislamiento entre
  hilos y limpieza ante excepción, tres modos, sin curación al aplicar,
  principal/skills/tres subs conservadas y persistencia al recargar.
- `RacialProfileVerification SUCCESS`: ocho comprobaciones existentes.
- Las pruebas usan exclusivamente `RaceMenuProbe` de `racialmenutest`; queda
  invisible y desconectado, sin NPC ni spawn. Hellkevin no fue modificado.
- Roster de19 y equivalencia con perfiles verificados nuevamente al finalizar.
- Respaldo/evidencia en `backups/race-customization-2026-10-09`.

Las pruebas se activan al iniciar el servidor con
`Start-L2Local.ps1 -VerifyRacialCustomization`; no se ejecutan en los arranques
normales. No activar en una instancia ya iniciada ni reiniciar con cliente conectado.
