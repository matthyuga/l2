# Muelle aéreo de Gludio sobre el Coliseo

Instalación de prueba: 14/10/2026, en `E:\l2-local` y cliente `E:\l2`.

## Entrar

- Personajes nuevos de las cinco razas: punto inicial `149000,46700,12040`.
- Personajes existentes: desmontar y escribir **`.muelle`**, estando vivos, fuera de combate, sin flag/karma y fuera de instancias/Olympiad.
- Para bajar a la práctica: **`.muelle coliseo`**, desde el muelle.
- Diagnóstico de llegada: **`.muelle estado`** muestra ubicación, instancia y si la carga del teleport sigue pendiente; funciona también antes de completar el viaje.
- El muelle es una zona pacífica. Su reaparición local devuelve allí; esto no cambia las reapariciones de todo el mundo.

Los personajes existentes no fueron movidos masivamente ni se modificó su equipo para esta instalación. No hay cambio de nivel inicial, rates ni reglas de subclases por este trabajo.

## Qué se instaló

Ocho actores arquitectónicos del muelle recuperado de Gracia (siete mallas distintas), trasladados sobre el Coliseo en `24_19.unr`. El suelo principal queda alrededor de Z=12016, frente al Coliseo inferior alrededor de Z=-3400. No se reemplazó el Coliseo por otro escenario.

Se conserva el cielo y el ciclo de iluminación del mapa nativo. Debajo de la roca se añadió una superficie opaca de nubes a Z=7600, de aproximadamente 200.000 unidades de ancho. Su material nativo mezcla bruma azulada y blanco utilizando la máscara alfa de WhiteCloud; incluye escalado y desplazamiento mediante TexPanner. Su propósito es ocultar el terreno inferior. No se instaló un sistema meteorológico nuevo ni lluvia global.

La superficie de nubes no tiene colisiones ni suelo de servidor. El muelle sí tiene geodata derivada de sus mallas con colisión: 15.145 triángulos, 41.900 celdas nuevas y 34.790 capas alcanzables desde la llegada en el análisis del generador. Los bordes sin vecino transitable se cierran. Esto no acredita un recorrido visual exhaustivo de barandillas y escaleras.

Los paquetes nuevos usan nombres HGGludio para evitar sustituir texturas originales que comparten nombre con Gracia. Se convirtieron explícitamente la estructura de las mallas y los bloques nativos de materiales de license 37 a 28; no se limitó a cambiar la cabecera. Se conservaron los píxeles de mipmaps, los grafos de materiales y las colisiones nativas; se descartaron los metadatos de shaders compilados de la crónica posterior.

## Verificaciones y límites

- Lectura completa de 98 mallas del paquete convertido con L2unreal, incluidas las tres estructuras de colisión con offsets reubicados.
- Carga nativa de las siete mallas utilizadas, sus texturas/shaders y el material de nubes con UModel.
- Dependencias de paquetes y objetos resueltas. Core.Package y Engine.StaticMesh son clases nativas sin export de script.
- Once paquetes de cliente con envoltura 121, clave vinculada al nombre, roundtrip completo y CRC32 independiente.
- Los 5.045 payloads originales del mapa distintos de myLevel permanecen idénticos; se conservan sus 1.788 actores de sonido y 2.007 actores originales, más los nueve añadidos.
- El servidor registró `GLUDIO_SKY_SMOKE PASS`: suelo alto, movimiento junto al nacimiento, zona pacífica, destino de reaparición y suelo inferior del Coliseo, con personaje transitorio sin inserción de cuenta/personaje persistente.

**Pendiente:** primera entrada visual desde el cliente y recorrido manual. No se certifican todavía la apariencia final de las nubes, ausencia de tierra visible desde todos los ángulos, niebla, iluminación, ni cada colisión del muelle. UModel avisa de FadeColor no soportado en su visor; la clase existe en el Engine del cliente. Las comprobaciones estructurales no sustituyen la entrada al juego.

No es todavía una edición reducida de Academy: los demás archivos y mapas siguen disponibles. Esta prueba añade una llegada aérea sobre el mundo actual.

## Respaldo y continuidad

Manifest: `research/gludio-sky/installation.json`.
Respaldo inicial: `backups/gludio-sky-20261014-092638`.
Restauración: `python research/gludio-sky/restore.py`, únicamente con cliente y GameServer cerrados. Verifica hashes y se niega a sobrescribir cambios posteriores. Restaura mapa, geodata y configuración anteriores; elimina solo los archivos nuevos de este despliegue. No reescribe posiciones persistentes de personajes que hayan visitado el muelle.

Código y evidencias: `research/gludio-sky/`. No reejecutar instaladores históricos ni build.py sobre el mapa ya instalado: aborta antes de duplicar actores. La configuración, script y XML se conservan en runtime, source y overlay local; no se hizo commit ni push.

## Revisión del acceso — 14/10/2026

Kevin informó que al usar `.muelle` veía Giran y no había llegado a ver el muelle. La posición persistida de Hellkevin quedó en 149000,46700,12021; eso acredita coordenadas del servidor, no la imagen observada por el usuario.

Se corrigieron dos diferencias estructurales del cliente:

- Nueve actores añadidos ahora tienen RF_HasStack, una cabecera de estado nativa y bDynamicActorFilterState/bIgnoredRange activados. Su construcción se contrastó con actores originales y [StaticMeshActorUtil de acmi/L2smr](https://github.com/acmi/L2smr/blob/master/src/main/java/acmi/l2/clientmod/l2smr/StaticMeshActorUtil.java).
- Los seis exports AcademyCloud ahora son públicos y cargables como recursos independientes (flags 0xf0004); el mapa importa el shader mediante su nombre de paquete.

Respaldo adicional: `backups/gludio-actor-registration-20261014-095028`. El manifest principal conserva el respaldo original y los hashes de la revisión instalada. No se cambió geodata, cielo original ni otros actores.

Se ejercitó el handler real `.muelle` en el servidor activo con un Player transitorio: Giran -> 149000,46700,12021 -> finalización del teleport mediante onTeleported -> Coliseo 148900,46100,-3403. PASS antes y después de añadir diagnóstico. Esta prueba no usa el render del cliente ni prueba que el usuario vea el destino.

El comando ahora usa instancia 0 y offset desactivado explícitamente, registra solicitud/destino y ofrece `.muelle estado`. Se recargaron únicamente los métodos de la clase custom GludioSky; código persistido en runtime/source/overlay, sin reiniciar el servidor ni cambiar personajes persistentes.

**Pendiente visual:** la conexión del control de Windows devolvió `Computer Use native pipe is unavailable` tras reintentos y reinicio del kernel. No fue posible observar la pantalla. No se ha demostrado aún la causa final de la percepción de retorno a Giran ni se declara validación visual completa. El cliente estaba cerrado durante las correcciones; la siguiente entrada cargará el mapa revisado. Evidencias: `actor-registration-v2.json`, `travel-probe.txt`, `reload-proof.txt`, `installed-native-load-proof.json`.

Actualización posterior del 14/10/2026: Kevin confirmó «ya se puede ver». Confirma visibilidad del muelle en su cliente tras la revisión; no equivale a una inspección visual del asistente ni a validar todas las colisiones, iluminación o ausencia de terreno desde cada ángulo. Preguntó por edición con UnrealEd/herramientas L2. UnrealEd.exe y UCC.exe están presentes en research/amber-l2/tools/l2editor/L2Editor; el pipeline usó UCC para assets. Abrir y guardar de forma segura el mapa completo con ese editor todavía requiere prueba sobre una copia. L2SMR se consultó como código fuente de referencia, no se acreditó una aplicación instalada.

## Aeronave estacionada integrada ? 14/10/2026

Ya instalada la aeronave externa adaptada junto al muelle: `.muelle nave` / `.muelle barco` para subir a cubierta; `.muelle` para regresar y `.muelle coliseo` para bajar. Modelo, materiales, geodata y zona instalados; handler real probado con Player transitorio. Todav?a no es transporte m?vil ni tiene NPCs; observaci?n visual ingame pendiente. Detalles, respaldo y rollback en `research/airship-integration/README.md`. Retirar esta integraci?n antes de intentar rollback hist?rico del muelle.
