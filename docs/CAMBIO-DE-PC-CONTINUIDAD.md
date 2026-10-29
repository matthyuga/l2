# Continuidad entre PCs: retorno a Windows 10

## Nueva bitácora de diseño y comunidad — 28/10/2026

Para retomar la conversación del 27–28/10, leer primero
[BITACORA-DISENO-COMUNIDAD-AVENTURAS-20261028.md](BITACORA-DISENO-COMUNIDAD-AVENTURAS-20261028.md).
Incluye rendimiento y población investigada, salas de clases experimentales,
Project Gorgon/The Endless Forest, aventuras sociales, fortaleza caminante,
torretas, tesorería de ciudades y 55 paquetes nuevos pendientes de revisión.
Son propuestas, no funciones instaladas. Copias idénticas en CONTINUIDAD-W10
y CONTINUIDAD-W11. Esta actualización guarda documentación; no constituye un
respaldo de la base ni una migración de la instalación. La letra del disco puede cambiar.
Las secciones siguientes conservan información histórica de otras sesiones.

Actualización de cierre del 10/10/2026: leer primero
**[CONTINUIDAD-W10/LEER-PRIMERO.md](CONTINUIDAD-W10/LEER-PRIMERO.md)**.
Incluye el estado final de Amber (61 comprobaciones), los efectos pendientes
de observar, Coliseo y GroupAgite, rutas y pasos de salida/arranque.
Inventario con hashes: `CONTINUIDAD-W10/inventario-2026-10-10.json`.
SQL y 54 copias verificadas de archivos clave:
`backups/retorno-w10-2026-10-10/`. Se tomó con el personaje conectado;
conservar la base operativa después del guardado y cierre limpio, sin restaurar
este SQL anterior sobre ella. Las secciones siguientes son el traslado previo
a W11 y no sustituyen la nueva bitácora de retorno.

Preparación revisada el 09/10/2026. No se hicieron reinicios, exportaciones de
base, transferencias ni commit/push durante esta revisión.

## Estado posterior en Windows 11

Validado el 10/10/2026 con la unidad como `D:`. Servidor, base, panel y cliente
`system-hud` iniciaron correctamente. El Game Server tardó 315 segundos en el
primer arranque frío, por lo que el lanzador ahora espera hasta 600 segundos.
El roster cerró `SUCCESS 19/19` y copias `7/7`. Consultar
`CONTINUIDAD-W11/07_VALIDACION_W11_2026-10-10.md` para el detalle y los ensayos
visuales/manuales pendientes.

## Estado que debe conservarse

- Proyecto operativo: `E:\l2-local`.
- Cliente operativo: `E:\l2`, perfil `system-hud`, launcher `2-JUGAR.cmd`
  en la raíz del proyecto.
- Repo de continuidad local: `E:\l2-local\cloud-repo`.
- Nexus: `K:\_CodexNexus`, resumen `sessions\lineage2-local.md` y notas
  recientes de Lineage2 en `inbox`.
- El repo local tiene modificaciones y archivos nuevos sin commit/push.
  Clonar GitHub no recupera por sí solo el estado actual.
- Git excluye base activa, cuentas/personajes, configuración privada, cliente,
  JARs, runtimes y herramientas. Es necesario conservarlos por separado si se
  quiere ejecutar una réplica completa.

## Coordinación antes de una copia definitiva

La sesión Amber cedió el GameServer a la sesión GroupAgite para una prueba
aislada 4vs4. Coordinar con esa sesión antes de detener servicios o tomar el
respaldo final. No activar verificadores optativos al iniciar normalmente.

Amber tiene 45 checks de servidor PASS y los probes quedaron offline. Sus
animaciones y altura corregidas siguen pendientes de revisión visual en L2.
Leer `AMBER-CONTRATO-SUMMON.md` y el informe
`reports\amber-contract-verification.json`.

Para GroupAgite, consultar el estado FINAL de la otra sesión y
`AGITE-GRUPAL-4VS4.md`; esta revisión no declara terminada su autoprueba.

## Si la PC actual seguirá alojando el proyecto

Mantenerla encendida y sin suspensión durante el uso remoto. Comprobar el
acceso desde Windows 11 antes de salir. `localhost`/`127.0.0.1` en la segunda
PC se refieren a la segunda PC, no a este servidor. Definir acceso remoto o
conectividad privada antes de cambiar direcciones/configuración del cliente.

## Si se ejecutará una copia independiente en Windows 11

Preparar el código y scripts actuales, runtime del servidor y su configuración,
herramientas portátiles necesarias y cliente actualizado. Conservar el conjunto
completo de recursos de Amber: no basta copiar únicamente sus archivos DAT.

Respaldar la base mediante una exportación SQL consistente, coordinada después
de la prueba y del guardado de personajes. No copiar `database\data` como respaldo
mientras MariaDB esté escribiendo. Una copia física requiere cierre limpio de
MariaDB o un mecanismo de backup físico consistente.

Restaurar primero en una base independiente, revisar rutas y configuración en
la nueva PC y comprobar personaje/equipo/subclases/perfiles raciales, summons,
cliente y panel. Definir cuál PC será la copia principal para evitar mezclar
dos bases de personajes que hayan evolucionado por separado.

Las credenciales y datos de personajes se transfieren por una vía privada;
no se añaden al repositorio público.

## Para continuar solamente la sesión de trabajo

Conservar este documento, las notas Nexus recientes y el repo LOCAL actual,
incluidos sus archivos sin seguimiento. La continuidad de conversación no
traslada automáticamente archivos, servidor ni acceso al disco de esta PC.


# Fafurion Weapons integradas — 12/10/2026

E:\l2-local. Pack recibido en descarga de assets/Fafurion_Weapons_H5_IL.rar; SHA256 176bae09025d96eeda562e6d32f96d342647500ad7f24c22952b9ad53f511f04. Cliente activo E:\l2\system-hud: dos DAT preservan 1313/9208 registros originales byte por byte y añaden siete; tres paquetes .u nuevos. IDs 54130–54136, XML 54100-54199.xml en runtime/source/cloud local. Base S sin SA/procs: Avenger281/132, Cutter281/132, Fighter342/132, Singer274/193 mágico (pack175 corregido), Shaper246/132, Stormer281/132 con skill3599/1 normal, Dual342/132 sin bonusPvP/+4 heredado. Material cliente8 y marca hero retirada.

CRC/codec413 roundtrip/hashes/refs y seis mallas+materiales exportados PASS. Parser nativo y funciones de stats S/tipos/skills PASS; siete templates agregados al GS17204 sin restart y sin reemplazar los existentes. XML se carga normalmente al próximo arranque. No se cambiaron core/métodos, personajes, inventarios ni DB; no se entregaron armas automáticamente. //create_item ID 1 con GM. Revisión visual ingame pendiente. No ejecutar build/install/agente como actualizadores; verificador read-only disponible.

Sockets son propuesta, NO implementación: tres slots por instancia, atributos y resonancias por bajas/daño/HP/CP efectivos. ItemVariables/eventos y callbacks de Heal/CP existen; hace falta lógica de sockets, persistencia consistente y observador de curación desacoplado de Amber, con origen/HP/CP. No hay gemas/poderes nuevos activos.

Documentos FAFURION-ARMAS-INTEGRACION.md y FAFURION-SOCKETS-PROPUESTA.md. Código/manifiestos/pruebas research/fafurion-weapons; backup backups/fafurion-weapons-20261012-202625. Preservar cliente activo completo al mover PC. Antes de deshacer revisar objetos persistidos y hashes: no quitar templates con instancias ni sobrescribir DAT con adiciones posteriores. Cloud local conserva código/docs/XML; no binarios del pack, sin commit/push.


## Fafurion en GM Shop — 12/10/2026

Por pedido de Kevin, siete armas54130–54136 a +0 disponibles en boton Fafurion de Mirella50010/Weapons (multisell50035413, 48.800.000 Adena cada una) y //gmshop/Weapons (buylist54130, gratis como otras listas administrativas). Cuatro HTML y dos XML nuevos sincronizados runtime/source/cloud local. Parser nativo verifica productos/precios/NPC y cache HTML; listas cargadas individualmente en GS17204, sin restart ni cambios de personajes/inventario. No se compro con personajes del usuario. No cambiar DAT/cliente. Backup backups/fafurion-shop-20261012-204201; research/fafurion-weapons/shop-installation.json y shop-verification.txt PASS. No reejecutar add_shop.py ni agente de carga. Documentacion FAFURION-ARMAS-INTEGRACION.md actualizada. Sin commit/push.


## Fafurion V2: shop y tooltip — 12/10/2026

Kevin mostró capturas: Avenger comprado/equipado e inventario281/132 correcto; multisell mostraba null/0/vacíos y tooltip arrastraba SA ajena. Corregidos alias visuales24130–24136 (campo short de MultiSellList salía negativo para54130–54136) y terminador NUL faltante en descripciones. DAT mantiene entradas altas y añade7alias; originales ajenos1313/9208 intactos. Templates54130–54136 ahora displayId24130–24136 en runtime/source/cloud; solo campo displayId cambiado en objetos de GS17204, sin reemplazar templates ni DB/inventarios/armas compradas/stats/precios. Itemnames14 Fafurion terminados; descripción simple Arma de grado S. No hay SA real nueva.

L2 se observó cerrado e instalación hecha. Verificación incluye paquete multisell real antes/después: signedshort negativo reproducido,7IDs positivos después; costes e IDs persistentes de productos conservados. verify_installation.py PASS actualizado aV2. Confirmación visual tras reabrir pendiente. Backup backups/fafurion-client-fix-v2-20261012-205047, manifiestos originales archivados; stage y pruebas research/fafurion-weapons/client-fix-v2. No reejecutar instaladores/agentes. Conservar cliente alias+XMLdisplayId juntos en otra PC. Rootdoc/README/continuidad/cloud actualizados, sin commit/push.
