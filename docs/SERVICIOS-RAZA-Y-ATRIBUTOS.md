# Servicios de cambio de raza y origen de atributos

Propuesta del usuario, 9 de octubre de 2026, actualizada con dos casillas
independientes. Prototipo GM implementado con `.raza`, selecciones, comparación,
actualización y confirmación. Instrucciones: PROBAR-PERSONALIZACION-RACIAL.md.
El acceso público, el NPC VIP y el cobro todavía no están implementados.

## Objetivo

Permitir cambiar una elección de creación sin rehacer el personaje. El precio
remunera la modificación y la personalización estética; todas las plantillas de
atributos ofrecidas deben existir también en la creación gratuita de personajes.
El equilibrio depende además de las condiciones de uso y de las reglas generales
de clases, equipo y combate del servidor.

## Acceso inicial por comando y futuro NPC VIP

Se propone desarrollar primero el apartado independiente mediante el comando
`.raza`, disponible inicialmente para GM en el laboratorio. Una macro del
cliente puede contener `.raza` y servir como acceso rápido al menú. La macro
solo abre la interfaz; las consultas, simulaciones, validaciones y cambios se
resuelven en el servidor.

Después se integra al NPC VIP como una opción «Apariencia y atributos raciales»
entre sus otros servicios. El comando y el NPC deben abrir el mismo apartado y
compartir el servicio de selección, vista previa, confirmación y aplicación.
No se mantienen dos implementaciones de reglas o cobro.

Flujo previsto:

1. Abrir por `.raza`/macro o por el NPC VIP.
2. Ver apariencia, origen de atributos y clase activa actuales.
3. Marcar qué cambiar y seleccionar los destinos independientes.
4. Consultar la comparación Actual→Proyectado y usar Actualizar valores cuando
   se cambie equipo, buffs o clase.
5. Revisar un resumen final de ambos cambios y el precio total, cuando exista.
6. Confirmar para que el servidor valide condiciones y aplique la operación.

Abrir o actualizar el menú no cambia el personaje. En el laboratorio, el resumen
identifica la prueba GM gratuita. El acceso público, los requisitos VIP y el
precio quedan pendientes; no se habilitan automáticamente por crear el comando.
Si el servicio público se restringe al NPC o requiere VIP, usar el comando o
una macro debe respetar esos mismos requisitos, sin eludirlos.

El formulario será HTML compatible con el cliente Interlude. Las dos casillas
son controles independientes; si el cliente no admite un checkbox nativo, se
representan mediante botones de activar/desactivar con estado visible. No se
depende de formularios o JavaScript de navegador dentro del cliente.

## Un formulario con dos casillas independientes

El servicio se presenta como «¿Qué querés cambiar?»:

- [ ] Cambiar apariencia racial.
- [ ] Cambiar atributos raciales.

| Apariencia marcada | Atributos marcados | Resultado |
|---|---|---|
| Sí | No | Cambia el aspecto racial; conserva el origen y perfil de atributos actuales |
| No | Sí | Cambia el origen y perfil de atributos; conserva el aspecto racial actual |
| Sí | Sí | Cambia ambos, con una elección independiente para cada uno |
| No | No | No hay operación; confirmar permanece deshabilitado y no hay cobro |

Marcar apariencia habilita el selector de raza visual. Marcar atributos habilita
el selector de origen de atributos. Si se marcan ambos, pueden elegirse la misma
raza o razas distintas: por ejemplo, aspecto de orco y atributos de elfo místico.
Una casilla desmarcada conserva su valor actual durante toda la operación.

El origen se elige como una plantilla completa: humano guerrero, humano místico,
elfo guerrero, elfo místico, elfo oscuro guerrero, elfo oscuro místico, orco
guerrero, orco místico o enano. El enano tiene una única plantilla nativa;
no se ofrecerá un perfil místico enano inventado ni una opción duplicada con precio.

Cambiar de perfil FIGHTER/MYSTIC forma parte de la elección de origen. El botón
actual de cambio de raza conserva ese perfil, por lo que todavía no cubre todas
las combinaciones solicitadas.

## Ejemplo de Hellkevin

- Apariencia humana + origen humano guerrero: base STR40/DEX30/CON43/INT21/WIT11/MEN25.
- Apariencia humana + origen elfo místico: base STR21/DEX24/CON25/INT37/WIT23/MEN40.
- Solo apariencia: pasar a aspecto de elfo manteniendo la primera plantilla
  humana guerrera; equipo, dyes y efectos sin cambios conservan sus aportes.
- Ambos, eligiendo elfo místico como origen y elfo como aspecto: apariencia
  élfica y la segunda plantilla de atributos.

Equipo, dyes, pasivos y buffs siguen calculando los valores finales normalmente.
No se trasladan los valores finales de otro personaje ni se suman dos orígenes.

## Vista previa estratégica de atributos y estadísticas

El usuario solicita que la gente pueda comparar configuraciones y decidir su
estrategia antes de comprar. Cada cambio en las casillas o selectores actualiza
una comparación «Actual → Proyectado», sin aplicar el cambio al personaje.

| Grupo | Datos de la comparación |
|---|---|
| Atributos base | STR, DEX, CON, INT, WIT y MEN de cada origen |
| Atributos finales | Los mismos seis valores después de dyes, equipo, pasivos y efectos |
| Recursos máximos | HP, CP y MP |
| Ataque y defensa | P. Atk., M. Atk., P. Def. y M. Def. |
| Velocidad de combate | Atk. Speed y Casting Speed |
| Precisión y críticos | Precisión, evasión, crítico físico y mágico; modificadores críticos disponibles |
| Movimiento y alcance | Velocidad al correr/caminar y alcance de ataque |

Cada fila muestra valor actual, valor proyectado, diferencia absoluta y cambio
porcentual cuando el valor de partida permite calcularlo. «Sube», «baja» y «sin
cambio» deben distinguirse con texto o símbolos además de color. Un valor más
alto no se etiqueta automáticamente como una configuración mejor: el jugador
decide qué compensaciones favorecen su estilo.

La comparación conserva la misma clase activa, principal, subclases, niveles,
skills aprendidas, equipo, encantamientos, dyes y buffs/toggles vigentes en ambos
escenarios. La pantalla identifica clase activa y condiciones de la captura.
Así, la diferencia representa la selección de origen y no un cambio simultáneo
de equipo o buffs. Si las condiciones cambian mientras se elige, se recalculan
ambas columnas con una misma captura reciente antes de confirmar.

La pantalla incluye el botón **Actualizar valores**. Al pulsarlo, consulta el
estado actual del personaje conectado en el GameServer y recalcula tanto la
columna Actual como Proyectado con esa misma captura. Conserva las casillas,
la apariencia y el origen seleccionados: el jugador puede cambiar equipo,
buffs, dyes o clase activa y volver a comparar sin rehacer su selección.
Muestra la hora de la última actualización. Abrir el menú y cambiar una opción
también generan una comparación nueva; no se requiere refresco continuo.

Actualizar es gratuito y no aplica cambios al personaje. Si la lectura falla,
no se presentan datos antiguos como recién actualizados. Antes de confirmar
se verifica la vigencia de las condiciones; si cambiaron y afectan los valores
mostrados, se actualiza la comparación para que el jugador revise el resultado
antes de aceptar y pagar.

En el modo solo apariencia, los atributos y estadísticas deben conservarse;
la vista previa muestra la nueva apariencia y valores sin cambios. En los modos
que cambian atributos, se muestran tanto ganancias como pérdidas. HP/CP/MP se
comparan por su capacidad máxima, separada de los recursos restantes del combate.

Los valores proyectados deben obtenerse del cálculo real del servidor en una
simulación aislada, sin mutar ni guardar el personaje del jugador. No se usarán
porcentajes inventados ni valores finales copiados de otro personaje. Debe
comprobarse que la proyección coincide con el resultado aplicado bajo las mismas
condiciones. Los críticos deben presentarse con las unidades correctas; un valor
interno de tasa no se rotula directamente como porcentaje.

La vista previa debe acompañar el resumen de compra y el precio total pendiente
de definición. Explorar opciones no cobra. La tabla compara la ficha del
personaje bajo las condiciones indicadas; daño por habilidad contra un rival,
DPS y resultados de PvP requieren cálculos adicionales y no se infieren de
M. Atk. o P. Atk. por sí solos.

## Condiciones del producto

- Se conserva principal, subclases, progreso, skills aprendidas, inventario y equipo.
- Se selecciona un origen completo; no hay sliders ni mezclas por atributo.
- Un único formulario con las dos casillas y sus selectores independientes.
- Vista previa de apariencia, atributos base/finales y estadísticas derivadas,
  con comparación actual/proyectado y diferencias, como se describe arriba.
- Confirmación con elección actual, elección nueva y precio total cuando esté
  definido. Si se cambian ambos, se confirma una sola operación.
- Aplicación en un lugar seguro, fuera de combate, duelo, arena y eventos activos.
- El cambio no funciona como cura ni como reposición de CP/MP; el tratamiento de
  recursos debe definirse y comprobarse junto al servicio.
- Una elección idéntica a la actual no genera un cobro. El cálculo debe basarse
  en cambios efectivos, no solamente en las casillas marcadas.
- Precio, moneda y disponibilidad pública pendientes de decisión. Durante el
  desarrollo, las pruebas deben mantenerse en herramientas GM.

## Cambio técnico necesario

Hoy `characters.race`/`Player.getRace()` determinan la apariencia y también la
plantilla de los seis atributos; `RACIAL_PROFILE` guarda FIGHTER/MYSTIC.
Se necesita una selección racial de atributos persistente e independiente de
la apariencia, además del perfil. Los personajes existentes deben conservar
exactamente sus atributos actuales al migrar.

Cambiar solo apariencia debe conservar el origen de los seis atributos y el
perfil guerrero/místico. Cambiar solo atributos debe conservar la apariencia.
Aplicar ambos debe persistir ambas elecciones como una única operación; el
futuro cobro debe completarse conjuntamente con el cambio, evitando cambios
parciales y cobros repetidos.

La separación de atributos solicitada afecta a los seis atributos base. Las curvas por nivel,
velocidades base y otras bases que hoy dependen de la clase activa conservan las
reglas documentadas en RAZA-Y-PERFIL-FIJO.md. El servicio no concede skills raciales
adicionales ni profesiones por cambiar el origen de atributos.

Actualizar y comprobar conjuntamente: creación/carga/guardado de Player,
servicios de cambio explícito, Build Lab, panel y telemetría. Las capturas deben
identificar tanto apariencia como origen de atributos y distinguir la nueva
regla de los registros históricos.

Verificar con personajes técnicos: las cuatro combinaciones de casillas; cambio
de aspecto con atributos intactos; mismo aspecto con dos orígenes distintos;
cambio de ambos con destinos iguales y diferentes; principal/subs intactas;
proyección igual al resultado aplicado con mismas condiciones y sin efectos
secundarios al explorar opciones; persistencia tras relog; rechazo durante combate; selección sin cambios y
repetición sin doble cobro cuando se implemente el pago. Hellkevin no debe
cambiar automáticamente por la preparación de este servicio.
