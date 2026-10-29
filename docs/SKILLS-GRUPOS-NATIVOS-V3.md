# Habilidades por clase: catalogo nativo V3 — 10/10/2026

Instalado en el cliente habitual `l2/system-hud` que abre `2-JUGAR.cmd`.

## Uso

Abrir Alt+K. `Todas` muestra Principal, Subclase1-3, Comunes, Amber y Especiales (solo grupos con habilidades).
Cada grupo empieza debajo de una franja dorada gruesa de una fila completa. Se rellena el final de la fila anterior para que la siguiente clase no se mezcle en ella.
Las pestanas activas/pasivas conservan la separacion y el scroll. Los iconos reales se siguen arrastrando a la barra.

`Principal`, `Sub1`, `Sub2`, `Sub3` filtran una clase; incluyen sus habilidades compartidas compatibles.
`Siguiente clase >` recorre unicamente la principal y las subclases existentes, y vuelve a la primera. En chat informa nombre y posicion (por ejemplo2/4).
Comunes y Amber tienen filtros separados; `Todas` restaura la lista completa. `Nombres / indice` abre el indice con nombres completos y recuentos.
Alternativas de chat: `.habilidades next`, `.habilidades quick -1`, `.habilidades`.

## Causas corregidas

El callback llamaba RequestBypassToServer como VirtualFunction aunque la funcion es final/nativa. Ahora usa el mismo FinalFunction/import que los callbacks originales del cliente.
El servidor exigia cache HTML a las llamadas del panel nativo. RequestBypassToServer ahora exime solo diez acciones exactas del catalogo/IA de Amber. Otros bypass conservan la validacion; quick valida ademas la clase poseida y se mantiene flood protection.
Los botones tienen texto en su propia textura, sin TextBox superpuesto sobre la superficie que recibe el clic.

## Presentacion y preservacion

Decoracion de UI19100-19141 y relleno19199 solo en SkillList, nunca concedidos ni definidos como skills del servidor. En el cliente se convierten en elementos bloqueados con ClassID/Level/ItemSubType cero, comando vacio y guardia que impide UseSkill(0). Columnas6, iconos32, gapX0 para franja continua.
Nuevo paquete aislado SkillGroupsV3.utx con70 texturas, wrapper Lineage2Ver121 con clave de nombre, checksum y decode verificados. Catalogos DAT413 agregan43 filas; todas las filas previas, incluido AmberV10, son identicas.
Interface.u cambia solo cuatro funciones: MagicSkillWnd.OnClickButton/OnClickItem/HandleSkillList y SummonedWnd.OnClickButton. XDAT cambia solo MagicSkillWnd. JAR cambia SkillList, SkillCatalogView/Model y RequestBypassToServer. El resto es identico a respaldo; no se cambian estadisticas, habilidades aprendidas, clase, accesos rapidos ni Amber/roster.

## Validacion y estado

1312 comprobaciones PASS: wire/opcode/recuento, atributos de cada skill real, franjas y alineacion independientes activa/pasiva, filtros completos y compartidos, toggle Amber, whitelist exacta, recorrido de1-4 clases mediante handler nativo registrado y ausencia de mutaciones de juego.
Paquete recompilado y releido: saltos VM correctos, import final nativo correcto y guardia de cero validos. DAT y textura roundtrip/checksum PASS. Roster19/19 preparado.
Verificacion automatica one-shot terminada y probe offline retirado. Servidor disponible; el proximo arranque habitual lleva verify=false. Falta validar el aspecto y clics dentro del cliente con el usuario: estos checks no equivalen a una captura de Alt+K en juego.
Una primera corrida del verificador fallo al intentar construir Script fuera del cargador; se corrigio para usar el handler registrado. Segunda corrida PASS completa. La causa fue del verificador, no del filtro de produccion.

Respaldo: `backups/skill-groups-v3-2026-10-10`. Pruebas/hashes/build: `research/client-comfort/v3`. Fuente/runtime/cloud sincronizados sin commit/push. Mantener juntas las carpetas l2 y l2-local al llevar el disco.
