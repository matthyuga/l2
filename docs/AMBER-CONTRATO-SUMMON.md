# Amber: contrato y summon arquero

Implementado el 09/10/2026. Prototipo gratuito, reservado a GM.

Revisado en W11 el 10/10: nueva prueba de 50 checks PASS. Clase aislada
`AmberActorsV1.AmberArcher` con enganches del arco ajustados al rig, cuatro
iconos propios en habilidades/Alt+K y `.amber`, y partículas instaladas también
en system, la ruta real de paquetes del cliente. No cambió el balance ni el core.
Detalle actual y checklist: `CONTINUIDAD-W11/09_AMBER_VISUAL_ICONOS_W11_2026-10-10.md`.
La reproducción final en L2 sigue pendiente; las pruebas no la certifican.

## Cómo probar

1. Abrir **2-JUGAR.cmd**, entrar con Hellkevin y hablar con Amber en el Coliseo.
2. Retirar Nightshade u otro summon y elegir **Firmar contrato e invocar**.
3. Abrir `.amber` para las órdenes **Atacar al objetivo**, **Seguirme**, **Detener**
   y **Retirar Amber**. También se admiten las acciones nativas del summon.
4. Activar Beast Soulshots (6645) con clic derecho en el inventario del dueño.
5. Arrastrar las cuatro habilidades temporales a la barra. Alternativa para macros:
   `.amber invocar`, `.amber fuego`, `.amber lluvia`, `.amber romper`.
   Órdenes: `.amber atacar`, `.amber seguir`, `.amber detener`, `.amber retirar`.
6. Seleccionar un enemigo PvP visible a no más de 900 de Amber para la lluvia.
7. Romper el contrato fuera de combate retira Amber y sus habilidades. Conserva
   habilidades de clase y consumibles restantes. Reaceptar conserva las recargas.

`.amber` abre el apartado; para firmar hay que hablar con el NPC. El contrato
persiste hasta romperlo. Sus habilidades se reconstruyen al login y al cambiar
de clase. Desconectarse retira Amber; se invoca de nuevo manualmente. Sus buffs
no se conservan al retirarla. Morir o retirarla no rompe el contrato.

## Valores iniciales

| Acción | MP de Amber | Beast Soulshots | Duración / recarga |
|---|---:|---:|---|
| Invocar | 0 | 0 | Recarga 120s; sin cristales de mantenimiento |
| Disparo normal | 0 | 1 con autoconsumo activo | Cadencia nativa de arco |
| Flechas de fuego | 60 | 0 | 15s / 30s; PAtk +25% |
| Lluvia de flechas | 120 | 3 por lanzamiento | Carga 3,5s / recarga 45s |

Lluvia: posición fija capturada del target, radio 200 y tres pulsos separados
por 500ms. El enemigo puede evitarla saliendo del círculo. Daño físico de tres
disparos con shots, sin crítico; captura PAtk y fuego al iniciar. Amber queda
quieta y no ataca durante la carga; después recupera el movimiento mientras
la lluvia continúa. Interrupción, muerte, retirada, desconexión o ruptura cancelan
acciones pendientes. Excluye dueño, grupo, clan/alianza, paz, invulnerables,
otras instancias y duelos/Olympiad. Comprueba posición, altura y línea de visión.
Fuego añade 25% PAtk y 20 de poder de fuego nativo durante 15 segundos.
Las resistencias de fuego del objetivo intervienen en el daño.

Plantilla nivel80: HP3200, MP1500, PAtk1000, PDef330, MDef245, AtkSpeed350,
alcance700. Son datos de plantilla, no DPS ni daño final. Infinity Bow6619
es cosmético: no entrega el item hero ni concede sus efectos. Balance pendiente
de combates comparables con distintos equipos y buffs.

## Recursos visuales

El NPC902500/display59001 usa L2AmberNPCv5.ukx. El servitor902501/
display59002 usa L2AmberArcherV2.ukx y L2AmberArcherMotion.ukx, con tiro y locomoción
de humana Fighter. Dos animaciones especiales se adaptaron hacia arriba.
AmberEffectsV2.usk y AmberParticlesV2.u contienen disparos ascendentes, lluvia
normal/ígnea, carga de soulshot en el arco y trazas de fuego. El marcador
902502/display59003 usa AmberAnchorsV1.RainAnchor y una malla válida diminuta. El marcador
emite sus propios efectos para que la lluvia no fuerce nuevas animaciones en Amber.

Los catálogos de system-hud agregan las filas del contrato. La corrección de
movimiento modifica únicamente las filas 59001 y 59002 del catálogo NPC;
las otras 6520 filas se conservan byte por byte. Usar **2-JUGAR** o
**13-PROBAR-AMBER**: ambos lanzadores apuntan ahora al perfil system-hud.
El parche visual V3 cambió solamente la clase de59002 y añadió la sección
AmberArcher con sus movimientos BOW5; no reemplazó LineageNPC.u.

UModel reexportó los paquetes; Blender verificó las poses modificadas. UCC compiló
las partículas, y se verificaron orientación de las mallas y colores/transparencia.
**Pendiente observar la reproducción en L2:** agarre, selección de la animación,
marca y sincronización de efectos pueden necesitar ajuste. Las pruebas del servidor
no confirman la apariencia final.

Corrección de movimiento y altura, 09/10: la clase a_traderB_FHuman carecía de
entradas de animación para la categoría BOW (índice 5). Se agregaron únicamente
esas entradas en LineageNpc.int; apuntan a los movimientos de arco ya presentes
en el paquete de Amber, incluida la preparación de lluvia hacia arriba. No se
cambian las entradas de armas anteriores. Las dos mallas tenían MeshOrigin y
RotOrigin en cero; se restauraron Z=26,5 y Yaw=49152 del esqueleto Fighter usado
para riggearlas. Geometría, texturas y enlaces de animación quedan idénticos.
Los paquetes anteriores se conservan; los nuevos tienen nombres distintos.

El menú ahora ofrece órdenes explícitas. Atacar utiliza canAttack y
doSummonAttack del motor, con la misma validación para el botón nativo. Un target
inválido produce un mensaje: la prueba está limitada a enemigos de zona PvP y
no permite atacar al NPC del contrato ni a aliados. Seguir/detener no interrumpen
la carga de lluvia. Retirar fuera de combate conserva el contrato.

## Verificación y archivos

45 comprobaciones pasaron con AmberOwnerProbe y AmberTargetProbe, cuenta
ambercontracttest, en una instancia privada. Ambos quedaron offline y la instancia
se destruyó. Cubren contrato, habilidades, daño real contra Player, shots, fuego,
carga, movimiento, salida de zona, interrupción y ruptura con carga pendiente.
Además comprueban la ruta real menú → SummonAI → daño, seguir/detener y el bloqueo
de órdenes durante la carga. No usan al usuario ni a los rivales. En esta ejecución
una lluvia ígnea sumó1883,75 y una normal1622,91
contra ese probe equipado; no son valores universales ni una calibración final.

Corrección del botón, 09/10: el cliente enviaba `Quest AmberContract accept`,
pero esta versión del servidor no registra el bypass `Quest`. El menú ahora usa
`voice .amber firmar` y `voice .amber romper`. Firmar exige seleccionar el NPC
Amber y estar cerca. La prueba ampliada entra por BypassHandler/VoiceCommand,
comprueba el rechazo de otro target y firma por la misma ruta que el botón.

Prueba opcional: `Start-L2Local.ps1 -VerifyAmberContract` al iniciar con servidor
detenido y cliente cerrado. Desactivada por defecto. Registro:
`backups/amber-contract-2026-10-09/motion-fix/verify-45-controls-checks.log`.
Manifest: `reports/amber-contract-verification.json`.

Scripts: `server/game/data/scripts/custom/AmberContract/` y efecto AmberOrder.
Datos: `stats/npcs/custom/amber_summon.xml`, `stats/skills/custom/amber_contract.xml`,
PetSkillData.xml. Su XSD admite NPC IDs int, igual que el lector Java existente.
GameServer.jar se conservó: SHA256
AB6DC1C692B98FB489F3D5BC8B5C3323C0DADCCF7BFCF89B63BA7E5DA5A5AA38.

Backups: `backups/amber-contract-2026-10-09`. Instalador del cliente:
`research/amber-l2/Install-AmberContract.ps1`, que rechaza catálogos con cambios
desconocidos. Corrección de movimiento: `research/amber-l2/Install-AmberMotionFix.ps1`.
También valida los archivos descifrados antes de instalar y guarda respaldo.
Scripts reproducibles en `research/amber-l2/scripts`; requieren los
recursos originales locales, UCC, Groovy/UnrealPackage, UModel y Blender.
Fuente/dist y overlay cloud se sincronizaron localmente, sin commit ni push.

Durante el reinicio apareció una incompatibilidad ajena a Amber: GroupAgite.java
usaba calculateDistance2D(x,y), aunque este core pide tres argumentos. Solo se
agregó getZ() a las dos llamadas; el cálculo 2D ignora ese argumento. Esto permite
cargar el conjunto de scripts. Se dejó una nota de coordinación en Nexus para
que la sesión que desarrolla GroupAgite conserve el ajuste.


## Controles nativos y animaciones, 10/10

Se instal? Attack para display59002 y dos acciones propias de Amber en la pesta?a Action del summon: Flechas de fuego y Lluvia de flechas. La clase AmberActorsV1.AmberArcher necesita su configuraci?n localizada en AmberActorsV1.int junto al paquete. Detalles, respaldo y verificaci?n en CONTINUIDAD-W11/11_AMBER_CONTROLES_ANIMACIONES_2026-10-10.md. Esta actualizaci?n modifica ?nicamente RequestActionUse.class del core para las dos acciones nuevas; el hash anterior documentado arriba corresponde al core previo. La apariencia en movimiento requiere observaci?n dentro de L2.

Prueba ampliada completada: 53 comprobaciones, incluidos los botones nativos de ataque, detener, fuego y lluvia. Registro: backups/amber-native-controls-2026-10-10/verify-53-checks.log. Archivo de animaciones localizado instalado en system-hud y system; reproducci?n visual pendiente de observar en L2.

## Efectos, fuego elemental y recargas, 10/10

Corrección instalada y verificada: 61 comprobaciones contra jugadores reservados. Fuego dura 15 segundos, con recarga de 30, PAtk +25% y poder de fuego +20; su indicador en el dueño muestra duración sin dar estadísticas. La recarga nativa se ve usando las habilidades de Alt+K en la barra. Los botones de Action ejecutan órdenes y no muestran la superposición de recarga de skills.

La lluvia cae en tres oleadas, con daño 650ms después de cada efecto de caída y resumen de impactos/daño en el chat. Las pruebas confirmaron tres impactos, evasión al salir de la zona y continuidad si Amber se mueve después del lanzamiento. Ver CONTINUIDAD-W11/12_AMBER_VFX_ENFRIAMIENTO_2026-10-10.md y reports/amber-combat-vfx-verification.json. Falta observar los nuevos efectos en el cliente.

## Amber VFX V3 en W10 — 10/10/2026

Instalada corrección de encendido de fuego y carga de soulshot en mano/arco,
lluvia circular de 30 flechas por oleada, destellos de impacto sincronizados a
650ms y trazas de fuego por distancia con origen vertical corregido. Recursos:
AmberEffectsV3.usk y AmberParticlesV3.u. Prueba aislada 64 checks PASS, incluidos
radio199 dentro/radio201 fuera; probes offline y arranque normal con 19 perfiles.
No cambian core ni balance. Ver CONTINUIDAD-W10/14_AMBER_VFX_V3_2026-10-10.md
 y reports/amber-vfx-v3-verification.json. La reproducción dentro de L2 todavía
requiere revisión visual. Respaldo backups/amber-vfx-v3-2026-10-10. Sin commit/push.

## Amber IA — actualización 10/10/2026
Asistencia autónoma instalada; 104 comprobaciones PASS. Nueva invocación empieza en IA, `.amber auto` reactiva, `.amber manual` y Seguir/Detener desactivan la asistencia. Detecta Anchor, Lightning Strike, controles de cubics y UD; evalúa concentración y daño/riesgo de lluvia. Documentación actual: `AMBER-ASISTENCIA-IA.md` en la raíz y `CONTINUIDAD-W10/16_AMBER_ASISTENCIA_IA_2026-10-10.md`. Fuente/cloud sincronizados, core y cliente preservados. Próximo paso: probar otro TvT y analizar AMBER_AI junto con la telemetría.


## 10/10/2026 — Activable de asistencia

Estado actual: cinco habilidades temporales, incluida **Asistencia de Amber** 19014. Nueva invocación empieza manual. Desde Alt+K/barra un clic enciende IA y otro la apaga; Seguir/Detener limpian también el indicador. Detalles en `AMBER-ASISTENCIA-ACTIVABLE.md`.
